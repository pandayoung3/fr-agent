# Streamlit P1 清理记录

更新日期：2026-07-01

## 结论

Streamlit 入口不再作为产品主线，也不再接受新功能。P1 已完成 deprecated 入口清理，但不删除历史代码和依赖。

## 已完成

- `ui/app.py` 已加入 deprecated 注释。
- Streamlit 页面启动后会显示归档警告，并提示使用 React + FastAPI 主线。
- README 和操作文档继续以 React + FastAPI 为推荐入口。
- `requirements.txt` 中的 `streamlit` 依赖暂时保留，避免历史入口无法启动。

## 后续删除条件

最终删除 `ui/` 和 `streamlit` 依赖前，需要用户单独确认，并在删除任务中重新跑完整 P1 验证。
