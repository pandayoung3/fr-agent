"""
FR 交接 Agent — FastAPI 后端
提供 REST + SSE 接口，供 React 前端调用
"""
import sys
import os
import json
import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── 路径配置，确保能找到 parser/ agent/ 模块 ──
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── 加载 .env ──
_env_path = ROOT / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8-sig").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ[_k.strip().lstrip("\ufeff")] = _v.strip()

from parser.cpt_parser import parse_cpt, summarize_to_dict
from agent.llm_analyzer import analyze_report, get_client, _get_model, _slim_for_llm
from agent.db_connector import parse_fr_connections, enrich_parsed_datasets
from agent.doc_generator import generate_handover_doc
from agent.html_generator import generate_handover_html
from agent.lineage_builder import build_lineage
from agent.scoring_engine import score_report
from agent.formula_validator import validate_formulas
from agent.change_impact_analyzer import analyze_change_impact

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="FR 交接 Agent API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 请求体模型 ────────────────────────────────────────────────────────────────

class EnrichRequest(BaseModel):
    parsed: dict
    fr_webinf_dir: str = ""
    passwords: dict  # {conn_name: password}

class AnalyzeRequest(BaseModel):
    parsed: dict

class ChatRequest(BaseModel):
    parsed: dict
    analysis: dict
    question: str
    history: list = []

class ExportRequest(BaseModel):
    parsed: dict
    analysis: dict

class FrConnectionsRequest(BaseModel):
    fr_webinf_dir: str

class ScoreRequest(BaseModel):
    parsed: dict
    analysis: dict = {}
    lineage: dict | None = None

class FormulaValidationRequest(BaseModel):
    parsed: dict

class ChangeImpactRequest(BaseModel):
    parsed: dict
    analysis: dict | None = None
    change_request: str
    lineage: dict | None = None

class LlmTestRequest(BaseModel):
    prompt: str = "请用一句话回复 FR-Agent LLM 配置已可用。"


# ── SSE 工具 ─────────────────────────────────────────────────────────────────

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ── 路由 ─────────────────────────────────────────────────────────────────────

@app.post("/api/parse")
async def parse_endpoint(file: UploadFile = File(...)):
    """上传 CPT 文件，返回解析结构"""
    if not file.filename.endswith(".cpt"):
        raise HTTPException(400, "仅支持 .cpt 文件")
    return await _parse_upload_file(file)


@app.post("/api/batch/parse")
async def batch_parse_endpoint(files: list[UploadFile] | None = File(default=None)):
    """批量上传 CPT 文件，返回每个文件的解析摘要和完整 parsed。"""
    if not files:
        raise HTTPException(400, "请至少上传一个 .cpt 文件")

    items = []
    for file in files:
        if not file.filename.endswith(".cpt"):
            items.append({
                "file_name": file.filename,
                "status": "failed",
                "error": "仅支持 .cpt 文件",
            })
            continue

        try:
            parsed = await _parse_upload_file(file)
            items.append({
                "file_name": file.filename,
                "status": "success",
                "parsed": parsed,
                "summary": _batch_summary(parsed),
            })
        except Exception as e:
            items.append({
                "file_name": file.filename,
                "status": "failed",
                "error": str(e),
            })

    success = sum(1 for item in items if item["status"] == "success")
    return {
        "total": len(items),
        "success": success,
        "failed": len(items) - success,
        "items": items,
    }


async def _parse_upload_file(file: UploadFile) -> dict:
    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".cpt", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        summary = await asyncio.to_thread(parse_cpt, tmp_path)
        parsed = await asyncio.to_thread(summarize_to_dict, summary)
        parsed["file_name"] = file.filename  # 保留原始文件名
        return parsed
    finally:
        os.unlink(tmp_path)


def _batch_summary(parsed: dict) -> dict:
    datasets = parsed.get("datasets") if isinstance(parsed.get("datasets"), list) else []
    widgets = parsed.get("widgets") if isinstance(parsed.get("widgets"), list) else []
    cell_bindings = parsed.get("cell_bindings") if isinstance(parsed.get("cell_bindings"), list) else []
    formulas = parsed.get("formula_cells") if isinstance(parsed.get("formula_cells"), list) else []
    db_datasets = [dataset for dataset in datasets if isinstance(dataset, dict) and dataset.get("type") == "DBTableData"]
    connections = [
        dataset.get("db_connection")
        for dataset in db_datasets
        if isinstance(dataset, dict) and dataset.get("db_connection")
    ]
    return {
        "report_type": parsed.get("report_type", "query"),
        "dataset_count": len(datasets),
        "db_dataset_count": len(db_datasets),
        "widget_count": len(widgets),
        "cell_binding_count": len(cell_bindings),
        "formula_count": len(formulas),
        "db_connections": sorted(set(connections)),
    }


@app.post("/api/fr-connections")
async def fr_connections_endpoint(req: FrConnectionsRequest):
    """读取 FineReport WEB-INF 连接配置"""
    if not req.fr_webinf_dir or not os.path.isdir(req.fr_webinf_dir):
        return {}
    try:
        conns = await asyncio.to_thread(parse_fr_connections, req.fr_webinf_dir)
        return conns
    except Exception as e:
        raise HTTPException(400, f"读取连接配置失败：{e}")


@app.post("/api/enrich")
async def enrich_endpoint(req: EnrichRequest):
    """数据库字段增强"""
    fr_conns = {}
    if req.fr_webinf_dir and os.path.isdir(req.fr_webinf_dir):
        try:
            fr_conns = await asyncio.to_thread(parse_fr_connections, req.fr_webinf_dir)
        except Exception:
            pass

    try:
        enriched, report = await asyncio.to_thread(
            enrich_parsed_datasets, req.parsed, fr_conns, req.passwords
        )
        return {"parsed": enriched, "report": report}
    except Exception as e:
        raise HTTPException(500, f"数据库增强失败：{e}")


@app.post("/api/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    """SSE 流式输出：分析进度 + 最终结果"""

    async def generator() -> AsyncGenerator[str, None]:
        yield _sse({"type": "progress", "step": 1, "message": "正在整理报表结构信息..."})
        await asyncio.sleep(0.1)
        yield _sse({"type": "progress", "step": 2, "message": "AI 正在深度分析业务逻辑，预计 15-40 秒..."})

        try:
            result = await asyncio.to_thread(analyze_report, req.parsed)
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})
            return

        if result.get("_parse_error"):
            yield _sse({"type": "error", "message": result["_parse_error"]})
        else:
            yield _sse({"type": "done", "data": result})

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """SSE 流式输出 Q&A 回答 token"""
    import json as _json

    async def generator() -> AsyncGenerator[str, None]:
        client = get_client()
        model = _get_model()
        slim = _slim_for_llm(req.parsed)

        messages = [
            {
                "role": "system",
                "content": "你是 FineReport 报表专家，根据报表解析数据和分析结论回答问题，重点说明交互链路、公式含义和业务逻辑。",
            }
        ]
        # 加入历史（最近 6 条）
        for msg in req.history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        context = (
            f"报表解析数据：\n{_json.dumps(slim, ensure_ascii=False)}\n\n"
            f"已有分析结论：\n{_json.dumps(req.analysis, ensure_ascii=False)}"
        )
        messages.append({"role": "user", "content": f"{context}\n\n问题：{req.question}"})

        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield _sse({"type": "token", "text": delta.content})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})
        finally:
            yield _sse({"type": "done"})

    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/export/markdown", response_class=PlainTextResponse)
async def export_markdown(req: ExportRequest):
    md = await asyncio.to_thread(generate_handover_doc, req.parsed, req.analysis)
    return PlainTextResponse(md, media_type="text/markdown; charset=utf-8")


@app.post("/api/export/html", response_class=HTMLResponse)
async def export_html(req: ExportRequest):
    html = await asyncio.to_thread(generate_handover_html, req.parsed, req.analysis)
    return HTMLResponse(html)


@app.post("/api/lineage")
async def lineage_endpoint(req: AnalyzeRequest):
    result = await asyncio.to_thread(build_lineage, req.parsed)
    return result


@app.post("/api/score")
async def score_endpoint(req: ScoreRequest):
    return await asyncio.to_thread(score_report, req.parsed, req.analysis, req.lineage)


@app.post("/api/validate/formulas")
async def validate_formulas_endpoint(req: FormulaValidationRequest):
    return await asyncio.to_thread(validate_formulas, req.parsed)


@app.post("/api/change-impact")
async def change_impact_endpoint(req: ChangeImpactRequest):
    if not req.change_request.strip():
        raise HTTPException(400, "变更描述不能为空")
    return await asyncio.to_thread(
        analyze_change_impact,
        req.parsed,
        req.analysis,
        req.change_request,
        req.lineage,
    )


@app.get("/api/llm/config")
async def llm_config_endpoint():
    api_key = os.environ.get("SILICONFLOW_API_KEY", "")
    base_url = os.environ.get("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model = _get_model()
    return {
        "configured": bool(api_key.strip()),
        "provider": "siliconflow",
        "base_url": base_url,
        "model": model,
        "api_key_hint": f"***{api_key[-4:]}" if api_key else "",
    }


@app.post("/api/llm/test")
async def llm_test_endpoint(req: LlmTestRequest):
    if not os.environ.get("SILICONFLOW_API_KEY", "").strip():
        raise HTTPException(400, "SILICONFLOW_API_KEY 未配置")

    def _test_call() -> dict:
        client = get_client()
        model = _get_model()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个用于验证 API 配置的助手。"},
                {"role": "user", "content": req.prompt},
            ],
            max_tokens=64,
            temperature=0,
        )
        text = completion.choices[0].message.content or ""
        return {"ok": True, "model": model, "message": text.strip()}

    try:
        return await asyncio.to_thread(_test_call)
    except Exception as e:
        raise HTTPException(502, f"LLM 测试失败：{e}")


# ── 生产模式：serve React build ───────────────────────────────────────────────
_web_dist = ROOT / "web" / "dist"
if _web_dist.exists():
    app.mount("/", StaticFiles(directory=str(_web_dist), html=True), name="static")
