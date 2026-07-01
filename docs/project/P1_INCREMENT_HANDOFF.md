# P1 增量交接记录

更新日期：2026-06-30

## 范围决策

本轮按用户最新边界推进：

- 真实 MySQL + FineReport DBTableData CPT：放入 P2 或更后。
- 批量 CPT 解析：放入 P2。
- 多轮问答系统验收：放入 P2。
- P1 主线：单 CPT 的前端可视化理解工作台、质量面板、测试门禁、公式校验、评分 MVP、LLM 配置验证和本地分析历史。

## 已完成

- 默认结果页改为“报表理解工作台”：`web/src/components/tabs/WorkbenchTab.tsx`。
- 导出从主功能降级为辅助入口，保留在工作台跳转与 Export tab。
- 新增 P1 质量面板：`web/src/components/P1QualityPanel.tsx`。
- 新增规则评分引擎和接口：`agent/scoring_engine.py`、`POST /api/score`。
- 新增公式校验引擎和接口：`agent/formula_validator.py`、`POST /api/validate/formulas`。
- 新增 LLM 配置读取和手动测试接口：`GET /api/llm/config`、`POST /api/llm/test`。
- LLM 配置接口只返回是否配置、模型、base URL 和 key 后 4 位提示，不返回完整 API Key。
- 新增浏览器本地分析历史与导出记录：`web/src/historyStore.ts`。
- 工作台支持分层节点、关联链路高亮、节点详情和一键带上下文进入问答。
- 导出页支持 Markdown / HTML 预览与下载记录，记录仅保存在浏览器本地。
- Streamlit 旧入口已加入 deprecated 注释和页面警告，不再作为主线入口。
- 新增 P1 一键验证脚本：`scripts/validate_p1.ps1`。
- 新增 `unittest` 测试：API smoke、评分、公式校验、血缘构建。

## 验证结果

已通过：

```powershell
.\scripts\validate_p1.ps1
```

覆盖：

- `git diff --check`
- `python -m compileall -q api agent parser scripts`
- `python -m unittest discover -s tests -t . -p "test_*.py" -v`
- `npm run lint`
- `npm run build`

测试结果：5 个测试通过。

备注：`npm run build` 仍提示部分 chunks 超过 500 kB，这是 Vite 构建优化提醒，不阻塞当前 P1。

## P1 收口结论

P1 计划内事项已完成。后续不再扩大 P1 范围，下一步应由用户试用工作台并反馈 UI / UX，再决定是否进入 P2。

P2 或更后：
- 真实 MySQL + FineReport DBTableData CPT 验证。
- 批量 CPT 解析。
- 多轮问答系统验收。
- Obsidian 式 CPT / 数据资产图谱。
- Streamlit 代码和依赖的最终删除，需用户单独确认。
