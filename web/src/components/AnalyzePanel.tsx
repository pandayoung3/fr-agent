import { useRef, useState } from 'react'
import type { ParsedReport, AnalysisResult } from '../types'
import { streamAnalyze } from '../api'

interface Props {
  parsed: ParsedReport
  dbEnriched: boolean
  onDone: (result: AnalysisResult) => void
  onError: (msg: string) => void
}

function SparkIcon({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2 9.6 9.6 2 12l7.6 2.4L12 22l2.4-7.6L22 12l-7.6-2.4L12 2Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function SpinnerIcon() {
  return (
    <svg className="spin flex-shrink-0" width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="var(--border-strong)" strokeWidth="2" />
      <path d="M12 3a9 9 0 0 1 9 9" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  )
}

export default function AnalyzePanel({ parsed, dbEnriched, onDone, onError }: Props) {
  const [analyzing, setAnalyzing] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const logsRef = useRef<HTMLDivElement>(null)

  async function handleStart() {
    setAnalyzing(true)
    setLogs([])
    try {
      await streamAnalyze(parsed, (event) => {
        if (event.type === 'progress') {
          setLogs(prev => {
            const next = [...prev, event.message as string]
            setTimeout(() => logsRef.current?.scrollTo(0, 9999), 50)
            return next
          })
        } else if (event.type === 'done') {
          const data = event.data as AnalysisResult
          setLogs(prev => [...prev, `分析完成，共消耗 ${data._tokens_used ?? '?'} tokens`])
          setTimeout(() => onDone(data), 400)
        } else if (event.type === 'error') {
          onError(event.message as string)
          setAnalyzing(false)
        }
      })
    } catch (e) {
      onError(String(e))
      setAnalyzing(false)
    }
  }

  if (!analyzing) {
    return (
      <section
        className="grid gap-4 rounded-lg p-4 lg:grid-cols-[minmax(0,1fr)_220px]"
        style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
        aria-label="AI 分析准备"
      >
        <div className="flex items-start gap-4">
          <div
            className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg"
            style={{ background: 'var(--accent-surface)', color: 'var(--accent)' }}
          >
            <SparkIcon size={17} />
          </div>
          <div className="min-w-0">
            <div className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              可以开始 AI 分析
            </div>
            <p className="mt-1 text-[12.5px] leading-5" style={{ color: 'var(--text-secondary)' }}>
              将基于当前 CPT 结构生成业务用途、数据关系、指标解释、交互链路和开发复刻步骤。
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {[
                `${parsed.datasets.length} 个数据集`,
                `${parsed.widgets.length} 个控件`,
                dbEnriched ? '数据库字段已增强' : '可跳过数据增强',
              ].map(item => (
                <span
                  key={item}
                  className="rounded-md px-2 py-1 text-[11px]"
                  style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-start lg:justify-end">
          <button
            type="button"
            onClick={handleStart}
            className="flex h-10 items-center justify-center gap-2 rounded-md px-4 text-[13px] font-semibold transition-colors"
            style={{ background: 'var(--accent)', color: '#fff', minWidth: 150 }}
            onMouseOver={e => (e.currentTarget.style.background = 'var(--accent-dim)')}
            onMouseOut={e => (e.currentTarget.style.background = 'var(--accent)')}
          >
            <SparkIcon size={13} />
            启动 AI 分析
          </button>
        </div>
      </section>
    )
  }

  return (
    <section
      className="rounded-lg p-4"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      aria-label="AI 分析进度"
    >
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <SpinnerIcon />
          <span className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            AI 正在分析报表结构
          </span>
        </div>
        <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
          流式生成中
        </span>
      </div>

      <div
        ref={logsRef}
        className="max-h-32 space-y-1 overflow-y-auto rounded-md px-3 py-2"
        style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
      >
        {logs.map((log, i) => (
          <div key={`${log}-${i}`} className="flex gap-2 text-[12px] leading-5 fade-in-up" style={{ color: 'var(--text-secondary)' }}>
            <span style={{ color: 'var(--accent)', flexShrink: 0 }}>•</span>
            <span>{log}</span>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-[12px] stream-cursor" style={{ color: 'var(--text-muted)' }}>
            初始化分析任务
          </div>
        )}
      </div>
    </section>
  )
}
