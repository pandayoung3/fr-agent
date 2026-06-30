"""
HTML 交接文档生成器
将解析结果 + LLM 分析渲染为自包含的高质量 HTML 文件。
- 内嵌 CSS，无外部样式表依赖
- Mermaid.js 通过 CDN 渲染数据血缘流向图
- 支持 @media print，可直接另存为 PDF
"""
from datetime import datetime
import html as _html
import os
from agent.lineage_builder import build_lineage


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """HTML 转义"""
    return _html.escape(str(text)) if text else ""


def _code(text: str) -> str:
    return f"<code>{_e(text)}</code>" if text else "—"


def _badge(text: str, color: str = "primary") -> str:
    colors = {
        "primary": "#1565c0",
        "accent": "#e65100",
        "success": "#2e7d32",
        "gray": "#607d8b",
        "warn": "#f57f17",
        "danger": "#c62828",
    }
    bg = colors.get(color, colors["primary"])
    return (
        f'<span style="display:inline-block;padding:1px 8px;border-radius:12px;'
        f'font-size:.72rem;font-weight:600;background:{bg};color:#fff;">'
        f"{_e(text)}</span>"
    )


def _table(headers: list[str], rows: list[list[str]], compact: bool = False) -> str:
    fs = ' style="font-size:.75rem;"' if compact else ""
    th = "".join(f"<th>{_e(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        tds = "".join(f"<td>{cell}</td>" for cell in row)
        body += f"<tr>{tds}</tr>"
    return f'<div class="table-wrap"{fs}><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def _callout(text: str, kind: str = "info") -> str:
    icons = {"warn": "⚠️", "info": "ℹ️", "success": "✅", "danger": "❌"}
    icon = icons.get(kind, "ℹ️")
    return (
        f'<div class="callout {kind}">'
        f'<span class="callout-icon">{icon}</span>'
        f"<span>{_e(text)}</span></div>"
    )


def _section(num: str, icon: str, title: str, body: str, collapsed: bool = False) -> str:
    sid = f"sec-{num}"
    disp = "none" if collapsed else "block"
    return f"""
<div class="section" id="{sid}">
  <div class="section-header" onclick="toggle('{sid}')">
    <span class="num">{num}</span>
    <h2>{icon} {_e(title)}</h2>
    <span class="toggle" id="{sid}-arrow">{"▸" if collapsed else "▾"}</span>
  </div>
  <div class="section-body" id="{sid}-body" style="display:{disp};">
    {body}
  </div>
</div>"""


def _sub(title: str, body: str, icon: str = "") -> str:
    prefix = f"{icon} " if icon else ""
    return f'<div class="subsection"><h3>{prefix}{_e(title)}</h3>{body}</div>'


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 14px; scroll-behavior: smooth; }
body {
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
  background: #f5f7fa; color: #1a1a2e; line-height: 1.7;
}
:root {
  --primary: #1565c0; --primary-l: #e3f0ff;
  --accent: #e65100;  --accent-l: #fff3e0;
  --success: #2e7d32; --success-l: #e8f5e9;
  --gray: #607d8b;    --gray-l: #eceff1;
  --warn: #f57f17;    --warn-l: #fffde7;
  --danger: #c62828;  --code-bg: #f5f5f5;
  --border: #dde3ec;  --shadow: 0 2px 8px rgba(0,0,0,.08); --radius: 8px;
}
/* Header */
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: var(--primary); color: #fff;
  padding: 12px 28px; display: flex; align-items: center;
  justify-content: space-between; box-shadow: 0 2px 12px rgba(21,101,192,.3);
}
.site-header h1 {
  font-size: 1rem; font-weight: 600; letter-spacing: .02em;
  max-width: 55%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.header-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.header-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip {
  font-size: .72rem; padding: 2px 10px; border-radius: 20px;
  border: 1px solid rgba(255,255,255,.4); background: rgba(255,255,255,.15);
  white-space: nowrap;
}
.print-btn {
  font-size: .75rem; padding: 4px 14px; border-radius: 20px; cursor: pointer;
  border: 1px solid rgba(255,255,255,.7); background: rgba(255,255,255,.2);
  color: #fff; transition: background .15s; white-space: nowrap;
}
.print-btn:hover { background: rgba(255,255,255,.35); }
/* Layout */
.page-body {
  display: flex; max-width: 1280px; margin: 0 auto;
  padding: 24px 16px; gap: 24px; align-items: flex-start;
}
/* Sidebar TOC */
.toc {
  width: 190px; flex-shrink: 0; position: sticky; top: 64px;
  background: #fff; border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px; box-shadow: var(--shadow);
}
.toc h3 {
  font-size: .75rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--gray); margin-bottom: 8px; padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.toc ol { list-style: none; }
.toc ol li a {
  display: block; font-size: .78rem; color: #555; text-decoration: none;
  padding: 3px 6px; border-left: 2px solid transparent; transition: all .15s;
}
.toc ol li a:hover, .toc ol li a.active {
  color: var(--primary); border-left-color: var(--primary); background: var(--primary-l);
}
/* Main Content */
.content { flex: 1; min-width: 0; }
/* Section Cards */
.section {
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius);
  margin-bottom: 18px; overflow: hidden; box-shadow: var(--shadow);
}
.section-header {
  background: linear-gradient(135deg, var(--primary) 0%, #1976d2 100%);
  color: #fff; padding: 13px 20px; display: flex; align-items: center;
  gap: 10px; cursor: pointer; user-select: none;
}
.section-header .num {
  width: 26px; height: 26px; border-radius: 50%; background: rgba(255,255,255,.2);
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 700; flex-shrink: 0;
}
.section-header h2 { font-size: .95rem; font-weight: 600; flex: 1; }
.section-header .toggle { font-size: 1rem; opacity: .7; }
.section-body { padding: 20px; }
/* Subsections */
.subsection { margin-bottom: 22px; }
.subsection:last-child { margin-bottom: 0; }
.subsection h3 {
  font-size: .88rem; font-weight: 700; color: var(--primary);
  padding: 5px 0; border-bottom: 2px solid var(--primary-l); margin-bottom: 10px;
}
.subsection h4 {
  font-size: .83rem; font-weight: 600; color: #333;
  margin: 14px 0 6px; padding-left: 8px; border-left: 3px solid var(--primary);
}
/* Tables */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: .79rem; }
thead tr { background: var(--primary); color: #fff; }
thead th { padding: 8px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
tbody tr:nth-child(even) { background: #f9fafc; }
tbody tr:hover { background: var(--primary-l); }
tbody td { padding: 6px 12px; border-bottom: 1px solid #eee; vertical-align: top; }
code {
  font-family: "SFMono-Regular", Consolas, "Courier New", monospace;
  font-size: .77rem; background: var(--code-bg); padding: 1px 5px;
  border-radius: 3px; color: var(--danger);
}
pre {
  background: #1e2a3a; color: #e2e8f0; padding: 14px 18px; border-radius: 6px;
  overflow-x: auto; font-size: .78rem; line-height: 1.6; margin: 8px 0;
}
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
/* Info Grid */
.info-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 10px; margin-bottom: 14px;
}
.info-card {
  background: var(--gray-l); border-radius: 6px; padding: 10px 13px;
  border-left: 3px solid var(--primary);
}
.info-card .label {
  font-size: .7rem; color: var(--gray); text-transform: uppercase;
  letter-spacing: .04em; margin-bottom: 3px;
}
.info-card .value { font-size: .92rem; font-weight: 700; color: var(--primary); }
/* Callouts */
.callout {
  border-radius: 6px; padding: 10px 14px; margin: 10px 0; font-size: .81rem;
  line-height: 1.6; display: flex; gap: 8px; align-items: flex-start;
}
.callout-icon { font-size: 1rem; flex-shrink: 0; margin-top: 2px; }
.callout.warn  { background: var(--warn-l);  border-left: 4px solid var(--warn);  color: #5d4037; }
.callout.info  { background: var(--primary-l); border-left: 4px solid var(--primary); color: #1a237e; }
.callout.danger{ background: #ffebee; border-left: 4px solid var(--danger); color: #b71c1c; }
.callout.success{ background: var(--success-l); border-left: 4px solid var(--success); color: #1b5e20; }
/* Chain Cards */
.chain-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(280px,1fr)); gap:14px; }
.chain-card {
  background: #fff; border:1px solid var(--border); border-radius: 8px;
  padding:14px; box-shadow: var(--shadow);
}
.chain-card .chain-title {
  font-size:.85rem; font-weight:700; color:var(--primary); margin-bottom:10px;
  padding-bottom:6px; border-bottom:2px solid var(--primary-l);
}
.chain-card .chain-row { display:flex; gap:6px; margin:5px 0; font-size:.78rem; }
.chain-card .chain-label {
  font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:.04em;
  color:var(--gray); white-space:nowrap; min-width:56px; margin-top:2px;
}
/* Steps Timeline */
.steps { list-style:none; position:relative; padding-left:24px; }
.steps::before {
  content:""; position:absolute; left:9px; top:4px; bottom:4px;
  width:2px; background:var(--border);
}
.steps li {
  position:relative; padding:8px 0 8px 18px; font-size:.82rem;
}
.steps li::before {
  content:attr(data-n); position:absolute; left:-15px; top:9px;
  width:22px; height:22px; border-radius:50%; background:var(--primary); color:#fff;
  font-size:.7rem; font-weight:700; display:flex; align-items:center; justify-content:center;
}
/* Mermaid */
.mermaid-wrap {
  background: #fafbfc; border:1px solid var(--border); border-radius:6px;
  padding:14px; overflow-x:auto; text-align:center;
}
/* Indicator badge */
.dim-badge {
  display:inline-block; padding:1px 7px; border-radius:10px; font-size:.7rem;
  font-weight:600; background:#e3f0ff; color:#1565c0;
}
.measure-badge {
  display:inline-block; padding:1px 7px; border-radius:10px; font-size:.7rem;
  font-weight:600; background:#fff3e0; color:#e65100;
}
/* Color preview */
.color-swatch {
  display:inline-block; width:14px; height:14px; border-radius:3px;
  border:1px solid #ccc; vertical-align:middle; margin-right:4px;
}
/* Confirm table */
.confirm-table td { padding: 12px 16px; }
/* Footer */
.doc-footer {
  text-align:center; padding:24px; font-size:.75rem; color:var(--gray);
  border-top:1px solid var(--border); margin-top:8px;
}
/* Print */
@media print {
  .site-header { position:static; }
  .toc, .print-btn { display:none; }
  .page-body { display:block; padding:0; }
  .content { width:100%; }
  .section { box-shadow:none; break-inside:avoid; }
  .section-body { display:block !important; }
  body { background:#fff; font-size:11pt; }
  a { color:inherit; text-decoration:none; }
  pre { white-space:pre-wrap; }
}
"""

# ── JS ────────────────────────────────────────────────────────────────────────

_JS = """
function toggle(id) {
  var body = document.getElementById(id + '-body');
  var arrow = document.getElementById(id + '-arrow');
  if (body.style.display === 'none') {
    body.style.display = 'block'; arrow.textContent = '▾';
  } else {
    body.style.display = 'none'; arrow.textContent = '▸';
  }
}
// TOC scroll-spy
(function() {
  var links = document.querySelectorAll('.toc a');
  var sections = Array.from(links).map(function(a) {
    return document.querySelector(a.getAttribute('href'));
  });
  window.addEventListener('scroll', function() {
    var scrollY = window.scrollY + 80;
    var current = 0;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i] && sections[i].offsetTop <= scrollY) current = i;
    }
    links.forEach(function(l) { l.classList.remove('active'); });
    if (links[current]) links[current].classList.add('active');
  });
})();
"""


# ── 各章节生成函数 ────────────────────────────────────────────────────────────

def _sec1_overview(analysis: dict) -> str:
    purpose = _e(analysis.get("purpose", "（AI 未能推断）"))
    layout = _e(analysis.get("layout_description", ""))
    body = f"<p style='font-size:.88rem;line-height:1.8;'>{purpose}</p>"
    if layout:
        layout_inner = f"<p style='font-size:.84rem;'>{layout}</p>"
        body += f'<div style="margin-top:12px;">{_sub("布局结构", layout_inner)}</div>'
    return _section("1", "📋", "报表概述", body)


def _sec2_info(parsed: dict, author: str) -> str:
    fname = parsed.get("file_name", "未知")
    rtype = "填报报表" if parsed.get("report_type") == "writeback" else "查询报表"
    cards = [
        ("文件名", fname),
        ("FR 版本", parsed.get("fr_version", "?")),
        ("报表类型", rtype),
        ("Sheet 数量", str(parsed.get("sheet_count", "?"))),
        ("文件大小", f'{parsed.get("file_size_kb", "?")} KB'),
        ("数据集数量", str(len(parsed.get("datasets", [])))),
        ("参数控件", str(len(parsed.get("widgets", [])))),
    ]
    if author:
        cards.append(("交接人", author))
    grid = "".join(
        f'<div class="info-card"><div class="label">{_e(k)}</div><div class="value">{_e(v)}</div></div>'
        for k, v in cards
    )
    body = f'<div class="info-grid">{grid}</div>'
    return _section("2", "📊", "基本信息", body)


def _sec3_data(parsed: dict, analysis: dict) -> str:
    parts = []

    # 血缘图
    lineage = build_lineage(parsed)
    mermaid_code = lineage.get("mermaid", "")
    if mermaid_code:
        # 提取 mermaid 代码块内容（去掉 ```mermaid ... ```）
        mc = mermaid_code.strip()
        if mc.startswith("```mermaid"):
            mc = mc[len("```mermaid"):].strip()
        if mc.endswith("```"):
            mc = mc[:-3].strip()
        legend = (
            '<p style="font-size:.75rem;color:#607d8b;margin-bottom:8px;">'
            '🔵 参数控件 &nbsp;|&nbsp; 🟢 SQL 数据集 &nbsp;|&nbsp; 🟠 展示字段 &nbsp;|&nbsp; ⚪ 控件选项数据集</p>'
        )
        mermaid_div = f'<div class="mermaid-wrap"><div class="mermaid">{_e(mc)}</div></div>'
        parts.append(_sub("数据血缘流向图", legend + mermaid_div, "🗺️"))

        unmatched = lineage.get("unmatched_widget_names", [])
        if unmatched:
            names_str = "、".join(unmatched[:10]) + ("..." if len(unmatched) > 10 else "")
            parts.append(
                _callout(
                    f"未找到 SQL 参数连接的控件（{len(unmatched)} 个）：{names_str}。"
                    "这些控件可能通过单元格过滤条件或前端 JS 实现筛选，需人工核实。",
                    "warn",
                )
            )
    else:
        parts.append(_sub("数据血缘流向图", _callout("未找到控件→SQL参数的直接连接（所有数据集为嵌入式或参数名不匹配）", "info"), "🗺️"))

    # 数据库连接
    db_conns = parsed.get("db_connections", [])
    if db_conns:
        rows = [[_code(c), "（请补充数据库类型和用途）"] for c in db_conns]
        parts.append(_sub("数据库连接", _table(["连接名", "说明"], rows), "🔌"))

    # 数据集清单
    datasets = parsed.get("datasets", [])
    if datasets:
        ds_html = ""
        for ds in datasets:
            type_zh = "实时DB查询" if ds.get("type") == "DBTableData" else "内嵌静态数据"
            cols = ds.get("columns", [])
            conn = ds.get("db_connection") or "—"
            ds_rows = [
                ["类型", type_zh],
                ["数据库连接", _code(conn) if conn != "—" else "—"],
                ["字段数量", str(len(cols))],
            ]
            sql_html = ""
            if ds.get("sql"):
                params_str = ""
                if ds.get("sql_params"):
                    params_str = (
                        '<p style="font-size:.78rem;margin-top:6px;">'
                        + "动态参数：" + "、".join(f"<code>{_e(p)}</code>" for p in ds["sql_params"])
                        + "（由参数控件传入）</p>"
                    )
                sql_html = f'<pre><code class="language-sql">{_e(ds["sql"])}</code></pre>{params_str}'

            cols_html = ""
            if cols:
                col_rows = [[_code(c), "—"] for c in cols[:30]]
                if len(cols) > 30:
                    col_rows.append([f"... 共 {len(cols)} 列", ""])
                cols_html = _table(["字段名", "业务含义"], col_rows, compact=True)

            ds_html += (
                f'<h4>{_e(ds.get("name", "未命名"))}</h4>'
                + _table(["属性", "值"], ds_rows, compact=True)
                + (cols_html or "")
                + sql_html
            )
        parts.append(_sub("数据集清单", ds_html, "📦"))

    # 数据集关系（AI）
    if analysis.get("dataset_relationships"):
        txt = _e(analysis["dataset_relationships"])
        parts.append(_sub("数据集关系与数据流向（AI 推断）", f"<p style='font-size:.83rem;'>{txt}</p>", "🔗"))

    # JOIN Key
    shared_keys = parsed.get("dataset_shared_keys", [])
    if shared_keys:
        rows = [[_code(sk.get("field", "")), _e("、".join(sk.get("shared_by", [])))] for sk in shared_keys]
        parts.append(_sub("跨数据集共享字段（推断 JOIN Key）", _table(["字段名", "共享于数据集"], rows), "🔑"))

    # 字段语义（AI）
    if analysis.get("field_semantics"):
        txt = _e(analysis["field_semantics"])
        parts.append(_sub("关键字段业务含义（AI 推断）", f"<p style='font-size:.83rem;'>{txt}</p>", "🏷️"))

    # 指标字典
    ind_list = analysis.get("indicator_dict", [])
    if ind_list:
        rows = []
        for ind in ind_list:
            type_val = ind.get("type", "")
            badge = (
                f'<span class="measure-badge">{_e(type_val)}</span>'
                if type_val == "度量"
                else f'<span class="dim-badge">{_e(type_val)}</span>'
            )
            formula = _code(ind.get("formula")) if ind.get("formula") else "—"
            rows.append([
                _e(ind.get("indicator_name", "")),
                _code(ind.get("source_field", "")),
                _e(ind.get("dataset") or "—"),
                badge,
                _e(ind.get("unit") or "—"),
                formula,
                _e(ind.get("description", "")),
            ])
        parts.append(_sub(
            "指标字典（AI 推断）",
            _table(["指标名", "来源字段", "数据集", "类型", "单位", "公式", "业务含义"], rows),
            "📋",
        ))

    return _section("3", "🗄️", "数据来源与字段关系", "\n".join(parts))


def _sec4_chains(parsed: dict, analysis: dict) -> str:
    chains = analysis.get("interaction_chains", [])
    widgets = parsed.get("widgets", [])

    parts = []
    if chains:
        cards = ""
        for i, ch in enumerate(chains, 1):
            w = ch.get("widget_name", f"链路{i}")
            wt = ch.get("widget_type", "")
            rows_html = ""
            for label, key in [
                ("控件作用", "param_role"),
                ("SQL 影响", "sql_impact"),
                ("数据展示", "data_displayed"),
                ("设计原因", "why_this_design"),
            ]:
                val = ch.get(key, "")
                if val:
                    rows_html += (
                        f'<div class="chain-row">'
                        f'<span class="chain-label">{label}</span>'
                        f'<span>{_e(val)}</span></div>'
                    )
            cards += (
                f'<div class="chain-card">'
                f'<div class="chain-title">{i}. {_e(w)}'
                + (f' <code>{_e(wt)}</code>' if wt else "")
                + f"</div>{rows_html}</div>"
            )
        parts.append(_sub("交互链路详情（AI 推断）", f'<div class="chain-grid">{cards}</div>', "⛓️"))
    else:
        parts.append(_callout("AI 未能推断交互链路，请人工补充。", "warn"))

    if widgets:
        rows = []
        for w in widgets:
            opts = " / ".join(f"{o['key']}={o['value']}" for o in w.get("custom_options", []))
            rows.append([
                _code(w.get("name", "")),
                _e(w.get("widget_type", "")),
                _e(w.get("bound_dataset") or "直接输入"),
                _e(w.get("key_column") or "—"),
                _e(w.get("display_column") or "—"),
                _e(opts or "—"),
            ])
        parts.append(_sub(
            "参数控件汇总",
            _table(["控件名", "类型", "数据来源", "key 字段", "显示字段", "固定选项"], rows),
            "🎛️",
        ))

    return _section("4", "🎛️", "控件 → 参数 → 数据 → 展示：交互链路", "\n".join(parts))


def _sec5_cells(parsed: dict, analysis: dict) -> str:
    parts = []

    # 标签-数据配对
    label_pairs = parsed.get("label_data_pairs", [])
    if label_pairs:
        rows = [
            [
                _e(p.get("label_text", "")),
                _code(p.get("label_pos", "")),
                _code(p.get("data_pos", "")),
                _e(p.get("dataset", "—")),
                _code(p.get("column", "—")),
                _e(p.get("widget_type") or "—"),
            ]
            for p in label_pairs
        ]
        parts.append(_sub(
            "表单字段对照（标签 → 数据绑定）",
            _table(["标签文字", "标签位置", "数据位置", "数据集", "字段", "控件类型"], rows, compact=True),
            "🏷️",
        ))

    # 数据绑定单元格
    bound_cells = [c for c in parsed.get("cell_bindings", []) if c.get("dataset")]
    if bound_cells:
        rows = []
        for c in bound_cells:
            arrow = {"row": "↓", "col": "→"}.get(c.get("expand_dir", ""), "")
            mode = _e((c.get("data_mode") or "—") + (" " + arrow if arrow else ""))
            rows.append([
                _code(c.get("pos", "")),
                _e(c.get("dataset", "")),
                _code(c.get("column", "")),
                _e(c.get("format_type") or "常规"),
                mode,
                _e(c.get("parent_left") or "—"),
                _e(c.get("cell_filter") or "—"),
                _e(c.get("widget_type") or "—"),
            ])
        parts.append(_sub(
            "数据绑定单元格明细",
            _table(["位置", "绑定数据集", "绑定字段", "格式类型", "数据模式", "左父格", "过滤条件", "控件"], rows, compact=True),
            "📌",
        ))

    # 公式单元格
    formula_cells = parsed.get("formula_cells", [])
    if formula_cells:
        llm_exp = {
            e.get("pos"): e.get("meaning", "")
            for e in analysis.get("formula_explanations", [])
            if e.get("pos")
        }
        rows = []
        for f in formula_cells:
            pos = f.get("pos", "")
            formula = f.get("formula", "")
            short = formula[:70] + "..." if len(formula) > 70 else formula
            js_targets = "、".join(f.get("js_events") or []) or "—"
            rows.append([
                _code(pos),
                _code(short),
                _e(llm_exp.get(pos, "—")),
                _e(js_targets),
            ])
        parts.append(_sub(
            "公式单元格",
            _table(["位置", "公式", "含义（AI 推断）", "JS 联动目标"], rows, compact=True),
            "🔢",
        ))

    if not parts:
        parts.append(_callout("无数据绑定或公式单元格信息。", "info"))

    return _section("5", "📌", "单元格展示与字段对照", "\n".join(parts))


def _sec6_steps(analysis: dict) -> str:
    steps = analysis.get("development_steps", [])
    if not steps:
        return _section("6", "🛠️", "从零复现开发步骤（AI 推断）",
                        _callout("AI 未能推断，请人工补充。", "warn"))
    items = ""
    for i, step in enumerate(steps, 1):
        items += f'<li data-n="{i}">{_e(step)}</li>'
    note = _callout("以下步骤由 AI 根据报表结构推断，供新开发人员参考，请核实后使用。", "info")
    return _section("6", "🛠️", "从零复现开发步骤（AI 推断）", note + f'<ol class="steps">{items}</ol>')


def _sec7_highlight(parsed: dict, analysis: dict) -> str:
    hl_rules = parsed.get("highlight_rules_summary", [])
    display_text = analysis.get("display_rules", "")
    if not hl_rules and (not display_text or display_text == "无条件高亮规则"):
        return _section("7", "🎨", "条件高亮规则", _callout("无条件高亮规则。", "info"), collapsed=True)

    parts = []
    if display_text and display_text != "无条件高亮规则":
        parts.append(f'<p style="font-size:.83rem;margin-bottom:10px;">{_e(display_text)}</p>')

    if hl_rules:
        rows = []
        for rule in hl_rules:
            affected = "、".join(rule.get("affected_columns", [])) or "—"
            color = rule.get("color", "")
            color_cell = ""
            if color:
                color_cell = (
                    f'<span class="color-swatch" style="background:{_e(color)};"></span>'
                    + _code(color)
                )
            else:
                color_cell = "—"
            rows.append([
                _e(rule.get("name", "")),
                _code(rule.get("condition", "")),
                _e(rule.get("action", "")),
                color_cell,
                _e(affected),
            ])
        parts.append(_table(["规则名称", "触发条件", "效果", "颜色", "影响字段"], rows))

    return _section("7", "🎨", "条件高亮规则（业务规则）", "\n".join(parts))


def _sec8_writeback(parsed: dict) -> str:
    wb = parsed.get("writeback_config")
    if not wb:
        return ""
    keys_str = "、".join(f"<code>{_e(k)}</code>" for k in wb.get("key_columns", [])) or "—"
    rows = [
        ["数据库连接", _code(wb.get("db_connection") or "—")],
        ["目标表", _code(wb.get("table") or "—")],
        ["主键字段", keys_str],
    ]
    body = _table(["属性", "值"], rows)
    if wb.get("column_mappings"):
        mapping_rows = []
        for m in wb["column_mappings"]:
            is_key = "✓" if m.get("is_key") else ""
            param = _e(m.get("param") or "（来自单元格）")
            mapping_rows.append([_code(m.get("db_column", "")), param, is_key])
        body += _sub("字段映射关系", _table(["数据库字段", "来源参数", "是否主键"], mapping_rows))
    return _section("8", "📝", "填报提交配置", body)


def _sec9_risks(analysis: dict) -> str:
    risks = analysis.get("notes_or_risks", [])
    if not risks:
        return ""
    items = "".join(_callout(r, "warn") for r in risks)
    note = _callout("以下风险点由 AI 识别，请人工复核。", "info")
    return _section("9", "⚠️", "注意事项与风险点", note + items)


def _sec10_confirm() -> str:
    rows = [
        ["确认人", "", ""],
        ["确认时间", "", ""],
        ["补充说明", "", ""],
    ]
    tbl = _table(["项目", "交接方", "接收方"], rows)
    return _section("10", "✅", "交接确认", tbl, collapsed=True)


# ── TOC ───────────────────────────────────────────────────────────────────────

def _build_toc(has_writeback: bool, has_risks: bool) -> str:
    items = [
        ("sec-1", "报表概述"),
        ("sec-2", "基本信息"),
        ("sec-3", "数据来源"),
        ("sec-4", "交互链路"),
        ("sec-5", "单元格对照"),
        ("sec-6", "开发步骤"),
        ("sec-7", "高亮规则"),
    ]
    if has_writeback:
        items.append(("sec-8", "填报配置"))
    if has_risks:
        items.append(("sec-9", "风险点"))
    items.append(("sec-10", "交接确认"))

    lis = "".join(f'<li><a href="#{sid}">{_e(title)}</a></li>' for sid, title in items)
    return f'<nav class="toc"><h3>目录</h3><ol>{lis}</ol></nav>'


# ── 主入口 ────────────────────────────────────────────────────────────────────

def generate_handover_html(parsed: dict, analysis: dict, author: str = "") -> str:
    """生成自包含的高质量 HTML 交接文档"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    model = os.environ.get("LLM_MODEL", "deepseek-ai/DeepSeek-V4-Flash")
    fname = parsed.get("file_name", "未知文件")
    fr_ver = parsed.get("fr_version", "?")
    rtype = "填报报表" if parsed.get("report_type") == "writeback" else "查询报表"
    file_kb = parsed.get("file_size_kb", "?")

    has_writeback = bool(parsed.get("writeback_config"))
    has_risks = bool(analysis.get("notes_or_risks"))

    # 章节
    sections = "\n".join(filter(None, [
        _sec1_overview(analysis),
        _sec2_info(parsed, author),
        _sec3_data(parsed, analysis),
        _sec4_chains(parsed, analysis),
        _sec5_cells(parsed, analysis),
        _sec6_steps(analysis),
        _sec7_highlight(parsed, analysis),
        _sec8_writeback(parsed) if has_writeback else "",
        _sec9_risks(analysis),
        _sec10_confirm(),
    ]))

    toc = _build_toc(has_writeback, has_risks)

    chips = "".join(
        f'<span class="chip">{_e(t)}</span>'
        for t in [f"FR {fr_ver}", rtype, f"{file_kb} KB", now]
    )
    ai_warn = (
        '<div style="background:#fff3e0;border-left:4px solid #f57f17;padding:8px 14px;'
        'font-size:.78rem;color:#5d4037;margin-bottom:16px;border-radius:4px;">'
        "⚠️ 本文档由 AI 自动推断生成，请交接双方核实确认后使用。</div>"
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>报表交接文档 | {_e(fname)}</title>
<style>{_CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'default', flowchart:{{curve:'basis'}}}});</script>
</head>
<body>
<header class="site-header">
  <h1>📊 报表交接文档：{_e(fname)}</h1>
  <div class="header-right">
    <div class="header-chips">{chips}</div>
    <button class="print-btn" onclick="window.print()">🖨️ 打印 / PDF</button>
  </div>
</header>
<div class="page-body">
  {toc}
  <main class="content">
    {ai_warn}
    {sections}
    <div class="doc-footer">
      FR 交接 Agent 自动生成 v4 &nbsp;|&nbsp; 模型：{_e(model)} &nbsp;|&nbsp; {_e(now)}
    </div>
  </main>
</div>
<script>{_JS}</script>
</body>
</html>"""
