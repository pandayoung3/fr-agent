"""
v4 生成测试脚本
对制单报表运行完整流程（解析 → 血缘图 → LLM分析 → 生成文档），保存 v4 交接文档
用法：cd fr-agent && python scripts/gen_v4.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载 .env
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from parser.cpt_parser import parse_cpt, summarize_to_dict
from agent.lineage_builder import build_lineage
from agent.llm_analyzer import analyze_report
from agent.doc_generator import generate_handover_doc

CPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..",
    "cpt示例", "2-C-制单-1的副本.cpt"
)

print("=" * 60)
print("Step 1: 解析 CPT 文件")
summary = parse_cpt(CPT_PATH)
parsed = summarize_to_dict(summary)
print(f"  数据集: {len(parsed['datasets'])} 个")
print(f"  控件: {len(parsed['widgets'])} 个")
print(f"  绑定单元格: {len([c for c in parsed['cell_bindings'] if c.get('dataset')])} 个")
print(f"  公式单元格: {len(parsed.get('formula_cells', []))} 个")

print("\nStep 2: 构建数据血缘图（无需 LLM）")
lineage = build_lineage(parsed)
print(f"  SQL驱动控件: {lineage['sql_driving_widget_names']}")
print(f"  未接SQL控件: {len(lineage['unmatched_widget_names'])} 个")
print("\n--- Graphviz DOT 预览（前10行）---")
for line in lineage["dot"].splitlines()[:10]:
    print(line)
print("...")

print("\nStep 3: LLM 语义分析（包含 indicator_dict）")
analysis = analyze_report(parsed)
tokens = analysis.get("_tokens_used", "?")
print(f"  Token 消耗: {tokens}")
ind_dict = analysis.get("indicator_dict", [])
print(f"  指标字典条数: {len(ind_dict)}")
if ind_dict:
    print("\n--- 指标字典预览 ---")
    for ind in ind_dict[:5]:
        print(f"  [{ind.get('type','')}] {ind.get('indicator_name','')} "
              f"({ind.get('source_field','')}) - {ind.get('description','')[:40]}")
    if len(ind_dict) > 5:
        print(f"  ... 另有 {len(ind_dict)-5} 条")

print("\nStep 4: 生成交接文档 v4")
doc = generate_handover_doc(parsed, analysis)
out_path = os.path.join(os.path.dirname(__file__), "..", "output", "制单报表_交接文档v4.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(doc)
print(f"  已保存至: {os.path.abspath(out_path)}")
print(f"  文档长度: {len(doc)} 字符")
print("=" * 60)
print("✅ 完成")
