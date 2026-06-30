# Codex Subagent 协作架构

## 目标

让 FR-Agent 的开发、测试、Bug 修复、Review、文档交接都能由 Codex subagent 分工协作，同时由主 Agent 保持最终决策、集成和长期文档一致。

本项目从 P1 起默认启用 subagent 协作；P0 后续收尾任务也可按本规则启用。

## 基本原则

- 主 Agent 负责用户沟通、任务拆解、最终集成和最终交付。
- Subagent 负责边界清楚、可并行、可验证的专项任务。
- 每个 subagent 必须有明确 ownership，不能和其他 agent 同时修改同一文件。
- Subagent 不能擅自扩大 Sprint 范围。
- Subagent 输出必须包含证据、风险和建议下一步。
- 主 Agent 必须审查 subagent 结果后再合入或改写文档。

## 角色

| Agent | 职责 | 不负责 |
| --- | --- | --- |
| 主 Agent | 任务拆解、最终决策、整合、交付 | 长时间并行检索 |
| Product Subagent | PRD、用户旅程、P0/P1/P2、验收口径 | 技术实现细节 |
| Parser Subagent | `parser/`、CPT 样例解析、字段提取风险 | UI 和 LLM 文案 |
| DB Subagent | `agent/db_connector.py`、FR 连接、数据库字段元数据 | 前端交互 |
| API Subagent | `api/main.py`、`web/src/api.ts`、API contract、SSE、错误处理 | 产品优先级 |
| UI Subagent | `web/src/` 页面、状态机、上传/导出体验 | Parser 规则 |
| LLM Subagent | `agent/llm_analyzer.py`、分析 schema、prompt、降级 | 数据库连接实现 |
| Export Subagent | `agent/doc_generator.py`、`agent/html_generator.py`、导出文档质量 | React 状态 |
| Test Subagent | Parser 样例、API smoke、前端 build/lint、评分记录 | 直接改产品范围 |
| Bugfix Subagent | 单一缺陷定位和最小修复 | 顺手重构 |
| Review Subagent | 风险、漏测、回归、文档不一致 | 直接扩大重构 |
| Context Steward | Handoff、需求池、devlog、上下文压缩 | 产品决策 |

## 标准协作流程

```text
用户目标
-> Product Agent 定义范围
-> 主 Agent 写 Task Brief
-> 主 Agent 判断哪些任务需要 subagent
-> 专项 Subagent 并行执行或分析
-> 主 Agent 审查和集成
-> Test Subagent / Review Subagent 验证
-> Context Steward 更新 Handoff
```

## 触发规则

必须启用 subagent 的场景：

- 同一任务涉及两个以上独立模块，例如 Parser + UI、API + Web、DB + LLM。
- Bug 修复后需要独立回归审查。
- 需要同时验证 Parser、API、前端、评分记录。
- 涉及真实样例 CPT 或真实数据库验收。
- 涉及 PRD / SOP / Handoff 的长期规则更新。

可以不启用 subagent 的场景：

- 单文件文案修正。
- 明确、低风险、无需并行验证的小改动。
- 用户明确要求主 Agent 直接处理。

## Ownership 规则

| 任务类型 | 默认 ownership |
| --- | --- |
| Parser 修复 | Parser Subagent：`parser/`；Test Subagent：样例验证文档 |
| DB 增强 | DB Subagent：`agent/db_connector.py`、DB 验证文档 |
| API 修改 | API Subagent：`api/main.py`、`web/src/api.ts`、`docs/architecture/API_CONTRACT.md` |
| UI 修改 | UI Subagent：`web/src/` 指定组件 |
| LLM 分析 | LLM Subagent：`agent/llm_analyzer.py`、schema 文档 |
| 导出文档 | Export Subagent：`agent/doc_generator.py`、`agent/html_generator.py` |
| Bug 修复 | Bugfix Subagent：单一缺陷涉及的最小文件集合 |
| 回归验证 | Test Subagent：验证命令、评分记录、测试报告 |
| 交接同步 | Context Steward：`docs/project/HANDOFF.md`、`docs/product/REQUIREMENTS_BACKLOG.md` |

## 冲突控制

- 每个 subagent brief 必须写明允许修改的文件。
- 不同 subagent 不允许同时修改同一文件。
- 如果必须修改同一文件，由主 Agent 统一整合。
- Subagent 看到他人改动时不能 revert，只能顺应已有改动。
- Subagent 完成后必须列出改动文件和验证命令。

## 开发 / 测试 / Bug 修复协作

### 开发任务

```text
主 Agent 写 Task Brief
-> Parser/API/UI/DB/LLM/Export Subagent 分模块实现
-> Test Subagent 跑验证
-> Review Subagent 查风险
-> Context Steward 更新 Handoff
```

### 测试任务

```text
主 Agent 指定样例和评分标准
-> Test Subagent 跑 Parser/API/Web/LLM 可用验证
-> Test Subagent 填写 SCORING_REVIEW
-> Review Subagent 审查扣分是否合理
-> 主 Agent 生成下一轮 P1 任务
```

### Bug 修复任务

```text
主 Agent 定义缺陷和复现路径
-> Bugfix Subagent 做最小修复
-> Test Subagent 跑回归
-> Review Subagent 检查是否扩大范围
-> Context Steward 更新需求池和 Handoff
```

## Subagent 交付格式

每个 subagent 最终回复必须包含：

- 结论
- 修改文件或只读文件
- 验证命令与结果
- 风险
- 建议下一步

## 当前实际使用记录

2026-06-30 已开始实际启用 Codex subagent：

- Development Subagent：审查开发分工机制。
- Test/Validation Subagent：审查测试与评分机制。
- Bugfix/Review Subagent：审查缺陷修复和 Review 机制。

主 Agent 负责整合这些建议并落入 SOP。

## P0 收口后的启用规则

P0 收口阶段只轻量启用 Review/Test 类 subagent，用于检查文档闭环、评分记录和验收风险，不再开启并行功能开发。

从 P1 起，subagent 协作进入默认工作方式：

- 真实 MySQL + FineReport DBTableData CPT 验证：启用 DB Subagent、Test Subagent、Review Subagent。
- 跨 Parser / API / UI / DB / LLM / Export 任意两个以上模块的任务：必须拆分 ownership 并启用对应 subagent。
- Bug 修复：Bugfix Subagent 做最小修复，Test Subagent 跑回归，Review Subagent 检查范围。
- 自动评分 MVP：Product / Test / LLM / API 或 UI Subagent 按模块拆分。
- 文档长期维护：Context Steward 负责同步 Handoff、Backlog、评分记录和 API contract。
