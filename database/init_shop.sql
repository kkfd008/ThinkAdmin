-- 创建供应商表
CREATE TABLE IF NOT EXISTS `shop_supplier` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(100) NOT NULL COMMENT '供应商名称',
  `code` varchar(50) UNIQUE COMMENT '供应商编码',
  `contact` varchar(50) COMMENT '联系人',
  `phone` varchar(20) COMMENT '联系电话',
  `address` varchar(255) COMMENT '地址',
  `category` varchar(50) COMMENT '供应商分类',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态(0禁用/1启用)',
  `remark` text COMMENT '备注',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '删除标记',
  `create_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 创建商品表
CREATE TABLE IF NOT EXISTS `shop_product` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` varchar(50) UNIQUE COMMENT '商品编码',
  `barcode` varchar(100) UNIQUE COMMENT '商品条码',
  `name` varchar(100) NOT NULL COMMENT '商品名称',
  `category` varchar(50) COMMENT '商品分类',
  `supplier_id` int(11) COMMENT '供应商ID',
  `price` decimal(10,2) NOT NULL COMMENT '售价',
  `cost_price` decimal(10,2) COMMENT '成本价',
  `unit` varchar(20) DEFAULT '件' COMMENT '计量单位',
  `specs` varchar(200) COMMENT '规格描述',
  `image` varchar(255) COMMENT '商品图片',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态(0禁用/1启用)',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '删除标记',
  `create_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `supplier_id` (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 创建库存表
CREATE TABLE IF NOT EXISTS `shop_stock` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product_id` int(11) NOT NULL COMMENT '商品ID',
  `stock` int(11) DEFAULT 0 COMMENT '当前库存',
  `min_stock` int(11) DEFAULT 10 COMMENT '预警库存',
  `warehouse` varchar(50) COMMENT '仓库名称',
  `location` varchar(100) COMMENT '存放位置',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '删除标记',
  `create_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存表';

-- 创建库存日志表
CREATE TABLE IF NOT EXISTS `shop_stock_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product_id` int(11) NOT NULL COMMENT '商品ID',
  `type` tinyint(1) COMMENT '操作类型(1入库/2出库/3盘点)',
  `quantity` int(11) NOT NULL COMMENT '数量',
  `before_stock` int(11) COMMENT '操作前库存',
  `after_stock` int(11) COMMENT '操作后库存',
  `operator` varchar(50) COMMENT '操作人',
  `remark` varchar(200) COMMENT '备注',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '删除标记',
  `create_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存日志表';

-- 插入示例数据
INSERT INTO `shop_supplier` (`name`, `code`, `contact`, `phone`, `category`, `status`) VALUES 
('示例供应商1', 'SUP202401010001', '张三', '13800138001', '食品供应商', 1),
('示例供应商2', 'SUP202401010002', '李四', '13800138002', '日用品供应商', 1);

INSERT INTO `shop_product` (`code`, `barcode`, `name`, `category`, `supplier_id`, `price`, `cost_price`, `unit`) VALUES 
('P001', '6901234567890', '矿泉水500ml', '饮料', 1, 2.00, 1.50, '瓶'),
('P002', '6901234567891', '方便面', '食品', 1, 4.50, 3.50, '盒'),
('P003', '6901234567892', '洗发水', '日用品', 2, 25.00, 18.00, '瓶');

INSERT INTO `shop_stock` (`product_id`, `stock`, `min_stock`, `warehouse`, `location`) VALUES 
(1, 100, 10, '主仓库', 'A区-01'),
(2, 50, 5, '主仓库', 'A区-02'),
(3, 30, 8, '主仓库', 'B区-01');