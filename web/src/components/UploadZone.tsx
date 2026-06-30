import { useRef, useState } from 'react'

interface Props {
  onFile: (file: File) => void
  loading: boolean
}

function UploadIcon({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="10" fill="var(--accent-surface)"/>
      <path
        d="M20 26V18m0 0-3 3m3-3 3 3"
        stroke="var(--accent)"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M13 27h14M13 14h3.5a1 1 0 0 1 .7.3l2.8 2.7h6a1 1 0 0 1 1 1v9"
        stroke="var(--accent)"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.4"
      />
    </svg>
  )
}

function SpinnerIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="spin">
      <circle cx="12" cy="12" r="9" stroke="var(--border-strong)" strokeWidth="2"/>
      <path d="M12 3a9 9 0 0 1 9 9" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  )
}

export default function UploadZone({ onFile, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(files: FileList | null) {
    if (!files) return
    const file = Array.from(files).find(f => f.name.endsWith('.cpt'))
    if (file) onFile(file)
  }

  return (
    <div
      className="flex flex-col items-center justify-center text-center cursor-pointer select-none transition-all duration-200"
      style={{
        padding: '52px 32px',
        borderRadius: 'var(--radius-xl)',
        border: `2px dashed ${dragging ? 'var(--accent)' : 'var(--border-strong)'}`,
        background: dragging ? 'var(--accent-surface)' : 'var(--surface)',
      }}
      onClick={() => !loading && inputRef.current?.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
      onMouseOver={e => {
        if (!dragging && !loading)
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--accent)'
      }}
      onMouseOut={e => {
        if (!dragging)
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border-strong)'
      }}
    >
      <div className="mb-4">
        {loading ? <SpinnerIcon /> : <UploadIcon />}
      </div>

      <h3
        className="text-[15px] font-semibold mb-1.5"
        style={{ color: loading ? 'var(--text-muted)' : 'var(--text-primary)' }}
      >
        {loading ? '解析中，请稍候...' : '上传 FineReport 报表文件'}
      </h3>

      <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>
        {loading
          ? '正在读取 CPT 结构'
          : '拖拽 .cpt 文件到此，或点击选择文件 · 支持 FR 9.0 / 10.0 / 11.0'
        }
      </p>

      {!loading && (
        <div
          className="mt-5 px-4 py-1.5 rounded-md text-[12px] font-medium"
          style={{ background: 'var(--accent-surface)', color: 'var(--accent)', border: '1px solid var(--accent-border)' }}
        >
          选择文件
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".cpt"
        className="hidden"
        onChange={e => handleFiles(e.target.files)}
      />
    </div>
  )
}
