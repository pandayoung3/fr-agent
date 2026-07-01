# 项目进度

更新日期：2026-07-02

## 当前阶段

FR-Agent 已完成 MVP 到 React + FastAPI v2 的演进雏形。当前阶段应定义为：

```text
P1.5 报表维护工作台：在 P1 可视化理解工作台基础上，新增变更定位与修改建议，帮助用户从“理解报表”进入“判断应该改哪里”。
```

P1 计划内事项已完成。当前新增的 P1.5 事项聚焦变更影响分析，不进入半自动 FineReport 设计器操作。P1.5 已补齐后端容错、API smoke 覆盖和 API Contract。真实 MySQL + FineReport DBTableData CPT、批量 CPT、多轮问答系统验收继续后移至 P2 或更后。

## 仓库状态

| 项目 | 当前状态 |
| --- | --- |
| GitHub remote | 已配置 `origin` |
| 当前分支 | `main` |
| 远端跟踪 | `origin/main` |
| 最新提交 | `f20326d feat: 同步完整项目状态 —— UI重设计、API层、Web前端、DB接入` |
| 备份分支 | `codex/prd-sop-docs` 保存上一轮 PRD/SOP 草稿 |
| 工作区 | 当前 P1 收口改动待提交 |

## 已实现能力

| 模块 | 现状 |
| --- | --- |
| CPT 解析 | 已实现数据集、SQL、控件、单元格、公式、格式、父子格、条件高亮、填报配置 |
| 数据库增强 | 已支持读取 FR WEB-INF 连接配置，并查询 MySQL `information_schema` |
| 数据血缘 | 已实现控件、SQL 参数、数据集、展示字段链路生成 |
| LLM 分析 | 已输出用途、交互链路、字段语义、公式解释、指标字典、复现步骤和风险点 |
| 问答 | 已基于 parsed + analysis 支持自然语言追问 |
| 变更定位 | 已支持输入业务变更描述，输出受影响的数据集、SQL、控件、字段、单元格、公式、修改步骤和复核点 |
| 文档导出 | 已支持 Markdown 和 HTML |
| React 前端 | 已有上传、分析、工作台、变更建议、深度分析、质量面板、导出、问答、问答联动、本地分析历史和导出记录 |
| FastAPI 后端 | 已有 parse、fr-connections、enrich、analyze、chat、export、lineage、score、validate/formulas、change-impact、llm/config、llm/test 接口 |
| Streamlit | 旧 MVP UI，已加 deprecated 注释和页面警告；最终删除需用户确认 |

## 主要缺口

- 批量资产图谱留后续迭代。
- Streamlit 最终删除节奏仍需用户确认。
- 真实 MySQL + FineReport DBTableData CPT 验证已移入 P2 或更后。

## 下一步建议

1. 让用户试用 P1 工作台，确认 UI 信息密度、图文比例和质量面板是否符合预期。
2. 让用户试用“变更建议”页，确认修改建议是否足以辅助 FineReport 设计器内的人工定位。
3. 请用户确认 Streamlit 是删除还是继续 deprecated。
4. P2 再准备真实 MySQL + FineReport DBTableData CPT、批量 CPT 和多轮问答系统验收。
# P0 收口状态（2026-06-30）

P0 已完成收口，当前基线为：

```text
React + FastAPI 本地工具主线：可启动、可验证、可交接。
```

收口证据：

- P0 Closure 评分记录：`docs/project/SCORING_REVIEW_P0_CLOSURE.md`。
- 样例：`习题 8.cpt`。
- 评分：`86 / 100`，B 级。
- 覆盖：上传、解析、AI 分析、问答、血缘、Markdown / HTML 导出预览。
- 未覆盖：真实 MySQL + FineReport DBTableData CPT，该项进入 P2 或更后。

P1 默认引入 subagent 协作。当前已完成前端可视化报表理解工作台、Parser / API / 前端质量门禁、公式校验、LLM 配置检测、评分系统 MVP、问答联动、分析历史和导出记录。

P2 或更后再推进真实 DB 验证、批量 CPT 解析、多轮问答系统验收和 Obsidian 式 CPT / 数据资产图谱。
