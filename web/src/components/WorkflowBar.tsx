import type { AppPhase } from '../types'

interface Props {
  phase: AppPhase
  dbEnriched: boolean
  hasDbDatasets: boolean
}

type StepStatus = 'pending' | 'active' | 'done' | 'skip'

function getStatuses(phase: AppPhase, dbEnriched: boolean, hasDbDatasets: boolean): StepStatus[] {
  const s1: StepStatus = phase === 'idle' || phase === 'uploading' ? 'active' : 'done'
  const s2: StepStatus = !hasDbDatasets
    ? 'skip'
    : dbEnriched
    ? 'done'
    : phase === 'uploaded' || phase === 'enriching'
    ? 'active'
    : phase === 'idle' || phase === 'uploading'
    ? 'pending'
    : 'skip'
  const s3: StepStatus = phase === 'analyzing' ? 'active' : phase === 'done' ? 'done' : 'pending'
  const s4: StepStatus = phase === 'done' ? 'active' : 'pending'
  return [s1, s2, s3, s4]
}

function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

function Step({ num, label, sub, status }: { num: number; label: string; sub?: string; status: StepStatus }) {
  const isDone    = status === 'done'
  const isActive  = status === 'active'
  const isSkip    = status === 'skip'

  const circleStyle: React.CSSProperties = isDone
    ? { background: 'var(--success)', color: '#fff', boxShadow: 'none' }
    : isActive
    ? { background: 'var(--accent)', color: '#fff', boxShadow: '0 0 0 3px var(--accent-surface)' }
    : isSkip
    ? { background: '#e2e8f0', color: '#94a3b8' }
    : { background: '#f1f5f9', color: '#94a3b8' }

  const labelColor = isDone
    ? 'var(--success)'
    : isActive
    ? 'var(--accent)'
    : 'var(--text-muted)'

  const labelWeight = isActive ? '600' : '500'

  return (
    <div className="flex items-center gap-2.5 flex-1 min-w-0">
      <div
        className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-200"
        style={circleStyle}
      >
        {isDone
          ? <CheckIcon />
          : isSkip
          ? <span style={{ fontSize: '11px', fontWeight: 600 }}>-</span>
          : <span style={{ fontSize: '11px', fontWeight: 700 }}>{num}</span>
        }
      </div>
      <div className="min-w-0">
        <div
          className="text-[13px] leading-tight truncate transition-colors duration-200"
          style={{ color: labelColor, fontWeight: labelWeight }}
        >
          {label}
        </div>
        {sub && (
          <div className="text-[11px] mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {sub}
          </div>
        )}
      </div>
    </div>
  )
}

function Connector({ filled }: { filled: boolean }) {
  return (
    <div className="flex-shrink-0 mx-2" style={{ width: 32 }}>
      <div
        className="h-px transition-colors duration-300"
        style={{ background: filled ? 'var(--success)' : 'var(--border-strong)' }}
      />
    </div>
  )
}

export default function WorkflowBar({ phase, dbEnriched, hasDbDatasets }: Props) {
  const [s1, s2, s3, s4] = getStatuses(phase, dbEnriched, hasDbDatasets)
  const s2sub = !hasDbDatasets ? '不需要' : dbEnriched ? '已接入' : '可选'

  return (
    <div
      className="flex items-center px-4 py-2.5 rounded-lg"
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <Step num={1} label="上传 CPT" status={s1} />
      <Connector filled={s1 === 'done'} />
      <Step num={2} label="数据库增强" sub={s2sub} status={s2} />
      <Connector filled={s2 === 'done' || (s1 === 'done' && !hasDbDatasets)} />
      <Step num={3} label="AI 分析" status={s3} />
      <Connector filled={s3 === 'done'} />
      <Step num={4} label="查看导出" status={s4} />
    </div>
  )
}
