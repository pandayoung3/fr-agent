# 文档清理记录

更新日期：2026-06-30

## 本轮处理原则

- 不修改当前已开发功能代码。
- 删除明显无意义的模板文档。
- 保留有历史证据价值的 devlog。
- 将长期规则沉淀到 `docs/`。
- README 和操作文档统一到 React + FastAPI 主线。

## 删除

| 文件 | 原因 |
| --- | --- |
| `web/README.md` | Vite 默认模板文档，与 FR-Agent 业务和当前 SOP 无关 |

## 保留

| 文件 / 目录 | 原因 |
| --- | --- |
| `devlog/` | 保存 Phase 0-4 的历史验证和开发事实 |
| `README.md` | 改写为项目入口 |
| `操作文档.md` | 改写为 React + FastAPI v2 操作文档 |

## 新增

- `AGENTS.md`
- `docs/README.md`
- `docs/project/*`
- `docs/product/*`
- `docs/architecture/*`
- `docs/agents/*`
- `docs/templates/*`
