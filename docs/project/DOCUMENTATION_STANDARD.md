# 文档规范

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `docs/project/` | 项目状态、SOP、Sprint、Handoff、验证记录、下线策略 |
| `docs/product/` | PRD、需求池、评分系统、产品范围 |
| `docs/architecture/` | 技术架构、API contract、数据流 |
| `docs/agents/` | 多 Agent 写作和开发分工 |
| `docs/templates/` | Task Brief、Agent Brief、Review、评分记录模板 |
| `devlog/` | 历史阶段开发记录，保留事实证据 |

## 命名规则

- 文件名使用大写英文和下划线。
- 需要用户确认的内容写 `TODO(CONFIRM): ...`。
- 风险写 `RISK: ...`。
- 后续动作写 `NEXT: ...`。

## 文档维护规则

- README 面向首次使用者。
- `操作文档.md` 面向实际操作者。
- `docs/product/PRD.md` 是产品范围真相源。
- `docs/project/HANDOFF.md` 是当前交接真相源。
- `docs/project/P0_VALIDATION.md` 是 P0 验收流程真相源。
- 代码接口变化必须同步 `docs/architecture/API_CONTRACT.md`。
- LLM 输出 schema 变化必须同步 Web types 和导出文档说明。

## 审查清单

- [ ] 文档是否有明确读者。
- [ ] 是否与 React + FastAPI 主线一致。
- [ ] 是否误把 Streamlit 当主线。
- [ ] 是否存在未标注假设。
- [ ] 链接和命令是否可执行。
- [ ] Handoff 是否同步。
