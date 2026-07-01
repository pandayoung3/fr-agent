import type { AnalysisResult } from '../../types'

interface Props { analysis: AnalysisResult }

export default function IndicatorsTab({ analysis }: Props) {
  const indicators = analysis.indicator_dict ?? []
  const formulaExps = analysis.formula_explanations ?? []

  return (
    <div className="space-y-5">
      {indicators.length === 0 ? (
        <div className="rounded-lg px-4 py-6 text-center text-[13px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
          暂无指标字典。可能是报表没有明确度量指标，或 AI 尚未能稳定推断字段业务含义。
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
          <table className="w-full text-[12px]">
            <thead style={{ background: '#334155', color: '#fff' }}>
              <tr>{['指标名', '来源字段', '数据集', '类型', '单位', '公式', '业务含义'].map(h => (
                <th key={h} className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {indicators.map((indicator, i) => (
                <tr key={`${indicator.indicator_name}-${i}`} style={{ borderTop: '1px solid var(--border)', background: i % 2 === 0 ? '#fff' : 'var(--bg)' }}>
                  <td className="px-3 py-2 font-semibold" style={{ color: 'var(--text-primary)' }}>{indicator.indicator_name}</td>
                  <td className="px-3 py-2 font-mono" style={{ color: 'var(--text-secondary)' }}>{indicator.source_field}</td>
                  <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{indicator.dataset ?? '-'}</td>
                  <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{indicator.type}</td>
                  <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{indicator.unit ?? '-'}</td>
                  <td className="max-w-[160px] truncate px-3 py-2 font-mono" style={{ color: 'var(--text-muted)' }} title={indicator.formula ?? ''}>{indicator.formula ?? '-'}</td>
                  <td className="max-w-[260px] px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{indicator.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {formulaExps.length > 0 && (
        <details>
          <summary className="flex cursor-pointer list-none items-center gap-1.5 py-1 text-[13px] font-semibold" style={{ color: 'var(--text-secondary)' }}>
            公式详细解释（{formulaExps.length} 条）
          </summary>
          <div className="mt-3 space-y-3">
            {formulaExps.map((formula, i) => (
              <div key={`${formula.pos}-${i}`} className="rounded-lg p-3" style={{ background: '#fff', border: '1px solid var(--border)' }}>
                <div className="mb-1 text-[12px] font-mono" style={{ color: 'var(--text-muted)' }}>
                  <span className="font-bold" style={{ color: 'var(--accent)' }}>{formula.pos}</span> · {formula.formula}
                </div>
                <div className="text-[13px] leading-5" style={{ color: 'var(--text-secondary)' }}>{formula.meaning}</div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
