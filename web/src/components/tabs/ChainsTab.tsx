import type { ParsedReport, AnalysisResult } from '../../types'

interface Props { parsed: ParsedReport; analysis: AnalysisResult }

export default function ChainsTab({ parsed, analysis }: Props) {
  const chains = analysis.interaction_chains ?? []
  const widgets = parsed.widgets

  return (
    <div className="space-y-5">
      {chains.length === 0 ? (
        <div className="rounded-lg px-4 py-6 text-center text-[13px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
          暂无 AI 推断的交互链路。可能是报表没有参数控件，或控件逻辑需要人工在深度证据中继续确认。
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {chains.map((chain, i) => (
            <div key={`${chain.widget_name}-${i}`} className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
              <div className="mb-3 flex items-center gap-2 border-b pb-2" style={{ borderColor: 'var(--border)' }}>
                <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
                  {i + 1}
                </span>
                <span className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>{chain.widget_name}</span>
                {chain.widget_type && (
                  <span className="ml-auto rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-500">
                    {chain.widget_type}
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {([
                  ['作用', chain.param_role],
                  ['SQL 影响', chain.sql_impact],
                  ['展示影响', chain.data_displayed],
                  ['设计原因', chain.why_this_design],
                ] as [string, string | undefined][]).map(([label, val]) =>
                  val ? (
                    <div key={label} className="flex gap-2 text-[12.5px] leading-5">
                      <span className="mt-0.5 min-w-[52px] text-[10px] font-bold uppercase" style={{ color: 'var(--text-muted)' }}>{label}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{val}</span>
                    </div>
                  ) : null
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {widgets.length > 0 && (
        <details>
          <summary className="flex cursor-pointer list-none items-center gap-1.5 py-1 text-[13px] font-semibold" style={{ color: 'var(--text-secondary)' }}>
            参数控件汇总表（{widgets.length} 个）
          </summary>
          <div className="mt-2 overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
            <table className="w-full text-[12px]">
              <thead style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
                <tr>{['控件名', '类型', '数据来源', 'key 字段', '显示字段'].map(h => (
                  <th key={h} className="px-3 py-2 text-left font-semibold">{h}</th>
                ))}</tr>
              </thead>
              <tbody>
                {widgets.map((widget, i) => (
                  <tr key={`${widget.name}-${i}`} style={{ borderTop: '1px solid var(--border)' }}>
                    <td className="px-3 py-2 font-mono" style={{ color: 'var(--text-primary)' }}>{widget.name}</td>
                    <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{widget.widget_type}</td>
                    <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{widget.bound_dataset ?? '直接输入或未识别'}</td>
                    <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{widget.key_column ?? '-'}</td>
                    <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{widget.display_column ?? '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </div>
  )
}
