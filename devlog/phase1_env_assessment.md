# Phase 1 前置评估：设备配置与依赖风险

> 日期：2026-05-21 | 类型：环境评估 | 状态：✅ 完成

---

## 一、当前设备配置

| 项目 | 规格 |
|------|------|
| 机型 | MacBook Pro |
| 芯片 | Apple M1 Pro |
| 物理内存 | 16 GB（统一内存，CPU/GPU 共享） |
| 磁盘总量 | 460 GB |
| 磁盘可用 | **约 15 GB** |
| Python 版本 | 3.9.6（系统自带） |
| 已安装关键库 | lxml 6.0.4（其余均未安装）|

---

## 二、当前内存压力状态（重要警示）

| 内存指标 | 数值 | 评级 |
|---------|------|------|
| 物理空闲内存 | ~80 MB | 🔴 极低 |
| 活跃使用 | 0.8 GB | — |
| 非活跃（可回收）| 0.8 GB | — |
| Wired（不可回收）| 0.5 GB | — |
| **Swap 已用** | **7.75 GB / 8 GB（97%）** | 🔴 临界满载 |

**结论**：设备当前处于重度内存压力下，Swap 几近耗尽。M1 的 Swap 基于高速 NVMe SSD，性能优于传统 HDD Swap，但持续满载状态下运行内存密集型进程仍存在明显风险（卡顿、进程 OOM 被系统杀掉）。

> **注意**：这是当前时刻快照。实际可用内存受后台应用影响，关闭其他应用后压力会降低。建议在运行 Agent 前关闭不必要的应用（浏览器标签页是最大内存消耗源）。

---

## 三、Phase 1 所需依赖评估

### 3.1 LLM 接入层（调整：使用 DeepSeek API）

DeepSeek API 采用 **OpenAI 兼容接口**，无需安装专用 SDK，直接使用 `openai` 包即可调用。

| 包 | 用途 | 安装体积 | 运行内存 | 备注 |
|----|------|---------|---------|------|
| `openai` | DeepSeek API 客户端 | ~15 MB（含依赖）| <50 MB | DeepSeek 使用 `base_url` 参数指向其 API |

相比原计划的 `anthropic` SDK，`openai` 依赖树更轻量，且 DeepSeek API 成本显著更低，适合 MVP 阶段高频测试。

### 3.2 解析层（已基本就绪）

| 包 | 用途 | 安装体积 | 运行内存 | 状态 |
|----|------|---------|---------|------|
| `lxml` | XML 解析增强 | 已安装 8 MB | <30 MB | ✅ 已就绪 |
| `sqlparse` | SQL 静态解析 | ~1 MB | <10 MB | 需安装 |

### 3.3 向量数据库层（修正评估：磁盘风险降低，内存风险仍存在）

ChromaDB 的大部分重量级依赖**已预装在本机 Python 环境中**（dry-run 验证）：

| 依赖组件 | 预估体积 | 本机状态 |
|---------|---------|---------|
| onnxruntime | ~85 MB 安装体积 | ✅ **已安装 1.19.2** |
| numpy | ~60 MB | ✅ **已安装 1.26.4** |
| tokenizers | ~15 MB | ✅ **已安装 0.21.4** |
| grpcio | ~25 MB | ❌ 需新装 |
| kubernetes | ~20 MB | ❌ 需新装 |
| opentelemetry 套件 | ~30 MB | ❌ 需新装 |
| chromadb 本体 + 其余新增 | ~80 MB | ❌ 需新装 |
| **实际新增磁盘** | **~155 MB** | 原评估 ~300 MB，修正后减半 |

**磁盘风险降级**：原评估约 300 MB 新增，修正后实际约 155 MB，15 GB 可用空间完全承受得住。

**内存风险维持原判**：onnxruntime 已装不等于已加载。ChromaDB 启动时会加载嵌入模型（`all-MiniLM-L6-v2`，~90 MB 模型文件需首次下载）并将其驻留内存，实际运行内存占用仍为 **400~600 MB**。当前 Swap 97% 满载的情况下此风险不变。

**结论：Phase 1 暂不引入 ChromaDB，使用 JSON 文件存储。Phase 2 时磁盘影响已可忽略，届时主要评估内存是否充裕。**

### 3.4 展示层

| 包 | 用途 | 安装体积 | 运行内存 |
|----|------|---------|---------|
| `streamlit` | MVP Demo UI | ~70 MB（含依赖）| 150~250 MB |

Streamlit 是当前最轻量的可交互 Demo 方案，无需前端开发，风险可控。

---

## 四、风险矩阵与应对策略

| 风险项 | 等级 | 触发条件 | 应对方案 |
|--------|------|---------|---------|
| Swap 满载 → 进程 OOM | 🔴 高 | 同时运行 ChromaDB + 嵌入模型 | Phase 1 不引入 ChromaDB |
| 磁盘空间不足 | 🟡 中 | 全栈安装 + 向量库数据增长 | 控制安装范围，监控磁盘 |
| Python 3.9 兼容性 | 🟡 中 | 部分新包已要求 3.10+ | 使用 venv 隔离，pinned 版本 |
| DeepSeek API 网络延迟 | 🟡 中 | 国内访问稳定性 | 配置超时重试，缓存已解析结果 |
| onnxruntime ARM 兼容性 | 🟢 低 | M1 Pro 有原生 arm64 wheel | 有 arm64 wheel，安装无障碍 |

---

## 五、Phase 1 推荐最小依赖方案

基于以上评估，Phase 1 MVP 采用**精简栈**，彻底规避内存风险：

```
Phase 1 精简栈
├── 解析层：lxml（已装）+ sqlparse（1 MB）
├── LLM层：openai（15 MB，调 DeepSeek API）
├── 存储层：JSON 文件（无需额外依赖）← 替代 ChromaDB
└── 展示层：streamlit（70 MB）
```

**安装命令：**
```bash
pip3 install openai sqlparse streamlit
# 预计新增安装体积：~30 MB（streamlit 大部分依赖已预装）
# 预计运行内存峰值：~300~400 MB（含 Streamlit + API 调用）
```

**向量数据库推迟到 Phase 2**，届时视内存压力决定：
- 仍在本机：选 `sqlite-vec`（纯 SQLite 扩展，无 onnxruntime，运行内存 <50 MB）
- 迁移到云端/高配机器：再引入 ChromaDB 或 Milvus Lite

---

## 六、其他端复用参考配置

| 配置等级 | 内存 | 磁盘 | 适用阶段 | 备注 |
|---------|------|------|---------|------|
| 最低配置（MVP 精简栈）| 8 GB | 5 GB 可用 | Phase 1 | 无向量库，JSON 存储 |
| 推荐配置 | 16 GB | 20 GB 可用 | Phase 1~2 | 可跑 ChromaDB，需关闭其他应用 |
| 理想配置 | 32 GB | 50 GB 可用 | Phase 2~3 | 全栈无压力，可同时跑多个 Agent 实例 |
| 云端部署 | 8 GB RAM 实例 | 50 GB SSD | Phase 3 生产 | 推荐 Docker 化，单独 ChromaDB 容器 |

**Python 版本建议**：生产/复用环境建议使用 **Python 3.11**（性能最佳，兼容性最广，M1/M2/M3 均有原生 wheel）。当前开发环境的 3.9.6 用于 MVP 可接受，但不建议作为长期标准。

---

## 七、DeepSeek API 接入说明

DeepSeek 提供 OpenAI 兼容端点，接入方式如下：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",          # DeepSeek-V3（通用推理）
    # model="deepseek-reasoner",    # DeepSeek-R1（复杂推理，成本更高）
    messages=[{"role": "user", "content": "..."}],
    max_tokens=2048
)
```

**费用参考**（2026年5月）：
- deepseek-chat：输入 ¥0.27/M tokens，输出 ¥1.1/M tokens（缓存命中后更低）
- 单张报表解析预估：约 2000~5000 tokens，费用 < ¥0.01

---

## 八、结论与行动建议

**可以进入 Phase 1，但需做两处调整：**

1. **LLM 层**：使用 DeepSeek API（`openai` 包 + `base_url` 指向 DeepSeek），替代原计划的 Anthropic Claude API ✅
2. **向量数据库**：Phase 1 不引入 ChromaDB，改用 JSON 文件存储解析结果，Phase 2 再按需引入轻量向量方案 ✅

**Phase 1 实际安装操作（约 90 MB，安全）：**
```bash
cd /Users/pandayoung3/Desktop/FR交接Agent/fr-agent
python3 -m venv .venv
source .venv/bin/activate
pip install openai sqlparse streamlit
```

> 建议使用 venv 虚拟环境隔离，避免污染系统 Python 3.9，同时方便后续在其他设备复现。

---

*由 FR 交接 Agent 开发日志系统自动记录 | Phase 1 前置评估*
