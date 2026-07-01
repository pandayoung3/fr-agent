-- FR-Agent P2 real DB validation schema.
-- Run in a local MySQL/MariaDB instance, then connect FineReport to database `fr_agent_demo`.

CREATE DATABASE IF NOT EXISTS fr_agent_demo
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE fr_agent_demo;

CREATE TABLE IF NOT EXISTS customer_order (
  order_id BIGINT PRIMARY KEY COMMENT '订单ID',
  order_date DATE NOT NULL COMMENT '下单日期',
  region VARCHAR(32) NOT NULL COMMENT '销售地区',
  customer_name VARCHAR(128) NOT NULL COMMENT '客户名称',
  product_category VARCHAR(64) NOT NULL COMMENT '产品品类',
  sales_amount DECIMAL(18, 2) NOT NULL COMMENT '销售金额',
  profit_amount DECIMAL(18, 2) NOT NULL COMMENT '利润金额',
  sales_owner VARCHAR(64) NOT NULL COMMENT '销售负责人',
  updated_at DATETIME NOT NULL COMMENT '更新时间'
) COMMENT='FR-Agent 查询型报表验证订单表';

CREATE TABLE IF NOT EXISTS market_share_writeback (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '填报记录ID',
  report_month VARCHAR(7) NOT NULL COMMENT '报表月份',
  region VARCHAR(32) NOT NULL COMMENT '销售地区',
  product_category VARCHAR(64) NOT NULL COMMENT '产品品类',
  target_share DECIMAL(8, 4) NOT NULL COMMENT '目标市场份额',
  owner VARCHAR(64) NOT NULL COMMENT '填报负责人',
  remark VARCHAR(255) NULL COMMENT '备注',
  updated_at DATETIME NOT NULL COMMENT '更新时间'
) COMMENT='FR-Agent 填报型报表验证写回表';

INSERT INTO customer_order
  (order_id, order_date, region, customer_name, product_category, sales_amount, profit_amount, sales_owner, updated_at)
VALUES
  (1001, '2026-01-05', '华东', '杭州样例客户A', '软件服务', 120000.00, 42000.00, '张三', NOW()),
  (1002, '2026-01-18', '华南', '深圳样例客户B', '硬件设备', 86000.00, 21000.00, '李四', NOW()),
  (1003, '2026-02-03', '华北', '北京样例客户C', '软件服务', 158000.00, 61000.00, '王五', NOW()),
  (1004, '2026-02-20', '华东', '上海样例客户D', '咨询交付', 66000.00, 18000.00, '张三', NOW())
ON DUPLICATE KEY UPDATE
  sales_amount = VALUES(sales_amount),
  profit_amount = VALUES(profit_amount),
  updated_at = VALUES(updated_at);

INSERT INTO market_share_writeback
  (id, report_month, region, product_category, target_share, owner, remark, updated_at)
VALUES
  (1, '2026-01', '华东', '软件服务', 0.3200, '张三', '样例填报数据', NOW()),
  (2, '2026-01', '华南', '硬件设备', 0.1800, '李四', '样例填报数据', NOW())
ON DUPLICATE KEY UPDATE
  target_share = VALUES(target_share),
  owner = VALUES(owner),
  remark = VALUES(remark),
  updated_at = VALUES(updated_at);
