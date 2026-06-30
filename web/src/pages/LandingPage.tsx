import React from 'react'

interface Props {
  onStart: () => void
}

// ── SVG 插图：产品界面 mockup ────────────────────────────────────────────────
function ProductMockup() {
  return (
    <div className="relative w-full" style={{ maxWidth: 680 }}>
      {/* 外框阴影 */}
      <div
        className="rounded-2xl overflow-hidden"
        style={{
          background: '#fff',
          boxShadow: '0 8px 48px rgba(37,99,235,0.12), 0 2px 12px rgba(0,0,0,0.06)',
          border: '1px solid #e5e8f0',
        }}
      >
        {/* 顶部导航条 */}
        <div style={{ background: '#0f172a', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 8 }}>
          <svg width="16" height="16" viewBox="0 0 22 22" fill="none">
            <rect x="2" y="10" width="4" height="10" rx="1.5" fill="#2563eb"/>
            <rect x="9" y="5" width="4" height="15" rx="1.5" fill="#2563eb" opacity="0.7"/>
            <rect x="16" y="1" width="4" height="19" rx="1.5" fill="#2563eb" opacity="0.45"/>
          </svg>
          <span style={{ color: '#fff', fontSize: 12, fontWeight: 600 }}>FR 报表交接 Agent</span>
          <div style={{ marginLeft: 'auto', background: '#1e293b', borderRadius: 6, padding: '2px 10px' }}>
            <span style={{ color: '#64748b', fontSize: 11 }}>习题5.cpt</span>
          </div>
        </div>

        {/* 工作流进度条 */}
        <div style={{ background: '#f8f9fc', borderBottom: '1px solid #e5e8f0', padding: '8px 16px', display: 'flex', alignItems: 'center', gap: 8 }}>
          {[
            { label: '上传 CPT', done: true },
            { label: '数据库增强', skip: true },
            { label: 'AI 分析', done: true },
            { label: '查看导出', active: true },
          ].map((step, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 20, height: 20, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700,
                background: step.done ? '#059669' : step.active ? '#2563eb' : '#e2e8f0',
                color: step.done || step.active ? '#fff' : '#94a3b8',
                boxShadow: step.active ? '0 0 0 3px rgba(37,99,235,0.2)' : 'none',
              }}>
                {step.done ? '✓' : step.skip ? '-' : i + 1}
              </div>
              <span style={{ fontSize: 11, fontWeight: step.active ? 600 : 400, color: step.done ? '#059669' : step.active ? '#2563eb' : '#94a3b8' }}>{step.label}</span>
              {i < 3 && <div style={{ width: 24, height: 1, background: step.done ? '#059669' : '#d1d5db', margin: '0 2px' }}/>}
            </div>
          ))}
        </div>

        <div style={{ display: 'flex' }}>
          {/* 左侧边栏 */}
          <div style={{ width: 160, borderRight: '1px solid #e5e8f0', padding: 12, flexShrink: 0 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: '#334155', marginBottom: 8 }}>数据库增强</div>
            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 6, padding: '6px 8px', fontSize: 10.5, color: '#059669' }}>
              内嵌数据集，无需连接
            </div>
            <div style={{ marginTop: 12, border: '1px solid #e5e8f0', borderRadius: 6, padding: '6px 8px', fontSize: 10.5, color: '#94a3b8', textAlign: 'center' }}>
              重新上传文件
            </div>
          </div>

          {/* 主内容区 */}
          <div style={{ flex: 1, padding: 14 }}>
            {/* 文件横幅 */}
            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: 6, padding: '5px 10px', fontSize: 11, color: '#059669', marginBottom: 10 }}>
              ✓ 已解析 <strong>习题5.cpt</strong>
            </div>

            {/* stat 卡片行 */}
            <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
              {[['FR 版本','11.5.0'], ['Sheet','1'], ['数据集','2'], ['参数控件','2'], ['大小','15.8 KB']].map(([label, val]) => (
                <div key={label} style={{ background: '#fff', border: '1px solid #e5e8f0', borderRadius: 6, padding: '5px 8px', minWidth: 56 }}>
                  <div style={{ fontSize: 9, color: '#94a3b8', textTransform: 'uppercase', marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: label === '数据集' ? '#2563eb' : '#0f172a' }}>{val}</div>
                </div>
              ))}
            </div>

            {/* Tab 栏 */}
            <div style={{ borderBottom: '1px solid #e5e8f0', display: 'flex', gap: 0, marginBottom: 10 }}>
              {['概览','交互链路','指标字典','开发步骤','数据血缘','问答','导出'].map((tab, i) => (
                <div key={tab} style={{
                  padding: '5px 10px', fontSize: 11, fontWeight: i === 0 ? 600 : 400,
                  color: i === 0 ? '#2563eb' : '#94a3b8',
                  borderBottom: i === 0 ? '2px solid #2563eb' : '2px solid transparent',
                  cursor: 'pointer',
                }}>{tab}</div>
              ))}
            </div>

            {/* 概览内容 */}
            <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 6, padding: '8px 10px', marginBottom: 8 }}>
              <div style={{ fontSize: 9, color: '#2563eb', fontWeight: 700, textTransform: 'uppercase', marginBottom: 4 }}>报表业务用途 · AI</div>
              <div style={{ fontSize: 11.5, color: '#1e3a5f', fontWeight: 500, lineHeight: 1.5 }}>该报表用于展示学生成绩信息，支持按班级和学号筛选，以列表形式显示班级、课程、姓名及对应成绩。</div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
              {[
                ['布局结构', '报表为列表型布局，A1单元格显示班级，B3单元格显示课程，第3/4行为数据扩展行。'],
                ['数据集关系', '两个数据集ds1和ds2结构完全相同，ds1为参数数据集，ds2为主数据集。'],
              ].map(([title, text]) => (
                <div key={title} style={{ background: '#f8f9fc', border: '1px solid #e5e8f0', borderRadius: 6, padding: '7px 9px' }}>
                  <div style={{ fontSize: 9.5, fontWeight: 600, color: '#64748b', marginBottom: 4 }}>{title} <span style={{ background: '#eff6ff', color: '#2563eb', fontSize: 8, padding: '1px 4px', borderRadius: 3 }}>AI</span></div>
                  <div style={{ fontSize: 10.5, color: '#475569', lineHeight: 1.4 }}>{text}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 装饰光晕 */}
      <div style={{
        position: 'absolute', inset: -20, borderRadius: 32, zIndex: -1,
        background: 'radial-gradient(ellipse at 50% 60%, rgba(37,99,235,0.08) 0%, transparent 70%)',
        pointerEvents: 'none',
      }}/>
    </div>
  )
}

// ── SVG 功能图标 ────────────────────────────────────────────────────────────
function FeatureIcon({ type }: { type: string }) {
  const base = 'var(--accent-surface)'
  const stroke = 'var(--accent)'
  const icons: Record<string, React.ReactElement> = {
    parse: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="3" width="18" height="18" rx="3" stroke={stroke} strokeWidth="1.5"/>
        <path d="M7 8h10M7 12h6M7 16h8" stroke={stroke} strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    lineage: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="5" cy="12" r="2.5" stroke={stroke} strokeWidth="1.5"/>
        <circle cx="12" cy="6" r="2.5" stroke={stroke} strokeWidth="1.5"/>
        <circle cx="12" cy="18" r="2.5" stroke={stroke} strokeWidth="1.5"/>
        <circle cx="19" cy="12" r="2.5" stroke={stroke} strokeWidth="1.5"/>
        <path d="M7.5 12h2M12 8.5v7M14.5 12h2" stroke={stroke} strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    ai: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L9.5 9.5 2 12l7.5 2.5L12 22l2.5-7.5L22 12l-7.5-2.5L12 2z" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    export: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 3v12m0 0-4-4m4 4 4-4" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke={stroke} strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    ),
    db: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <ellipse cx="12" cy="6" rx="8" ry="3" stroke={stroke} strokeWidth="1.5"/>
        <path d="M4 6v6c0 1.657 3.582 3 8 3s8-1.343 8-3V6" stroke={stroke} strokeWidth="1.5"/>
        <path d="M4 12v6c0 1.657 3.582 3 8 3s8-1.343 8-3v-6" stroke={stroke} strokeWidth="1.5"/>
      </svg>
    ),
    chat: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z" stroke={stroke} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  }
  return (
    <div style={{
      width: 44, height: 44, borderRadius: 10, background: base,
      display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
    }}>
      {icons[type]}
    </div>
  )
}

// ── 主组件 ───────────────────────────────────────────────────────────────────
export default function LandingPage({ onStart }: Props) {
  return (
    <div style={{ background: '#f7f8fc', minHeight: '100vh', fontFamily: 'Geist, PingFang SC, Noto Sans SC, sans-serif' }}>

      {/* ── 导航 ── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(255,255,255,0.88)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid #e5e8f0',
        padding: '0 40px', height: 56,
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
          <rect x="2" y="10" width="4" height="10" rx="1.5" fill="#2563eb"/>
          <rect x="9" y="5" width="4" height="15" rx="1.5" fill="#2563eb" opacity="0.7"/>
          <rect x="16" y="1" width="4" height="19" rx="1.5" fill="#2563eb" opacity="0.45"/>
        </svg>
        <span style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>FR 报表交接 Agent</span>
        <div style={{ width: 1, height: 16, background: '#e2e8f0', margin: '0 4px' }}/>
        <span style={{ fontSize: 12, color: '#94a3b8' }}>帆软报表智能交接工具</span>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
          <a href="#features" style={{ fontSize: 13, color: '#475569', textDecoration: 'none' }}>功能特性</a>
          <a href="#how" style={{ fontSize: 13, color: '#475569', textDecoration: 'none' }}>使用流程</a>
          <button
            onClick={onStart}
            style={{
              background: '#2563eb', color: '#fff', border: 'none',
              padding: '7px 18px', borderRadius: 8, fontSize: 13, fontWeight: 600,
              cursor: 'pointer', transition: 'background 0.15s',
            }}
            onMouseOver={e => (e.currentTarget.style.background = '#1d4ed8')}
            onMouseOut={e => (e.currentTarget.style.background = '#2563eb')}
          >
            立即使用
          </button>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section style={{ maxWidth: 1280, margin: '0 auto', padding: '80px 40px 64px', display: 'flex', alignItems: 'center', gap: 64 }}>
        {/* 左侧文案 */}
        <div style={{ flex: '0 0 420px' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: '#eff6ff', border: '1px solid #bfdbfe',
            borderRadius: 20, padding: '4px 12px', marginBottom: 24,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563eb', display: 'inline-block' }}/>
            <span style={{ fontSize: 12, color: '#2563eb', fontWeight: 500 }}>FR 报表开发团队专属</span>
          </div>

          <h1 style={{
            fontSize: 44, fontWeight: 800, lineHeight: 1.15,
            color: '#0f172a', margin: '0 0 20px', letterSpacing: '-0.03em',
          }}>
            报表交接<br/>
            <span style={{ color: '#2563eb' }}>从几天到 60 秒</span>
          </h1>

          <p style={{ fontSize: 16, color: '#475569', lineHeight: 1.7, margin: '0 0 32px', maxWidth: 380 }}>
            上传 .cpt 文件，AI 自动解析业务逻辑、还原数据血缘、推断指标含义，生成可交付的完整交接文档。
          </p>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button
              onClick={onStart}
              style={{
                background: '#2563eb', color: '#fff', border: 'none',
                padding: '12px 28px', borderRadius: 10, fontSize: 14, fontWeight: 600,
                cursor: 'pointer', transition: 'all 0.15s',
                boxShadow: '0 2px 12px rgba(37,99,235,0.3)',
              }}
              onMouseOver={e => { e.currentTarget.style.background = '#1d4ed8'; e.currentTarget.style.transform = 'translateY(-1px)' }}
              onMouseOut={e => { e.currentTarget.style.background = '#2563eb'; e.currentTarget.style.transform = 'none' }}
            >
              立即体验 →
            </button>
            <a
              href="#how"
              style={{
                display: 'inline-block',
                padding: '12px 24px', borderRadius: 10, fontSize: 14, fontWeight: 500,
                color: '#475569', background: '#fff',
                border: '1px solid #e5e8f0', textDecoration: 'none',
                transition: 'border-color 0.15s',
              }}
              onMouseOver={e => (e.currentTarget.style.borderColor = '#2563eb')}
              onMouseOut={e => (e.currentTarget.style.borderColor = '#e5e8f0')}
            >
              查看使用流程
            </a>
          </div>

          {/* 数字指标 */}
          <div style={{ display: 'flex', gap: 32, marginTop: 40, paddingTop: 32, borderTop: '1px solid #e5e8f0' }}>
            {[['60s', '生成一份交接文档'], ['10+', '解析内容维度'], ['0', '手动操作步骤']].map(([num, label]) => (
              <div key={num}>
                <div style={{ fontSize: 26, fontWeight: 800, color: '#2563eb', lineHeight: 1 }}>{num}</div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧产品图 */}
        <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
          <ProductMockup />
        </div>
      </section>

      {/* ── 痛点对比 ── */}
      <section style={{ background: '#fff', borderTop: '1px solid #e5e8f0', borderBottom: '1px solid #e5e8f0', padding: '56px 40px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <h2 style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '0 0 12px', letterSpacing: '-0.02em' }}>
              告别低效的手工交接
            </h2>
            <p style={{ fontSize: 15, color: '#64748b' }}>交接质量不再取决于交接人的耐心和经验</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 0, alignItems: 'stretch' }}>
            {/* 之前 */}
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px 0 0 12px', padding: 28 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 16 }}>之前</div>
              {[
                '逐行阅读 CPT 的 XML 结构，人工推断逻辑',
                '字段含义靠经验猜测，容易理解偏差',
                '不知道控件如何驱动 SQL 参数',
                '交接文档靠手写，耗时数小时甚至数天',
                '接手方仍需反复向原开发者追问细节',
              ].map(item => (
                <div key={item} style={{ display: 'flex', gap: 10, marginBottom: 12, fontSize: 13.5, color: '#7f1d1d', lineHeight: 1.5 }}>
                  <span style={{ color: '#ef4444', flexShrink: 0, marginTop: 1 }}>✕</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>

            {/* 箭头 */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 20px', background: '#f7f8fc' }}>
              <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </div>
            </div>

            {/* 之后 */}
            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '0 12px 12px 0', padding: 28 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#059669', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 16 }}>之后</div>
              {[
                '上传文件，60 秒内自动解析全部业务结构',
                'AI 推断字段语义，结合真实 DB 字段注释',
                '交互链路图自动还原控件到 SQL 的完整路径',
                '结构化 Markdown / HTML 文档一键导出',
                '接手方打开文档即可完整理解，独立上手',
              ].map(item => (
                <div key={item} style={{ display: 'flex', gap: 10, marginBottom: 12, fontSize: 13.5, color: '#14532d', lineHeight: 1.5 }}>
                  <span style={{ color: '#059669', flexShrink: 0, marginTop: 1 }}>✓</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── 功能特性 ── */}
      <section id="features" style={{ padding: '72px 40px', maxWidth: 1280, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '0 0 12px', letterSpacing: '-0.02em' }}>
            一次上传，全面解析
          </h2>
          <p style={{ fontSize: 15, color: '#64748b' }}>覆盖 FineReport 报表交接所需的全部信息维度</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          {[
            {
              icon: 'parse', title: '深度 CPT 解析',
              desc: '解析 .cpt 文件的 ZIP+XML 结构，提取数据集 SQL、参数控件绑定、单元格公式、条件高亮、填报配置、父子格关系，完整还原报表骨架。',
            },
            {
              icon: 'lineage', title: '数据血缘流向图',
              desc: '确定性算法自动生成「控件 → 参数 → SQL 数据集 → 展示字段」完整链路，可视化所有数据流向，支持 Mermaid 和 Graphviz 格式。',
            },
            {
              icon: 'ai', title: 'AI 语义推断',
              desc: '调用大语言模型分析报表业务用途、交互链路逻辑、公式业务含义、指标字典，输出结构化 JSON，驱动文档生成。',
            },
            {
              icon: 'db', title: '真实字段接入',
              desc: '自动读取 FineReport 连接配置，通过 MySQL information_schema 补全字段类型和注释，让 AI 理解字段真实含义，提升分析精准度。',
            },
            {
              icon: 'export', title: '专业文档导出',
              desc: '生成标准化 Markdown（适配 Confluence / Notion / 飞书）和自包含 HTML（含目录、折叠章节、血缘图、打印为 PDF）两种格式。',
            },
            {
              icon: 'chat', title: '报表问答',
              desc: '基于解析结果和 AI 分析，支持流式自然语言追问。新人可直接提问「这个字段是什么」「控件如何影响数据」，实时获得准确答复。',
            },
          ].map(f => (
            <div key={f.title} style={{
              background: '#fff', border: '1px solid #e5e8f0', borderRadius: 12,
              padding: '22px 22px', boxShadow: '0 1px 3px rgba(15,23,42,0.05)',
              transition: 'box-shadow 0.2s, transform 0.2s',
            }}
              onMouseOver={e => {
                (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 24px rgba(37,99,235,0.1)'
                ;(e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)'
              }}
              onMouseOut={e => {
                (e.currentTarget as HTMLDivElement).style.boxShadow = '0 1px 3px rgba(15,23,42,0.05)'
                ;(e.currentTarget as HTMLDivElement).style.transform = 'none'
              }}
            >
              <FeatureIcon type={f.icon} />
              <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: '14px 0 8px' }}>{f.title}</h3>
              <p style={{ fontSize: 13.5, color: '#64748b', lineHeight: 1.65, margin: 0 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── 使用流程 ── */}
      <section id="how" style={{ background: '#fff', borderTop: '1px solid #e5e8f0', padding: '72px 40px' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <h2 style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '0 0 12px', letterSpacing: '-0.02em' }}>
              三步完成交接文档
            </h2>
            <p style={{ fontSize: 15, color: '#64748b' }}>从上传到导出，最快 60 秒</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 0, position: 'relative' }}>
            {/* 连接线 */}
            <div style={{
              position: 'absolute', top: 28, left: '16.5%', right: '16.5%', height: 2,
              background: 'linear-gradient(to right, #2563eb, #2563eb)',
              zIndex: 0,
            }}/>

            {[
              {
                num: 1, title: '上传 CPT 文件',
                desc: '拖拽或点击选择 .cpt 文件，系统自动解析报表结构，提取所有数据集、控件、公式、绑定关系。',
                detail: '支持 FR 9.0 / 10.0 / 11.0',
              },
              {
                num: 2, title: 'AI 深度分析',
                desc: '可选接入数据库获取真实字段信息，然后启动 AI 分析，推断业务语义、交互链路、指标含义和开发步骤。',
                detail: '分析过程约 15-60 秒',
              },
              {
                num: 3, title: '查看并导出',
                desc: '在 7 个内容 Tab 中浏览全部分析结果，一键导出 Markdown 或 HTML 格式的完整交接文档。',
                detail: '文档包含 10 个标准章节',
              },
            ].map(step => (
              <div key={step.num} style={{ textAlign: 'center', padding: '0 28px', position: 'relative', zIndex: 1 }}>
                <div style={{
                  width: 56, height: 56, borderRadius: '50%',
                  background: step.num === 3 ? '#2563eb' : '#2563eb',
                  color: '#fff', fontSize: 20, fontWeight: 800,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 20px',
                  boxShadow: '0 0 0 6px #eff6ff, 0 2px 12px rgba(37,99,235,0.3)',
                }}>
                  {step.num}
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', margin: '0 0 10px' }}>{step.title}</h3>
                <p style={{ fontSize: 13.5, color: '#64748b', lineHeight: 1.6, margin: '0 0 10px' }}>{step.desc}</p>
                <span style={{
                  display: 'inline-block', fontSize: 11.5, color: '#2563eb',
                  background: '#eff6ff', border: '1px solid #bfdbfe',
                  padding: '3px 10px', borderRadius: 20,
                }}>{step.detail}</span>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div style={{ textAlign: 'center', marginTop: 56 }}>
            <button
              onClick={onStart}
              style={{
                background: '#2563eb', color: '#fff', border: 'none',
                padding: '14px 36px', borderRadius: 10, fontSize: 15, fontWeight: 600,
                cursor: 'pointer', boxShadow: '0 2px 16px rgba(37,99,235,0.3)',
                transition: 'all 0.15s',
              }}
              onMouseOver={e => { e.currentTarget.style.background = '#1d4ed8'; e.currentTarget.style.transform = 'translateY(-1px)' }}
              onMouseOut={e => { e.currentTarget.style.background = '#2563eb'; e.currentTarget.style.transform = 'none' }}
            >
              立即体验 FR 报表交接 Agent →
            </button>
          </div>
        </div>
      </section>

      {/* ── 输出内容展示 ── */}
      <section style={{ padding: '72px 40px', maxWidth: 1280, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, color: '#0f172a', margin: '0 0 12px', letterSpacing: '-0.02em' }}>
            交接文档包含什么
          </h2>
          <p style={{ fontSize: 15, color: '#64748b' }}>10 个标准章节，覆盖接手方需要了解的全部内容</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, maxWidth: 800, margin: '0 auto' }}>
          {[
            ['报表概述', '一句话业务用途 + 布局结构描述'],
            ['数据来源与字段关系', '血缘图 + 数据集清单 + SQL 语句 + 指标字典'],
            ['控件交互链路', '控件 → 参数 → SQL → 展示的完整数据流'],
            ['从零复现开发步骤', 'AI 推断的开发顺序，新人可直接参考'],
            ['单元格展示与字段对照', '字段映射表 + 公式解释 + 绑定明细'],
            ['条件高亮与业务规则', '触发条件、颜色含义、设计意图说明'],
            ['注意事项与风险点', 'AI 识别的潜在问题，降低踩坑概率'],
            ['填报配置（如有）', '写入表、主键、字段映射关系'],
          ].map(([title, desc]) => (
            <div key={title} style={{
              display: 'flex', gap: 12, padding: '14px 16px',
              background: '#fff', border: '1px solid #e5e8f0', borderRadius: 10,
              alignItems: 'flex-start',
            }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563eb', flexShrink: 0, marginTop: 6 }}/>
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 600, color: '#0f172a', marginBottom: 3 }}>{title}</div>
                <div style={{ fontSize: 12.5, color: '#64748b', lineHeight: 1.5 }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{
        background: '#0f172a', borderTop: '1px solid #1e293b',
        padding: '40px 40px 32px',
      }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 24 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <svg width="18" height="18" viewBox="0 0 22 22" fill="none">
                <rect x="2" y="10" width="4" height="10" rx="1.5" fill="#2563eb"/>
                <rect x="9" y="5" width="4" height="15" rx="1.5" fill="#2563eb" opacity="0.7"/>
                <rect x="16" y="1" width="4" height="19" rx="1.5" fill="#2563eb" opacity="0.45"/>
              </svg>
              <span style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>FR 报表交接 Agent</span>
            </div>
            <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6, maxWidth: 300, margin: 0 }}>
              帆软报表开发团队的 AI 交接助手，让报表知识不再随人员流动而流失。
            </p>
          </div>
          <div style={{ display: 'flex', gap: 48 }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>技术栈</div>
              {['React + TypeScript', 'FastAPI + Python 3.9', 'DeepSeek-V4-Flash', 'Tailwind CSS v4'].map(t => (
                <div key={t} style={{ fontSize: 13, color: '#64748b', marginBottom: 6 }}>{t}</div>
              ))}
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>支持</div>
              {['FR 9.0 / 10.0 / 11.x', 'MySQL 数据库', 'Markdown 导出', 'HTML 导出'].map(t => (
                <div key={t} style={{ fontSize: 13, color: '#64748b', marginBottom: 6 }}>{t}</div>
              ))}
            </div>
          </div>
        </div>
        <div style={{ maxWidth: 1280, margin: '24px auto 0', paddingTop: 20, borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 12, color: '#475569' }}>FR 报表交接 Agent - 内部工具</span>
          <button
            onClick={onStart}
            style={{
              background: '#2563eb', color: '#fff', border: 'none',
              padding: '8px 20px', borderRadius: 8, fontSize: 13, fontWeight: 600,
              cursor: 'pointer',
            }}
            onMouseOver={e => (e.currentTarget.style.background = '#1d4ed8')}
            onMouseOut={e => (e.currentTarget.style.background = '#2563eb')}
          >
            进入工具
          </button>
        </div>
      </footer>
    </div>
  )
}
