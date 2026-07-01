import { useRef, useState } from 'react'

interface Props {
  onFile: (file: File) => void
  loading: boolean
}

function UploadIcon({ size = 38 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <rect x="3" y="5" width="34" height="28" rx="8" fill="var(--accent-surface)" />
      <path
        d="M14 27h12M20 25V14m0 0-4 4m4-4 4 4"
        stroke="var(--accent)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12 12h5.5l2.2 2.5H28"
        stroke="var(--accent)"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.42"
      />
    </svg>
  )
}

function SpinnerIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" className="spin" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="var(--border-strong)" strokeWidth="2" />
      <path d="M12 3a9 9 0 0 1 9 9" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export default function UploadZone({ onFile, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(files: FileList | null) {
    if (!files) return
    const file = Array.from(files).find(f => f.name.toLowerCase().endsWith('.cpt'))
    if (file) onFile(file)
  }

  const active = dragging || loading

  return (
    <section
      className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px]"
      aria-label="CPT 文件上传"
    >
      <button
        type="button"
        className="group text-left cursor-pointer select-none transition-all duration-200"
        style={{
          minHeight: 260,
          padding: '24px',
          borderRadius: 'var(--radius-lg)',
          border: `1.5px dashed ${active ? 'var(--accent)' : 'var(--border-strong)'}`,
          background: active ? 'var(--accent-surface)' : 'var(--surface)',
          boxShadow: active ? 'var(--shadow-md)' : 'var(--shadow-sm)',
        }}
        onClick={() => !loading && inputRef.current?.click()}
        onDragOver={e => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => {
          e.preventDefault()
          setDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
        disabled={loading}
      >
        <div className="flex h-full flex-col justify-between gap-8">
          <div className="flex items-start justify-between gap-5">
            <div className="flex items-start gap-4">
              <div
                className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg"
                style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
              >
                {loading ? <SpinnerIcon /> : <UploadIcon />}
              </div>
              <div>
                <div className="text-[12px] font-medium" style={{ color: 'var(--accent)' }}>
                  Step 01
                </div>
                <h2 className="mt-1 text-[20px] font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
                  {loading ? '正在解析 CPT 结构' : '上传 FineReport CPT 文件'}
                </h2>
                <p className="mt-2 max-w-[560px] text-[13px] leading-6" style={{ color: 'var(--text-secondary)' }}>
                  {loading
                    ? '系统正在读取报表结构、数据集、控件、单元格绑定和公式信息。'
                    : '拖入 .cpt 文件，或点击此区域选择文件。解析完成后会进入摘要、AI 分析和血缘工作台。'}
                </p>
              </div>
            </div>
            <span
              className="hidden rounded-md px-2.5 py-1 text-[12px] font-medium sm:inline-flex"
              style={{
                background: loading ? 'var(--bg)' : 'var(--accent)',
                color: loading ? 'var(--text-muted)' : '#fff',
              }}
            >
              {loading ? '解析中' : '选择文件'}
            </span>
          </div>

          <div
            className="grid grid-cols-3 gap-2"
            style={{ color: 'var(--text-muted)' }}
          >
            {['FR 9/10/11', '单文件解析', '本地运行'].map(item => (
              <div
                key={item}
                className="rounded-md px-3 py-2 text-center text-[12px]"
                style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".cpt"
          className="hidden"
          onChange={e => handleFiles(e.target.files)}
        />
      </button>

      <div
        className="flex flex-col justify-between gap-4 rounded-lg p-4"
        style={{ background: 'var(--surface)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
      >
        <div>
          <div className="text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            解析范围
          </div>
          <div className="mt-3 space-y-2">
            {['数据集与 SQL', '参数控件', '单元格绑定', '公式与填报'].map(item => (
              <div key={item} className="flex items-center gap-2 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: 'var(--accent)' }} />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md px-3 py-2 text-[11.5px] leading-5" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
          API Key 仅从本地环境变量读取，不会随文件上传或导出。
        </div>
      </div>
    </section>
  )
}
