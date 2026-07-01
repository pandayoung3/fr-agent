import { useState, useCallback } from 'react'
import type { AppState, ParsedReport, AnalysisResult, ChatMessage, BatchParseResult } from './types'
import LandingPage from './pages/LandingPage'
import { parseCpt, parseBatchCpts, getLineage } from './api'
import WorkflowBar from './components/WorkflowBar'
import UploadZone from './components/UploadZone'
import StatCards from './components/StatCards'
import Sidebar from './components/Sidebar'
import AnalyzePanel from './components/AnalyzePanel'
import BatchAssetsPanel from './components/BatchAssetsPanel'
import ResultTabs from './components/tabs/ResultTabs'
import {
  loadAnalysisHistory,
  loadExportHistory,
  saveAnalysisHistory,
  saveExportHistory,
  type AnalysisHistoryItem,
  type ExportHistoryItem,
} from './historyStore'

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

function LogoMark() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="12" width="4" height="8" rx="1.5" fill="var(--accent)" />
      <rect x="10" y="7" width="4" height="13" rx="1.5" fill="var(--accent)" opacity="0.72" />
      <rect x="17" y="3" width="4" height="17" rx="1.5" fill="var(--accent)" opacity="0.46" />
    </svg>
  )
}

export default function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [state, setState] = useState<AppState>(INIT)
  const [batchResult, setBatchResult] = useState<BatchParseResult | null>(null)
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisHistoryItem[]>(() => loadAnalysisHistory())
  const [exportHistory, setExportHistory] = useState<ExportHistoryItem[]>(() => loadExportHistory())

  const update = useCallback((patch: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...patch }))
  }, [])

  async function handleFile(file: File) {
    setBatchResult(null)
    update({ phase: 'uploading', error: null })
    try {
      const parsed = await parseCpt(file)
      update({ phase: 'uploaded', parsed, analysis: null, lineage: null, dbEnriched: false, chatHistory: [], streamLog: [] })
    } catch (e) {
      update({ phase: 'idle', error: String(e) })
    }
  }

  async function handleFiles(files: File[]) {
    if (files.length === 1) {
      await handleFile(files[0])
      return
    }

    update({ phase: 'uploading', error: null, parsed: null, analysis: null, lineage: null, chatHistory: [], streamLog: [] })
    try {
      const result = await parseBatchCpts(files)
      setBatchResult(result)
      update({ phase: 'idle' })
    } catch (e) {
      setBatchResult(null)
      update({ phase: 'idle', error: String(e) })
    }
  }

  function openBatchReport(parsed: ParsedReport) {
    setBatchResult(null)
    setState({
      ...INIT,
      phase: 'uploaded',
      parsed,
    })
  }

  function handleEnriched(enriched: ParsedReport) {
    update({ parsed: enriched, dbEnriched: true, analysis: null })
  }

  function handleAnalysisDone(result: AnalysisResult) {
    if (state.parsed) {
      setAnalysisHistory(saveAnalysisHistory(state.parsed, result))
    }
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
      <header
        className="sticky top-0 z-50 flex items-center gap-4 px-5"
        style={{
          background: 'rgba(255,255,255,0.92)',
          backdropFilter: 'blur(14px)',
          borderBottom: '1px solid var(--border)',
          height: 60,
        }}
      >
        <div className="flex items-center gap-3 select-none">
          <LogoMark />
          <div>
            <div className="text-[15px] font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
              FR-Agent
            </div>
            <div className="hidden text-[11px] sm:block" style={{ color: 'var(--text-muted)' }}>
              FineReport 报表交接分析工作台
            </div>
          </div>
        </div>

        <div className="ml-auto flex min-w-0 items-center gap-2">
          {state.parsed && (
            <span
              className="hidden max-w-[320px] truncate rounded-md px-2.5 py-1 text-[12px] md:inline-block"
              style={{ color: 'var(--text-secondary)', background: 'var(--bg)', border: '1px solid var(--border)' }}
              title={state.parsed.file_name}
            >
              {state.parsed.file_name}
            </span>
          )}
          <button
            type="button"
            onClick={() => setShowLanding(true)}
            className="rounded-md px-3 py-1.5 text-[12px] transition-colors"
            style={{ color: 'var(--text-muted)', border: '1px solid var(--border)', background: 'transparent' }}
            onMouseOver={e => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.color = 'var(--accent)'
            }}
            onMouseOut={e => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.color = 'var(--text-muted)'
            }}
          >
            产品介绍
          </button>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1520px] flex-1 flex-col gap-4 px-4 py-4 lg:flex-row">
        <Sidebar
          parsed={state.parsed}
          dbEnriched={state.dbEnriched}
          history={analysisHistory}
          exportHistory={exportHistory}
          onEnriched={handleEnriched}
          onRestore={(item: AnalysisHistoryItem) => {
            setBatchResult(null)
            setState({
              ...INIT,
              phase: 'done',
              parsed: item.parsed,
              analysis: item.analysis,
            })
          }}
          onReset={() => {
            setBatchResult(null)
            setState(INIT)
          }}
        />

        <main className="flex min-w-0 flex-1 flex-col gap-3">
          <WorkflowBar
            phase={state.phase}
            dbEnriched={state.dbEnriched}
            hasDbDatasets={hasDbDatasets}
          />

          {state.error && (
            <div
              className="flex items-start gap-3 rounded-lg px-4 py-3 text-[13px]"
              style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c' }}
            >
              <svg className="mt-0.5 flex-shrink-0" width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1Zm-.75 4a.75.75 0 0 1 1.5 0v3a.75.75 0 0 1-1.5 0V5ZM8 11.5a.875.875 0 1 1 0-1.75.875.875 0 0 1 0 1.75Z" />
              </svg>
              <span className="flex-1">{state.error}</span>
              <button
                type="button"
                onClick={() => update({ error: null })}
                className="flex-shrink-0 text-red-300 transition-colors hover:text-red-500"
                aria-label="关闭错误提示"
              >
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06Z" />
                </svg>
              </button>
            </div>
          )}

          {(state.phase === 'idle' || state.phase === 'uploading') && (
            <UploadZone onFile={handleFile} onFiles={handleFiles} loading={state.phase === 'uploading'} />
          )}

          {batchResult && state.phase !== 'uploading' && (
            <BatchAssetsPanel
              result={batchResult}
              onOpenReport={openBatchReport}
              onClear={() => setBatchResult(null)}
            />
          )}

          {state.parsed && (
            <>
              <div
                className="flex flex-wrap items-center gap-2 rounded-lg px-3.5 py-2 text-[12.5px]"
                style={{ background: 'var(--success-surface)', border: '1px solid var(--success-border)', color: 'var(--success)' }}
              >
                <svg width="15" height="15" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                  <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 0 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z" />
                </svg>
                <span className="min-w-0">
                  已解析 <strong>{state.parsed.file_name}</strong>
                </span>
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
                  <div className="flex items-center justify-end gap-3 text-[12px]" style={{ color: 'var(--text-muted)' }}>
                    <span>分析完成，消耗 {state.analysis._tokens_used ?? '?'} tokens</span>
                    <button
                      type="button"
                      onClick={() => update({ analysis: null, phase: 'uploaded', lineage: null })}
                      className="font-medium transition-colors"
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
                    onExportRecord={(item) => setExportHistory(saveExportHistory(item))}
                  />
                </>
              )}
            </>
          )}

          {state.phase === 'idle' && (
            <p className="text-center text-[12px]" style={{ color: 'var(--text-muted)' }}>
              支持解析：数据集结构、SQL 语句、参数控件、单元格绑定、数据血缘与 AI 业务语义分析
            </p>
          )}
        </main>
      </div>
    </div>
  )
}
