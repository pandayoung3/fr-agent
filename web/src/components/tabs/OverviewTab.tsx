import type { AnalysisResult } from '../../types'

interface Props { analysis: AnalysisResult }

function AIBadge() {
  return (
    <span
      className="text-[9px] font-semibold px-1.5 py-0.5 rounded"
      style={{ background: 'var(--accent-surface)', color: 'var(--accent)', border: '1px solid var(--accent-border)' }}
    >
      AI
    </span>
  )
}

function Card({ title, children, ai }: { title: string; children: React.ReactNode; ai?: boolean }) {
  return (
    <div
      className="rounded-lg p-4"
      style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
    >
      <div className="flex items-center gap-1.5 mb-2.5">
        <span className="text-[11px] font-semibold uppercase tracking-[0.07em]" style={{ color: 'var(--text-muted)' }}>
          {title}
        </span>
        {ai && <AIBadge />}
      </div>
      {children}
    </div>
  )
}

export default function OverviewTab({ analysis }: Props) {
  return (
    <div className="space-y-4">
      {/* Purpose */}
      <div
        className="rounded-lg p-4"
        style={{
          background: 'var(--accent-surface)',
          border: '1px solid var(--accent-border)',
        }}
      >
        <div className="flex items-center gap-1.5 mb-2">
          <span className="text-[11px] font-semibold uppercase tracking-[0.07em]" style={{ color: 'var(--accent)' }}>
            报表业务用途
          </span>
          <AIBadge />
        </div>
        <p
          className="text-[14px] font-medium leading-relaxed"
          style={{ color: '#1e3a5f' }}
        >
          {analysis.purpose ?? '（AI 未能推断）'}
        </p>
      </div>

      {/* Layout + Dataset */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {analysis.layout_description && (
          <Card title="布局结构" ai>
            <p className="text-[13px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {analysis.layout_description}
            </p>
          </Card>
        )}
        {analysis.dataset_relationships && (
          <Card title="数据集关系" ai>
            <p className="text-[13px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {analysis.dataset_relationships}
            </p>
          </Card>
        )}
      </div>

      {/* Field semantics - collapsible */}
      {analysis.field_semantics && (
        <details>
          <summary
            className="cursor-pointer list-none flex items-center gap-2 py-1.5 select-none"
            style={{ color: 'var(--text-secondary)' }}
          >
            <svg
              width="10" height="10" viewBox="0 0 10 10" fill="none"
              className="transition-transform"
              style={{ display: 'inline-block' }}
            >
              <path d="M3 2l4 3-4 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span className="text-[12.5px] font-medium">关键字段业务含义（AI 推断）</span>
          </summary>
          <div
            className="text-[13px] leading-relaxed mt-2 pl-4 py-3"
            style={{
              color: 'var(--text-secondary)',
              borderLeft: '2px solid var(--accent-border)',
            }}
          >
            {analysis.field_semantics}
          </div>
        </details>
      )}

      {/* Risks */}
      {(analysis.notes_or_risks ?? []).length > 0 && (
        <div className="space-y-2">
          <div className="text-[11px] font-semibold uppercase tracking-[0.07em]" style={{ color: 'var(--text-muted)' }}>
            风险点与注意事项
          </div>
          {analysis.notes_or_risks!.map((r, i) => (
            <div
              key={i}
              className="flex gap-2.5 px-3.5 py-2.5 rounded-lg text-[13px] leading-relaxed"
              style={{
                background: '#fffbeb',
                borderLeft: '3px solid #f59e0b',
                color: '#92400e',
              }}
            >
              <svg className="flex-shrink-0 mt-0.5" width="13" height="13" viewBox="0 0 16 16" fill="#f59e0b">
                <path d="M8 1.333a.667.667 0 0 1 .577.334l6 10.333A.667.667 0 0 1 14 13H2a.667.667 0 0 1-.577-1L7.423 1.667A.667.667 0 0 1 8 1.333zM8 6a.667.667 0 0 0-.667.667v2.666a.667.667 0 1 0 1.334 0V6.667A.667.667 0 0 0 8 6zm0 5.333a.667.667 0 1 0 0 1.334.667.667 0 0 0 0-1.334z"/>
              </svg>
              <span>{r}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
