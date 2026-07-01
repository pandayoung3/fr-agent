# P2 增量交接记录

更新日期：2026-07-02

## 范围决策

P2 按顺序推进：

1. 同步 P1.5 远端基线。
2. 完成批量 CPT 解析 MVP。
3. 准备真实 MySQL + FineReport DBTableData CPT 验收工具。
4. 准备多轮问答验收工具。
5. 将完整 Obsidian 式跨报表图谱、批量 AI 分析、批量导出和持久知识库留到后续阶段。

## 已完成

- 已将 P1.5 commit `3574248 feat: complete P1.5 maintenance workbench baseline` 推送到 `origin/main`。
- 新增 `POST /api/batch/parse`，支持多 `.cpt` 文件上传、逐文件解析、部分失败容错和资产摘要。
- 前端上传区支持多文件选择；单文件保持原工作台流程，多文件进入批量资产索引。
- 新增批量资产面板：显示成功/失败、DB 报表、填报报表、数据集、控件、公式、DB 连接。
- 批量面板支持从成功项打开单报表工作台，继续 AI 分析、血缘、变更建议和导出。
- 新增轻量资产关系视图，作为 Obsidian 式图谱的 P2 MVP 雏形。
- 新增 `scripts/mysql_demo_schema.sql`，用于本地 MySQL 验证库初始化。
- 新增 `scripts/validate_real_db_sample.py`，用于真实 DBTableData CPT 结构验收。
- 新增 `scripts/run_chat_acceptance.py`，用于多轮问答验收。
- 更新 API Contract、需求池、项目状态和真实 DB 验证计划。

## 待人工完成

- 用户需要在 FineReport 设计器中配置 MySQL JDBC 连接。
- 用户需要基于 `fr_agent_demo` 制作查询型 DBTableData CPT 和填报型 DBTableData CPT。
- 用户需要导出脱敏 CPT 后执行 `scripts/validate_real_db_sample.py`。
- 多轮问答验收需要本地后端、LLM Key、parsed JSON 和 analysis JSON 后执行 `scripts/run_chat_acceptance.py`。

## 验收命令

当前自动化验证应至少运行：

```powershell
python -m compileall -q api agent parser scripts
python -m unittest discover -s tests -t . -p "test_*.py" -v
cd web
npm run lint
npm run build
```

真实 DB CPT 准备完成后运行：

```powershell
python scripts/validate_real_db_sample.py "D:\path\to\report.cpt" --fr-webinf-dir "D:\FineReport\webapps\webroot\WEB-INF" --passwords ".\local_passwords.json"
```

多轮问答样例准备完成后运行：

```powershell
python scripts/run_chat_acceptance.py --parsed-json ".\parsed.json" --analysis-json ".\analysis.json"
```

## 风险与边界

- 批量解析 MVP 不默认调用 LLM，避免批量场景 token 和响应时间失控。
- 批量 DB enrich、批量导出、跨报表持久资产库仍未实现。
- 真实 DB 验证脚本能证明解析和结构增强能力，但不能代替 FineReport 设计器中的人工报表制作。
- 半自动修改 CPT / 操控 FineReport 设计器仍不进入 P2。
