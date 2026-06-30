import type { AnalysisResult } from '../../types'

interface Props { analysis: AnalysisResult }

export default function IndicatorsTab({ analysis }: Props) {
  const indicators = analysis.indicator_dict ?? []
  const formulaExps = analysis.formula_explanations ?? []

  if (indicators.length === 0) {
    return <div className="text-sm text-slate-400 text-center py-8">无指标字典（AI 未能推断，或报表无明确度量指标）</div>
  }

  return (
    <div className="space-y-5">
      <div className="overflow-x-auto rounded-xl border border-slate-100">
        <table className="w-full text-xs">
          <thead className="bg-slate-700 text-white">
            <tr>{['指标名', '来源字段', '数据集', '类型', '单位', '公式', '业务含义'].map(h => (
              <th key={h} className="text-left px-3 py-2.5 font-semibold whitespace-nowrap">{h}</th>
            ))}</tr>
          </thead>
          <tbody>
            {indicators.map((ind, i) => (
              <tr key={i} className={`border-t border-slate-50 ${i % 2 === 0 ? '' : 'bg-slate-50/50'} hover:bg-blue-50/30`}>
                <td className="px-3 py-2 font-semibold text-slate-700">{ind.indicator_name}</td>
                <td className="px-3 py-2 font-mono text-slate-500">{ind.source_field}</td>
                <td className="px-3 py-2 text-slate-400">{ind.dataset ?? '—'}</td>
                <td className="px-3 py-2">
                  <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                    ind.type === '度量'
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>{ind.type}</span>
                </td>
                <td className="px-3 py-2 text-slate-400">{ind.unit ?? '—'}</td>
                <td className="px-3 py-2 font-mono text-slate-400 max-w-[120px] truncate" title={ind.formula ?? ''}>{ind.formula ?? '—'}</td>
                <td className="px-3 py-2 text-slate-600 max-w-[200px]">{ind.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {formulaExps.length > 0 && (
        <details>
          <summary className="cursor-pointer text-sm font-semibold text-slate-500 hover:text-blue-600 list-none flex items-center gap-1.5 py-1">
            <span className="text-xs">▶</span> 公式详细解释（{formulaExps.length} 条）
          </summary>
          <div className="mt-3 space-y-3">
            {formulaExps.map((fe, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-xl p-3">
                <div className="text-xs font-mono text-slate-500 mb-1">
                  <span className="text-blue-600 font-bold">{fe.pos}</span> — {fe.formula}
                </div>
                <div className="text-sm text-slate-600">{fe.meaning}</div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
