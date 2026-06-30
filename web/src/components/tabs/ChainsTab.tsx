import type { ParsedReport, AnalysisResult } from '../../types'

interface Props { parsed: ParsedReport; analysis: AnalysisResult }

export default function ChainsTab({ parsed, analysis }: Props) {
  const chains = analysis.interaction_chains ?? []
  const widgets = parsed.widgets

  return (
    <div className="space-y-5">
      {chains.length === 0 ? (
        <div className="text-sm text-slate-400 text-center py-8">
          无交互链路（该报表可能无参数控件，或 AI 未能推断）
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {chains.map((chain, i) => (
            <div key={i} className="bg-white border border-slate-100 rounded-xl p-4 shadow-sm">
              <div className="text-sm font-bold text-blue-700 border-b border-blue-50 pb-2 mb-3 flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] flex items-center justify-center flex-shrink-0">{i + 1}</span>
                <span>{chain.widget_name}</span>
                {chain.widget_type && (
                  <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-mono ml-auto">
                    {chain.widget_type}
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {([
                  ['作用', chain.param_role],
                  ['SQL', chain.sql_impact],
                  ['展示', chain.data_displayed],
                  ['原因', chain.why_this_design],
                ] as [string, string | undefined][]).map(([label, val]) =>
                  val ? (
                    <div key={label} className="flex gap-2 text-[12.5px] leading-snug">
                      <span className="text-[10px] font-bold text-slate-400 uppercase min-w-[32px] mt-0.5">{label}</span>
                      <span className="text-slate-600">{val}</span>
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
          <summary className="cursor-pointer text-sm font-semibold text-slate-500 hover:text-blue-600 list-none flex items-center gap-1.5 py-1">
            <span className="text-xs">▶</span> 参数控件汇总表（{widgets.length} 个）
          </summary>
          <div className="mt-2 overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full text-xs">
              <thead className="bg-slate-50 text-slate-500">
                <tr>{['控件名', '类型', '数据来源', 'key 字段', '显示字段'].map(h => (
                  <th key={h} className="text-left px-3 py-2 font-semibold">{h}</th>
                ))}</tr>
              </thead>
              <tbody>
                {widgets.map((w, i) => (
                  <tr key={i} className="border-t border-slate-50 hover:bg-slate-50/50">
                    <td className="px-3 py-2 font-mono text-slate-700">{w.name}</td>
                    <td className="px-3 py-2 text-slate-500">{w.widget_type}</td>
                    <td className="px-3 py-2 text-slate-500">{w.bound_dataset ?? '直接输入'}</td>
                    <td className="px-3 py-2 text-slate-400">{w.key_column ?? '—'}</td>
                    <td className="px-3 py-2 text-slate-400">{w.display_column ?? '—'}</td>
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
