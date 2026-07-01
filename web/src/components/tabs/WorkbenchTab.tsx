import { useMemo, useState } from 'react'
import type { AnalysisResult, LineageResult, ParsedReport } from '../../types'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
  onSelectTab: (tab: string) => void
  onAskQuestion: (question: string) => void
}

type StageTone = 'blue' | 'green' | 'amber' | 'violet' | 'slate' | 'rose'

interface HandoffStage {
  id: string
  title: string
  verb: string
  summary: string
  evidence: string[]
  aiNote?: string
  confidence: '确定性解析' | 'AI 辅助' | '需复核'
  tone: StageTone
}

const TONE: Record<StageTone, { text: string; bg: string; border: string }> = {
  blue: { text: '#1d4ed8', bg: '#eff6ff', border: '#bfdbfe' },
  green: { text: '#047857', bg: '#ecfdf5', border: '#a7f3d0' },
  amber: { text: '#b45309', bg: '#fffbeb', border: '#fde68a' },
  violet: { text: '#6d28d9', bg: '#f5f3ff', border: '#ddd6fe' },
  slate: { text: '#475569', bg: '#f8fafc', border: '#cbd5e1' },
  rose: { text: '#be123c', bg: '#fff1f2', border: '#fecdd3' },
}

function short(text: string | undefined, fallback: string, max = 120) {
  const value = (text ?? '').trim() || fallback
  return value.length > max ? `${value.slice(0, max)}...` : value
}

function datasetTypeText(type: string) {
  if (type === 'DBTableData') return '数据库数据集'
  if (type === 'EmbeddedTableData') return '内置数据集'
  return type || '未知类型'
}

function makeStages(parsed: ParsedReport, analysis: AnalysisResult, lineage: LineageResult | null): HandoffStage[] {
  const dbDatasets = parsed.datasets.filter(dataset => dataset.type === 'DBTableData')
  const embeddedDatasets = parsed.datasets.filter(dataset => dataset.type !== 'DBTableData')
  const sqlDatasets = parsed.datasets.filter(dataset => dataset.sql)
  const displayFields = Array.from(new Set(parsed.cell_bindings.filter(cell => cell.dataset && cell.column).map(cell => `${cell.dataset}.${cell.column}`)))
  const labels = parsed.label_data_pairs.slice(0, 4).map(pair => `${pair.label_text || pair.label_pos} -> ${pair.dataset ?? ''}.${pair.column ?? pair.data_pos}`)
  const chainCount = analysis.interaction_chains?.length ?? 0
  const unmatchedCount = lineage?.unmatched_widget_names?.length ?? 0

  return [
    {
      id: 'purpose',
      title: '理解业务目标',
      verb: '先判断这张报表要解决什么问题',
      summary: short(analysis.purpose, 'AI 暂未给出业务目的；可以先从数据集、控件和展示字段反推报表用途。', 150),
      evidence: [
        `报表类型：${parsed.report_type === 'writeback' ? '填报报表' : '查询报表'}`,
        `Sheet 数量：${parsed.sheet_count}`,
        `AI 布局判断：${short(analysis.layout_description, '暂无布局解释', 80)}`,
      ],
      aiNote: '这是 AI 对业务目的的辅助判断，复现前仍应结合需求方口径确认。',
      confidence: analysis.purpose ? 'AI 辅助' : '需复核',
      tone: 'blue',
    },
    {
      id: 'datasets',
      title: '准备数据集',
      verb: '先把数据来源准备出来',
      summary: parsed.datasets.length > 0
        ? `已识别 ${parsed.datasets.length} 个数据集，其中 ${dbDatasets.length} 个数据库数据集、${embeddedDatasets.length} 个内置或非 DB 数据集。`
        : '未识别到数据集，复现时需要先人工确认数据来源。',
      evidence: parsed.datasets.slice(0, 3).map(dataset => `${dataset.name}：${datasetTypeText(dataset.type)}，字段 ${dataset.columns?.length ?? 0} 个`),
      aiNote: short(analysis.dataset_relationships, '暂无 AI 数据集关系解释。', 120),
      confidence: parsed.datasets.length > 0 ? '确定性解析' : '需复核',
      tone: 'green',
    },
    {
      id: 'sql',
      title: '配置取数逻辑',
      verb: '再还原 SQL 或取数方式',
      summary: sqlDatasets.length > 0
        ? `有 ${sqlDatasets.length} 个数据集包含 SQL，可优先复现这些查询，再补充参数。`
        : '当前 CPT 未暴露 SQL，多数逻辑可能来自内置数据或非 DB 数据集。',
      evidence: sqlDatasets.length > 0
        ? sqlDatasets.slice(0, 3).map(dataset => `${dataset.name}：参数 ${dataset.sql_params?.length ?? 0} 个${dataset.db_connection ? `，连接 ${dataset.db_connection}` : ''}`)
        : parsed.datasets.slice(0, 3).map(dataset => `${dataset.name}：${datasetTypeText(dataset.type)}`),
      aiNote: '第一屏只展示取数结论，SQL 原文和字段明细放在深度分析中查看。',
      confidence: sqlDatasets.length > 0 ? '确定性解析' : '需复核',
      tone: 'amber',
    },
    {
      id: 'widgets',
      title: '配置参数控件',
      verb: '确认用户如何影响查询和展示',
      summary: parsed.widgets.length > 0
        ? `已识别 ${parsed.widgets.length} 个控件，AI 推断出 ${chainCount} 条交互链路。`
        : '未识别到参数控件，这张报表可能偏静态展示或控件逻辑未被解析到。',
      evidence: parsed.widgets.slice(0, 4).map(widget => `${widget.name}：${widget.widget_type}${widget.bound_dataset ? `，选项来自 ${widget.bound_dataset}` : ''}`),
      aiNote: unmatchedCount > 0 ? `${unmatchedCount} 个控件未匹配到直接 SQL 链路，可能通过单元格过滤、JS 或其他配置生效。` : '控件链路用于帮助复现交互思路，不等同于原开发者全部实现细节。',
      confidence: unmatchedCount > 0 ? '需复核' : '确定性解析',
      tone: 'violet',
    },
    {
      id: 'display',
      title: '设计展示区域',
      verb: '最后把字段放回报表布局',
      summary: `已识别 ${parsed.cell_bindings.length} 个单元格绑定、${displayFields.length} 个展示字段、${parsed.formula_cells.length} 个公式单元格。`,
      evidence: labels.length > 0 ? labels : displayFields.slice(0, 4),
      aiNote: short(analysis.field_semantics, '字段业务含义可在深度分析中继续核对。', 130),
      confidence: parsed.cell_bindings.length > 0 ? '确定性解析' : '需复核',
      tone: 'slate',
    },
    {
      id: 'verify',
      title: '复现与验证',
      verb: '按步骤复刻并做人工确认',
      summary: (analysis.development_steps?.length ?? 0) > 0
        ? `AI 给出 ${analysis.development_steps!.length} 条复现步骤，建议按数据集、控件、展示、校验的顺序执行。`
        : 'AI 暂未生成复现步骤，建议按本页流程逐项复刻。',
      evidence: (analysis.development_steps ?? []).slice(0, 3),
      aiNote: (analysis.notes_or_risks?.length ?? 0) > 0
        ? `深度分析中还有 ${analysis.notes_or_risks!.length} 条风险或注意事项，交付前需要复核。`
        : '当前未发现明显风险提示，仍建议用真实参数跑一遍结果对账。',
      confidence: (analysis.notes_or_risks?.length ?? 0) > 0 ? '需复核' : 'AI 辅助',
      tone: 'rose',
    },
  ]
}

function Badge({ children, tone }: { children: React.ReactNode; tone: StageTone }) {
  const meta = TONE[tone]
  return (
    <span
      className="inline-flex rounded-md px-2 py-1 text-[11px] font-semibold"
      style={{ color: meta.text, background: meta.bg, border: `1px solid ${meta.border}` }}
    >
      {children}
    </span>
  )
}

function StageCard({
  stage,
  index,
  active,
  onSelect,
}: {
  stage: HandoffStage
  index: number
  active: boolean
  onSelect: (stage: HandoffStage) => void
}) {
  const meta = TONE[stage.tone]
  return (
    <button
      type="button"
      onClick={() => onSelect(stage)}
      className="w-full rounded-lg p-3 text-left transition-all"
      style={{
        background: active ? meta.bg : '#fff',
        border: `1px solid ${active ? meta.border : 'var(--border)'}`,
        boxShadow: active ? '0 10px 22px rgba(15, 23, 42, 0.10)' : 'var(--shadow-sm)',
      }}
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className="flex h-7 w-7 items-center justify-center rounded-full text-[12px] font-bold"
            style={{ background: meta.text, color: '#fff' }}
          >
            {index + 1}
          </span>
          <div>
            <div className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              {stage.title}
            </div>
            <div className="mt-0.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>
              {stage.verb}
            </div>
          </div>
        </div>
        <Badge tone={stage.tone}>{stage.confidence}</Badge>
      </div>
      <p className="line-clamp-2 text-[12.5px] leading-5" style={{ color: 'var(--text-secondary)' }}>
        {stage.summary}
      </p>
    </button>
  )
}

function QuickMetric({ label, value, hint }: { label: string; value: string | number; hint: string }) {
  return (
    <div className="rounded-lg px-3 py-2" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
      <div className="text-[18px] font-semibold leading-none" style={{ color: 'var(--text-primary)' }}>{value}</div>
      <div className="mt-1 text-[11px] font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</div>
      <div className="mt-1 text-[10.5px] leading-snug" style={{ color: 'var(--text-muted)' }}>{hint}</div>
    </div>
  )
}

export default function WorkbenchTab({ parsed, analysis, lineage, onSelectTab, onAskQuestion }: Props) {
  const stages = useMemo(() => makeStages(parsed, analysis, lineage), [analysis, lineage, parsed])
  const [selectedId, setSelectedId] = useState(stages[0]?.id ?? 'purpose')
  const selected = stages.find(stage => stage.id === selectedId) ?? stages[0]
  const dbDatasets = parsed.datasets.filter(dataset => dataset.type === 'DBTableData').length
  const sqlDatasets = parsed.datasets.filter(dataset => dataset.sql).length
  const displayFields = new Set(parsed.cell_bindings.filter(cell => cell.dataset && cell.column).map(cell => `${cell.dataset}.${cell.column}`)).size

  return (
    <div className="space-y-4">
      <section
        className="rounded-lg p-4"
        style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f8fbff 100%)', border: '1px solid var(--border)' }}
      >
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.3fr)_360px]">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.08em]" style={{ color: 'var(--accent)' }}>
              接手开发总览
            </div>
            <h2 className="mt-1 text-[21px] font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
              {parsed.file_name}
            </h2>
            <p className="mt-2 max-w-4xl text-[13.5px] leading-6" style={{ color: 'var(--text-secondary)' }}>
              {short(analysis.purpose, '这张报表的业务目的需要结合数据集、控件和展示字段继续确认。', 210)}
            </p>
            <div className="mt-3 rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }}>
              本页优先展示可帮助开发者复现报表的关键信息；AI 解释仅作为辅助判断，不等同于原开发者真实意图。
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <QuickMetric label="数据集" value={parsed.datasets.length} hint={`${dbDatasets} 个 DB 数据集`} />
            <QuickMetric label="SQL 数据集" value={sqlDatasets} hint="原文在深度分析" />
            <QuickMetric label="参数控件" value={parsed.widgets.length} hint="影响查询或展示" />
            <QuickMetric label="展示字段" value={displayFields} hint={`${parsed.cell_bindings.length} 个单元格绑定`} />
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.5fr)_380px]">
        <div className="rounded-lg p-4" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <div className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                报表复现路线
              </div>
              <div className="mt-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>
                按开发顺序理解，不把复杂证据默认压到第一屏。
              </div>
            </div>
            <button
              type="button"
              onClick={() => onSelectTab('deep')}
              className="rounded-md px-3 py-2 text-[12px] font-semibold"
              style={{ color: 'var(--accent)', background: 'var(--accent-surface)', border: '1px solid var(--accent-border)' }}
            >
              查看深度分析
            </button>
          </div>
          <div className="grid gap-2 lg:grid-cols-2">
            {stages.map((stage, index) => (
              <StageCard
                key={stage.id}
                stage={stage}
                index={index}
                active={selected.id === stage.id}
                onSelect={stage => setSelectedId(stage.id)}
              />
            ))}
          </div>
        </div>

        <aside className="space-y-3">
          <section className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
            <div className="mb-3 flex items-start justify-between gap-3">
              <div>
                <Badge tone={selected.tone}>{selected.confidence}</Badge>
                <h3 className="mt-2 text-[16px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {selected.title}
                </h3>
                <p className="mt-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>
                  {selected.verb}
                </p>
              </div>
            </div>
            <p className="text-[13px] leading-6" style={{ color: 'var(--text-secondary)' }}>
              {selected.summary}
            </p>
            <div className="mt-3 space-y-2">
              <div className="text-[11px] font-semibold" style={{ color: 'var(--text-muted)' }}>
                第一屏只保留的关键证据
              </div>
              {(selected.evidence.length > 0 ? selected.evidence : ['暂无可直接展示的关键证据，请进入深度分析继续查看。']).slice(0, 4).map(item => (
                <div key={item} className="rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                  {item}
                </div>
              ))}
            </div>
            {selected.aiNote && (
              <div className="mt-3 rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: '#f8fafc', border: '1px solid #cbd5e1', color: 'var(--text-secondary)' }}>
                AI 辅助：{selected.aiNote}
              </div>
            )}
            <div className="mt-4 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => onSelectTab('deep')}
                className="rounded-md px-3 py-2 text-[12px] font-semibold"
                style={{ background: 'var(--accent)', color: '#fff' }}
              >
                看完整证据
              </button>
              <button
                type="button"
                onClick={() => onAskQuestion(`请围绕「${selected.title}」解释这张报表如何复现，优先给出开发步骤和需要人工确认的点。`)}
                className="rounded-md px-3 py-2 text-[12px] font-semibold"
                style={{ background: 'var(--bg)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              >
                追问 AI
              </button>
            </div>
          </section>

          <section className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)' }}>
            <div className="mb-3 text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              接手建议
            </div>
            <div className="space-y-2 text-[12px] leading-5" style={{ color: 'var(--text-secondary)' }}>
              <p>1. 先确认业务目标和筛选口径，再复现数据集。</p>
              <p>2. 优先复刻 SQL/内置数据，再绑定参数控件。</p>
              <p>3. 最后按展示字段和公式还原页面，并用真实参数对账。</p>
            </div>
          </section>
        </aside>
      </section>
    </div>
  )
}
