# 真实数据库验证计划

## 当前结论

仅用内置数据集 CPT 做验证是不够的。FR-Agent 最终要交付给客户使用，必须补一轮“真实数据库连接 + FineReport 开发报表 + FR-Agent 解析交接”的闭环测试。

当前样例 `MS填报-脱敏-llp.cpt` 主要是 `EmbeddedTableData`，适合验证 Parser、填报配置、控件和导出能力，但不能证明 DBTableData、JDBC 连接、SQL 参数、字段元数据增强在客户真实场景可用。

## 当前数据库识别与支持范围

### 能识别

- CPT 中的 `DBTableData` 数据集。
- 数据集内 SQL。
- 数据集的 FineReport 连接名。
- FineReport `WEB-INF/embed/prop/config_entity.properties` 中的连接元数据。
- JDBC driver / URL 对应的数据库类型：
  - MySQL / MariaDB
  - Oracle
  - SQL Server
  - PostgreSQL
  - SQLite
  - unknown

### 能增强

当前实际可连接并读取字段元数据的是：

- MySQL / MariaDB

增强方式：

- 从 SQL 提取表名。
- 连接 MySQL。
- 查询 `information_schema.COLUMNS`。
- 回填字段名、类型、注释、键类型到 parsed 数据集。

### 暂不支持增强

以下数据库当前能识别类型，但不会读取字段元数据：

- Oracle
- SQL Server
- PostgreSQL
- SQLite
- 其他 unknown JDBC

这些类型需要后续分别实现 schema 查询逻辑。

## 为什么需要真实 MySQL + FineReport 测试

真实客户场景通常不是内置数据集，而是：

```text
FineReport 参数控件
-> SQL 参数
-> DBTableData
-> JDBC 连接
-> 真实数据库表字段
-> 报表展示 / 填报
```

如果不做真实 DBTableData 样例，以下能力无法证明：

- 是否能正确识别 JDBC 连接名。
- 是否能正确解析 SQL 和 SQL 参数。
- 是否能从 FineReport WEB-INF 中读取连接元数据。
- 是否能通过用户提供的数据库密码读取字段类型和注释。
- 是否能把数据库字段元数据用于 LLM 语义分析。
- 是否能解释控件到 SQL 条件再到展示字段的完整链路。

## 建议测试环境

### MySQL

创建一个本地 MySQL 数据库，例如：

```text
database: fr_agent_demo
user: fr_agent_demo
password: 仅本地测试使用
```

建议准备两张表：

- `customer_order`
- `market_share_writeback`

字段要覆盖：

- 主键
- varchar
- decimal
- date / datetime
- 字段注释
- 可作为筛选条件的维度字段

### FineReport

在 FineReport 中配置 MySQL JDBC 连接，并开发两份样例：

| 样例 | 目的 |
| --- | --- |
| 查询型 DBTableData CPT | 验证 SQL、参数控件、字段展示、数据库字段增强 |
| 填报型 DBTableData CPT | 验证写回表、主键、字段映射、字段元数据 |

## 验收路径

1. 用 FineReport 开发真实 DBTableData 报表。
2. 导出 `.cpt`。
3. 在 FR-Agent 上传 CPT。
4. 填写 FineReport `WEB-INF` 路径。
5. 输入测试库密码。
6. 执行数据库增强。
7. 执行 AI 分析。
8. 导出 Markdown / HTML。
9. 按 `docs/templates/SCORING_REVIEW.md` 打分。

## 通过标准

真实 DBTableData 样例至少应满足：

- `datasets[].type` 能识别为 `DBTableData`。
- `datasets[].db_connection` 能匹配 FineReport 连接名。
- `datasets[].sql` 能提取。
- `datasets[].sql_params` 能识别主要参数。
- `/api/fr-connections` 能读取连接元数据。
- `/api/enrich` 能回填 `column_details`。
- 血缘能显示控件到 SQL / 数据集 / 展示字段链路。
- 导出文档能说明数据库字段类型、注释、复现步骤和风险。

## 建议优先级

真实 MySQL + FineReport 样例验证进入 P2 或更后。当前 P1 优先优化单个 CPT 的前端可视化理解体验、测试自动化、公式校验和评分系统 MVP。

该验证仍然是证明客户真实数据库连接场景的必要工作，但不阻塞 P1 的产品体验主线。
