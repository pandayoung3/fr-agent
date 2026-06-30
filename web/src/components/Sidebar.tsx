import { useState } from 'react'
import type { ParsedReport } from '../types'
import { enrichParsed } from '../api'

interface Props {
  parsed: ParsedReport | null
  dbEnriched: boolean
  onEnriched: (enriched: ParsedReport) => void
  onReset: () => void
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  fontSize: '12px',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: '6px 10px',
  outline: 'none',
  color: 'var(--text-primary)',
  background: 'var(--bg)',
  transition: 'border-color 0.15s',
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-medium mb-1" style={{ color: 'var(--text-muted)' }}>
      {children}
    </div>
  )
}

export default function Sidebar({ parsed, dbEnriched, onEnriched, onReset }: Props) {
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

  const panelStyle: React.CSSProperties = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '14px',
    boxShadow: 'var(--shadow-sm)',
  }

  return (
    <aside className="flex-shrink-0 flex flex-col gap-3" style={{ width: 240 }}>
      {/* DB 增强 */}
      <div style={panelStyle}>
        <div className="flex items-center gap-2 mb-1">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="10" rx="2" stroke="var(--accent)" strokeWidth="1.4"/>
            <path d="M2 7h12M6 7v6" stroke="var(--accent)" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
          <span className="text-[12.5px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            数据库增强
          </span>
          <span
            className="text-[10px] px-1.5 py-0.5 rounded-full ml-auto"
            style={{ background: 'var(--bg)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}
          >
            可选
          </span>
        </div>
        <p className="text-[11px] leading-relaxed mb-3" style={{ color: 'var(--text-muted)' }}>
          接入数据库获取字段信息，提升分析质量
        </p>

        {!parsed && (
          <p className="text-[11px] text-center py-2" style={{ color: 'var(--text-muted)' }}>
            请先上传 CPT 文件
          </p>
        )}

        {parsed && dbDatasets.length === 0 && (
          <div
            className="text-[11px] rounded-md px-3 py-2"
            style={{ background: 'var(--success-surface)', color: 'var(--success)', border: '1px solid var(--success-border)' }}
          >
            此报表使用内嵌数据集，无需连接
          </div>
        )}

        {parsed && dbDatasets.length > 0 && (
          <>
            {dbEnriched ? (
              <div className="space-y-1.5">
                <div
                  className="text-[11px] rounded-md px-3 py-2"
                  style={{ background: 'var(--success-surface)', color: 'var(--success)', border: '1px solid var(--success-border)' }}
                >
                  字段信息已成功接入
                </div>
                {Object.entries(connStatus).map(([conn, st]) => (
                  <div key={conn} className="text-[11px] flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
                    <span style={{ color: st === 'ok' ? 'var(--success)' : st === 'error' ? '#dc2626' : 'var(--text-muted)' }}>
                      {st === 'ok' ? '✓' : st === 'error' ? '✗' : '-'}
                    </span>
                    {conn}
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2.5">
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
                  onClick={handleConnect}
                  disabled={loading || Object.keys(passwords).filter(k => passwords[k]).length === 0}
                  className="w-full text-[12px] py-2 rounded-md font-medium transition-colors"
                  style={{
                    background: 'var(--accent)',
                    color: '#fff',
                  }}
                  onMouseOver={e => { if (!loading) e.currentTarget.style.background = 'var(--accent-dim)' }}
                  onMouseOut={e => e.currentTarget.style.background = 'var(--accent)'}
                >
                  {loading ? '连接中...' : '连接并获取字段信息'}
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* 重新上传 */}
      {parsed && (
        <div style={panelStyle}>
          {!resetConfirm ? (
            <button
              onClick={() => setResetConfirm(true)}
              className="w-full text-[12px] py-1.5 rounded-md transition-colors"
              style={{
                border: '1px solid var(--border)',
                color: 'var(--text-muted)',
                background: 'transparent',
              }}
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
              <p className="text-[11px] text-center" style={{ color: 'var(--text-muted)' }}>
                当前分析数据将被清除
              </p>
              <div className="flex gap-1.5">
                <button
                  onClick={() => { setResetConfirm(false); onReset() }}
                  className="flex-1 text-[11px] py-1.5 rounded-md transition-colors"
                  style={{ background: '#fee2e2', color: '#dc2626' }}
                >
                  确认清除
                </button>
                <button
                  onClick={() => setResetConfirm(false)}
                  className="flex-1 text-[11px] py-1.5 rounded-md transition-colors"
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
