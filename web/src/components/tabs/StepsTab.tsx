import type { ParsedReport, AnalysisResult } from '../../types'

interface Props { parsed: ParsedReport; analysis: AnalysisResult }

export default function StepsTab({ parsed, analysis }: Props) {
  const steps = analysis.development_steps ?? []
  const hlRules = parsed.highlight_rules_summary ?? []
  const displayRules = analysis.display_rules ?? ''
  const wb = parsed.writeback_config

  return (
    <div className="space-y-6">
      {/* 开发步骤 */}
      <div>
        <p className="text-xs text-slate-400 mb-4">以下步骤由 AI 根据报表结构推断，供新开发人员参考，请核实后使用。</p>
        {steps.length === 0 ? (
          <div className="text-sm text-slate-400">AI 未能推断开发步骤</div>
        ) : (
          <div className="space-y-0">
            {steps.map((step, i) => (
              <div key={i} className="flex gap-4 relative pb-4">
                {i < steps.length - 1 && (
                  <div className="absolute left-[14px] top-7 bottom-0 w-0.5 bg-slate-100" />
                )}
                <div className="w-7 h-7 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 z-10">
                  {i + 1}
                </div>
                <div className="text-[13.5px] text-slate-600 leading-relaxed pt-1">{step}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 条件高亮规则 */}
      {(hlRules.length > 0 || (displayRules && displayRules !== '无条件高亮规则')) && (
        <div>
          <div className="text-sm font-bold text-slate-600 mb-3">🎨 条件高亮规则</div>
          {displayRules && displayRules !== '无条件高亮规则' && (
            <div className="text-sm text-slate-600 bg-blue-50 rounded-lg px-4 py-2.5 mb-3">{displayRules}</div>
          )}
          {hlRules.length > 0 && (
            <div className="overflow-x-auto rounded-xl border border-slate-100">
              <table className="w-full text-xs">
                <thead className="bg-slate-50 text-slate-500">
                  <tr>{['规则名称', '触发条件', '效果', '颜色', '影响字段'].map(h => (
                    <th key={h} className="text-left px-3 py-2 font-semibold">{h}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {hlRules.map((r, i) => (
                    <tr key={i} className="border-t border-slate-50 hover:bg-slate-50">
                      <td className="px-3 py-2 text-slate-700">{r.name}</td>
                      <td className="px-3 py-2 font-mono text-slate-500">{r.condition}</td>
                      <td className="px-3 py-2 text-slate-500">{r.action}</td>
                      <td className="px-3 py-2">
                        {r.color ? (
                          <span className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-sm border border-slate-200 inline-block" style={{ background: r.color }} />
                            <span className="font-mono text-slate-400">{r.color}</span>
                          </span>
                        ) : '—'}
                      </td>
                      <td className="px-3 py-2 text-slate-400">{(r.affected_columns ?? []).join('、') || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 填报配置 */}
      {wb && (
        <div>
          <div className="text-sm font-bold text-slate-600 mb-3">📝 填报提交配置</div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white border border-slate-100 rounded-xl p-3 space-y-1.5">
              <Info label="连接" value={wb.db_connection} />
              <Info label="目标表" value={wb.table} />
              <Info label="主键" value={(wb.key_columns ?? []).join(', ')} />
            </div>
            {(wb.column_mappings ?? []).length > 0 && (
              <div className="overflow-x-auto rounded-xl border border-slate-100">
                <table className="w-full text-xs">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr><th className="text-left px-3 py-2">数据库字段</th><th className="text-left px-3 py-2">来源参数</th><th className="text-left px-3 py-2">主键</th></tr>
                  </thead>
                  <tbody>
                    {wb.column_mappings!.map((m, i) => (
                      <tr key={i} className="border-t border-slate-50">
                        <td className="px-3 py-1.5 font-mono">{m.db_column}</td>
                        <td className="px-3 py-1.5 text-slate-500">{m.param ?? '（来自单元格）'}</td>
                        <td className="px-3 py-1.5 text-green-600">{m.is_key ? '✓' : ''}</td>
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
    <div className="flex gap-2 text-xs">
      <span className="text-slate-400 min-w-[44px]">{label}</span>
      <span className="font-mono text-slate-700">{value ?? '—'}</span>
    </div>
  )
}
