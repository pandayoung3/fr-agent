# Streamlit 下线策略

## 当前结论

`ui/app.py` 是历史 MVP 入口。React + FastAPI v2 已成为主线，后续新增能力不再进入 Streamlit。

## 为什么不立即删除

- 旧 UI 可能仍可作为历史行为参考。
- P0 当前重点是主线稳定，不扩大代码删除风险。
- 是否存在用户仍依赖 Streamlit 尚未确认。

## P0 处理方式

- README 和 `操作文档.md` 不再把 Streamlit 作为推荐入口。
- `requirements.txt` 暂时保留 `streamlit`，并标注为 historical MVP UI。
- 所有新任务默认只改 React + FastAPI 主线。
- Handoff 中记录 Streamlit 状态，等待用户确认删除节奏。

## 删除条件

满足以下条件后，可以进入删除任务：

- React + FastAPI 完成 P0 验收。
- 用户确认不需要继续保留 Streamlit 入口。
- Streamlit 中不存在 React 主线尚未覆盖的关键能力。
- 删除任务有独立 Task Brief 和回归验证。

## 删除范围候选

- `ui/app.py`
- `ui/streamlit_compact.css`
- `ui/__init__.py`
- `requirements.txt` 中的 `streamlit`
- README、操作文档和 Handoff 中的历史说明

## 保留替代

如果不立即删除，可在 P0 后标记为 deprecated：

- 文件顶部增加 deprecated 注释。
- README 明确不推荐使用。
- 不接受新功能进入 `ui/`。
