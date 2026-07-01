import type {
  ParsedReport,
  BatchParseResult,
  AnalysisResult,
  LineageResult,
  ChatMessage,
  ScoreResult,
  FormulaValidationResult,
  ChangeImpactResult,
  LlmConfig,
  LlmTestResult,
} from './types'

const BASE = '/api'

// ── helpers ───────────────────────────────────────────────────────────────────

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`API ${path} failed (${res.status}): ${text}`)
  }
  return res.json() as Promise<T>
}

// ── SSE helper ────────────────────────────────────────────────────────────────
// onEvent 每次收到 data: {...} 行时被调用，返回值 true 表示提前终止

export type SseEvent = { type: string; [key: string]: unknown }

export async function ssePost(
  path: string,
  body: unknown,
  onEvent: (event: SseEvent) => boolean | void,
): Promise<void> {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`SSE ${path} failed (${res.status}): ${text}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6)) as SseEvent
          const stop = onEvent(event)
          if (stop) { reader.cancel(); return }
        } catch { /* ignore malformed */ }
      }
    }
  }
}

// ── API 函数 ──────────────────────────────────────────────────────────────────

export async function parseCpt(file: File): Promise<ParsedReport> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/parse`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`解析失败 (${res.status})`)
  return res.json()
}

export async function parseBatchCpts(files: File[]): Promise<BatchParseResult> {
  const form = new FormData()
  files.forEach(file => form.append('files', file))
  const res = await fetch(`${BASE}/batch/parse`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`批量解析失败 (${res.status})`)
  return res.json()
}

export async function getFrConnections(frWebinfDir: string): Promise<Record<string, unknown>> {
  return post('/fr-connections', { fr_webinf_dir: frWebinfDir })
}

export async function enrichParsed(
  parsed: ParsedReport,
  frWebinfDir: string,
  passwords: Record<string, string>,
): Promise<{ parsed: ParsedReport; report: { success: string[]; failed: unknown[]; skipped: string[] } }> {
  return post('/enrich', { parsed, fr_webinf_dir: frWebinfDir, passwords })
}

export function streamAnalyze(
  parsed: ParsedReport,
  onEvent: (event: SseEvent) => boolean | void,
): Promise<void> {
  return ssePost('/analyze', { parsed }, onEvent)
}

export function streamChat(
  parsed: ParsedReport,
  analysis: AnalysisResult,
  question: string,
  history: ChatMessage[],
  onEvent: (event: SseEvent) => boolean | void,
): Promise<void> {
  return ssePost('/chat', { parsed, analysis, question, history }, onEvent)
}

export async function exportMarkdown(parsed: ParsedReport, analysis: AnalysisResult): Promise<string> {
  const res = await fetch(`${BASE}/export/markdown`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parsed, analysis }),
  })
  if (!res.ok) throw new Error('导出 Markdown 失败')
  return res.text()
}

export async function exportHtml(parsed: ParsedReport, analysis: AnalysisResult): Promise<string> {
  const res = await fetch(`${BASE}/export/html`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parsed, analysis }),
  })
  if (!res.ok) throw new Error('导出 HTML 失败')
  return res.text()
}

export async function getLineage(parsed: ParsedReport): Promise<LineageResult> {
  return post('/lineage', { parsed })
}

export async function scoreReport(
  parsed: ParsedReport,
  analysis: AnalysisResult,
  lineage: LineageResult | null,
): Promise<ScoreResult> {
  return post('/score', { parsed, analysis, lineage })
}

export async function validateFormulas(parsed: ParsedReport): Promise<FormulaValidationResult> {
  return post('/validate/formulas', { parsed })
}

export async function analyzeChangeImpact(
  parsed: ParsedReport,
  analysis: AnalysisResult,
  changeRequest: string,
  lineage: LineageResult | null,
): Promise<ChangeImpactResult> {
  return post('/change-impact', { parsed, analysis, change_request: changeRequest, lineage })
}

export async function getLlmConfig(): Promise<LlmConfig> {
  const res = await fetch(`${BASE}/llm/config`)
  if (!res.ok) throw new Error('LLM 配置读取失败')
  return res.json()
}

export async function testLlmConfig(): Promise<LlmTestResult> {
  return post('/llm/test', {})
}

// ── 工具 ──────────────────────────────────────────────────────────────────────

export function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
