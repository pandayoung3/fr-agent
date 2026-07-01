import { useState } from 'react'
import type { ParsedReport } from '../types'
import { enrichParsed } from '../api'
import type { AnalysisHistoryItem, ExportHistoryItem } from '../historyStore'

interface Props {
  parsed: ParsedReport | null
  dbEnriched: boolean
  history: AnalysisHistoryItem[]
  exportHistory: ExportHistoryItem[]
  onEnriched: (enriched: ParsedReport) => void
  onRestore: (item: AnalysisHistoryItem) => void
  onReset: () => void
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  fontSize: '12px',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '7px 10px',
  outline: 'none',
  color: 'var(--text-primary)',
  background: 'var(--bg)',
  transition: 'border-color 0.15s',
}

const panelStyle: React.CSSProperties = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)',
  padding: 14,
  boxShadow: 'var(--shadow-sm)',
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-1 text-[11px] font-medium" style={{ color: 'var(--text-muted)' }}>
      {children}
    </div>
  )
}

function SectionTitle({ children, badge }: { children: React.ReactNode; badge?: string }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-2">
      <div className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
        {children}
      </div>
      {badge && (
        <span
          className="rounded-full px-2 py-0.5 text-[10.5px]"
          style={{ background: 'var(--bg)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}
        >
          {badge}
        </span>
      )}
    </div>
  )
}

export default function Sidebar({ parsed, dbEnriched, history, exportHistory, onEnriched, onRestore, onReset }: Props) {
  const [frDir, setFrDir] = useState(() => {
    const home = navigator.platform.includes('Mac') ? '/Users' : '/home'
    return `${home}/${import.meta.env.VITE_USER ?? 'pandayoung3'}/FineReport/webapps/webroot/WEB-INF`
  })
  const [passwords, setPasswords] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [connStatus, setConnStatus] = useState<Record<string, 'ok' | 'error' | 'skip'>>({})
  const [resetConfirm, setResetConfirm] = useState(false)

  const dbDatasets = parsed?.datasets.filter(d => d.type === 'DBTableData') ?? []

  async function handleConnect() {
    if (!parsed) return
    setLoading(true)
    try {
      const { parsed: enriched, report } = await enrichParsed(parsed, frDir, passwords)
      const status: Record<string, 'ok' | 'error' | 'skip'> = {}
      for (const item of report.success) status[(item as string).split('/')[0]] = 'ok'
      for (const item of report.failed as Array<{ conn: string }>) status[item.conn] = 'error'
      for (const conn of report.skipped) status[conn] = 'skip'
      setConnStatus(status)
      if (report.success.length > 0) onEnriched(enriched)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="flex w-full flex-shrink-0 flex-col gap-3 lg:w-[270px]">
      <div style={panelStyle}>
        <SectionTitle badge="可选">数据增强</SectionTitle>
        <p className="mb-3 text-[11.5px] leading-5" style={{ color: 'var(--text-muted)' }}>
          连接 FineReport 本地配置后，可补全 DBTableData 字段类型与注释。
        </p>

        {!parsed && (
          <div className="rounded-md px-3 py-2 text-[11.5px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
            上传 CPT 后可查看是否需要增强。
          </div>
        )}

        {parsed && dbDatasets.length === 0 && (
          <div
            className="rounded-md px-3 py-2 text-[11.5px] leading-5"
            style={{ background: 'var(--success-surface)', color: 'var(--success)', border: '1px solid var(--success-border)' }}
          >
            当前报表使用内置数据集，无需连接真实数据库。
          </div>
        )}

        {parsed && dbDatasets.length > 0 && (
          <>
            {dbEnriched ? (
              <div className="space-y-2">
                <div
                  className="rounded-md px-3 py-2 text-[11.5px]"
                  style={{ background: 'var(--success-surface)', color: 'var(--success)', border: '1px solid var(--success-border)' }}
                >
                  字段信息已成功接入
                </div>
                {Object.entries(connStatus).map(([conn, st]) => (
                  <div key={conn} className="flex items-center gap-2 text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
                    <span style={{ color: st === 'ok' ? 'var(--success)' : st === 'error' ? '#dc2626' : 'var(--text-muted)' }}>
                      {st === 'ok' ? '✓' : st === 'error' ? '!' : '-'}
                    </span>
                    <span className="truncate">{conn}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <Label>FineReport WEB-INF 路径</Label>
                  <input
                    type="text"
                    value={frDir}
                    onChange={e => setFrDir(e.target.value)}
                    placeholder="/path/to/WEB-INF"
                    style={inputStyle}
                    onFocus={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
                    onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}
                  />
                </div>

                {parsed.db_connections.map(conn => (
                  <div key={conn}>
                    <Label>
                      {conn} 密码
                      {connStatus[conn] === 'error' && (
                        <span style={{ color: '#dc2626', marginLeft: 4 }}>连接失败</span>
                      )}
                    </Label>
                    <input
                      type="password"
                      value={passwords[conn] ?? ''}
                      onChange={e => setPasswords(p => ({ ...p, [conn]: e.target.value }))}
                      placeholder="留空则跳过"
                      style={inputStyle}
                      onFocus={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
                      onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}
                    />
                  </div>
                ))}

                <button
                  type="button"
                  onClick={handleConnect}
                  disabled={loading || Object.keys(passwords).filter(k => passwords[k]).length === 0}
                  className="w-full rounded-md py-2 text-[12px] font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50"
                  style={{ background: 'var(--accent)', color: '#fff' }}
                  onMouseOver={e => {
                    if (!loading) e.currentTarget.style.background = 'var(--accent-dim)'
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.background = 'var(--accent)'
                  }}
                >
                  {loading ? '连接中...' : '连接并获取字段信息'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {history.length > 0 && (
        <div style={panelStyle}>
          <SectionTitle>最近分析</SectionTitle>
          <div className="space-y-2">
            {history.slice(0, 4).map(item => (
              <button
                key={item.id}
                type="button"
                onClick={() => onRestore(item)}
                className="w-full rounded-md px-2.5 py-2 text-left transition-colors"
                style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
              >
                <div className="truncate text-[11.5px] font-medium" style={{ color: 'var(--text-primary)' }}>
                  {item.file_name}
                </div>
                <div className="mt-0.5 truncate text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                  {item.purpose || item.report_type}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {exportHistory.length > 0 && (
        <div style={panelStyle}>
          <SectionTitle>最近导出</SectionTitle>
          <div className="space-y-2">
            {exportHistory.slice(0, 4).map(item => (
              <div
                key={item.id}
                className="rounded-md px-2.5 py-2"
                style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
                title={item.filename}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-[11.5px] font-medium" style={{ color: 'var(--text-primary)' }}>
                    {item.format === 'markdown' ? 'MD' : 'HTML'} · {item.action === 'download' ? '下载' : '预览'}
                  </span>
                  <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                    {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="mt-0.5 truncate text-[10.5px]" style={{ color: 'var(--text-muted)' }}>
                  {item.file_name}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {parsed && (
        <div style={panelStyle}>
          {!resetConfirm ? (
            <button
              type="button"
              onClick={() => setResetConfirm(true)}
              className="w-full rounded-md py-2 text-[12px] transition-colors"
              style={{ border: '1px solid var(--border)', color: 'var(--text-muted)', background: 'transparent' }}
              onMouseOver={e => {
                e.currentTarget.style.background = 'var(--bg)'
                e.currentTarget.style.color = 'var(--text-secondary)'
              }}
              onMouseOut={e => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = 'var(--text-muted)'
              }}
            >
              重新上传文件
            </button>
          ) : (
            <div className="space-y-2">
              <p className="text-center text-[11.5px]" style={{ color: 'var(--text-muted)' }}>
                当前分析数据将被清除
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setResetConfirm(false)
                    onReset()
                  }}
                  className="flex-1 rounded-md py-1.5 text-[11px] transition-colors"
                  style={{ background: '#fee2e2', color: '#dc2626' }}
                >
                  确认清除
                </button>
                <button
                  type="button"
                  onClick={() => setResetConfirm(false)}
                  className="flex-1 rounded-md py-1.5 text-[11px] transition-colors"
                  style={{ background: 'var(--bg)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}
                >
                  取消
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
