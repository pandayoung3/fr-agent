"""
FR 交接 Agent — Streamlit UI v2
工作流：上传 CPT → (可选)数据库增强 → AI 分析 → 查看结果 → 导出
"""
import sys
import os
import json
import tempfile
import pathlib

# Deprecated: React + FastAPI is the maintained product surface.
# Keep this Streamlit UI only as historical MVP reference.

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from parser.cpt_parser import parse_cpt, summarize_to_dict
from agent.llm_analyzer import analyze_report, answer_question
from agent.doc_generator import generate_handover_doc
from agent.lineage_builder import build_lineage
from agent.html_generator_v5 import generate_handover_html
from agent.db_connector import parse_fr_connections, enrich_parsed_datasets

# ── 环境变量 ──────────────────────────────────────────────────────────────────
_env_path = pathlib.Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ[_k.strip()] = _v.strip()

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FR 报表交接 Agent",
    page_icon="📊",
    layout="wide",
)

st.warning(
    "此 Streamlit 页面已归档为历史 MVP 入口。当前主线是 React + FastAPI；"
    "请优先使用 http://127.0.0.1:5173/。"
)

# ── 全局 CSS：Vercel 紧凑设计系统 ──────────────────────────────────────────
st.markdown("""
<style>
/* ── Design Tokens ── */
:root {
  --text: #171717;
  --text-2: #4d4d4d;
  --text-3: #666;
  --bg: #ffffff;
  --bg-subtle: #fafafa;
  --border: rgba(0,0,0,0.08) 0px 0px 0px 1px;
  --border-l: rgb(235,235,235) 0px 0px 0px 1px;
  --shadow: rgba(0,0,0,0.08) 0px 0px 0px 1px, rgba(0,0,0,0.04) 0px 2px 2px;
  --radius: 8px;
  --radius-s: 6px;
  --acc-blue: #0072f5;
  --acc-green: #2e7d32;
  --acc-orange: #e65100;
}
body { font-family: 'Geist', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.35rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #fafafa; box-shadow: var(--border); }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding: 1rem 0.8rem; }

/* ── Compact page container ── */
.stApp .main .block-container { max-width: 1100px; padding: 1.2rem 1.5rem !important; }

/* ── 工作流进度条 ── */
.wf-bar {
  display: flex; align-items: center;
  background: var(--bg); box-shadow: var(--border-l);
  border-radius: var(--radius);
  padding: 10px 16px; margin-bottom: 14px;
}
.wf-step { display: flex; align-items: center; gap: 7px; flex: 1; }
.wf-circle {
  width: 24px; height: 24px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
  transition: all .25s;
}
.wf-step.pending .wf-circle { background: #f0f0f0; color: #bbb; }
.wf-step.active  .wf-circle { background: var(--text); color: #fff; box-shadow: 0 0 0 3px rgba(23,23,23,.12); }
.wf-step.done    .wf-circle { background: var(--acc-green); color: #fff; }
.wf-step.skip    .wf-circle { background: #bbb; color: #fff; }
.wf-label { font-size: 12px; font-weight: 500; line-height: 1.3; }
.wf-sub   { font-size: 10px; color: var(--text-3); }
.wf-step.pending .wf-label { color: #bbb; }
.wf-step.active  .wf-label { color: var(--text); font-weight: 600; }
.wf-step.done    .wf-label { color: var(--acc-green); }
.wf-step.skip    .wf-label { color: var(--text-3); }
.wf-connector { height: 2px; background: #e0e0e0; flex: 0 0 24px; margin: 0 4px; }
.wf-connector.done { background: var(--acc-green); }
.wf-connector.active { background: var(--text); }

/* ── 统计卡 ── */
.stat-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.stat-card {
  background: var(--bg); box-shadow: var(--border-l);
  border-radius: var(--radius-s);
  padding: 8px 14px; min-width: 80px;
}
.stat-lbl { font-size: 10px; color: var(--text-3); text-transform: uppercase; letter-spacing: .04em; margin-bottom: 2px; }
.stat-val { font-size: 17px; font-weight: 700; color: var(--text); line-height: 1.2; }
.stat-card.type .stat-val { font-size: 12px; color: var(--acc-orange); font-weight: 600; margin-top: 2px; }

/* ── Purpose hero ── */
.purpose-hero {
  background: var(--bg-subtle); box-shadow: var(--border-l);
  border-radius: var(--radius);
  padding: 14px 18px; margin-bottom: 14px;
  font-size: 14px; font-weight: 450; line-height: 1.7; color: var(--text);
}
.purpose-hero .lbl {
  font-size: 9px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .06em; color: var(--text-3); margin-bottom: 4px;
}

/* ── Upload zone ── */
.upload-zone {
  text-align: center; padding: 36px 16px 28px;
  background: var(--bg-subtle); box-shadow: var(--border);
  border-radius: var(--radius); margin-bottom: 12px;
}
.upload-zone .icon { font-size: 40px; margin-bottom: 8px; display: block; }
.upload-zone h3 { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.upload-zone p  { font-size: 12px; color: var(--text-3); margin: 0; }

/* ── Analyze zone ── */
.analyze-zone {
  background: var(--bg); box-shadow: var(--border-l);
  border-radius: var(--radius);
  padding: 20px; text-align: center;
  margin: 6px 0 16px;
}
.analyze-zone h3 { font-size: 15px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.analyze-zone p  { font-size: 12px; color: var(--text-3); margin-bottom: 14px; }

/* ── File banner ── */
.file-banner {
  display: flex; align-items: center; gap: 10px;
  background: #e8f5e9; box-shadow: var(--border-l);
  border-radius: var(--radius-s);
  padding: 8px 14px; margin-bottom: 12px;
  font-size: 13px; color: var(--acc-green);
}

/* ── Chain cards ── */
.chain-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; margin-top: 4px; }
.chain-card {
  background: var(--bg); box-shadow: var(--border-l);
  border-radius: var(--radius-s);
  padding: 10px 14px;
}
.chain-title { font-size: 12px; font-weight: 600; color: var(--acc-blue); padding-bottom: 7px; box-shadow: var(--border-l); margin-bottom: 8px; }
.chain-row { display: flex; gap: 6px; margin: 4px 0; font-size: 12px; line-height: 1.5; }
.chain-lbl { font-size: 9px; font-weight: 600; color: var(--text-3); text-transform: uppercase; min-width: 38px; flex-shrink: 0; }

/* ── Steps timeline ── */
.step-list { list-style: none; padding: 0; margin: 0; position: relative; }
.step-list::before { content: ""; position: absolute; left: 13px; top: 6px; bottom: 6px; width: 2px; background: #e0e0e0; }
.step-item { display: flex; align-items: flex-start; gap: 12px; padding: 6px 0; position: relative; }
.step-num {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--text); color: #fff;
  font-size: 11px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative; z-index: 1;
}
.step-text { font-size: 13px; line-height: 1.6; padding-top: 3px; color: var(--text); }

/* ── Risk card ── */
.risk-card {
  background: #fef7e8; color: #7c6a3e;
  border-radius: var(--radius-s); padding: 8px 12px;
  margin: 6px 0; font-size: 12.5px; line-height: 1.5;
}

/* ── AI tag ── */
.ai-tag {
  display: inline-block; font-size: 9px; font-weight: 600;
  padding: 1px 7px; border-radius: 9999px;
  background: #ebf5ff; color: var(--acc-blue);
  margin-left: 4px; vertical-align: middle;
}

/* ── Streamlit native overrides ── */
.stTabs [data-baseweb="tab-list"] { gap: 0; }
.stTabs [data-baseweb="tab"] { font-size: 12px; padding: 6px 14px; }
.stButton button { font-size: 13px; border-radius: var(--radius-s); }
</style>
""", unsafe_allow_html=True)

# ── 会话状态 ──────────────────────────────────────────────────────────────────
_default_webinf = os.path.expanduser("~/FineReport/webapps/webroot/WEB-INF")
_session_defaults = {
    "parsed": None,
    "analysis": None,
    "chat_history": [],
    "html_doc": None,
    "uploaded_filename": None,
    "fr_webinf_dir": _default_webinf if os.path.isdir(_default_webinf) else "",
    "db_conn_status": {},
    "db_enriched": False,
}
for _k, _v in _session_defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── 工作流进度条 ──────────────────────────────────────────────────────────────
def _render_workflow_bar():
    has_file = st.session_state.parsed is not None
    has_db_ds = has_file and any(
        ds.get("type") == "DBTableData"
        for ds in st.session_state.parsed.get("datasets", [])
    )
    enriched = st.session_state.db_enriched
    has_analysis = st.session_state.analysis is not None

    s1 = "done" if has_file else "active"
    s2 = ("done" if enriched else ("active" if has_file and has_db_ds else "skip"))
    s3 = "done" if has_analysis else ("active" if has_file else "pending")
    s4 = "active" if has_analysis else "pending"

    c1 = "done" if has_file else ""
    c2 = "done" if (enriched or (has_file and not has_db_ds)) else ("active" if has_file else "")
    c3 = "done" if has_analysis else ("active" if has_file else "")

    def _step(status, num, label, sub=""):
        icons = {"done": "✓", "active": str(num), "pending": str(num), "skip": "—"}
        sub_html = f'<div class="wf-sub">{sub}</div>' if sub else ""
        # 紧凑单行，避免 Markdown 把 4 空格缩进解析为 code block
        return f'<div class="wf-step {status}"><div class="wf-circle">{icons[status]}</div><div><div class="wf-label">{label}</div>{sub_html}</div></div>'

    s2_sub = "已接入" if enriched else ("不需要" if has_file and not has_db_ds else "可选")

    # 整个 bar 也写成单行，彻底规避 Markdown 缩进解析问题
    bar_html = (
        '<div class="wf-bar">'
        + _step(s1, 1, "上传 CPT")
        + f'<div class="wf-connector {c1}"></div>'
        + _step(s2, 2, "数据库增强", s2_sub)
        + f'<div class="wf-connector {c2}"></div>'
        + _step(s3, 3, "AI 分析")
        + f'<div class="wf-connector {c3}"></div>'
        + _step(s4, 4, "查看 & 导出")
        + '</div>'
    )
    st.markdown(bar_html, unsafe_allow_html=True)


# ── 页面顶部 ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:18px;">
  <span style="font-size:32px;line-height:1;">📊</span>
  <div>
    <h1 style="margin:0;font-size:22px;font-weight:800;color:#1a1a2e;letter-spacing:-.3px;">
      FR 报表交接 Agent
    </h1>
    <p style="margin:0;font-size:13px;color:#93a0b4;">
      上传 FineReport .cpt 文件 · AI 自动解析结构 · 一键生成交接文档
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

_render_workflow_bar()

# ── 侧边栏：数据库增强 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔌 数据库增强")
    st.caption("接入真实数据库获取字段类型和注释，显著提升 AI 分析质量。")
    st.divider()

    if not st.session_state.parsed:
        st.info("请先上传 CPT 文件")
    else:
        d = st.session_state.parsed
        db_datasets = [ds for ds in d["datasets"] if ds.get("type") == "DBTableData"]

        if not db_datasets:
            st.success("此报表使用内嵌数据集，无需数据库连接。")
        elif st.session_state.db_enriched:
            st.success("✅ 数据库字段已成功接入")
            for conn, status in st.session_state.db_conn_status.items():
                if status == "ok":
                    st.caption(f"✅ {conn}")
                elif status.startswith("error:"):
                    st.caption(f"❌ {conn}: {status[6:]}")
            if st.button("重新配置连接", use_container_width=True):
                st.session_state.db_enriched = False
                st.session_state.db_conn_status = {}
                st.session_state.analysis = None
                st.session_state.html_doc = None
                st.rerun()
        else:
            fr_dir = st.text_input(
                "FineReport WEB-INF 路径",
                value=st.session_state.fr_webinf_dir,
                help="自动读取连接配置（host/port/DB/用户名）",
            )
            st.session_state.fr_webinf_dir = fr_dir

            fr_conns = {}
            if fr_dir and os.path.isdir(fr_dir):
                try:
                    fr_conns = parse_fr_connections(fr_dir)
                    st.caption(f"找到 {len(fr_conns)} 个连接配置")
                except Exception as e:
                    st.warning(f"读取配置失败：{e}")

            st.markdown("**为以下连接输入密码：**")
            passwords = {}
            for conn_name in d["db_connections"]:
                meta = fr_conns.get(conn_name, {})
                if meta:
                    st.caption(
                        f"`{conn_name}` — {meta.get('db_type','').upper()} "
                        f"{meta.get('username','')}@{meta.get('host','')}:{meta.get('port','')}"
                    )
                else:
                    st.caption(f"`{conn_name}` — 未找到自动配置")
                status = st.session_state.db_conn_status.get(conn_name, "")
                if status.startswith("error:"):
                    st.error(f"上次失败：{status[6:]}", icon="❌")
                pwd = st.text_input("密码", type="password", key=f"pwd_{conn_name}", placeholder="留空则跳过")
                if pwd:
                    passwords[conn_name] = pwd

            if st.button("🔗 连接并获取字段信息", use_container_width=True, disabled=not passwords):
                with st.spinner("连接数据库，获取字段结构..."):
                    try:
                        enriched, report = enrich_parsed_datasets(d, fr_conns, passwords)
                        st.session_state.parsed = enriched
                        new_status = {}
                        for item in report["success"]:
                            new_status[item.split("/")[0]] = "ok"
                        for item in report["failed"]:
                            new_status[item["conn"]] = f"error:{item['error']}"
                        for conn in report["skipped"]:
                            new_status[conn] = "skipped"
                        st.session_state.db_conn_status = new_status
                        if report["success"]:
                            st.session_state.db_enriched = True
                            st.session_state.analysis = None
                            st.session_state.html_doc = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"失败：{e}")

    st.divider()
    if st.session_state.parsed:
        if st.button("↩️ 重新上传文件", use_container_width=True):
            for k in list(_session_defaults.keys()):
                st.session_state[k] = _session_defaults[k]
            st.rerun()


# ── 主区：上传 ────────────────────────────────────────────────────────────────
if not st.session_state.parsed:
    st.markdown("""
    <div class="upload-zone">
      <span class="icon">📂</span>
      <h3>上传 FineReport 报表文件</h3>
      <p>支持 .cpt 格式 · FineReport 9.0 / 10.0 / 11.0</p>
    </div>
    """, unsafe_allow_html=True)

uploaded = st.file_uploader("选择 .cpt 文件", type=["cpt"], label_visibility="collapsed")

if uploaded and uploaded.name != st.session_state.uploaded_filename:
    st.session_state.uploaded_filename = uploaded.name
    with tempfile.NamedTemporaryFile(suffix=".cpt", delete=False) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name
    with st.spinner("📦 解析 CPT 文件结构..."):
        summary = parse_cpt(tmp_path)
        parsed = summarize_to_dict(summary)
        parsed["file_name"] = uploaded.name  # 用原始上传名覆盖临时文件名
        st.session_state.parsed = parsed
        st.session_state.analysis = None
        st.session_state.chat_history = []
        st.session_state.html_doc = None
        st.session_state.db_conn_status = {}
        st.session_state.db_enriched = False
    os.unlink(tmp_path)
    st.rerun()


# ── 主区：解析完成后 ──────────────────────────────────────────────────────────
if st.session_state.parsed:
    d = st.session_state.parsed

    # 文件横幅
    st.markdown(f"""
    <div class="file-banner">
      <span style="font-size:20px;">✅</span>
      <span>已解析&nbsp;<strong>{d['file_name']}</strong></span>
    </div>
    """, unsafe_allow_html=True)

    # 统计卡
    rtype_label = "📝 填报" if d["report_type"] == "writeback" else "🔍 查询"
    db_enriched_label = " ✅" if st.session_state.db_enriched else ""
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-lbl">FR 版本</div>
        <div class="stat-val">{d['fr_version']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Sheet 数</div>
        <div class="stat-val">{d['sheet_count']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">数据集</div>
        <div class="stat-val">{len(d['datasets'])}{db_enriched_label}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">参数控件</div>
        <div class="stat-val">{len(d['widgets'])}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">文件大小</div>
        <div class="stat-val">{d['file_size_kb']}</div>
        <div style="font-size:11px;color:#aaa;">KB</div>
      </div>
      <div class="stat-card type">
        <div class="stat-lbl">报表类型</div>
        <div class="stat-val">{rtype_label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI 分析触发 ──────────────────────────────────────────────────────────
    if st.session_state.analysis is None:
        db_note = (
            "已接入数据库字段信息，分析质量将显著提升 ✨"
            if st.session_state.db_enriched
            else "可在左侧侧边栏配置数据库连接以提升分析质量（可跳过）"
        )
        st.markdown(f"""
        <div class="analyze-zone">
          <h3>准备好开始 AI 分析了</h3>
          <p>{db_note}</p>
        </div>
        """, unsafe_allow_html=True)
        col_l, col_btn, col_r = st.columns([1, 2, 1])
        with col_btn:
            if st.button("🤖 启动 AI 分析", use_container_width=True, type="primary"):
                with st.spinner("🧠 AI 正在分析报表结构与业务逻辑，通常需要 15-30 秒..."):
                    try:
                        result = analyze_report(d)
                    except Exception as e:
                        result = {"_parse_error": str(e), "_tokens_used": 0}
                    try:
                        out_dir = pathlib.Path(__file__).parent.parent / "output"
                        out_dir.mkdir(exist_ok=True)
                        (out_dir / (d["file_name"].replace(".cpt", "_analysis_debug.json"))).write_text(
                            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                        )
                    except Exception:
                        pass
                    st.session_state.analysis = result
                st.rerun()

    else:
        # ── 分析结果展示 ─────────────────────────────────────────────────────
        a = st.session_state.analysis

        if a.get("_parse_error"):
            st.error(f"AI 分析失败：{a['_parse_error']}")
            with st.expander("查看原始返回内容"):
                st.code(a.get("raw_response", "（无内容）"))
            if st.button("🔄 重新分析"):
                st.session_state.analysis = None
                st.rerun()

        else:
            st.markdown(
                f'<div style="text-align:right;font-size:12px;color:#bbb;margin-bottom:4px;">'
                f'分析完成 · 消耗 {a.get("_tokens_used","?")} tokens</div>',
                unsafe_allow_html=True,
            )

            tab_overview, tab_chains, tab_indicators, tab_steps, tab_lineage, tab_qa, tab_export = st.tabs([
                "📋 概览",
                "⛓️ 交互链路",
                "📊 指标字典",
                "🛠️ 开发步骤",
                "🗺️ 数据血缘",
                "💬 问答",
                "⬇️ 导出",
            ])

            # ── 概览 ─────────────────────────────────────────────────────────
            with tab_overview:
                purpose = a.get("purpose", "（AI 未能推断）")
                st.markdown(f"""
                <div class="purpose-hero">
                  <div class="lbl">📌 报表业务用途</div>
                  {purpose}
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    with st.container(border=True):
                        st.markdown("**布局结构** <span class='ai-tag'>AI</span>", unsafe_allow_html=True)
                        st.write(a.get("layout_description") or "—")
                with col_b:
                    with st.container(border=True):
                        st.markdown("**数据集关系** <span class='ai-tag'>AI</span>", unsafe_allow_html=True)
                        st.write(a.get("dataset_relationships") or "—")

                if a.get("field_semantics"):
                    with st.expander("🏷️ 关键字段业务含义（AI 推断）"):
                        st.write(a["field_semantics"])

                risks = a.get("notes_or_risks", [])
                if risks:
                    st.markdown("#### ⚠️ 风险点与注意事项")
                    risks_html = "".join(
                        f'<div class="risk-card">⚠️ {r}</div>' for r in risks
                    )
                    st.markdown(risks_html, unsafe_allow_html=True)

            # ── 交互链路 ─────────────────────────────────────────────────────
            with tab_chains:
                chains = a.get("interaction_chains", [])
                if not chains:
                    st.info("无交互链路（该报表可能无参数控件，或 AI 未能推断）")
                else:
                    cards_html = ""
                    for i, ch in enumerate(chains, 1):
                        w = ch.get("widget_name", f"链路 {i}")
                        wt = ch.get("widget_type", "")
                        wt_tag = f'<code style="font-size:11px;background:#f0f2f5;padding:1px 6px;border-radius:4px;">{wt}</code>' if wt else ""
                        rows_html = ""
                        for lbl, key in [
                            ("作用", "param_role"),
                            ("SQL", "sql_impact"),
                            ("展示", "data_displayed"),
                            ("原因", "why_this_design"),
                        ]:
                            val = ch.get(key, "")
                            if val:
                                rows_html += f'<div class="chain-row"><span class="chain-lbl">{lbl}</span><span>{val}</span></div>'
                        cards_html += f"""
                        <div class="chain-card">
                          <div class="chain-title">{i}. {w} {wt_tag}</div>
                          {rows_html}
                        </div>"""
                    st.markdown(f'<div class="chain-grid">{cards_html}</div>', unsafe_allow_html=True)

                widgets = d.get("widgets", [])
                if widgets:
                    st.markdown("")
                    with st.expander("参数控件汇总表"):
                        rows = [
                            {
                                "控件名": w.get("name", ""),
                                "类型": w.get("widget_type", ""),
                                "数据来源": w.get("bound_dataset") or "直接输入",
                                "key 字段": w.get("key_column") or "—",
                                "显示字段": w.get("display_column") or "—",
                            }
                            for w in widgets
                        ]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # ── 指标字典 ─────────────────────────────────────────────────────
            with tab_indicators:
                ind_list = a.get("indicator_dict", [])
                if not ind_list:
                    st.info("无指标字典（AI 未能推断，或报表无明确度量指标）")
                else:
                    rows = [
                        {
                            "指标名": ind.get("indicator_name", ""),
                            "来源字段": ind.get("source_field", ""),
                            "数据集": ind.get("dataset") or "—",
                            "类型": ind.get("type", ""),
                            "单位": ind.get("unit") or "—",
                            "公式": ind.get("formula") or "—",
                            "业务含义": ind.get("description", ""),
                        }
                        for ind in ind_list
                    ]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                formula_exps = a.get("formula_explanations", [])
                if formula_exps:
                    with st.expander(f"公式详细解释（{len(formula_exps)} 条）"):
                        for fe in formula_exps:
                            st.markdown(f"**`{fe.get('pos','')}`** — `{fe.get('formula','')}`")
                            st.caption(fe.get("meaning", ""))
                            st.divider()

            # ── 开发步骤 ─────────────────────────────────────────────────────
            with tab_steps:
                steps = a.get("development_steps", [])
                if not steps:
                    st.info("AI 未能推断开发步骤")
                else:
                    st.caption("以下步骤由 AI 根据报表结构推断，供新开发人员参考，请核实后使用。")
                    items_html = "".join(
                        f'<li class="step-item"><div class="step-num">{i}</div><div class="step-text">{step}</div></li>'
                        for i, step in enumerate(steps, 1)
                    )
                    st.markdown(f'<ul class="step-list">{items_html}</ul>', unsafe_allow_html=True)

                # 条件高亮规则（附在开发步骤下，较少用）
                display_rules = a.get("display_rules", "")
                hl_rules = d.get("highlight_rules_summary", [])
                if hl_rules or (display_rules and display_rules != "无条件高亮规则"):
                    st.markdown("---")
                    st.markdown("#### 🎨 条件高亮规则")
                    if display_rules and display_rules != "无条件高亮规则":
                        st.info(display_rules)
                    if hl_rules:
                        rows = [
                            {
                                "规则名称": r.get("name", ""),
                                "触发条件": r.get("condition", ""),
                                "效果": r.get("action", ""),
                                "颜色": r.get("color", "—"),
                                "影响字段": "、".join(r.get("affected_columns", [])) or "—",
                            }
                            for r in hl_rules
                        ]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                # 填报配置（仅填报报表）
                wb_cfg = d.get("writeback_config")
                if wb_cfg:
                    st.markdown("---")
                    st.markdown("#### 📝 填报提交配置")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown(f"- **连接**：`{wb_cfg.get('db_connection','—')}`")
                        st.markdown(f"- **目标表**：`{wb_cfg.get('table','—')}`")
                        keys = "、".join(f"`{k}`" for k in wb_cfg.get("key_columns", []))
                        st.markdown(f"- **主键**：{keys or '—'}")
                    if wb_cfg.get("column_mappings"):
                        with col_c2:
                            mapping_rows = [
                                {
                                    "数据库字段": m.get("db_column", ""),
                                    "来源参数": m.get("param") or "（来自单元格）",
                                    "是否主键": "✓" if m.get("is_key") else "",
                                }
                                for m in wb_cfg["column_mappings"]
                            ]
                            st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True, hide_index=True)

            # ── 数据血缘 ─────────────────────────────────────────────────────
            with tab_lineage:
                lineage = build_lineage(d)
                if lineage["sql_driving_widget_names"]:
                    st.graphviz_chart(lineage["dot"])
                    unmatched = lineage.get("unmatched_widget_names", [])
                    if unmatched:
                        names_str = "、".join(unmatched[:8]) + ("..." if len(unmatched) > 8 else "")
                        st.warning(f"未找到 SQL 参数连接的控件（{len(unmatched)} 个）：{names_str}\n\n这些控件可能通过单元格过滤条件或前端 JS 实现筛选，需人工核实。")
                else:
                    st.info("未找到控件→SQL参数的直接连接（所有数据集为嵌入式或参数名不匹配）")

                datasets = d.get("datasets", [])
                if datasets:
                    with st.expander("数据集详情", expanded=False):
                        for ds in datasets:
                            tag = "🗄️ DB查询" if ds.get("type") == "DBTableData" else "📋 内嵌数据"
                            st.markdown(f"**{tag} · {ds['name']}**")
                            if ds.get("db_connection"):
                                st.caption(f"连接：`{ds['db_connection']}`")
                            cols = ds.get("columns", [])
                            if cols:
                                cols_str = "  `" + "`  `".join(cols[:20]) + "`"
                                suffix = f"  *(共 {len(cols)} 列)*" if len(cols) > 20 else ""
                                st.caption("字段：" + cols_str + suffix)
                            if ds.get("sql"):
                                with st.expander(f"SQL — {ds['name']}", expanded=False):
                                    st.code(ds["sql"], language="sql")
                                    if ds.get("sql_params"):
                                        st.caption(f"动态参数：{', '.join(ds['sql_params'])}")
                            st.divider()

            # ── 问答 ─────────────────────────────────────────────────────────
            with tab_qa:
                st.caption("基于报表结构和 AI 分析结论，回答关于这张报表的具体问题。")
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                question = st.chat_input("问一个关于这张报表的问题...")
                if question:
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    with st.spinner("回答中..."):
                        answer = answer_question(d, a, question)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()

            # ── 导出 ─────────────────────────────────────────────────────────
            with tab_export:
                fname_stem = d["file_name"].replace(".cpt", "")
                doc_md = generate_handover_doc(d, a)

                col_md, col_html = st.columns(2)

                with col_md:
                    with st.container(border=True):
                        st.markdown("#### 📄 Markdown 交接文档")
                        st.caption("适合粘贴到 Confluence / Notion / 飞书文档")
                        st.download_button(
                            label="⬇️ 下载 Markdown",
                            data=doc_md.encode("utf-8"),
                            file_name=f"{fname_stem}_交接文档.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                        with st.expander("预览内容"):
                            tab_render, tab_raw = st.tabs(["渲染视图", "原始文本"])
                            with tab_render:
                                st.markdown(doc_md)
                            with tab_raw:
                                st.code(doc_md, language="markdown")

                with col_html:
                    with st.container(border=True):
                        st.markdown("#### 🌐 HTML 交接文档")
                        st.caption("自包含 HTML，含目录导航、血缘图、可折叠章节，可直接另存 PDF")
                        if not st.session_state.html_doc:
                            if st.button("⚙️ 生成 HTML 文档", use_container_width=True):
                                with st.spinner("渲染 HTML..."):
                                    st.session_state.html_doc = generate_handover_html(d, a)
                                st.rerun()
                        else:
                            st.download_button(
                                label="⬇️ 下载 HTML",
                                data=st.session_state.html_doc.encode("utf-8"),
                                file_name=f"{fname_stem}_交接文档.html",
                                mime="text/html",
                                use_container_width=True,
                            )
                            if st.button("重新生成", use_container_width=True):
                                st.session_state.html_doc = None
                                st.rerun()
                            with st.expander("在线预览"):
                                st.caption("💡 下载后在浏览器中打开效果更佳；支持 🖨️ 打印为 PDF")
                                components.html(st.session_state.html_doc, height=600, scrolling=True)

else:
    # 未上传时的引导
    st.markdown("""
    <div style="text-align:center;padding:48px 20px 32px;color:#bbb;">
      <div style="font-size:14px;margin-top:8px;">
        支持解析：数据集结构 · SQL 语句 · 参数控件 · 单元格绑定 · 数据血缘 · AI 业务语义分析
      </div>
    </div>
    """, unsafe_allow_html=True)
