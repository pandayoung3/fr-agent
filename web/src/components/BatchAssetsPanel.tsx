import type { BatchParseItem, BatchParseResult, ParsedReport } from '../types'

interface Props {
  result: BatchParseResult
  onOpenReport: (parsed: ParsedReport) => void
  onClear: () => void
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md px-3 py-2" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
      <div className="text-[17px] font-semibold leading-none" style={{ color: 'var(--text-primary)' }}>
        {value}
      </div>
      <div className="mt-1 text-[11px]" style={{ color: 'var(--text-muted)' }}>
        {label}
      </div>
    </div>
  )
}

function StatusBadge({ item }: { item: BatchParseItem }) {
  const ok = item.status === 'success'
  return (
    <span
      className="rounded-md px-2 py-1 text-[11px] font-semibold"
      style={{
        color: ok ? '#047857' : '#be123c',
        background: ok ? '#ecfdf5' : '#fff1f2',
        border: `1px solid ${ok ? '#a7f3d0' : '#fecdd3'}`,
      }}
    >
      {ok ? '解析成功' : '解析失败'}
    </span>
  )
}

function AssetGraph({ items }: { items: BatchParseItem[] }) {
  const successItems = items.filter(item => item.status === 'success' && item.summary)
  if (successItems.length === 0) {
    return (
      <div className="rounded-md px-3 py-2 text-[12px]" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>
        暂无可生成图谱的成功解析文件。
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {successItems.map(item => (
        <div key={`graph-${item.file_name}`} className="rounded-lg p-3" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-md px-2 py-1 text-[11px] font-semibold" style={{ background: '#eff6ff', border: '1px solid #bfdbfe', color: '#1d4ed8' }}>
              报表
            </span>
            <span className="max-w-[360px] truncate text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }} title={item.file_name}>
              {item.file_name}
            </span>
          </div>
          <div className="mt-3 grid gap-2 md:grid-cols-4">
            <GraphNode label="数据集" value={item.summary?.dataset_count ?? 0} tone="#047857" />
            <GraphNode label="DB 连接" value={item.summary?.db_connections.join('、') || '无'} tone="#b45309" />
            <GraphNode label="控件" value={item.summary?.widget_count ?? 0} tone="#6d28d9" />
            <GraphNode label="公式" value={item.summary?.formula_count ?? 0} tone="#be123c" />
          </div>
        </div>
      ))}
    </div>
  )
}

function GraphNode({ label, value, tone }: { label: string; value: string | number; tone: string }) {
  return (
    <div className="rounded-md px-3 py-2" style={{ background: '#fff', border: '1px solid var(--border)' }}>
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 rounded-full" style={{ background: tone }} />
        <span className="text-[11px] font-semibold" style={{ color: 'var(--text-muted)' }}>
          {label}
        </span>
      </div>
      <div className="mt-1 truncate text-[12px] font-semibold" style={{ color: 'var(--text-primary)' }} title={String(value)}>
        {value}
      </div>
    </div>
  )
}

export default function BatchAssetsPanel({ result, onOpenReport, onClear }: Props) {
  const dbReports = result.items.filter(item => (item.summary?.db_dataset_count ?? 0) > 0).length
  const writebackReports = result.items.filter(item => item.summary?.report_type === 'writeback').length
  const totalDatasets = result.items.reduce((sum, item) => sum + (item.summary?.dataset_count ?? 0), 0)
  const totalWidgets = result.items.reduce((sum, item) => sum + (item.summary?.widget_count ?? 0), 0)

  return (
    <section className="space-y-4" aria-label="批量 CPT 解析结果">
      <div
        className="rounded-lg p-4"
        style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f8fbff 100%)', border: '1px solid var(--border)' }}
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.08em]" style={{ color: 'var(--accent)' }}>
              P2 批量资产索引
            </div>
            <h2 className="mt-1 text-[20px] font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
              已批量解析 {result.total} 个 CPT 文件
            </h2>
            <p className="mt-2 max-w-3xl text-[13px] leading-6" style={{ color: 'var(--text-secondary)' }}>
              这里先建立客户报表资产的轻量索引。选择任一成功文件，可进入单报表工作台继续做 AI 分析、血缘、变更建议和导出。
            </p>
          </div>
          <button
            type="button"
            onClick={onClear}
            className="rounded-md px-3 py-2 text-[12px] font-semibold"
            style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}
          >
            清空批量结果
          </button>
        </div>

        <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-6">
          <Metric label="成功" value={result.success} />
          <Metric label="失败" value={result.failed} />
          <Metric label="DB 报表" value={dbReports} />
          <Metric label="填报报表" value={writebackReports} />
          <Metric label="数据集" value={totalDatasets} />
          <Metric label="控件" value={totalWidgets} />
        </div>
      </div>

      <section className="rounded-lg p-4" style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}>
        <div className="mb-3">
          <div className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
            报表资产图谱雏形
          </div>
          <div className="mt-1 text-[12px]" style={{ color: 'var(--text-muted)' }}>
            P2 先用轻量关系视图呈现报表、数据集、DB 连接、控件和公式，后续可演进为 Obsidian 式跨报表图谱。
          </div>
        </div>
        <AssetGraph items={result.items} />
      </section>

      <div className="grid gap-3 xl:grid-cols-2">
        {result.items.map(item => (
          <article
            key={item.file_name}
            className="rounded-lg p-4"
            style={{ background: '#fff', border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)' }}
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="max-w-full truncate text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }} title={item.file_name}>
                  {item.file_name}
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <StatusBadge item={item} />
                  {item.summary?.report_type && (
                    <span className="rounded-md px-2 py-1 text-[11px]" style={{ background: 'var(--bg)', color: 'var(--text-muted)' }}>
                      {item.summary.report_type === 'writeback' ? '填报' : '查询'}
                    </span>
                  )}
                </div>
              </div>
              {item.parsed && (
                <button
                  type="button"
                  onClick={() => onOpenReport(item.parsed!)}
                  className="rounded-md px-3 py-2 text-[12px] font-semibold"
                  style={{ background: 'var(--accent)', color: '#fff' }}
                >
                  打开工作台
                </button>
              )}
            </div>

            {item.status === 'failed' && (
              <div className="mt-3 rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: '#fff1f2', border: '1px solid #fecdd3', color: '#be123c' }}>
                {item.error ?? '解析失败'}
              </div>
            )}

            {item.summary && (
              <>
                <div className="mt-3 grid grid-cols-3 gap-2">
                  <Metric label="数据集" value={item.summary.dataset_count} />
                  <Metric label="DB 数据集" value={item.summary.db_dataset_count} />
                  <Metric label="控件" value={item.summary.widget_count} />
                  <Metric label="单元格" value={item.summary.cell_binding_count} />
                  <Metric label="公式" value={item.summary.formula_count} />
                  <Metric label="连接" value={item.summary.db_connections.length} />
                </div>
                <div className="mt-3 rounded-md px-3 py-2 text-[12px] leading-5" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                  数据库连接：{item.summary.db_connections.join('、') || '未识别 DB 连接'}
                </div>
              </>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}
