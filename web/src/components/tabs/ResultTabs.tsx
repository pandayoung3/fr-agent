import { useState } from 'react'
import type { ParsedReport, AnalysisResult, LineageResult, ChatMessage } from '../../types'
import ChatTab from './ChatTab'
import ExportTab from './ExportTab'
import WorkbenchTab from './WorkbenchTab'
import ChangeImpactTab from './ChangeImpactTab'
import DeepAnalysisTab from './DeepAnalysisTab'
import type { ExportHistoryItem } from '../../historyStore'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
  onLoadLineage: () => void
  chatHistory: ChatMessage[]
  onChatHistory: (h: ChatMessage[]) => void
  onExportRecord: (item: Omit<ExportHistoryItem, 'id' | 'created_at'>) => void
}

const TABS = [
  { id: 'workbench', label: '工作台' },
  { id: 'change', label: '变更建议' },
  { id: 'deep', label: '深度分析' },
  { id: 'chat', label: '问答' },
  { id: 'export', label: '导出' },
]

export default function ResultTabs({
  parsed,
  analysis,
  lineage,
  onLoadLineage,
  chatHistory,
  onChatHistory,
  onExportRecord,
}: Props) {
  const [active, setActive] = useState('workbench')
  const [chatPrompt, setChatPrompt] = useState('')

  function askFromWorkbench(question: string) {
    setChatPrompt(question)
    setActive('chat')
  }

  return (
    <section
      className="overflow-hidden rounded-lg"
      style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-md)' }}
      aria-label="分析结果"
    >
      <div className="flex items-center justify-between gap-3 px-3 pt-2" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex overflow-x-auto">
          {TABS.map(tab => {
            const isActive = active === tab.id
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActive(tab.id)}
                className="relative flex-shrink-0 rounded-t-md px-4 py-2.5 text-[12.5px] font-semibold whitespace-nowrap transition-colors"
                style={{
                  color: isActive ? 'var(--accent)' : 'var(--text-muted)',
                  background: isActive ? 'var(--accent-surface)' : 'transparent',
                }}
                onMouseOver={e => {
                  if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)'
                }}
                onMouseOut={e => {
                  if (!isActive) e.currentTarget.style.color = 'var(--text-muted)'
                }}
              >
                {tab.label}
                {isActive && (
                  <span
                    className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full"
                    style={{ background: 'var(--accent)' }}
                  />
                )}
              </button>
            )
          })}
        </div>
        <div className="hidden text-[11px] md:block" style={{ color: 'var(--text-muted)' }}>
          工作台看结论，深度分析看完整证据
        </div>
      </div>

      <div className="p-5">
        {active === 'workbench' && (
          <WorkbenchTab
            parsed={parsed}
            analysis={analysis}
            lineage={lineage}
            onSelectTab={setActive}
            onAskQuestion={askFromWorkbench}
          />
        )}
        {active === 'change' && (
          <ChangeImpactTab
            parsed={parsed}
            analysis={analysis}
            lineage={lineage}
            onSelectTab={setActive}
          />
        )}
        {active === 'deep' && (
          <DeepAnalysisTab
            parsed={parsed}
            analysis={analysis}
            lineage={lineage}
            onLoadLineage={onLoadLineage}
          />
        )}
        {active === 'chat' && (
          <ChatTab
            parsed={parsed}
            analysis={analysis}
            history={chatHistory}
            onHistoryChange={onChatHistory}
            initialQuestion={chatPrompt}
          />
        )}
        {active === 'export' && <ExportTab parsed={parsed} analysis={analysis} onExportRecord={onExportRecord} />}
      </div>
    </section>
  )
}
