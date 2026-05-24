"""
FR 交接 Agent — Streamlit MVP Demo
上传 .cpt 文件 → 解析 → LLM 语义分析 → 展示结构 + 问答
"""
import sys
import os
import json
import tempfile

import streamlit as st

# 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from parser.cpt_parser import parse_cpt, summarize_to_dict
from agent.llm_analyzer import analyze_report, answer_question
from agent.doc_generator import generate_handover_doc
from agent.lineage_builder import build_lineage
from agent.html_generator import generate_handover_html
from agent.db_connector import parse_fr_connections, enrich_parsed_datasets

# ── 环境变量（从 .env 文件或系统环境读取）────────────────────────────────────
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FR 报表交接 Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 FR 报表交接 Agent")
st.caption("上传 FineReport (.cpt) 文件，自动解析结构并生成业务交接分析")

# ── 会话状态 ──────────────────────────────────────────────────────────────────
if "parsed" not in st.session_state:
    st.session_state.parsed = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_doc_preview" not in st.session_state:
    st.session_state.show_doc_preview = False
if "show_html_preview" not in st.session_state:
    st.session_state.show_html_preview = False
if "html_doc" not in st.session_state:
    st.session_state.html_doc = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "fr_webinf_dir" not in st.session_state:
    # 尝试自动检测 FR WEB-INF 目录
    _default_fr = os.path.expanduser("~/FineReport/webapps/webroot/WEB-INF")
    st.session_state.fr_webinf_dir = _default_fr if os.path.isdir(_default_fr) else ""
if "db_conn_status" not in st.session_state:
    st.session_state.db_conn_status = {}  # {conn_name: "ok"/"error:xxx"}
if "db_enriched" not in st.session_state:
    st.session_state.db_enriched = False

# ── 上传区 ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("选择 .cpt 文件", type=["cpt"], label_visibility="collapsed")

if uploaded:
    # 只在文件名变化时（新文件上传）才重新解析，避免每次 rerun 都清空 analysis
    if uploaded.name != st.session_state.uploaded_filename:
        st.session_state.uploaded_filename = uploaded.name
        with tempfile.NamedTemporaryFile(suffix=".cpt", delete=False) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        with st.spinner("解析中..."):
            summary = parse_cpt(tmp_path)
            parsed = summarize_to_dict(summary)
            st.session_state.parsed = parsed
            st.session_state.analysis = None
            st.session_state.chat_history = []
            st.session_state.show_doc_preview = False
            st.session_state.show_html_preview = False
            st.session_state.html_doc = None
            st.session_state.db_conn_status = {}
            st.session_state.db_enriched = False
        os.unlink(tmp_path)

# ── 主体内容 ──────────────────────────────────────────────────────────────────
if st.session_state.parsed:
    d = st.session_state.parsed

    # 顶部基本信息
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("FR 版本", d["fr_version"])
    col2.metric("Sheet 数", d["sheet_count"])
    col3.metric("数据集", len(d["datasets"]))
    col4.metric("文件大小", f'{d["file_size_kb"]} KB')
    col5.metric("报表类型", "填报" if d["report_type"] == "writeback" else "查询")

    st.divider()

    # 左右两栏
    left, right = st.columns([1, 1])

    # ── 左栏：解析结构 ────────────────────────────────────────────────────────
    with left:
        st.subheader("解析结构")

        # 数据集
        with st.expander(f"📦 数据集（{len(d['datasets'])}个）", expanded=True):
            for ds in d["datasets"]:
                tag = "🗄️" if ds["type"] == "DBTableData" else "📋"
                st.markdown(f"**{tag} {ds['name']}** `{ds['type']}`")
                if ds.get("db_connection"):
                    st.caption(f"  DB连接: {ds['db_connection']}")
                if ds.get("columns"):
                    cols_str = "、".join(ds["columns"][:10])
                    if len(ds["columns"]) > 10:
                        cols_str += f" ... 共{len(ds['columns'])}列"
                    st.caption(f"  字段: {cols_str}")
                if ds.get("sql"):
                    with st.expander("查看 SQL", expanded=False):
                        st.code(ds["sql"], language="sql")
                    if ds.get("sql_params"):
                        st.caption(f"  动态参数: {', '.join(ds['sql_params'])}")

        # 参数控件
        if d["widgets"]:
            with st.expander(f"🎛️ 参数控件（{len(d['widgets'])}个）", expanded=True):
                for w in d["widgets"]:
                    line = f"**{w['name']}** `{w['widget_type']}`"
                    if w.get("bound_dataset"):
                        line += f" → 数据集 `{w['bound_dataset']}`"
                        if w.get("key_column"):
                            line += f" (key={w['key_column']}, display={w['display_column']})"
                    st.markdown(line)
                    if w.get("custom_options"):
                        opts = " / ".join(f"{o['key']}={o['value']}" for o in w["custom_options"])
                        st.caption(f"  选项: {opts}")

        # 单元格绑定摘要
        bound_cells = [c for c in d["cell_bindings"] if c.get("dataset")]
        if bound_cells:
            with st.expander(f"🔗 单元格-数据集绑定（{len(bound_cells)}个）"):
                for c in bound_cells[:20]:
                    st.caption(f"  Cell{c['pos']} → {c['dataset']}.{c['column']}"
                               + (f" [{c['widget_type']}]" if c.get("widget_type") else ""))

        # ── 数据库连接增强（可选）────────────────────────────────────────────
        db_datasets = [ds for ds in d["datasets"] if ds.get("type") == "DBTableData"]
        if db_datasets:
            enriched_label = " ✅ 已接入" if st.session_state.db_enriched else ""
            with st.expander(f"🔌 数据库连接{enriched_label}（{len(d['db_connections'])} 个）", expanded=not st.session_state.db_enriched):

                # FR WEB-INF 路径配置
                fr_dir = st.text_input(
                    "FineReport WEB-INF 路径",
                    value=st.session_state.fr_webinf_dir,
                    key="fr_webinf_input",
                    help="用于自动读取数据库连接配置（host/port/数据库名/用户名）",
                )
                st.session_state.fr_webinf_dir = fr_dir

                # 读取 FR 连接配置
                fr_conns = {}
                if fr_dir and os.path.isdir(fr_dir):
                    try:
                        fr_conns = parse_fr_connections(fr_dir)
                    except Exception as e:
                        st.warning(f"读取 FR 连接配置失败：{e}")

                st.markdown("**为以下数据库连接输入密码：**")
                passwords = {}
                for conn_name in d["db_connections"]:
                    meta = fr_conns.get(conn_name, {})
                    if meta:
                        db_type = meta.get("db_type", "?").upper()
                        host = meta.get("host", "?")
                        port = meta.get("port", "?")
                        database = meta.get("database", "?")
                        username = meta.get("username", "?")
                        st.caption(f"`{conn_name}` → {db_type} {username}@{host}:{port}/{database}")
                    else:
                        st.caption(f"`{conn_name}` → 未在 FR 配置中找到（请手动填写）")
                        col_h, col_p, col_db, col_u = st.columns(4)
                        meta = {
                            "db_type": col_h.text_input("类型", "mysql", key=f"dbtype_{conn_name}"),
                            "host": col_h.text_input("Host", "localhost", key=f"host_{conn_name}"),
                            "port": col_p.number_input("Port", value=3306, key=f"port_{conn_name}"),
                            "database": col_db.text_input("数据库", "", key=f"db_{conn_name}"),
                            "username": col_u.text_input("用户名", "root", key=f"user_{conn_name}"),
                        }
                        fr_conns[conn_name] = meta

                    pwd = st.text_input(
                        f"密码（{conn_name}）",
                        type="password",
                        key=f"pwd_{conn_name}",
                        placeholder="留空则跳过此连接",
                    )
                    if pwd:
                        passwords[conn_name] = pwd

                    # 显示上次连接状态
                    status = st.session_state.db_conn_status.get(conn_name, "")
                    if status == "ok":
                        st.success(f"✅ {conn_name} 字段已获取")
                    elif status.startswith("error:"):
                        st.error(f"❌ {conn_name} 连接失败：{status[6:]}")

                if st.button("🔗 连接数据库并获取字段信息", use_container_width=True,
                             disabled=not passwords):
                    with st.spinner("连接中，获取字段结构..."):
                        try:
                            enriched, report = enrich_parsed_datasets(
                                st.session_state.parsed, fr_conns, passwords
                            )
                            st.session_state.parsed = enriched
                            # 更新状态
                            new_status = {}
                            for item in report["success"]:
                                conn = item.split("/")[0]
                                new_status[conn] = "ok"
                            for item in report["failed"]:
                                new_status[item["conn"]] = f"error:{item['error']}"
                            for conn in report["skipped"]:
                                new_status[conn] = "skipped"
                            st.session_state.db_conn_status = new_status
                            if report["success"]:
                                st.session_state.db_enriched = True
                                # 字段变了，清空旧的分析和文档缓存
                                st.session_state.analysis = None
                                st.session_state.html_doc = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"获取字段信息失败：{e}")

        # 数据血缘流向图（确定性，不需要 LLM）
        with st.expander("🗺️ 数据血缘流向图", expanded=False):
            lineage = build_lineage(d)
            if lineage["sql_driving_widget_names"]:
                st.graphviz_chart(lineage["dot"])
                unmatched = lineage["unmatched_widget_names"]
                if unmatched:
                    st.caption(
                        f"⚠️ 未找到SQL参数连接的控件（{len(unmatched)}个）：" +
                        "、".join(unmatched[:8]) +
                        ("..." if len(unmatched) > 8 else "")
                    )
            else:
                st.info("未找到控件→SQL参数的直接连接（所有数据集为嵌入式或参数名不匹配）")

    # ── 右栏：LLM 分析 ────────────────────────────────────────────────────────
    with right:
        st.subheader("业务分析")

        if st.session_state.analysis is None:
            if st.button("🤖 生成 LLM 分析", use_container_width=True):
                with st.spinner("DeepSeek 分析中..."):
                    try:
                        result = analyze_report(d)
                    except Exception as e:
                        result = {"_parse_error": str(e), "_tokens_used": 0}
                    # 落盘：无论成功失败都保存，方便离线排查
                    try:
                        import pathlib
                        out_dir = pathlib.Path(__file__).parent.parent / "output"
                        out_dir.mkdir(exist_ok=True)
                        debug_path = out_dir / (d["file_name"].replace(".cpt", "_analysis_debug.json"))
                        debug_path.write_text(
                            json.dumps(result, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                    except Exception:
                        pass
                    st.session_state.analysis = result
                st.rerun()
        else:
            a = st.session_state.analysis
            if a.get("_parse_error"):
                st.error(f"LLM 分析失败：{a['_parse_error']}")
                with st.expander("查看原始返回内容"):
                    st.code(a.get("raw_response", "（无内容）"))
            else:
                st.success(f"分析完成（消耗 {a.get('_tokens_used', '?')} tokens）")

            st.markdown("**报表用途**")
            st.info(a.get("purpose", "—"))

            st.markdown("**布局结构**")
            st.write(a.get("layout_description", "—"))

            st.markdown("**数据集关系**")
            st.write(a.get("dataset_relationships", "—"))

            # 交互链路
            chains = a.get("interaction_chains", [])
            if chains:
                st.markdown(f"**交互链路（{len(chains)} 条）**")
                for i, chain in enumerate(chains, 1):
                    w = chain.get("widget_name", f"链路{i}")
                    with st.expander(f"链路 {i}：{w}"):
                        if chain.get("param_role"):
                            st.caption(f"控件作用：{chain['param_role']}")
                        if chain.get("sql_impact"):
                            st.caption(f"SQL 影响：{chain['sql_impact']}")
                        if chain.get("data_displayed"):
                            st.caption(f"数据展示：{chain['data_displayed']}")
                        if chain.get("why_this_design"):
                            st.caption(f"设计原因：{chain['why_this_design']}")

            # 指标字典
            indicator_dict = a.get("indicator_dict", [])
            if indicator_dict:
                st.markdown(f"**📋 指标字典（{len(indicator_dict)} 条）**")
                with st.expander("查看指标字典", expanded=False):
                    rows = []
                    for ind in indicator_dict:
                        rows.append({
                            "指标名": ind.get("indicator_name", ""),
                            "来源字段": ind.get("source_field", ""),
                            "类型": ind.get("type", ""),
                            "单位": ind.get("unit") or "—",
                            "公式": ind.get("formula") or "—",
                            "业务含义": ind.get("description", ""),
                        })
                    import pandas as pd
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            risks = a.get("notes_or_risks", [])
            if risks:
                st.markdown("**注意事项 / 风险点**")
                for r in risks:
                    st.warning(r)

            st.divider()

            # 导出交接文档
            st.subheader("📄 导出交接文档")
            doc_md = generate_handover_doc(d, a)
            fname_stem = d["file_name"].replace(".cpt", "")

            # ── 行1：Markdown 预览 + 下载 ──────────────────────────────────
            btn_prev, btn_dl = st.columns(2)
            with btn_prev:
                label = "🙈 收起 Markdown" if st.session_state.show_doc_preview else "👁️ 预览 Markdown"
                if st.button(label, use_container_width=True):
                    st.session_state.show_doc_preview = not st.session_state.show_doc_preview
                    st.rerun()
            with btn_dl:
                st.download_button(
                    label="⬇️ 下载 Markdown",
                    data=doc_md.encode("utf-8"),
                    file_name=f"{fname_stem}_交接文档.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            if st.session_state.show_doc_preview:
                with st.expander("📄 Markdown 交接文档预览", expanded=True):
                    tab_render, tab_raw = st.tabs(["渲染视图", "原始 Markdown"])
                    with tab_render:
                        st.markdown(doc_md)
                    with tab_raw:
                        st.code(doc_md, language="markdown")

            # ── 行2：HTML 生成 + 下载 ───────────────────────────────────────
            st.markdown("---")
            btn_html_gen, btn_html_dl = st.columns(2)
            with btn_html_gen:
                html_label = "🙈 收起 HTML 预览" if st.session_state.show_html_preview else "🌐 生成 HTML 交接文档"
                if st.button(html_label, use_container_width=True):
                    if not st.session_state.show_html_preview:
                        # 首次点击：生成 HTML
                        with st.spinner("正在生成 HTML 文档..."):
                            st.session_state.html_doc = generate_handover_html(d, a)
                        st.session_state.show_html_preview = True
                    else:
                        st.session_state.show_html_preview = False
                    st.rerun()
            with btn_html_dl:
                if st.session_state.html_doc:
                    st.download_button(
                        label="⬇️ 下载 HTML",
                        data=st.session_state.html_doc.encode("utf-8"),
                        file_name=f"{fname_stem}_交接文档.html",
                        mime="text/html",
                        use_container_width=True,
                    )
                else:
                    st.button("⬇️ 下载 HTML", disabled=True, use_container_width=True,
                              help="请先点击「生成 HTML 交接文档」")

            if st.session_state.show_html_preview and st.session_state.html_doc:
                st.caption("💡 点击右上角 🖨️ 按钮可打印或另存为 PDF；下载 HTML 后在浏览器中打开效果更佳")
                import streamlit.components.v1 as components
                components.html(st.session_state.html_doc, height=750, scrolling=True)

            st.divider()

            # 问答区
            st.subheader("💬 报表问答")
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

else:
    st.info("请上传一个 FineReport .cpt 文件开始分析")
    st.markdown("""
    **支持能力：**
    - 解析数据集结构（字段、SQL、数据库连接）
    - 提取参数控件及其数据源绑定
    - 还原单元格与数据集的绑定关系
    - 识别报表类型（查询报表 / 填报报表）
    - LLM 自动推断报表业务用途和数据流向
    - 自然语言问答
    """)
