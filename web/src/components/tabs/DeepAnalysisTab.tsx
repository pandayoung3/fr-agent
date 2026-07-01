import type { AnalysisResult, LineageResult, ParsedReport } from '../../types'
import LineageTab from './LineageTab'
import ChainsTab from './ChainsTab'
import IndicatorsTab from './IndicatorsTab'
import StepsTab from './StepsTab'
import P1QualityPanel from '../P1QualityPanel'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
  onLoadLineage: () => void
}

function Section({ title, hint, children }: { title: string; hint: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
      <div className="mb-3">
        <div className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
          {title}
        </div>
        <div className="mt-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>
          {hint}
        </div>
      </div>
      {children}
    </section>
  )
}

function EvidenceBadge({ children, tone = 'fact' }: { children: React.ReactNode; tone?: 'fact' | 'ai' | 'review' }) {
  const style = tone === 'fact'
    ? { color: '#047857', background: '#ecfdf5', border: '1px solid #a7f3d0' }
    : tone === 'ai'
      ? { color: '#1d4ed8', background: '#eff6ff', border: '1px solid #bfdbfe' }
      : { color: '#b45309', background: '#fffbeb', border: '1px solid #fde68a' }

  return (
    <span className="rounded-md px-2 py-1 text-[11px] font-semibold" style={style}>
      {children}
    </span>
  )
}

function DatasetTable({ parsed }: { parsed: ParsedReport }) {
  if (parsed.datasets.length === 0) {
    return <div className="rounded-md px-3 py-2 text-[12px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>未识别到数据集。</div>
  }

  return (
    <div className="overflow-x-auto rounded-lg" style={{ border: '1px solid var(--border)' }}>
      <table className="w-full text-[12px]">
        <thead style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
          <tr>
            {['数据集', '类型', '连接', '字段数', 'SQL 参数', '共享字段'].map(header => (
              <th key={header} className="px-3 py-2 text-left font-semibold whitespace-nowrap">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {parsed.datasets.map(dataset => {
            const shared = parsed.dataset_shared_keys.filter(item => item.shared_by.includes(dataset.name)).map(item => item.field)
            return (
              <tr key={dataset.name} style={{ borderTop: '1px solid var(--border)' }}>
                <td className="px-3 py-2 font-mono" style={{ color: 'var(--text-primary)' }}>{dataset.name}</td>
                <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{dataset.type}</td>
                <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{dataset.db_connection ?? '-'}</td>
                <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{dataset.columns?.length ?? 0}</td>
                <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{dataset.sql_params?.join(', ') || '-'}</td>
                <td className="px-3 py-2" style={{ color: 'var(--text-secondary)' }}>{shared.slice(0, 4).join(', ') || '-'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function SqlBlocks({ parsed }: { parsed: ParsedReport }) {
  const sqlDatasets = parsed.datasets.filter(dataset => dataset.sql)
  if (sqlDatasets.length === 0) {
    return <div className="rounded-md px-3 py-2 text-[12px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>当前 CPT 未解析到 SQL 原文。</div>
  }

  return (
    <div className="space-y-3">
      {sqlDatasets.map(dataset => (
        <details key={dataset.name} className="rounded-lg p-3" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
          <summary className="cursor-pointer list-none text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            {dataset.name} · SQL 原文
          </summary>
          <div className="mt-2 flex flex-wrap gap-2">
            <EvidenceBadge>确定性解析</EvidenceBadge>
            {(dataset.sql_params ?? []).map(param => <EvidenceBadge key={param} tone="review">参数：{param}</EvidenceBadge>)}
          </div>
          <pre className="mt-3 max-h-72 overflow-auto rounded-md p-3 text-[12px] leading-5" style={{ background: '#0f172a', color: '#e2e8f0' }}>
            {dataset.sql}
          </pre>
        </details>
      ))}
    </div>
  )
}

function ReviewList({ parsed, analysis, lineage }: { parsed: ParsedReport; analysis: AnalysisResult; lineage: LineageResult | null }) {
  const items = [
    ...(lineage?.unmatched_widget_names ?? []).map(name => `控件 ${name} 未匹配到直接 SQL 链路，可能通过单元格过滤、JS 或其他配置生效。`),
    ...(analysis.notes_or_risks ?? []),
    ...parsed.formula_cells.filter(formula => !analysis.formula_explanations?.some(item => item.pos === formula.pos)).map(formula => `公式单元格 ${formula.pos} 需要人工确认：${formula.formula}`),
  ]

  if (items.length === 0) {
    return <div className="rounded-md px-3 py-2 text-[12px]" style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', color: '#047857' }}>暂无明显待复核项，但交付前仍建议用真实参数对账。</div>
  }

  return (
    <div className="space-y-2">
      {items.slice(0, 12).map((item, index) => (
        <div key={`${item}-${index}`} className="rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e' }}>
          {item}
        </div>
      ))}
    </div>
  )
}

export default function DeepAnalysisTab({ parsed, analysis, lineage, onLoadLineage }: Props) {
  return (
    <div className="space-y-4">
      <section className="rounded-lg p-4" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
        <div className="mb-2 flex flex-wrap gap-2">
          <EvidenceBadge>确定性解析证据</EvidenceBadge>
          <EvidenceBadge tone="ai">AI 辅助解释</EvidenceBadge>
          <EvidenceBadge tone="review">待人工复核</EvidenceBadge>
        </div>
        <p className="text-[12.5px] leading-5" style={{ color: 'var(--text-secondary)' }}>
          深度分析页保留复杂信息，用于排障、复核、验收和二次开发。默认工作台只展示帮助快速接手的结论级信息。
        </p>
      </section>

      <Section title="完整数据血缘" hint="查看控件、参数、数据集和展示字段之间的完整关系。">
        <LineageTab parsed={parsed} lineage={lineage} onLoadLineage={onLoadLineage} />
      </Section>

      <Section title="数据集与字段证据" hint="数据集类型、字段数量、连接、参数和共享字段。">
        <DatasetTable parsed={parsed} />
      </Section>

      <Section title="SQL 与取数逻辑" hint="SQL 原文默认折叠，避免干扰第一屏判断。">
        <SqlBlocks parsed={parsed} />
      </Section>

      <Section title="控件联动链路" hint="控件如何影响参数、SQL、数据集和展示结果。">
        <ChainsTab parsed={parsed} analysis={analysis} />
      </Section>

      <Section title="指标、公式与展示规则" hint="字段业务语义、公式解释、条件高亮和填报配置。">
        <div className="space-y-4">
          <IndicatorsTab analysis={analysis} />
          <StepsTab parsed={parsed} analysis={analysis} />
        </div>
      </Section>

      <Section title="人工复核清单" hint="AI 不确定项、未匹配链路、公式和交付前风险。">
        <ReviewList parsed={parsed} analysis={analysis} lineage={lineage} />
      </Section>

      <Section title="质量评分与验收辅助" hint="评分用于复核和验收，不作为开发者第一眼接手信息。">
        <P1QualityPanel parsed={parsed} analysis={analysis} lineage={lineage} />
      </Section>
    </div>
  )
}
