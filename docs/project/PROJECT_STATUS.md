# 项目进度

更新日期：2026-07-02

## 当前阶段

FR-Agent 已完成 MVP 到 React + FastAPI v2 的演进雏形。当前阶段应定义为：

```text
P2 真实场景验证与批量资产索引：在 P1.5 报表维护工作台基础上，完成批量 CPT 解析 MVP，并准备真实 MySQL + FineReport DBTableData 验收和多轮问答验收。
```

P1.5 已推送远端。P2 已完成批量 CPT 解析 MVP 与轻量资产关系视图；真实 MySQL + FineReport DBTableData CPT 验证和多轮问答验收已补齐脚本化入口，但最终通过仍依赖用户在 FineReport 中制作真实 DBTableData CPT、配置本地 MySQL 和 LLM Key 后执行。

## 仓库状态

| 项目 | 当前状态 |
| --- | --- |
| GitHub remote | 已配置 `origin` |
| 当前分支 | `main` |
| 远端跟踪 | `origin/main` |
| 最新提交 | `3574248 feat: complete P1.5 maintenance workbench baseline` |
| 备份分支 | `codex/prd-sop-docs` 保存上一轮 PRD/SOP 草稿 |
| 工作区 | 当前 P2 批量解析与验收脚本开发中 |

## 已实现能力

| 模块 | 现状 |
| --- | --- |
| CPT 解析 | 已实现数据集、SQL、控件、单元格、公式、格式、父子格、条件高亮、填报配置 |
| 数据库增强 | 已支持读取 FR WEB-INF 连接配置，并查询 MySQL `information_schema` |
| 数据血缘 | 已实现控件、SQL 参数、数据集、展示字段链路生成 |
| LLM 分析 | 已输出用途、交互链路、字段语义、公式解释、指标字典、复现步骤和风险点 |
| 问答 | 已基于 parsed + analysis 支持自然语言追问 |
| 变更定位 | 已支持输入业务变更描述，输出受影响的数据集、SQL、控件、字段、单元格、公式、修改步骤和复核点 |
| 批量解析 | 已支持多 CPT 上传、逐文件解析、部分失败容错、资产摘要和打开单报表工作台 |
| 资产图谱 | 已提供批量结果内的轻量关系视图，覆盖报表、数据集、DB 连接、控件和公式 |
| 文档导出 | 已支持 Markdown 和 HTML |
| React 前端 | 已有上传、分析、工作台、变更建议、深度分析、质量面板、导出、问答、问答联动、本地分析历史和导出记录 |
| FastAPI 后端 | 已有 parse、fr-connections、enrich、analyze、chat、export、lineage、score、validate/formulas、change-impact、llm/config、llm/test 接口 |
| Streamlit | 旧 MVP UI，已加 deprecated 注释和页面警告；最终删除需用户确认 |

## 主要缺口

- 完整 Obsidian 式跨报表图谱留 P3。
- Streamlit 最终删除节奏仍需用户确认。
- 真实 MySQL + FineReport DBTableData CPT 需要用户在 FineReport 设计器中制作查询型和填报型样例后执行脚本验收。
- 多轮问答验收需要本地 LLM Key 和已生成的 parsed/analysis JSON 后执行脚本验收。

## 下一步建议

1. 用户制作真实 MySQL + FineReport DBTableData 查询型和填报型 CPT。
2. 使用 `scripts/validate_real_db_sample.py` 跑真实 DB 样例验收。
3. 使用 `scripts/run_chat_acceptance.py` 跑多轮问答验收。
4. 根据真实样例结果优化 DBTableData 解析、字段增强、血缘和变更建议质量。
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
