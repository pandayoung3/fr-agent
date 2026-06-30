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
| REQ-013 | Streamlit 下线方案 | Done | P0 先标记 deprecated，不直接删除；P1 再清理 |
| REQ-014 | 100 分交接可用性评分标准 | Done | P0 初版已定稿，先不自动化 |
| REQ-015 | Parser 单元测试 | P1 | 保护解析能力 |
| REQ-016 | API smoke test | P1 | 保护后端主线 |
| REQ-017 | 前端 build / lint 固化 | P1 | 保护 React 主线 |
| REQ-018 | 批量解析 CPT | P1 | 来自 devlog 后续方向 |
| REQ-019 | 评分系统 MVP 自动化实现 | P1 | 基于 P0 初版评分标准实现 |
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
| REQ-030 | 真实 MySQL + FineReport DBTableData CPT 验证 | P1 | 用户确认不阻塞 P0；用于证明客户真实数据库连接场景 |
| REQ-031 | 公式坐标与字段位置校验增强 | P1 | 当前能提示风险，但需更强自动校验 |
| REQ-032 | 多轮问答验收用例 | P1 | 当前只验证单轮问题 |

## 当前决策

- P0 确认：先做稳定化和文档 / 依赖 / 验收，不做新业务功能。
- Streamlit：P0 仅标记为历史 MVP / deprecated，不直接删除；删除或迁移进入 P1 后续清理。
- 固定验收样例：暂不提交 CPT 文件入仓，避免脱敏和业务数据风险；P0 通过本地样例路径与评分记录保留证据。
