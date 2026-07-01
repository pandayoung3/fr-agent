# 需求池

## 状态说明

- `Done`：远端已有实现。
- `P0`：稳定化必须处理。
- `P1`：重要增强。
- `P2`：后续平台化或体验增强。
- `Discuss`：需要用户进一步确认。

## 列表

| ID | 需求 | 状态 | 说明 |
| --- | --- | --- | --- |
| REQ-001 | 上传并解析 `.cpt` | Done | `api/main.py` `/api/parse`，`parser/cpt_parser.py` |
| REQ-002 | 提取数据集、SQL、控件、单元格绑定 | Done | Parser 已实现 |
| REQ-003 | 提取公式、父子格、条件高亮、填报配置 | Done | Parser v3 / devlog 已记录 |
| REQ-004 | 数据库字段元数据增强 | Done | MySQL `information_schema` |
| REQ-005 | 数据血缘图 | Done | `agent/lineage_builder.py` |
| REQ-006 | LLM 语义分析 | Done | `agent/llm_analyzer.py` |
| REQ-007 | 报表问答 | Done | `/api/chat` |
| REQ-008 | Markdown / HTML 导出 | Done | `doc_generator.py` / `html_generator.py` |
| REQ-009 | 统一 README 与操作文档 | Done | 已统一到 React + FastAPI v2 主线 |
| REQ-010 | 补齐 FastAPI 运行依赖 | Done | `requirements.txt` 已补齐主线依赖 |
| REQ-011 | API contract 文档 | Done | 已建立 `docs/architecture/API_CONTRACT.md` |
| REQ-012 | 固定样例验收流程 | Done | 已建立 P0 验收流程和 closure 评分记录 |
| REQ-013 | Streamlit 下线方案 | Done | `ui/app.py` 已添加 deprecated 注释和页面警告；依赖暂保留为历史入口 |
| REQ-014 | 100 分交接可用性评分标准 | Done | P0 初版已定稿，先不自动化 |
| REQ-015 | Parser 单元测试 | Done | `tests/unit/` 已建立最小回归测试，统一由 `scripts/validate_p1.ps1` 执行 |
| REQ-016 | API smoke test | Done | `tests/api/test_api_smoke.py` 覆盖 LLM 配置、评分和公式校验接口 |
| REQ-017 | 前端 build / lint 固化 | Done | `scripts/validate_p1.ps1` 固化 `npm run lint` 与 `npm run build` |
| REQ-018 | 批量解析 CPT | Done | P2 MVP 已实现 `/api/batch/parse`、批量上传入口、资产摘要和打开单报表工作台 |
| REQ-019 | 评分系统 MVP 自动化实现 | Done | `agent/scoring_engine.py` + `/api/score` + 前端 P1 质量面板 |
| REQ-020 | MCP Server / 插件 | P2 | 平台嫁接方向 |
| REQ-021 | 报表差异对比 | P2 | 迁移/重构增强 |
| REQ-022 | Docker / 内网部署 | P2 | 团队使用增强 |
| REQ-023 | 修正填报报表类型识别 | Done | `writeback_config` 存在时优先判定为 `writeback` |
| REQ-024 | 修正中文数据集名编码异常 | Closed | UTF-8 文件验证显示 Parser 输出正常，早期异常来自终端管道编码 |
| REQ-025 | 增强 EmbeddedTableData 控件链路 | Done | lineage 已支持控件选项数据集和 Embedded 展示字段链路 |
| REQ-026 | 完成样例 CPT 前端全链路评分 | Done | `习题 8.cpt` 已完成上传、分析、问答、导出人工评分 |
| REQ-027 | P0 收口基线评分 | Done | `习题 8.cpt` 全链路评分 `86 / 100`，见 `docs/project/SCORING_REVIEW_P0_CLOSURE.md` |
| REQ-028 | `.env` UTF-8 BOM 兼容 | Done | `api/main.py` 使用 `utf-8-sig` 读取并剥离隐藏 BOM |
| REQ-029 | 导出文档模型名一致性 | Done | Markdown / HTML 导出读取运行时 `LLM_MODEL` |
| REQ-030 | 真实 MySQL + FineReport DBTableData CPT 验证 | P2-Ready | 已提供 demo schema 与验证脚本；仍需用户在 FineReport 制作真实 DBTableData CPT 后跑验收 |
| REQ-031 | 公式坐标与字段位置校验增强 | Done | `agent/formula_validator.py` + `/api/validate/formulas`，覆盖引用坐标和风险函数 |
| REQ-032 | 多轮问答验收用例 | P2-Ready | 已提供 `prepare_chat_context.py` 和 `run_chat_acceptance.py`；需本地后端、LLM Key 和样例 CPT 执行验收 |
| REQ-033 | 前端可视化报表理解工作台 | Done | `WorkbenchTab` 已上线，支持分层节点、关联高亮、节点详情和问答联动 |
| REQ-034 | Obsidian 式 CPT / 数据资产图谱 | Done | P2 MVP 已在批量解析结果中提供轻量资产关系视图；完整 Obsidian 式图谱留 P3 |
| REQ-035 | 多模型配置体验优化 | Done | 新增 `/api/llm/config`、`/api/llm/test` 和前端配置状态/测试入口 |
| REQ-036 | 分析历史和导出记录 | Done | 已实现本地分析历史和本地导出记录，均保存在浏览器 `localStorage` |
| REQ-037 | 变更定位与修改建议 | Done | 新增 `/api/change-impact` 和前端“变更建议”页，已补容错、API smoke 覆盖和 API Contract |

## 当前决策

- P0 确认：先做稳定化和文档 / 依赖 / 验收，不做新业务功能。
- Streamlit：已标记为历史 MVP / deprecated，并在旧入口加入页面警告；删除代码和依赖需单独确认。
- 固定验收样例：暂不提交 CPT 文件入仓，避免脱敏和业务数据风险；P0 通过本地样例路径与评分记录保留证据。
- P1 重心：前端 UI 从“导出文档为主”转为“可视化理解 CPT 为主”，导出成为辅助能力。
- P1.5 方向：先完成“变更定位与修改建议”，帮助维护人员判断需求变化应修改哪些数据集、SQL、控件、字段、单元格或公式；半自动修改 CPT / 设计器操作暂不进入本周期。
- P2 顺序：先同步 P1.5 基线，再完成批量 CPT 资产索引 MVP；真实 MySQL CPT 和多轮问答验收已具备脚本化入口，但最终证据依赖用户本地 FineReport CPT 和 LLM 环境。
