import type { AnalysisResult, ParsedReport } from './types'

const KEY = 'fr-agent-analysis-history'
const EXPORT_KEY = 'fr-agent-export-history'
const LIMIT = 8

export interface AnalysisHistoryItem {
  id: string
  created_at: string
  file_name: string
  purpose?: string
  report_type: string
  parsed: ParsedReport
  analysis: AnalysisResult
}

export interface ExportHistoryItem {
  id: string
  created_at: string
  file_name: string
  format: 'markdown' | 'html'
  action: 'preview' | 'download'
  filename: string
}

export function loadAnalysisHistory(): AnalysisHistoryItem[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveAnalysisHistory(parsed: ParsedReport, analysis: AnalysisResult): AnalysisHistoryItem[] {
  const next: AnalysisHistoryItem = {
    id: `${Date.now()}-${parsed.file_name}`,
    created_at: new Date().toISOString(),
    file_name: parsed.file_name,
    purpose: analysis.purpose,
    report_type: parsed.report_type,
    parsed,
    analysis,
  }

  const items = [next, ...loadAnalysisHistory().filter(item => item.file_name !== parsed.file_name)].slice(0, LIMIT)
  localStorage.setItem(KEY, JSON.stringify(items))
  return items
}

export function loadExportHistory(): ExportHistoryItem[] {
  try {
    const raw = localStorage.getItem(EXPORT_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveExportHistory(item: Omit<ExportHistoryItem, 'id' | 'created_at'>): ExportHistoryItem[] {
  const next: ExportHistoryItem = {
    ...item,
    id: `${Date.now()}-${item.format}-${item.action}-${item.file_name}`,
    created_at: new Date().toISOString(),
  }
  const items = [next, ...loadExportHistory()].slice(0, LIMIT)
  localStorage.setItem(EXPORT_KEY, JSON.stringify(items))
  return items
}
