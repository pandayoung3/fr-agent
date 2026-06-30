import { useState, useRef } from 'react'
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
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M12 2L9.5 9.5 2 12l7.5 2.5L12 22l2.5-7.5L22 12l-7.5-2.5L12 2z"
        stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round"/>
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

  // ── 待分析：横条布局 ──────────────────────────────────────────────────────
  if (!analyzing) {
    return (
      <div
        className="flex items-center gap-4 px-4 py-3 rounded-lg"
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ background: 'var(--accent-surface)', color: 'var(--accent)' }}
        >
          <SparkIcon size={15} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            准备就绪，开始 AI 分析
          </div>
          <div className="text-[11px] mt-0.5 truncate" style={{ color: 'var(--text-muted)' }}>
            {dbEnriched
              ? '已接入数据库字段信息，分析结果将更加精准'
              : '可在左侧配置数据库连接（可跳过）'
            }
          </div>
        </div>

        <button
          onClick={handleStart}
          className="flex items-center gap-1.5 px-4 py-2 rounded-md text-[12.5px] font-medium flex-shrink-0 transition-colors"
          style={{ background: 'var(--accent)', color: '#fff' }}
          onMouseOver={e => (e.currentTarget.style.background = 'var(--accent-dim)')}
          onMouseOut={e => (e.currentTarget.style.background = 'var(--accent)')}
        >
          <SparkIcon size={12} />
          启动 AI 分析
        </button>
      </div>
    )
  }

  // ── 分析中：紧凑日志条 ────────────────────────────────────────────────────
  return (
    <div
      className="rounded-lg px-4 py-3"
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <svg className="spin flex-shrink-0" width="13" height="13" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="var(--border-strong)" strokeWidth="2"/>
          <path d="M12 3a9 9 0 0 1 9 9" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
        <span className="text-[12.5px] font-medium" style={{ color: 'var(--text-primary)' }}>
          AI 正在分析报表结构...
        </span>
      </div>

      <div
        ref={logsRef}
        className="space-y-1 max-h-24 overflow-y-auto pl-3"
        style={{ borderLeft: '2px solid var(--border)' }}
      >
        {logs.map((log, i) => (
          <div key={i} className="flex gap-1.5 text-[11.5px] leading-relaxed fade-in-up" style={{ color: 'var(--text-secondary)' }}>
            <span style={{ color: 'var(--accent)', flexShrink: 0 }}>›</span>
            <span>{log}</span>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-[11.5px] stream-cursor" style={{ color: 'var(--text-muted)' }}>初始化</div>
        )}
      </div>
    </div>
  )
}
