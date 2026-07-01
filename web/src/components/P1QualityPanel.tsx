import { useEffect, useState } from 'react'
import type {
  AnalysisResult,
  FormulaValidationResult,
  LineageResult,
  LlmConfig,
  ParsedReport,
  ScoreResult,
} from '../types'
import { getLlmConfig, scoreReport, testLlmConfig, validateFormulas } from '../api'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
}

function StatusBadge({ tone, children }: { tone: 'ok' | 'warn' | 'muted'; children: React.ReactNode }) {
  const styles = {
    ok: { color: 'var(--success)', background: 'var(--success-surface)', border: 'var(--success-border)' },
    warn: { color: '#b45309', background: '#fffbeb', border: '#fde68a' },
    muted: { color: 'var(--text-muted)', background: 'var(--bg)', border: 'var(--border)' },
  }[tone]

  return (
    <span
      className="text-[10px] font-medium px-2 py-1 rounded-full"
      style={{ color: styles.color, background: styles.background, border: `1px solid ${styles.border}` }}
    >
      {children}
    </span>
  )
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl p-4" style={{ background: '#fff', border: '1px solid var(--border)' }}>
      <div className="text-[13px] font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>{title}</div>
      {children}
    </section>
  )
}

export default function P1QualityPanel({ parsed, analysis, lineage }: Props) {
  const [score, setScore] = useState<ScoreResult | null>(null)
  const [formula, setFormula] = useState<FormulaValidationResult | null>(null)
  const [llm, setLlm] = useState<LlmConfig | null>(null)
  const [llmTest, setLlmTest] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      try {
        const [scoreResult, formulaResult, llmConfig] = await Promise.all([
          scoreReport(parsed, analysis, lineage),
          validateFormulas(parsed),
          getLlmConfig(),
        ])
        if (!cancelled) {
          setScore(scoreResult)
          setFormula(formulaResult)
          setLlm(llmConfig)
        }
      } catch (error) {
        if (!cancelled) setLlmTest(`质量面板加载失败：${String(error)}`)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [analysis, lineage, parsed])

  async function handleLlmTest() {
    setLlmTest('正在测试 LLM 配置...')
    try {
      const result = await testLlmConfig()
      setLlmTest(result.ok ? `LLM 可用：${result.message || result.model}` : 'LLM 测试未通过')
    } catch (error) {
      setLlmTest(`LLM 测试失败：${String(error)}`)
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl p-4 text-[12px]" style={{ color: 'var(--text-muted)', background: '#fff', border: '1px solid var(--border)' }}>
        正在生成 P1 质量视图...
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[1fr_1fr_1fr] gap-4">
      <Panel title="交付评分">
        {score ? (
          <div className="space-y-3">
            <div className="flex items-baseline gap-2">
              <span className="text-[30px] font-semibold leading-none" style={{ color: 'var(--text-primary)' }}>
                {score.score}
              </span>
              <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>分 / {score.grade} 级</span>
            </div>
            <div className="space-y-2">
              {score.dimensions.map(item => (
                <div key={item.key}>
                  <div className="flex justify-between text-[11px] mb-1" style={{ color: 'var(--text-secondary)' }}>
                    <span>{item.label}</span>
                    <span>{item.score}/{item.max_score}</span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg)' }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${(item.score / item.max_score) * 100}%`, background: 'var(--accent)' }}
                    />
                  </div>
                </div>
              ))}
            </div>
            {score.recommendations[0] && (
              <p className="text-[12px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                {score.recommendations[0]}
              </p>
            )}
          </div>
        ) : (
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>暂无评分。</p>
        )}
      </Panel>

      <Panel title="公式校验">
        {formula ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <StatusBadge tone={formula.issue_count ? 'warn' : 'ok'}>
                {formula.issue_count ? `${formula.issue_count} 个需复核` : '全部通过'}
              </StatusBadge>
              <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                共 {formula.total} 个公式
              </span>
            </div>
            <div className="space-y-2 max-h-36 overflow-y-auto">
              {formula.items.slice(0, 4).map(item => (
                <div key={item.pos} className="rounded-lg p-2" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>{item.pos}</span>
                    <StatusBadge tone={item.status === 'ok' ? 'ok' : 'warn'}>
                      {item.status === 'ok' ? 'OK' : '复核'}
                    </StatusBadge>
                  </div>
                  <div className="text-[11px] mt-1 truncate" title={item.formula} style={{ color: 'var(--text-muted)' }}>
                    {item.formula}
                  </div>
                </div>
              ))}
              {formula.total === 0 && (
                <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>当前 CPT 未检测到公式单元格。</p>
              )}
            </div>
          </div>
        ) : (
          <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>暂无公式校验结果。</p>
        )}
      </Panel>

      <Panel title="LLM 配置">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <StatusBadge tone={llm?.configured ? 'ok' : 'warn'}>
              {llm?.configured ? '已配置' : '未配置'}
            </StatusBadge>
            {llm?.api_key_hint && (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>{llm.api_key_hint}</span>
            )}
          </div>
          <div className="text-[11px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
            <div>模型：{llm?.model ?? '-'}</div>
            <div className="truncate" title={llm?.base_url}>地址：{llm?.base_url ?? '-'}</div>
          </div>
          <button
            type="button"
            onClick={handleLlmTest}
            disabled={!llm?.configured}
            className="text-xs font-medium rounded-md px-3 py-2 disabled:opacity-50"
            style={{ color: '#fff', background: 'var(--accent)' }}
          >
            测试 LLM
          </button>
          {llmTest && (
            <p className="text-[11px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{llmTest}</p>
          )}
        </div>
      </Panel>
    </div>
  )
}
