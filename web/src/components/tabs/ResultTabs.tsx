import { useState } from 'react'
import type { ParsedReport, AnalysisResult, LineageResult, ChatMessage } from '../../types'
import OverviewTab from './OverviewTab'
import ChainsTab from './ChainsTab'
import IndicatorsTab from './IndicatorsTab'
import StepsTab from './StepsTab'
import LineageTab from './LineageTab'
import ChatTab from './ChatTab'
import ExportTab from './ExportTab'

interface Props {
  parsed: ParsedReport
  analysis: AnalysisResult
  lineage: LineageResult | null
  onLoadLineage: () => void
  chatHistory: ChatMessage[]
  onChatHistory: (h: ChatMessage[]) => void
}

const TABS = [
  { id: 'overview',    label: '概览' },
  { id: 'chains',      label: '交互链路' },
  { id: 'indicators',  label: '指标字典' },
  { id: 'steps',       label: '开发步骤' },
  { id: 'lineage',     label: '数据血缘' },
  { id: 'chat',        label: '问答' },
  { id: 'export',      label: '导出' },
]

export default function ResultTabs({ parsed, analysis, lineage, onLoadLineage, chatHistory, onChatHistory }: Props) {
  const [active, setActive] = useState('overview')

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-md)',
      }}
    >
      {/* Tab bar */}
      <div
        className="flex overflow-x-auto"
        style={{ borderBottom: '1px solid var(--border)' }}
      >
        {TABS.map(tab => {
          const isActive = active === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              className="relative px-4 py-3 text-[12.5px] font-medium whitespace-nowrap transition-colors duration-150 flex-shrink-0"
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

      {/* Tab content */}
      <div className="p-5">
        {active === 'overview'   && <OverviewTab analysis={analysis} />}
        {active === 'chains'     && <ChainsTab parsed={parsed} analysis={analysis} />}
        {active === 'indicators' && <IndicatorsTab analysis={analysis} />}
        {active === 'steps'      && <StepsTab parsed={parsed} analysis={analysis} />}
        {active === 'lineage'    && (
          <LineageTab parsed={parsed} lineage={lineage} onLoadLineage={onLoadLineage} />
        )}
        {active === 'chat'       && (
          <ChatTab
            parsed={parsed}
            analysis={analysis}
            history={chatHistory}
            onHistoryChange={onChatHistory}
          />
        )}
        {active === 'export'     && <ExportTab parsed={parsed} analysis={analysis} />}
      </div>
    </div>
  )
}
