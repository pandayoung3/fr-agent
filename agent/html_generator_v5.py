"""
FR 交接 Agent · Handover HTML Generator v5
Vercel Design System · Geist Font · Compact Layout · Smooth Animations

改进要点：
- Vercel 设计令牌（Geist 字体、shadow-as-border、紧凑间距）
- Sticky table headers
- 过渡动画折叠/展开
- 紧凑布局，减少浪费空间
- 打印模式按钮
- 统一视觉层次
"""
import re
from datetime import datetime
from .lineage_builder import build_lineage


# ── 辅助函数 ──────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    """HTML escape"""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _code(text: str) -> str:
    return f"<code>{_e(text)}</code>"


def _section(num: str, icon: str, title: str, body: str, collapsed: bool = False) -> str:
    vis = "" if collapsed else ""
    arrow = "▾" if not collapsed else "▸"
    return (
        f'<section class="sec" id="sec-{num}">'
        f'<div class="sec-h" onclick="toggleS(\'sec-{num}\')">'
        f'<span class="sec-num">{num}</span>'
        f'<span class="sec-icon">{icon}</span>'
        f'<h2>{_e(title)}</h2>'
        f'<span class="sec-toggle" id="sec-{num}-arr">{arrow}</span>'
        f"</div>"
        f'<div class="sec-b" id="sec-{num}-b" style="display:{vis}">'
        f"{body}</div></section>"
    )


def _sub(title: str, body: str, icon: str = "") -> str:
    icon_html = f'<span class="sub-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="sub">'
        f'<h3>{icon_html}{_e(title)}</h3>'
        f"{body}</div>"
    )


def _table(headers: list, rows: list, compact: bool = False) -> str:
    if not rows:
        return ""
    cls = ' class="tbl-compact"' if compact else ""
    ths = "".join(f"<th>{_e(h)}</th>" for h in headers)
    trs = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f'<div class="tbl-wrap"><table{cls}><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>'


def _callout(text: str, kind: str = "info") -> str:
    icons = {"info": "ℹ️", "warn": "⚠️", "danger": "🚨", "success": "✅"}
    return (
        f'<div class="callout {kind}">'
        f'<span class="callout-icon">{icons.get(kind, "ℹ️")}</span>'
        f'<span>{_e(text)}</span></div>'
    )


def _info_card(label: str, value: str) -> str:
    return (
        f'<div class="info-c">'
        f'<div class="info-l">{_e(label)}</div>'
        f'<div class="info-v">{_e(value)}</div></div>'
    )


def _chip(text: str) -> str:
    return f'<span class="chip">{_e(text)}</span>'


# ── CSS: Vercel Design System ────────────────────────────────────────────────

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 14px; scroll-behavior: smooth; }
body {
  font-family: 'Geist', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  background: #f5f6f8; color: #171717; line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'liga';
}
:root {
  --text: #171717;
  --text-2: #4d4d4d;
  --text-3: #666666;
  --bg: #ffffff;
  --bg-card: #ffffff;
  --bg-subtle: #fafafa;
  --border: rgba(0,0,0,0.08) 0px 0px 0px 1px;
  --border-l: rgb(235,235,235) 0px 0px 0px 1px;
  --shadow: rgba(0,0,0,0.08) 0px 0px 0px 1px, rgba(0,0,0,0.04) 0px 2px 2px, #fafafa 0px 0px 0px 1px;
  --shadow-e: rgba(0,0,0,0.1) 0px 0px 0px 1px, rgba(0,0,0,0.06) 0px 4px 12px;
  --acc-blue: #0072f5;
  --acc-green: #2e7d32;
  --acc-orange: #e65100;
  --acc-red: #c62828;
  --radius: 8px;
  --radius-s: 6px;
  --font-mono: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* ── Header ── */
.site-h {
  position: sticky; top: 0; z-index: 100;
  background: #171717; color: #fff;
  padding: 10px 24px;
  display: flex; align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 1px 0 rgba(255,255,255,.08);
}
.site-h h1 {
  font-size: .92rem; font-weight: 500;
  letter-spacing: -0.24px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.site-h .h-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.chip {
  font-size: .7rem; font-weight: 400;
  padding: 2px 10px; border-radius: 9999px;
  border: 1px solid rgba(255,255,255,.15);
  background: rgba(255,255,255,.08);
  color: rgba(255,255,255,.7);
  white-space: nowrap;
}
.print-btn {
  font-size: .72rem; font-weight: 500;
  padding: 4px 12px; border-radius: var(--radius-s);
  border: 1px solid rgba(255,255,255,.25);
  background: transparent; color: #fff;
  cursor: pointer; transition: all .15s;
  white-space: nowrap;
}
.print-btn:hover {
  background: rgba(255,255,255,.1);
  border-color: rgba(255,255,255,.4);
}

/* ── Layout ── */
.page-body {
  display: flex;
  max-width: 1100px; margin: 0 auto;
  padding: 20px 16px; gap: 20px;
  align-items: flex-start;
}

/* ── Sidebar TOC ── */
.toc {
  width: 160px; flex-shrink: 0;
  position: sticky; top: 58px;
  background: var(--bg);
  box-shadow: var(--border);
  border-radius: var(--radius);
  padding: 12px;
}
.toc h3 {
  font-size: .7rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .06em;
  color: var(--text-3); margin-bottom: 6px;
  padding-bottom: 6px;
  box-shadow: var(--border-l);
}
.toc ol {
  list-style: none;
}
.toc a {
  display: block;
  font-size: .75rem; font-weight: 400;
  color: var(--text-2);
  text-decoration: none;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all .15s;
}
.toc a:hover,
.toc a.active {
  color: var(--acc-blue);
  background: #ebf5ff;
}

/* ── Main Content ── */
.content { flex: 1; min-width: 0; }

/* ── AI warning banner ── */
.ai-warn {
  background: #fef7e8;
  box-shadow: var(--border);
  border-radius: var(--radius);
  padding: 8px 14px;
  font-size: .78rem;
  color: #7c6a3e;
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 16px;
}

/* ── Sections ── */
.sec {
  background: var(--bg);
  box-shadow: var(--border-l);
  border-radius: var(--radius);
  margin-bottom: 12px;
  overflow: hidden;
  transition: box-shadow .2s;
}
.sec:hover {
  box-shadow: var(--shadow);
}
.sec-h {
  background: #fafafa;
  padding: 10px 16px;
  display: flex; align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  transition: background .15s;
}
.sec-h:hover {
  background: #f0f0f0;
}
.sec-num {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--text);
  color: #fff;
  font-size: .7rem; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sec-icon { font-size: .88rem; flex-shrink: 0; }
.sec-h h2 {
  font-size: .85rem; font-weight: 600;
  letter-spacing: -0.24px;
  flex: 1;
}
.sec-toggle {
  font-size: .72rem;
  color: var(--text-3);
  transition: transform .2s;
}
.sec-b {
  padding: 16px 20px;
  /* display: block; */
}

/* ── Subsections ── */
.sub {
  margin-bottom: 18px;
}
.sub:last-child { margin-bottom: 0; }
.sub h3 {
  font-size: .82rem; font-weight: 600;
  color: var(--text);
  padding: 4px 0 6px;
  box-shadow: var(--border-l);
  margin-bottom: 10px;
  display: flex; align-items: center; gap: 6px;
}
.sub-icon { font-size: .82rem; }
.sub h4 {
  font-size: .78rem; font-weight: 600;
  color: var(--text);
  margin: 12px 0 6px;
  padding-left: 8px;
  border-left: 3px solid var(--acc-blue);
}

/* ── Info Grid ── */
.info-g {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}
.info-c {
  background: var(--bg-subtle);
  box-shadow: var(--border-l);
  border-radius: var(--radius-s);
  padding: 8px 12px;
}
.info-l {
  font-size: .65rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--text-3);
  margin-bottom: 2px;
}
.info-v {
  font-size: .85rem; font-weight: 600;
  color: var(--text);
}

/* ── Tables ── */
.tbl-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: .77rem;
}
table.tbl-compact { font-size: .74rem; }
thead { position: sticky; top: 0; }
thead tr {
  background: #171717;
  color: #fff;
}
thead th {
  padding: 7px 10px;
  text-align: left;
  font-weight: 500;
  font-size: .74rem;
  white-space: nowrap;
  letter-spacing: -0.16px;
}
table.tbl-compact thead th { padding: 5px 8px; font-size: .7rem; }
tbody tr:nth-child(even) { background: #fafbfc; }
tbody tr:hover { background: #ebf5ff; }
tbody td {
  padding: 5px 10px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
  line-height: 1.5;
}
table.tbl-compact tbody td { padding: 4px 8px; }

/* ── Code ── */
code {
  font-family: var(--font-mono);
  font-size: .75rem;
  background: #f5f5f5;
  padding: 1px 5px;
  border-radius: 3px;
  color: var(--acc-red);
}
pre {
  background: #171717;
  color: #e2e8f0;
  padding: 12px 16px;
  border-radius: var(--radius-s);
  overflow-x: auto;
  font-size: .76rem;
  line-height: 1.6;
  margin: 8px 0;
}
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }

/* ── Callouts ── */
.callout {
  border-radius: var(--radius-s);
  padding: 8px 12px;
  margin: 8px 0;
  font-size: .78rem;
  line-height: 1.5;
  display: flex; gap: 6px; align-items: flex-start;
}
.callout-icon { font-size: .85rem; flex-shrink: 0; }
.callout.info  { background: #ebf5ff; color: #0050a0; }
.callout.warn  { background: #fef7e8; color: #7c6a3e; }
.callout.danger { background: #fde8e8; color: #a02020; }
.callout.success { background: #e8f5e9; color: #1b5e20; }

/* ── Chain Cards ── */
.chain-g {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.chain-c {
  background: var(--bg);
  box-shadow: var(--border-l);
  border-radius: var(--radius);
  padding: 12px;
  transition: box-shadow .15s;
}
.chain-c:hover { box-shadow: var(--shadow); }
.chain-c .chain-t {
  font-size: .82rem; font-weight: 600;
  color: var(--acc-blue);
  margin-bottom: 8px;
  padding-bottom: 6px;
  box-shadow: var(--border-l);
}
.chain-row {
  display: flex; gap: 6px;
  margin: 4px 0;
  font-size: .76rem;
  line-height: 1.5;
}
.chain-l {
  font-size: .65rem; font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: var(--text-3);
  white-space: nowrap;
  min-width: 54px;
  margin-top: 2px;
}

/* ── Steps Timeline ── */
.steps {
  list-style: none;
  padding: 0;
  margin: 10px 0;
  position: relative;
  padding-left: 28px;
}
.steps::before {
  content: "";
  position: absolute; left: 11px; top: 4px; bottom: 4px;
  width: 2px;
  background: #e0e0e0;
}
.steps li {
  position: relative;
  padding: 6px 0 6px 16px;
  font-size: .8rem;
  color: var(--text);
}
.steps li::before {
  content: attr(data-n);
  position: absolute; left: -19px; top: 7px;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--text);
  color: #fff;
  font-size: .68rem; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
}

/* ── Mermaid ── */
.mermaid-wrap {
  background: var(--bg-subtle);
  box-shadow: var(--border-l);
  border-radius: var(--radius-s);
  padding: 12px;
  overflow-x: auto;
  text-align: center;
}

/* ── Badges ── */
.badge-dim {
  display: inline-block;
  padding: 1px 7px; border-radius: 10px;
  font-size: .68rem; font-weight: 600;
  background: #ebf5ff; color: var(--acc-blue);
}
.badge-mea {
  display: inline-block;
  padding: 1px 7px; border-radius: 10px;
  font-size: .68rem; font-weight: 600;
  background: #fff3e0; color: var(--acc-orange);
}

/* ── Color swatch ── */
.color-s {
  display: inline-block;
  width: 12px; height: 12px;
  border-radius: 3px;
  box-shadow: var(--border-l);
  vertical-align: middle;
  margin-right: 3px;
}

/* ── Confirm table ── */
.confirm-t td { padding: 10px 14px; }

/* ── Footer ── */
.doc-f {
  text-align: center;
  padding: 20px;
  font-size: .72rem;
  color: var(--text-3);
  box-shadow: var(--border-l) inset;
  margin-top: 8px;
}

/* ── Print ── */
@media print {
  .site-h { position: static; background: #fff !important; color: #171717 !important; }
  .site-h .chip { border-color: #ddd; color: #999; }
  .print-btn, .toc { display: none !important; }
  .page-body { display: block; padding: 0; }
  .content { width: 100%; }
  .sec { break-inside: avoid; box-shadow: var(--border-l) !important; }
  .sec-b { display: block !important; }
  .sec-toggle { display: none; }
  body { background: #fff; font-size: 10.5pt; }
  a { color: inherit; text-decoration: none; }
  pre { white-space: pre-wrap; }
  thead { position: static; }
}
"""


# ── JS: Smooth Toggle + Scroll Spy ──────────────────────────────────────────

_JS = """
function toggleS(id) {
  var b = document.getElementById(id + '-b');
  var a = document.getElementById(id + '-arr');
  if (!b || !a) return;
  if (b.style.display === 'none') {
    b.style.display = 'block';
    a.textContent = '\u25be';
  } else {
    b.style.display = 'none';
    a.textContent = '\u25b8';
  }
}
(function() {
  var links = document.querySelectorAll('.toc a');
  var sections = Array.from(links).map(function(a) {
    return document.querySelector(a.getAttribute('href'));
  });
  window.addEventListener('scroll', function() {
    var scrollY = window.scrollY + 60;
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
    body = f"<p style='font-size:.85rem;line-height:1.7;'>{purpose}</p>"
    if layout:
        body += _sub("布局结构", f"<p style='font-size:.82rem;'>{layout}</p>")
    return _section("1", "📋", "报表概述", body)


def _sec2_info(parsed: dict, author: str) -> str:
    fname = parsed.get("file_name", "未知")
    rtype = "填报报表" if parsed.get("report_type") == "writeback" else "查询报表"
    cards = [
        _info_card("文件名", fname),
        _info_card("FR 版本", parsed.get("fr_version", "?")),
        _info_card("报表类型", rtype),
        _info_card("Sheet 数量", str(parsed.get("sheet_count", "?"))),
        _info_card("文件大小", f'{parsed.get("file_size_kb", "?")} KB'),
        _info_card("数据集", str(len(parsed.get("datasets", [])))),
        _info_card("参数控件", str(len(parsed.get("widgets", [])))),
    ]
    if author:
        cards.append(_info_card("交接人", author))
    body = f'<div class="info-g">{"".join(cards)}</div>'
    return _section("2", "📊", "基本信息", body)


def _sec3_data(parsed: dict, analysis: dict) -> str:
    parts = []

    # 血缘图
    lineage = build_lineage(parsed)
    mermaid_code = lineage.get("mermaid", "")
    if mermaid_code:
        mc = mermaid_code.strip()
        if mc.startswith("```mermaid"):
            mc = mc[len("```mermaid"):].strip()
        if mc.endswith("```"):
            mc = mc[:-3].strip()
        legend = (
            '<p style="font-size:.72rem;color:var(--text-3);margin-bottom:6px;">'
            '🔵 参数控件 &nbsp;|&nbsp; 🟢 SQL 数据集 &nbsp;|&nbsp; 🟠 展示字段 &nbsp;|&nbsp; ⚪ 控件选项数据集</p>'
        )
        parts.append(_sub(
            "数据血缘流向图",
            legend + f'<div class="mermaid-wrap"><div class="mermaid">{_e(mc)}</div></div>',
            "🗺️",
        ))
        unmatched = lineage.get("unmatched_widget_names", [])
        if unmatched:
            names_str = "、".join(unmatched[:10]) + ("..." if len(unmatched) > 10 else "")
            parts.append(_callout(
                f"未找到 SQL 参数连接的控件（{len(unmatched)} 个）：{names_str}。"
                "这些控件可能通过单元格过滤条件或前端 JS 实现筛选，需人工核实。",
                "warn",
            ))
    else:
        parts.append(_sub(
            "数据血缘流向图",
            _callout("未找到控件→SQL参数的直接连接（所有数据集为嵌入式或参数名不匹配）"),
            "🗺️",
        ))

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
                        '<p style="font-size:.76rem;margin-top:6px;">'
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

    # 数据集关系
    if analysis.get("dataset_relationships"):
        txt = _e(analysis["dataset_relationships"])
        parts.append(_sub("数据集关系与数据流向（AI 推断）", f"<p style='font-size:.8rem;'>{txt}</p>", "🔗"))

    # JOIN Key
    shared_keys = parsed.get("dataset_shared_keys", [])
    if shared_keys:
        rows = [[_code(sk.get("field", "")), _e("、".join(sk.get("shared_by", [])))] for sk in shared_keys]
        parts.append(_sub("跨数据集共享字段（推断 JOIN Key）", _table(["字段名", "共享于数据集"], rows), "🔑"))

    # 字段语义
    if analysis.get("field_semantics"):
        txt = _e(analysis["field_semantics"])
        parts.append(_sub("关键字段业务含义（AI 推断）", f"<p style='font-size:.8rem;'>{txt}</p>", "🏷️"))

    # 指标字典
    ind_list = analysis.get("indicator_dict", [])
    if ind_list:
        rows = []
        for ind in ind_list:
            type_val = ind.get("type", "")
            badge = (
                f'<span class="badge-mea">{_e(type_val)}</span>'
                if type_val == "度量"
                else f'<span class="badge-dim">{_e(type_val)}</span>'
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
                        f'<span class="chain-l">{label}</span>'
                        f'<span>{_e(val)}</span></div>'
                    )
            cards += (
                f'<div class="chain-c">'
                f'<div class="chain-t">{i}. {_e(w)}'
                + (f' <code>{_e(wt)}</code>' if wt else "")
                + f"</div>{rows_html}</div>"
            )
        parts.append(_sub("交互链路详情（AI 推断）", f'<div class="chain-g">{cards}</div>', "⛓️"))
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
            [_e(p.get("label_text", "")), _code(p.get("label_pos", "")),
             _code(p.get("data_pos", "")), _e(p.get("dataset", "—")),
             _code(p.get("column", "—")), _e(p.get("widget_type") or "—")]
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
                _code(c.get("pos", "")), _e(c.get("dataset", "")),
                _code(c.get("column", "")), _e(c.get("format_type") or "常规"),
                mode, _e(c.get("parent_left") or "—"),
                _e(c.get("cell_filter") or "—"), _e(c.get("widget_type") or "—"),
            ])
        parts.append(_sub(
            "数据绑定单元格明细",
            _table(["位置", "绑定数据集", "绑定字段", "格式", "数据模式", "左父格", "过滤条件", "控件"], rows, compact=True),
            "📌",
        ))

    # 公式单元格
    formula_cells = parsed.get("formula_cells", [])
    if formula_cells:
        llm_exp = {e.get("pos"): e.get("meaning", "") for e in analysis.get("formula_explanations", []) if e.get("pos")}
        rows = []
        for f in formula_cells:
            pos = f.get("pos", "")
            formula = f.get("formula", "")
            short = formula[:70] + "..." if len(formula) > 70 else formula
            js_targets = "、".join(f.get("js_events") or []) or "—"
            rows.append([_code(pos), _code(short), _e(llm_exp.get(pos, "—")), _e(js_targets)])
        parts.append(_sub(
            "公式单元格",
            _table(["位置", "公式", "含义（AI 推断）", "JS 联动目标"], rows, compact=True),
            "🔢",
        ))

    if not parts:
        parts.append(_callout("无数据绑定或公式单元格信息。"))

    return _section("5", "📌", "单元格展示与字段对照", "\n".join(parts))


def _sec6_steps(analysis: dict) -> str:
    steps = analysis.get("development_steps", [])
    if not steps:
        return _section("6", "🛠️", "从零复现开发步骤（AI 推断）", _callout("AI 未能推断，请人工补充。", "warn"))
    items = "".join(f'<li data-n="{i}">{_e(step)}</li>' for i, step in enumerate(steps, 1))
    note = _callout("以下步骤由 AI 根据报表结构推断，供新开发人员参考，请核实后使用。", "info")
    return _section("6", "🛠️", "从零复现开发步骤（AI 推断）", note + f'<ol class="steps">{items}</ol>')


def _sec7_highlight(parsed: dict, analysis: dict) -> str:
    hl_rules = parsed.get("highlight_rules_summary", [])
    display_text = analysis.get("display_rules", "")
    if not hl_rules and (not display_text or display_text == "无条件高亮规则"):
        return _section("7", "🎨", "条件高亮规则", _callout("无条件高亮规则。"), collapsed=True)

    parts = []
    if display_text and display_text != "无条件高亮规则":
        parts.append(f'<p style="font-size:.8rem;margin-bottom:8px;">{_e(display_text)}</p>')

    if hl_rules:
        rows = []
        for rule in hl_rules:
            affected = "、".join(rule.get("affected_columns", [])) or "—"
            color = rule.get("color", "")
            color_cell = f'<span class="color-s" style="background:{_e(color)};"></span>{_code(color)}' if color else "—"
            rows.append([
                _e(rule.get("name", "")), _code(rule.get("condition", "")),
                _e(rule.get("action", "")), color_cell, _e(affected),
            ])
        parts.append(_table(["规则名称", "触发条件", "效果", "颜色", "影响字段"], rows))

    return _section("7", "🎨", "条件高亮规则", "\n".join(parts))


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
            param = _e(m.get("param") or "（来自单元格）")
            mapping_rows.append([_code(m.get("db_column", "")), param, "✓" if m.get("is_key") else ""])
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
    rows = [["确认人", "", ""], ["确认时间", "", ""], ["补充说明", "", ""]]
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
    """生成 Vercel 风格的高质量自包含 HTML 交接文档 v5"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    fname = parsed.get("file_name", "未知文件")
    fr_ver = parsed.get("fr_version", "?")
    rtype = "填报报表" if parsed.get("report_type") == "writeback" else "查询报表"
    file_kb = parsed.get("file_size_kb", "?")

    has_writeback = bool(parsed.get("writeback_config"))
    has_risks = bool(analysis.get("notes_or_risks"))

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
        _chip(t) for t in [f"FR {fr_ver}", rtype, f"{file_kb} KB", now]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>报表交接文档 | {_e(fname)}</title>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{_CSS}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'default', flowchart:{{curve:'basis'}}}});</script>
</head>
<body>
<header class="site-h">
  <h1>📊 报表交接文档：{_e(fname)}</h1>
  <div class="h-right">
    <div style="display:flex;gap:4px;flex-wrap:wrap;">{chips}</div>
    <button class="print-btn" onclick="window.print()">🖨️ PDF</button>
  </div>
</header>
<div class="page-body">
  {toc}
  <main class="content">
    <div class="ai-warn">
      <span>🤖</span>
      <span><strong>AI 自动生成</strong> — 本文档由 DeepSeek-V4-Flash 根据 .cpt 结构推断生成，请交接双方核实确认后使用。</span>
    </div>
    {sections}
    <div class="doc-f">
      FR 交接 Agent v5 · Vercel 设计系统 · DeepSeek-V4-Flash · {_e(now)}
    </div>
  </main>
</div>
<script>{_JS}</script>
</body>
</html>"""
