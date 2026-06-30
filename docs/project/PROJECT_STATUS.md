# 项目进度

更新日期：2026-06-30

## 当前阶段

FR-Agent 已完成 MVP 到 React + FastAPI v2 的演进雏形。当前阶段应定义为：

```text
P0 React + FastAPI 主线稳定化：统一文档、依赖、API contract、验收流程和后续评分标准讨论
```

本轮不做新功能开发，先完成项目准备和需求定稿。

## 仓库状态

| 项目 | 当前状态 |
| --- | --- |
| GitHub remote | 已配置 `origin` |
| 当前分支 | `main` |
| 远端跟踪 | `origin/main` |
| 最新提交 | `f20326d feat: 同步完整项目状态 —— UI重设计、API层、Web前端、DB接入` |
| 备份分支 | `codex/prd-sop-docs` 保存上一轮 PRD/SOP 草稿 |
| 工作区 | 当前 P0 文档与依赖基线改动中 |

## 已实现能力

| 模块 | 现状 |
| --- | --- |
| CPT 解析 | 已实现数据集、SQL、控件、单元格、公式、格式、父子格、条件高亮、填报配置 |
| 数据库增强 | 已支持读取 FR WEB-INF 连接配置，并查询 MySQL `information_schema` |
| 数据血缘 | 已实现控件、SQL 参数、数据集、展示字段链路生成 |
| LLM 分析 | 已输出用途、交互链路、字段语义、公式解释、指标字典、复现步骤和风险点 |
| 问答 | 已基于 parsed + analysis 支持自然语言追问 |
| 文档导出 | 已支持 Markdown 和 HTML |
| React 前端 | 已有上传、分析、结果 Tab、导出和问答页面 |
| FastAPI 后端 | 已有 parse、fr-connections、enrich、analyze、chat、export、lineage 接口 |
| Streamlit | 旧 MVP UI，后续计划下线或归档 |

## 主要缺口

- 固定样例 CPT 尚未确认是否可以入仓。
- Streamlit 下线节奏仍需用户确认。
- 尚未运行完整本地安装、构建和启动验收。
- 评分标准需要在 P0 最后一步与用户讨论定稿。

## 下一步建议

1. 运行 P0 可用验证命令，记录依赖或环境阻断。
2. 请用户确认 Streamlit 是删除还是先 deprecated。
3. 在 P0 最后一步讨论 100 分交接可用性评分标准。
4. 用评分标准初步检验当前产品效果，再决定 P1 开发内容。
