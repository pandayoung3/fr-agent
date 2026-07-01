import type { ParsedReport } from '../types'

interface Props {
  parsed: ParsedReport
  dbEnriched: boolean
}

interface Metric {
  label: string
  value: string | number
  meta?: string
  accent?: boolean
}

function MetricCard({ label, value, meta, accent }: Metric) {
  return (
    <div
      className="rounded-lg px-3.5 py-3"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
    >
      <div className="text-[11px] font-medium" style={{ color: 'var(--text-muted)' }}>
        {label}
      </div>
      <div className="mt-2 flex items-end justify-between gap-2">
        <div
          className="truncate text-[20px] font-semibold leading-none"
          style={{ color: accent ? 'var(--accent)' : 'var(--text-primary)' }}
        >
          {value}
        </div>
        {meta && (
          <div className="mb-0.5 rounded px-1.5 py-0.5 text-[10.5px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
            {meta}
          </div>
        )}
      </div>
    </div>
  )
}

export default function StatCards({ parsed, dbEnriched }: Props) {
  const isWriteback = parsed.report_type === 'writeback'
  const metrics: Metric[] = [
    { label: 'FR 版本', value: parsed.fr_version },
    { label: 'Sheet', value: parsed.sheet_count },
    { label: '数据集', value: parsed.datasets.length, meta: dbEnriched ? '已增强' : undefined, accent: true },
    { label: '参数控件', value: parsed.widgets.length },
    { label: '文件大小', value: parsed.file_size_kb, meta: 'KB' },
    { label: '报表类型', value: isWriteback ? '填报' : '查询', meta: isWriteback ? 'Writeback' : 'Query' },
  ]

  return (
    <section
      className="grid gap-2 sm:grid-cols-2 xl:grid-cols-6"
      aria-label="报表解析摘要"
    >
      {metrics.map(metric => (
        <MetricCard key={metric.label} {...metric} />
      ))}
    </section>
  )
}
