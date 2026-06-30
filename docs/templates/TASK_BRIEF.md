# Task Brief

## 用户故事

作为 [用户类型]，我希望 [能力]，以便 [结果]。

## 范围

包含：

- ...

不包含：

- ...

## 影响面

- Parser：
- API：
- Web：
- LLM：
- DB：
- Export：
- 文档：

## 参与 Subagent

| Subagent | 角色 | Ownership | 输出 |
| --- | --- | --- | --- |
| ... | Parser / API / UI / DB / LLM / Export / Test / Bugfix / Review / Context | 可修改文件或只读范围 | 代码 / 测试报告 / Review / Handoff |

## 冲突风险

- 可能冲突文件：
- 需要主 Agent 统一整合的文件：
- 不允许 subagent 修改的文件：

## 缺陷类任务字段

现象：

预期：

实际：

复现步骤：

影响范围：

严重级别：P0 / P1 / P2 / Discuss

## 验收标准

- [ ] 正常路径可用。
- [ ] 错误路径有反馈。
- [ ] 验证命令已运行或记录无法运行原因。
- [ ] Subagent 输出已审查。
- [ ] 文档和 Handoff 已同步。

## 开放问题

- TODO(CONFIRM): ...
