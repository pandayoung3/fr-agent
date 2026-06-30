import { useCallback, useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import type { ParsedReport, LineageResult } from '../../types'

interface Props {
  parsed: ParsedReport
  lineage: LineageResult | null
  onLoadLineage: () => void
}

mermaid.initialize({ startOnLoad: false, theme: 'default', flowchart: { curve: 'basis' } })

let _mermaidCounter = 0

export default function LineageTab({ parsed, lineage, onLoadLineage }: Props) {
  const [svgHtml, setSvgHtml] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const requestedRef = useRef(false)

  const renderMermaid = useCallback(async (raw: string) => {
    // Strip markdown code fences if present
    let code = raw.trim()
    if (code.startsWith('```mermaid')) code = code.slice(10)
    if (code.startsWith('```')) code = code.slice(3)
    if (code.endsWith('```')) code = code.slice(0, -3)
    code = code.trim()
    if (!code) return

    setLoading(true)
    try {
      const id = `mermaid-${++_mermaidCounter}`
      const { svg } = await mermaid.render(id, code)
      setSvgHtml(svg)
    } catch (e) {
      console.error('Mermaid render error', e)
      setSvgHtml(`<pre class="text-xs text-red-500 p-2">${String(e)}</pre>`)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!lineage) {
      if (!requestedRef.current) {
        requestedRef.current = true
        onLoadLineage()
      }
      return
    }

    requestedRef.current = false
    const renderTimer = window.setTimeout(() => {
      void renderMermaid(lineage.mermaid_raw || lineage.mermaid)
    }, 0)

    return () => window.clearTimeout(renderTimer)
  }, [lineage, onLoadLineage, renderMermaid])

  const datasets = parsed.datasets

  return (
    <div className="space-y-5">
      {/* 血缘图 */}
      <div>
        <div className="text-xs text-slate-400 mb-3">
          🔵 参数控件 &nbsp;|&nbsp; 🟢 SQL 数据集 &nbsp;|&nbsp; 🟠 展示字段 &nbsp;|&nbsp; ⚪ 控件选项数据集
        </div>

        {loading && (
          <div className="flex items-center gap-2 text-sm text-slate-400 py-8 justify-center">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            加载血缘图...
          </div>
        )}

        {!loading && lineage && lineage.sql_driving_widget_names.length === 0 && (
          <div className="text-sm text-slate-400 bg-slate-50 rounded-xl p-4">
            未找到控件→SQL参数的直接连接（所有数据集为嵌入式或参数名不匹配）
          </div>
        )}

        {!loading && svgHtml && (
          <div
            ref={containerRef}
            className="mermaid-container bg-slate-50 border border-slate-100 rounded-xl p-4 overflow-x-auto"
            dangerouslySetInnerHTML={{ __html: svgHtml }}
          />
        )}

        {lineage && (lineage.unmatched_widget_names ?? []).length > 0 && (
          <div className="text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2 mt-2">
            ⚠️ 未找到 SQL 参数连接的控件（{lineage.unmatched_widget_names.length} 个）：
            {lineage.unmatched_widget_names.slice(0, 8).join('、')}
            {lineage.unmatched_widget_names.length > 8 ? '...' : ''}
            <br />这些控件可能通过单元格过滤条件或前端 JS 实现筛选，需人工核实。
          </div>
        )}
      </div>

      {/* 数据集详情 */}
      {datasets.length > 0 && (
        <details>
          <summary className="cursor-pointer text-sm font-semibold text-slate-500 hover:text-blue-600 list-none flex items-center gap-1.5 py-1">
            <span className="text-xs">▶</span> 数据集详情（{datasets.length} 个）
          </summary>
          <div className="mt-3 space-y-3">
            {datasets.map((ds, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-xl p-3">
                <div className="text-sm font-semibold text-slate-700 mb-1.5">
                  {ds.type === 'DBTableData' ? '🗄️ DB查询' : '📋 内嵌数据'} · {ds.name}
                </div>
                {ds.db_connection && (
                  <div className="text-xs text-slate-400 mb-1">连接：<code className="bg-slate-100 px-1 rounded">{ds.db_connection}</code></div>
                )}
                {(ds.columns ?? []).length > 0 && (
                  <div className="text-xs text-slate-400 flex flex-wrap gap-1 mt-1">
                    {ds.columns!.slice(0, 20).map(c => (
                      <code key={c} className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{c}</code>
                    ))}
                    {ds.columns!.length > 20 && <span className="text-slate-300 italic">+{ds.columns!.length - 20} 列</span>}
                  </div>
                )}
                {ds.sql && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-xs text-slate-400 hover:text-blue-500 list-none">▶ SQL</summary>
                    <pre className="mt-1 text-xs bg-slate-800 text-slate-100 rounded-lg p-3 overflow-x-auto">{ds.sql}</pre>
                    {(ds.sql_params ?? []).length > 0 && (
                      <div className="text-xs text-slate-400 mt-1">动态参数：{ds.sql_params!.join(', ')}</div>
                    )}
                  </details>
                )}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
