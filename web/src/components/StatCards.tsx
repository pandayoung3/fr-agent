import type { ParsedReport } from '../types'

interface Props {
  parsed: ParsedReport
  dbEnriched: boolean
}

function Card({ label, value, sub, accent }: { label: string; value: string | number; sub?: string; accent?: boolean }) {
  return (
    <div
      className="flex flex-col rounded-lg px-3 py-2"
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)',
        minWidth: 72,
      }}
    >
      <div className="text-[10px] uppercase tracking-[0.07em] font-medium mb-1" style={{ color: 'var(--text-muted)' }}>
        {label}
      </div>
      <div
        className="text-[18px] leading-none font-bold tracking-tight"
        style={{ color: accent ? 'var(--accent)' : 'var(--text-primary)' }}
      >
        {value}
      </div>
      {sub && (
        <div className="text-[10px] mt-0.5" style={{ color: 'var(--text-muted)' }}>{sub}</div>
      )}
    </div>
  )
}

export default function StatCards({ parsed, dbEnriched }: Props) {
  const isWriteback = parsed.report_type === 'writeback'
  return (
    <div className="flex flex-wrap gap-1.5">
      <Card label="FR 版本" value={parsed.fr_version} />
      <Card label="Sheet" value={parsed.sheet_count} />
      <Card label="数据集" value={parsed.datasets.length} sub={dbEnriched ? '已增强' : undefined} accent />
      <Card label="参数控件" value={parsed.widgets.length} />
      <Card label="大小" value={parsed.file_size_kb} sub="KB" />
      <div
        className="flex flex-col rounded-lg px-3 py-2"
        style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      >
        <div className="text-[10px] uppercase tracking-[0.07em] font-medium mb-1" style={{ color: 'var(--text-muted)' }}>
          类型
        </div>
        <div className="text-[12px] font-semibold leading-tight" style={{ color: isWriteback ? '#d97706' : 'var(--text-secondary)' }}>
          {isWriteback ? '填报' : '查询'}
        </div>
      </div>
    </div>
  )
}
