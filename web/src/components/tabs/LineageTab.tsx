import { useCallback, useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import type { ParsedReport, LineageResult } from '../../types'

interface Props {
  parsed: ParsedReport
  lineage: LineageResult | null
  onLoadLineage: () => void
}

mermaid.initialize({ startOnLoad: false, theme: 'default', flowchart: { curve: 'basis' } })

let mermaidCounter = 0

export default function LineageTab({ parsed, lineage, onLoadLineage }: Props) {
  const [svgHtml, setSvgHtml] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const requestedRef = useRef(false)

  const renderMermaid = useCallback(async (raw: string) => {
    let code = raw.trim()
    if (code.startsWith('```mermaid')) code = code.slice(10)
    if (code.startsWith('```')) code = code.slice(3)
    if (code.endsWith('```')) code = code.slice(0, -3)
    code = code.trim()
    if (!code) return

    setLoading(true)
    try {
      const id = `mermaid-${++mermaidCounter}`
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

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-2 text-[11px]">
        <Legend color="#2563eb" label="参数控件" />
        <Legend color="#059669" label="SQL / 数据集" />
        <Legend color="#d97706" label="展示字段" />
        <Legend color="#7c3aed" label="控件选项数据集" />
      </div>

      {loading && (
        <div className="flex items-center justify-center gap-2 py-8 text-[13px]" style={{ color: 'var(--text-muted)' }}>
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" />
          正在加载数据血缘图...
        </div>
      )}

      {!loading && lineage && lineage.sql_driving_widget_names.length === 0 && (
        <div className="rounded-lg p-4 text-[13px]" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
          未找到控件到 SQL 参数的直接连接。可能是内置数据集、参数名不匹配，或通过单元格过滤 / JS / 其他配置实现。
        </div>
      )}

      {!loading && svgHtml && (
        <div
          ref={containerRef}
          className="mermaid-container overflow-x-auto rounded-lg p-4"
          style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
          dangerouslySetInnerHTML={{ __html: svgHtml }}
        />
      )}

      {lineage && (lineage.unmatched_widget_names ?? []).length > 0 && (
        <div className="rounded-lg px-3 py-2 text-[12px] leading-5" style={{ background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }}>
          未找到 SQL 参数连接的控件（{lineage.unmatched_widget_names.length} 个）：
          {lineage.unmatched_widget_names.slice(0, 8).join('、')}
          {lineage.unmatched_widget_names.length > 8 ? '...' : ''}
          <br />
          这些控件可能通过单元格过滤条件或前端 JS 实现筛选，需要人工复核。
        </div>
      )}

      {parsed.datasets.length > 0 && (
        <details>
          <summary className="flex cursor-pointer list-none items-center gap-1.5 py-1 text-[13px] font-semibold" style={{ color: 'var(--text-secondary)' }}>
            数据集详情（{parsed.datasets.length} 个）
          </summary>
          <div className="mt-3 space-y-3">
            {parsed.datasets.map((dataset, index) => (
              <div key={`${dataset.name}-${index}`} className="rounded-lg p-3" style={{ background: '#fff', border: '1px solid var(--border)' }}>
                <div className="mb-1.5 text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {dataset.type === 'DBTableData' ? 'DB 查询' : '内置/非 DB 数据'} · {dataset.name}
                </div>
                {dataset.db_connection && (
                  <div className="mb-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>连接：<code className="rounded bg-slate-100 px-1">{dataset.db_connection}</code></div>
                )}
                {(dataset.columns ?? []).length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1 text-[11px]">
                    {dataset.columns!.slice(0, 20).map(column => (
                      <code key={column} className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-600">{column}</code>
                    ))}
                    {dataset.columns!.length > 20 && <span className="italic text-slate-400">+{dataset.columns!.length - 20} 列</span>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md px-2 py-1" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
      <span className="h-2 w-2 rounded-full" style={{ background: color }} />
      {label}
    </span>
  )
}
