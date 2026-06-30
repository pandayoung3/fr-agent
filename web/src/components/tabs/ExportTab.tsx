import { useState } from 'react'
import type { ParsedReport, AnalysisResult } from '../../types'
import { exportMarkdown, exportHtml, downloadBlob } from '../../api'

interface Props { parsed: ParsedReport; analysis: AnalysisResult }

export default function ExportTab({ parsed, analysis }: Props) {
  const stem = parsed.file_name.replace(/\.cpt$/i, '')
  const [mdContent, setMdContent] = useState<string | null>(null)
  const [htmlContent, setHtmlContent] = useState<string | null>(null)
  const [loadingMd, setLoadingMd] = useState(false)
  const [loadingHtml, setLoadingHtml] = useState(false)
  const [mdPreview, setMdPreview] = useState(false)
  const [htmlPreview, setHtmlPreview] = useState(false)

  async function handleMd() {
    if (!mdContent) {
      setLoadingMd(true)
      try { setMdContent(await exportMarkdown(parsed, analysis)) }
      catch (e) { alert(String(e)) }
      finally { setLoadingMd(false) }
    }
    setMdPreview(v => !v)
  }

  async function handleHtml() {
    if (!htmlContent) {
      setLoadingHtml(true)
      try { setHtmlContent(await exportHtml(parsed, analysis)) }
      catch (e) { alert(String(e)) }
      finally { setLoadingHtml(false) }
    }
    setHtmlPreview(v => !v)
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Markdown */}
      <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
        <div>
          <h4 className="text-sm font-bold text-slate-700 mb-1">📄 Markdown 交接文档</h4>
          <p className="text-xs text-slate-400">适合粘贴到 Confluence / Notion / 飞书文档</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleMd}
            disabled={loadingMd}
            className="flex-1 text-xs py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600
              font-semibold transition-colors disabled:opacity-50"
          >
            {loadingMd ? '生成中...' : mdPreview ? '▲ 收起预览' : '👁️ 预览'}
          </button>
          {mdContent && (
            <button
              onClick={() => downloadBlob(mdContent, `${stem}_交接文档.md`, 'text/markdown')}
              className="flex-1 text-xs py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white
                font-semibold transition-colors"
            >
              ⬇️ 下载 MD
            </button>
          )}
        </div>
        {mdPreview && mdContent && (
          <div className="mt-2 overflow-auto max-h-96 rounded-xl border border-slate-100">
            <pre className="text-xs p-4 text-slate-600 whitespace-pre-wrap leading-relaxed">{mdContent}</pre>
          </div>
        )}
      </div>

      {/* HTML */}
      <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-3">
        <div>
          <h4 className="text-sm font-bold text-slate-700 mb-1">🌐 HTML 交接文档</h4>
          <p className="text-xs text-slate-400">自包含 HTML，含目录导航、血缘图、可折叠章节，可另存 PDF</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleHtml}
            disabled={loadingHtml}
            className="flex-1 text-xs py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600
              font-semibold transition-colors disabled:opacity-50"
          >
            {loadingHtml ? '生成中...' : htmlPreview ? '▲ 收起预览' : htmlContent ? '👁️ 预览' : '⚙️ 生成预览'}
          </button>
          {htmlContent && (
            <button
              onClick={() => downloadBlob(htmlContent, `${stem}_交接文档.html`, 'text/html')}
              className="flex-1 text-xs py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white
                font-semibold transition-colors"
            >
              ⬇️ 下载 HTML
            </button>
          )}
        </div>
        {htmlPreview && htmlContent && (
          <div className="mt-2 rounded-xl overflow-hidden border border-slate-100">
            <p className="text-[10px] text-slate-400 text-center py-1 bg-slate-50">
              💡 下载后在浏览器中打开效果更佳
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
      </div>
    </div>
  )
}
