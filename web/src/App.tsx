import { useState, useCallback } from 'react'
import type { AppState, ParsedReport, AnalysisResult, ChatMessage } from './types'
import LandingPage from './pages/LandingPage'
import { parseCpt, getLineage } from './api'
import WorkflowBar from './components/WorkflowBar'
import UploadZone from './components/UploadZone'
import StatCards from './components/StatCards'
import Sidebar from './components/Sidebar'
import AnalyzePanel from './components/AnalyzePanel'
import ResultTabs from './components/tabs/ResultTabs'

const INIT: AppState = {
  phase: 'idle',
  parsed: null,
  analysis: null,
  lineage: null,
  dbEnriched: false,
  streamLog: [],
  chatHistory: [],
  error: null,
}

export default function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [state, setState] = useState<AppState>(INIT)

  const update = useCallback((patch: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...patch }))
  }, [])

  async function handleFile(file: File) {
    update({ phase: 'uploading', error: null })
    try {
      const parsed = await parseCpt(file)
      update({ phase: 'uploaded', parsed, analysis: null, lineage: null, dbEnriched: false, chatHistory: [], streamLog: [] })
    } catch (e) {
      update({ phase: 'idle', error: String(e) })
    }
  }

  function handleEnriched(enriched: ParsedReport) {
    update({ parsed: enriched, dbEnriched: true, analysis: null })
  }

  function handleAnalysisDone(result: AnalysisResult) {
    update({ phase: 'done', analysis: result })
  }

  function handleAnalysisError(msg: string) {
    update({ error: msg })
  }

  async function handleLoadLineage() {
    if (!state.parsed) return
    try {
      const lineage = await getLineage(state.parsed)
      update({ lineage })
    } catch (e) {
      console.error('lineage load failed', e)
    }
  }

  const hasDbDatasets = (state.parsed?.datasets ?? []).some(d => d.type === 'DBTableData')

  if (showLanding) {
    return <LandingPage onStart={() => setShowLanding(false)} />
  }

  return (
    <div className="min-h-[100dvh] flex flex-col" style={{ background: 'var(--bg)' }}>
      {/* Header */}
      <header
        className="sticky top-0 z-50 flex items-center gap-3 px-6"
        style={{
          background: 'rgba(255,255,255,0.9)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid var(--border)',
          height: '56px',
        }}
      >
        {/* Logo mark */}
        <div className="flex items-center gap-2.5 select-none">
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <rect x="2" y="10" width="4" height="10" rx="1.5" fill="#2563eb"/>
            <rect x="9" y="5" width="4" height="15" rx="1.5" fill="#2563eb" opacity="0.7"/>
            <rect x="16" y="1" width="4" height="19" rx="1.5" fill="#2563eb" opacity="0.45"/>
          </svg>
          <span className="text-[15px] font-semibold tracking-tight text-slate-800">
            FR 报表交接 Agent
          </span>
        </div>

        {/* Divider */}
        <div className="w-px h-4 bg-slate-200 mx-1" />

        <span className="text-xs text-slate-400 hidden sm:block">
          FineReport 报表智能交接工具
        </span>

        <div className="ml-auto flex items-center gap-2">
          {state.parsed && (
            <span
              className="text-xs px-2.5 py-1 rounded-md"
              style={{ color: 'var(--text-muted)', background: 'var(--bg)', border: '1px solid var(--border)' }}
            >
              {state.parsed.file_name}
            </span>
          )}
          <button
            onClick={() => setShowLanding(true)}
            className="text-xs px-3 py-1.5 rounded-md transition-colors"
            style={{ color: 'var(--text-muted)', border: '1px solid var(--border)', background: 'transparent', cursor: 'pointer' }}
            onMouseOver={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
            onMouseOut={e => (e.currentTarget.style.borderColor = 'var(--border)')}
          >
            产品介绍
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 gap-4 px-4 py-3 max-w-[1440px] mx-auto w-full">
        <Sidebar
          parsed={state.parsed}
          dbEnriched={state.dbEnriched}
          onEnriched={handleEnriched}
          onReset={() => setState(INIT)}
        />

        <main className="flex-1 min-w-0 flex flex-col gap-2">
          <WorkflowBar
            phase={state.phase}
            dbEnriched={state.dbEnriched}
            hasDbDatasets={hasDbDatasets}
          />

          {/* Error */}
          {state.error && (
            <div
              className="flex items-start gap-2.5 px-4 py-3 rounded-lg text-sm"
              style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c' }}
            >
              <svg className="flex-shrink-0 mt-0.5" width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4a.75.75 0 0 1 1.5 0v3a.75.75 0 0 1-1.5 0V5zm.75 6.5a.875.875 0 1 1 0-1.75.875.875 0 0 1 0 1.75z"/>
              </svg>
              <span className="flex-1">{state.error}</span>
              <button
                onClick={() => update({ error: null })}
                className="text-red-300 hover:text-red-500 flex-shrink-0 transition-colors"
                aria-label="关闭"
              >
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06z"/>
                </svg>
              </button>
            </div>
          )}

          {/* Upload */}
          {(state.phase === 'idle' || state.phase === 'uploading') && (
            <UploadZone onFile={handleFile} loading={state.phase === 'uploading'} />
          )}

          {/* Post-upload */}
          {state.parsed && (
            <>
              {/* File badge */}
              <div
                className="flex items-center gap-2 px-3 py-1.5 rounded-md text-[12.5px]"
                style={{ background: 'var(--success-surface)', border: '1px solid var(--success-border)', color: 'var(--success)' }}
              >
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0z"/>
                </svg>
                <span>已解析 <strong>{state.parsed.file_name}</strong></span>
              </div>

              <StatCards parsed={state.parsed} dbEnriched={state.dbEnriched} />

              {!state.analysis && (
                <AnalyzePanel
                  parsed={state.parsed}
                  dbEnriched={state.dbEnriched}
                  onDone={handleAnalysisDone}
                  onError={handleAnalysisError}
                />
              )}

              {state.analysis && state.phase === 'done' && (
                <>
                  <div className="flex items-center justify-end gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <span>分析完成，消耗 {state.analysis._tokens_used ?? '?'} tokens</span>
                    <button
                      onClick={() => update({ analysis: null, phase: 'uploaded', lineage: null })}
                      className="transition-colors"
                      style={{ color: 'var(--accent)' }}
                      onMouseOver={e => (e.currentTarget.style.color = 'var(--accent-dim)')}
                      onMouseOut={e => (e.currentTarget.style.color = 'var(--accent)')}
                    >
                      重新分析
                    </button>
                  </div>
                  <ResultTabs
                    parsed={state.parsed}
                    analysis={state.analysis}
                    lineage={state.lineage}
                    onLoadLineage={handleLoadLineage}
                    chatHistory={state.chatHistory}
                    onChatHistory={(h: ChatMessage[]) => update({ chatHistory: h })}
                  />
                </>
              )}
            </>
          )}

          {state.phase === 'idle' && (
            <p className="text-center text-xs pt-1" style={{ color: 'var(--text-muted)' }}>
              支持解析：数据集结构 · SQL 语句 · 参数控件 · 单元格绑定 · 数据血缘 · AI 业务语义分析
            </p>
          )}
        </main>
      </div>
    </div>
  )
}
