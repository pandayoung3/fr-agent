import type { ParsedReport, AnalysisResult } from '../../types'

interface Props { parsed: ParsedReport; analysis: AnalysisResult }

export default function StepsTab({ parsed, analysis }: Props) {
  const steps = analysis.development_steps ?? []
  const highlightRules = parsed.highlight_rules_summary ?? []
  const displayRules = analysis.display_rules ?? ''
  const writeback = parsed.writeback_config

  return (
    <div className="space-y-6">
      <div>
        <p className="mb-4 text-[12px] leading-5" style={{ color: 'var(--text-muted)' }}>
          以下步骤由 AI 根据解析结构推断，适合用作复现路线草稿；实际开发前仍需结合业务口径和真实数据结果核对。
        </p>
        {steps.length === 0 ? (
          <div className="rounded-lg px-4 py-6 text-center text-[13px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
            AI 暂未推断出开发步骤。
          </div>
        ) : (
          <div className="space-y-0">
            {steps.map((step, i) => (
              <div key={`${step}-${i}`} className="relative flex gap-4 pb-4">
                {i < steps.length - 1 && (
                  <div className="absolute bottom-0 left-[14px] top-7 w-0.5" style={{ background: 'var(--border)' }} />
                )}
                <div className="z-10 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                  {i + 1}
                </div>
                <div className="pt-1 text-[13.5px] leading-6" style={{ color: 'var(--text-secondary)' }}>{step}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {(highlightRules.length > 0 || displayRules) && (
        <div>
          <div className="mb-3 text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>条件高亮与展示规则</div>
          {displayRules && (
            <div className="mb-3 rounded-lg px-4 py-2.5 text-[13px] leading-5" style={{ background: 'var(--accent-surface)', border: '1px solid var(--accent-border)', color: 'var(--text-secondary)' }}>
              {displayRules}
            </div>
          )}
          {highlightRules.length > 0 && (
            <div className="overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
              <table className="w-full text-[12px]">
                <thead style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
                  <tr>{['规则名称', '触发条件', '效果', '颜色', '影响字段'].map(header => (
                    <th key={header} className="px-3 py-2 text-left font-semibold">{header}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {highlightRules.map((rule, i) => (
                    <tr key={`${rule.name}-${i}`} style={{ borderTop: '1px solid var(--border)' }}>
                      <td className="px-3 py-2" style={{ color: 'var(--text-primary)' }}>{rule.name}</td>
                      <td className="px-3 py-2 font-mono" style={{ color: 'var(--text-secondary)' }}>{rule.condition}</td>
                      <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{rule.action}</td>
                      <td className="px-3 py-2">
                        {rule.color ? (
                          <span className="flex items-center gap-1.5">
                            <span className="inline-block h-3 w-3 rounded-sm border border-slate-200" style={{ background: rule.color }} />
                            <span className="font-mono" style={{ color: 'var(--text-muted)' }}>{rule.color}</span>
                          </span>
                        ) : '-'}
                      </td>
                      <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{(rule.affected_columns ?? []).join('、') || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {writeback && (
        <div>
          <div className="mb-3 text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>填报提交配置</div>
          <div className="grid gap-3 lg:grid-cols-2">
            <div className="space-y-1.5 rounded-lg p-3" style={{ background: '#fff', border: '1px solid var(--border)' }}>
              <Info label="连接" value={writeback.db_connection} />
              <Info label="目标表" value={writeback.table} />
              <Info label="主键" value={(writeback.key_columns ?? []).join(', ')} />
            </div>
            {(writeback.column_mappings ?? []).length > 0 && (
              <div className="overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
                <table className="w-full text-[12px]">
                  <thead style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
                    <tr><th className="px-3 py-2 text-left">数据库字段</th><th className="px-3 py-2 text-left">来源参数</th><th className="px-3 py-2 text-left">主键</th></tr>
                  </thead>
                  <tbody>
                    {writeback.column_mappings!.map((mapping, i) => (
                      <tr key={`${mapping.db_column}-${i}`} style={{ borderTop: '1px solid var(--border)' }}>
                        <td className="px-3 py-1.5 font-mono">{mapping.db_column}</td>
                        <td className="px-3 py-1.5" style={{ color: 'var(--text-secondary)' }}>{mapping.param ?? '来自单元格'}</td>
                        <td className="px-3 py-1.5" style={{ color: 'var(--success)' }}>{mapping.is_key ? '是' : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function Info({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="flex gap-2 text-[12px]">
      <span className="min-w-[44px]" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{value || '-'}</span>
    </div>
  )
}
