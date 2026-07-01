import { useState } from 'react'
import type { AnalysisResult, ParsedReport } from '../../types'
import type { ExportHistoryItem } from '../../historyStore'
import { downloadBlob, exportHtml, exportMarkdown } from '../../api'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  onExportRecord: (item: Omit<ExportHistoryItem, 'id' | 'created_at'>) => void
}

export default function ExportTab({ parsed, analysis, onExportRecord }: Props) {
  const stem = parsed.file_name.replace(/\.cpt$/i, '')
  const mdFilename = `${stem}_handover.md`
  const htmlFilename = `${stem}_handover.html`
  const [mdContent, setMdContent] = useState<string | null>(null)
  const [htmlContent, setHtmlContent] = useState<string | null>(null)
  const [loadingMd, setLoadingMd] = useState(false)
  const [loadingHtml, setLoadingHtml] = useState(false)
  const [mdPreview, setMdPreview] = useState(false)
  const [htmlPreview, setHtmlPreview] = useState(false)

  async function ensureMarkdown() {
    if (mdContent) return mdContent
    setLoadingMd(true)
    try {
      const content = await exportMarkdown(parsed, analysis)
      setMdContent(content)
      return content
    } finally {
      setLoadingMd(false)
    }
  }

  async function ensureHtml() {
    if (htmlContent) return htmlContent
    setLoadingHtml(true)
    try {
      const content = await exportHtml(parsed, analysis)
      setHtmlContent(content)
      return content
    } finally {
      setLoadingHtml(false)
    }
  }

  async function handleMdPreview() {
    try {
      await ensureMarkdown()
      setMdPreview(v => !v)
      onExportRecord({ file_name: parsed.file_name, format: 'markdown', action: 'preview', filename: mdFilename })
    } catch (e) {
      alert(String(e))
    }
  }

  async function handleHtmlPreview() {
    try {
      await ensureHtml()
      setHtmlPreview(v => !v)
      onExportRecord({ file_name: parsed.file_name, format: 'html', action: 'preview', filename: htmlFilename })
    } catch (e) {
      alert(String(e))
    }
  }

  async function handleMdDownload() {
    try {
      const content = await ensureMarkdown()
      downloadBlob(content, mdFilename, 'text/markdown')
      onExportRecord({ file_name: parsed.file_name, format: 'markdown', action: 'download', filename: mdFilename })
    } catch (e) {
      alert(String(e))
    }
  }

  async function handleHtmlDownload() {
    try {
      const content = await ensureHtml()
      downloadBlob(content, htmlFilename, 'text/html')
      onExportRecord({ file_name: parsed.file_name, format: 'html', action: 'download', filename: htmlFilename })
    } catch (e) {
      alert(String(e))
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl p-4" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
        <div className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>交付导出</div>
        <p className="text-[12px] leading-relaxed mt-1" style={{ color: 'var(--text-secondary)' }}>
          导出是工作台理解结果的快照，适合交接、评审和留档。导出记录仅保存在当前浏览器本地。
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <section className="bg-white border border-slate-100 rounded-xl p-5 shadow-sm space-y-3">
          <div>
            <h4 className="text-sm font-bold text-slate-700 mb-1">Markdown 交接文档</h4>
            <p className="text-xs text-slate-400">适合粘贴到 Confluence、Notion、飞书文档等协作空间。</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleMdPreview}
              disabled={loadingMd}
              className="flex-1 text-xs py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600
                font-semibold transition-colors disabled:opacity-50"
            >
              {loadingMd ? '生成中...' : mdPreview ? '收起预览' : '预览'}
            </button>
            <button
              onClick={handleMdDownload}
              disabled={loadingMd}
              className="flex-1 text-xs py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white
                font-semibold transition-colors disabled:opacity-50"
            >
              下载 MD
            </button>
          </div>
          {mdPreview && mdContent && (
            <div className="mt-2 overflow-auto max-h-96 rounded-xl border border-slate-100">
              <pre className="text-xs p-4 text-slate-600 whitespace-pre-wrap leading-relaxed">{mdContent}</pre>
            </div>
          )}
        </section>

        <section className="bg-white border border-slate-100 rounded-xl p-5 shadow-sm space-y-3">
          <div>
            <h4 className="text-sm font-bold text-slate-700 mb-1">HTML 交接文档</h4>
            <p className="text-xs text-slate-400">自包含 HTML，适合本地预览、归档或另存为 PDF。</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleHtmlPreview}
              disabled={loadingHtml}
              className="flex-1 text-xs py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600
                font-semibold transition-colors disabled:opacity-50"
            >
              {loadingHtml ? '生成中...' : htmlPreview ? '收起预览' : '预览'}
            </button>
            <button
              onClick={handleHtmlDownload}
              disabled={loadingHtml}
              className="flex-1 text-xs py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white
                font-semibold transition-colors disabled:opacity-50"
            >
              下载 HTML
            </button>
          </div>
          {htmlPreview && htmlContent && (
            <div className="mt-2 rounded-xl overflow-hidden border border-slate-100">
              <p className="text-[10px] text-slate-400 text-center py-1 bg-slate-50">
                下载后在浏览器中打开效果更完整。
              </p>
              <iframe
                srcDoc={htmlContent}
                className="w-full"
                style={{ height: 420 }}
                sandbox="allow-scripts"
                title="HTML 预览"
              />
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
