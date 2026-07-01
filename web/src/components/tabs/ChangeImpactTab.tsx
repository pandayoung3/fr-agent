import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { analyzeChangeImpact } from '../../api'
import type { AnalysisResult, ChangeImpactAffected, ChangeImpactItem, ChangeImpactResult, LineageResult, ParsedReport } from '../../types'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
  onSelectTab: (tab: string) => void
}

type CategoryKey = keyof ChangeImpactAffected

const PROMPTS = [
  '新增按地区筛选',
  '成绩字段改为及格率',
  '班级筛选改成年级 + 班级联动',
  '新增一个展示字段',
  '调整汇总指标计算口径',
]

const CATEGORY_CONFIG: Array<{ key: CategoryKey; title: string; hint: string; tone: string }> = [
  { key: 'datasets', title: '数据集', hint: '优先确认取数来源和字段口径', tone: '#047857' },
  { key: 'sql', title: 'SQL / 取数', hint: '检查 SELECT、WHERE 与参数条件', tone: '#b45309' },
  { key: 'widgets', title: '参数控件', hint: '检查筛选、默认值和联动配置', tone: '#6d28d9' },
  { key: 'fields', title: '字段', hint: '确认业务字段与展示口径', tone: '#2563eb' },
  { key: 'cells', title: '单元格', hint: '定位 FineReport 设计器中的展示位置', tone: '#475569' },
  { key: 'formulas', title: '公式', hint: '复核计算范围和指标逻辑', tone: '#be123c' },
  { key: 'writeback', title: '填报写回', hint: '检查提交表、主键和字段映射', tone: '#0f766e' },
]

function confidenceStyle(confidence: ChangeImpactResult['confidence']) {
  if (confidence === '高') return { color: '#047857', background: '#ecfdf5', border: '1px solid #a7f3d0' }
  if (confidence === '中') return { color: '#b45309', background: '#fffbeb', border: '1px solid #fde68a' }
  return { color: '#be123c', background: '#fff1f2', border: '1px solid #fecdd3' }
}

function Panel({ title, hint, children }: { title: string; hint?: string; children: ReactNode }) {
  return (
    <section className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
      <div className="mb-3">
        <div className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
          {title}
        </div>
        {hint && (
          <div className="mt-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>
            {hint}
          </div>
        )}
      </div>
      {children}
    </section>
  )
}

function EmptyBox({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
      {children}
    </div>
  )
}

function ImpactList({ items, tone }: { items: ChangeImpactItem[]; tone: string }) {
  if (items.length === 0) return <EmptyBox>本次未定位到直接影响对象。</EmptyBox>

  return (
    <div className="space-y-2">
      {items.slice(0, 8).map(item => (
        <div key={`${item.name}-${item.reason}`} className="rounded-md px-3 py-2" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
          <div className="flex flex-wrap items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ background: tone }} />
            <span className="font-mono text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              {item.name}
            </span>
          </div>
          <div className="mt-1 text-[12px] leading-5" style={{ color: 'var(--text-secondary)' }}>
            {item.reason}
          </div>
          {item.detail && (
            <div className="mt-1 text-[11.5px] leading-5" style={{ color: 'var(--text-muted)' }}>
              {item.detail}
            </div>
          )}
        </div>
      ))}
      {items.length > 8 && (
        <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          还有 {items.length - 8} 项，请结合深度分析继续复核。
        </div>
      )}
    </div>
  )
}

function ListBlock({ items, tone = 'neutral' }: { items: string[]; tone?: 'neutral' | 'warning' | 'success' }) {
  const style = tone === 'warning'
    ? { background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }
    : tone === 'success'
      ? { background: '#ecfdf5', border: '1px solid #a7f3d0', color: '#047857' }
      : { background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <div key={`${item}-${index}`} className="rounded-md px-3 py-2 text-[12px] leading-5" style={style}>
          {item}
        </div>
      ))}
    </div>
  )
}

export default function ChangeImpactTab({ parsed, analysis, lineage, onSelectTab }: Props) {
  const [request, setRequest] = useState('')
  const [result, setResult] = useState<ChangeImpactResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const affectedCount = useMemo(() => {
    if (!result) return 0
    return Object.values(result.affected).reduce((sum, items) => sum + items.length, 0)
  }, [result])

  async function submit() {
    const trimmed = request.trim()
    if (!trimmed) {
      setError('请先描述要调整的业务需求或报表细节。')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const next = await analyzeChangeImpact(parsed, analysis, trimmed, lineage)
      setResult(next)
    } catch (err) {
      setError(err instanceof Error ? err.message : '变更影响分析失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <section
        className="rounded-lg p-4"
        style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f8fbff 100%)', border: '1px solid var(--border)' }}
      >
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_360px]">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.08em]" style={{ color: 'var(--accent)' }}>
              变更定位与修改建议
            </div>
            <h2 className="mt-1 text-[21px] font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
              先定位影响范围，再决定如何改报表
            </h2>
            <p className="mt-2 max-w-4xl text-[13.5px] leading-6" style={{ color: 'var(--text-secondary)' }}>
              输入业务口径、筛选条件、展示字段或指标计算的变化，系统会基于当前解析结果给出受影响对象、修改步骤和人工复核点。
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-lg px-3 py-2" style={{ background: '#fff', border: '1px solid var(--border)' }}>
              <div className="text-[18px] font-semibold" style={{ color: 'var(--text-primary)' }}>{parsed.datasets.length}</div>
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>数据集可检查</div>
            </div>
            <div className="rounded-lg px-3 py-2" style={{ background: '#fff', border: '1px solid var(--border)' }}>
              <div className="text-[18px] font-semibold" style={{ color: 'var(--text-primary)' }}>{parsed.widgets.length}</div>
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>控件可定位</div>
            </div>
            <div className="rounded-lg px-3 py-2" style={{ background: '#fff', border: '1px solid var(--border)' }}>
              <div className="text-[18px] font-semibold" style={{ color: 'var(--text-primary)' }}>{parsed.cell_bindings.length}</div>
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>单元格绑定</div>
            </div>
            <div className="rounded-lg px-3 py-2" style={{ background: '#fff', border: '1px solid var(--border)' }}>
              <div className="text-[18px] font-semibold" style={{ color: 'var(--text-primary)' }}>{parsed.formula_cells.length}</div>
              <div className="text-[11px]" style={{ color: 'var(--text-muted)' }}>公式可复核</div>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[420px_minmax(0,1fr)]">
        <Panel title="描述这次要改什么" hint="建议写业务语言，比如新增筛选、调整字段口径、修改展示或计算逻辑。">
          <textarea
            value={request}
            onChange={event => setRequest(event.target.value)}
            className="min-h-32 w-full resize-y rounded-md px-3 py-2 text-[13px] leading-6 outline-none"
            style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}
            placeholder="例如：新增按地区筛选，并且只影响当前报表的销售金额展示。"
          />
          <div className="mt-3 flex flex-wrap gap-2">
            {PROMPTS.map(prompt => (
              <button
                key={prompt}
                type="button"
                onClick={() => setRequest(prompt)}
                className="rounded-md px-2.5 py-1.5 text-[11.5px] font-semibold"
                style={{ background: 'var(--accent-surface)', border: '1px solid var(--accent-border)', color: 'var(--accent)' }}
              >
                {prompt}
              </button>
            ))}
          </div>
          {error && (
            <div className="mt-3 rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: '#fff1f2', border: '1px solid #fecdd3', color: '#be123c' }}>
              {error}
            </div>
          )}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={submit}
              disabled={loading}
              className="rounded-md px-4 py-2 text-[12px] font-semibold disabled:opacity-60"
              style={{ background: 'var(--accent)', color: '#fff' }}
            >
              {loading ? '正在分析...' : '分析影响范围'}
            </button>
            <button
              type="button"
              onClick={() => onSelectTab('deep')}
              className="rounded-md px-4 py-2 text-[12px] font-semibold"
              style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
            >
              查看深度证据
            </button>
          </div>
        </Panel>

        <div className="space-y-4">
          {!result && (
            <Panel title="等待变更输入" hint="这里会展示结论级定位，不会替你自动修改 CPT。">
              <EmptyBox>
                当前阶段的目标是帮助开发人员快速判断“应该去 FineReport 的哪个数据集、控件、单元格或公式里改”，半自动操作设计器暂时不进入本周期。
              </EmptyBox>
            </Panel>
          )}

          {result && (
            <>
              <Panel title="定位结论" hint="先看影响范围和可信度，再进入具体修改步骤。">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] leading-6" style={{ color: 'var(--text-secondary)' }}>
                      {result.summary}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {result.change_types.map(type => (
                        <span key={type} className="rounded-md px-2 py-1 text-[11px] font-semibold" style={{ background: 'var(--accent-surface)', border: '1px solid var(--accent-border)', color: 'var(--accent)' }}>
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-lg px-3 py-2 text-center" style={confidenceStyle(result.confidence)}>
                    <div className="text-[18px] font-semibold leading-none">{result.confidence}</div>
                    <div className="mt-1 text-[11px]">定位置信度</div>
                  </div>
                </div>
                <div className="mt-3 rounded-md px-3 py-2 text-[12px]" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                  已定位 {affectedCount} 个影响对象。结论来自确定性解析和现有 AI 分析结果，不依赖额外 LLM 调用。
                </div>
              </Panel>

              <Panel title="建议修改步骤" hint="按这个顺序检查，可以减少反复回到设计器查找的成本。">
                <ListBlock items={result.suggested_steps} />
              </Panel>
            </>
          )}
        </div>
      </div>

      {result && (
        <>
          <section className="grid gap-3 lg:grid-cols-2">
            {CATEGORY_CONFIG.map(category => (
              <Panel key={category.key} title={category.title} hint={category.hint}>
                <ImpactList items={result.affected[category.key]} tone={category.tone} />
              </Panel>
            ))}
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            <Panel title="定位证据" hint="帮助你判断为什么系统认为这些对象会受影响。">
              <ListBlock items={result.evidence} tone="success" />
            </Panel>
            <Panel title="人工复核点" hint="这些点建议在 FineReport 设计器或业务侧再确认一次。">
              <ListBlock items={result.review_points} tone="warning" />
            </Panel>
          </section>
        </>
      )}
    </div>
  )
}
