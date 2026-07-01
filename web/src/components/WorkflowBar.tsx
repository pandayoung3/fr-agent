import type { AppPhase } from '../types'

interface Props {
  phase: AppPhase
  dbEnriched: boolean
  hasDbDatasets: boolean
}

type StepStatus = 'pending' | 'active' | 'done' | 'skip'

const STEPS = [
  { label: '上传 CPT', detail: '读取文件结构' },
  { label: '数据增强', detail: '补全字段语义' },
  { label: 'AI 分析', detail: '生成理解结果' },
  { label: '工作台', detail: '血缘与问答' },
]

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

function StatusGlyph({ status, index }: { status: StepStatus; index: number }) {
  if (status === 'done') {
    return (
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M3.5 8.4 6.7 11.5 12.8 4.8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  }

  if (status === 'skip') {
    return <span className="text-[12px] font-semibold">-</span>
  }

  return <span className="text-[11px] font-bold">{index + 1}</span>
}

function Step({ step, status, index }: { step: { label: string; detail: string }; status: StepStatus; index: number }) {
  const tone = status === 'done'
    ? 'var(--success)'
    : status === 'active'
      ? 'var(--accent)'
      : 'var(--text-muted)'

  const dotStyle: React.CSSProperties = {
    background: status === 'done'
      ? 'var(--success)'
      : status === 'active'
        ? 'var(--accent)'
        : status === 'skip'
          ? '#e2e8f0'
          : '#f1f5f9',
    color: status === 'pending' || status === 'skip' ? 'var(--text-muted)' : '#fff',
    boxShadow: status === 'active' ? '0 0 0 4px var(--accent-surface)' : 'none',
  }

  return (
    <div className="relative flex min-w-[150px] flex-1 items-center gap-3">
      <div
        className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full transition-all"
        style={dotStyle}
      >
        <StatusGlyph status={status} index={index} />
      </div>
      <div className="min-w-0">
        <div className="truncate text-[13px] font-semibold leading-tight" style={{ color: tone }}>
          {step.label}
        </div>
        <div className="mt-0.5 truncate text-[11px]" style={{ color: 'var(--text-muted)' }}>
          {status === 'skip' ? '当前可跳过' : step.detail}
        </div>
      </div>
    </div>
  )
}

export default function WorkflowBar({ phase, dbEnriched, hasDbDatasets }: Props) {
  const statuses = getStatuses(phase, dbEnriched, hasDbDatasets)

  return (
    <section
      className="rounded-lg px-4 py-3"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      aria-label="解析流程"
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <div className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            解析流程
          </div>
          <div className="mt-0.5 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
            从 CPT 文件到可解释的报表血缘与业务语义
          </div>
        </div>
        <div
          className="rounded-md px-2.5 py-1 text-[11px] font-medium"
          style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
        >
          {phase === 'done' ? '已完成' : phase === 'uploading' ? '解析中' : phase === 'idle' ? '待上传' : '处理中'}
        </div>
      </div>

      <div className="flex items-center gap-3 overflow-x-auto pb-0.5">
        {STEPS.map((step, index) => (
          <div key={step.label} className="flex min-w-fit flex-1 items-center gap-3">
            <Step step={step} status={statuses[index]} index={index} />
            {index < STEPS.length - 1 && (
              <div
                className="h-px w-8 flex-shrink-0"
                style={{
                  background: statuses[index] === 'done' ? 'var(--success)' : 'var(--border-strong)',
                }}
              />
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
