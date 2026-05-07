# 超市库存管理系统 - 实现计划

## 一、需求分析

### 1.1 业务概述
根据用户需求，超市库存管理系统包含三个核心子模块：

| 模块 | 功能描述 |
|------|----------|
| 供应商管理 | 供应商信息的增删改查，支持供应商分类管理 |
| 库存记录管理 | 库存出入库记录管理，库存预警，库存盘点 |
| 库存导入 | 支持Excel批量导入库存数据 |

### 1.2 核心功能需求

**供应商管理**
- 供应商列表展示（支持搜索、筛选）
- 添加/编辑供应商信息
- 删除供应商（软删除）
- 供应商状态管理（启用/禁用）

**库存记录管理**
- 库存列表展示（商品名称、条码、库存数量、预警值）
- 库存入库操作
- 库存出库操作
- 库存盘点调整
- 库存预警提示（低于预警值高亮显示）
- 根据商品名称和条码进行库存查询

**库存导入**
- 支持Excel文件上传
- 数据预览和批量导入
- 导入错误提示和日志记录

## 二、技术方案

### 2.1 模块结构

```
app/admin/
├── controller/
│   ├── ShopSupplier.php    # 供应商管理控制器
│   ├── ShopStockRecord.php # 库存记录管理控制器
│   └── ShopStockImport.php # 库存导入控制器
├── model/
│   ├── ShopSupplier.php    # 供应商模型
│   ├── ShopProduct.php     # 商品模型
│   ├── ShopStock.php       # 库存模型
│   └── ShopStockLog.php    # 库存日志模型
└── view/
    ├── shop_supplier/      # 供应商管理视图
    ├── shop_stock_record/  # 库存记录视图
    └── shop_stock_import/  # 库存导入视图
```

### 2.2 数据库设计

#### 2.2.1 供应商表 (shop_supplier)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | int | 主键 | AUTO_INCREMENT |
| name | varchar(100) | 供应商名称 | NOT NULL |
| code | varchar(50) | 供应商编码 | UNIQUE |
| contact | varchar(50) | 联系人 | |
| phone | varchar(20) | 联系电话 | |
| address | varchar(255) | 地址 | |
| category | varchar(50) | 供应商分类 | |
| status | tinyint(1) | 状态 | 0禁用/1启用 |
| remark | text | 备注 | |
| create_at | datetime | 创建时间 | |
| update_at | datetime | 更新时间 | |

#### 2.2.2 商品表 (shop_product)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | int | 主键 | AUTO_INCREMENT |
| code | varchar(50) | 商品编码 | UNIQUE |
| barcode | varchar(100) | 商品条码 | UNIQUE |
| name | varchar(100) | 商品名称 | NOT NULL |
| category | varchar(50) | 商品分类 | |
| supplier_id | int | 供应商ID | FOREIGN KEY |
| price | decimal(10,2) | 售价 | NOT NULL |
| cost_price | decimal(10,2) | 成本价 | |
| unit | varchar(20) | 计量单位 | 默认'件' |
| specs | varchar(200) | 规格描述 | |
| image | varchar(255) | 商品图片 | |
| status | tinyint(1) | 状态 | 0禁用/1启用 |
| create_at | datetime | 创建时间 | |
| update_at | datetime | 更新时间 | |

#### 2.2.3 库存表 (shop_stock)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | int | 主键 | AUTO_INCREMENT |
| product_id | int | 商品ID | NOT NULL, FOREIGN KEY |
| stock | int | 当前库存 | DEFAULT 0 |
| min_stock | int | 预警库存 | DEFAULT 10 |
| warehouse | varchar(50) | 仓库名称 | |
| location | varchar(100) | 存放位置 | |
| create_at | datetime | 创建时间 | |
| update_at | datetime | 更新时间 | |

#### 2.2.4 库存日志表 (shop_stock_log)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | int | 主键 | AUTO_INCREMENT |
| product_id | int | 商品ID | NOT NULL, FOREIGN KEY |
| type | tinyint(1) | 操作类型 | 1入库/2出库/3盘点 |
| quantity | int | 数量 | NOT NULL |
| before_stock | int | 操作前库存 | |
| after_stock | int | 操作后库存 | |
| operator | varchar(50) | 操作人 | |
| remark | varchar(200) | 备注 | |
| create_at | datetime | 创建时间 | |

## 三、控制器设计

### 3.1 ShopSupplier 控制器

| 方法名 | 功能 | 权限注解 |
|--------|------|----------|
| index | 供应商列表 | @auth true @menu true |
| add | 添加供应商 | @auth true |
| edit | 编辑供应商 | @auth true |
| state | 修改状态 | @auth true |
| remove | 删除供应商 | @auth true |
| _form_filter | 表单数据处理 | - |

### 3.2 ShopStockRecord 控制器

| 方法名 | 功能 | 权限注解 |
|--------|------|----------|
| index | 库存列表 | @auth true @menu true |
| inbound | 入库操作 | @auth true |
| outbound | 出库操作 | @auth true |
| adjust | 库存盘点 | @auth true |
| log | 库存日志 | @auth true |
| _form_filter | 表单数据处理 | - |

### 3.3 ShopStockImport 控制器

| 方法名 | 功能 | 权限注解 |
|--------|------|----------|
| index | 导入页面 | @auth true @menu true |
| preview | 预览数据 | @auth true |
| import | 执行导入 | @auth true |
| template | 下载模板 | @auth true |

## 四、实现步骤

### 4.1 创建模型文件

**步骤1**: 创建供应商模型
```bash
文件路径: app/admin/model/ShopSupplier.php
```

**步骤2**: 创建商品模型
```bash
文件路径: app/admin/model/ShopProduct.php
```

**步骤3**: 创建库存模型
```bash
文件路径: app/admin/model/ShopStock.php
```

**步骤4**: 创建库存日志模型
```bash
文件路径: app/admin/model/ShopStockLog.php
```

### 4.2 创建控制器文件

**步骤5**: 创建供应商管理控制器
```bash
文件路径: app/admin/controller/ShopSupplier.php
```

**步骤6**: 创建库存记录管理控制器
```bash
文件路径: app/admin/controller/ShopStockRecord.php
```

**步骤7**: 创建库存导入控制器
```bash
文件路径: app/admin/controller/ShopStockImport.php
```

### 4.3 创建视图文件

**步骤8**: 创建供应商管理视图
```bash
文件路径: app/admin/view/shop_supplier/index.html
文件路径: app/admin/view/shop_supplier/index_search.html
文件路径: app/admin/view/shop_supplier/form.html
```

**步骤9**: 创建库存记录管理视图
```bash
文件路径: app/admin/view/shop_stock_record/index.html
文件路径: app/admin/view/shop_stock_record/index_search.html
文件路径: app/admin/view/shop_stock_record/inbound.html
文件路径: app/admin/view/shop_stock_record/outbound.html
文件路径: app/admin/view/shop_stock_record/adjust.html
文件路径: app/admin/view/shop_stock_record/log.html
```

**步骤10**: 创建库存导入视图
```bash
文件路径: app/admin/view/shop_stock_import/index.html
文件路径: app/admin/view/shop_stock_import/preview.html
```

### 4.4 初始化数据库

**步骤11**: 创建数据库表结构
```bash
使用 SQL 脚本创建四张表：shop_supplier, shop_product, shop_stock, shop_stock_log
```

## 五、依赖与风险

### 5.1 依赖关系

| 依赖项 | 说明 |
|--------|------|
| think\admin\Controller | 基础控制器类 |
| think\admin\Model | 基础模型类 |
| think\admin\helper\QueryHelper | 查询助手 |
| PHPExcel/PhpSpreadsheet | Excel处理（项目已有xlsx.min.js） |
| layui | 前端UI框架（已在项目中） |

### 5.2 风险评估

| 风险项 | 风险等级 | 应对措施 |
|--------|----------|----------|
| 数据库表不存在 | 高 | 首次访问时自动创建表结构 |
| 库存负数 | 中 | 出库时检查库存数量 |
| 商品不存在 | 中 | 入库时校验商品ID |
| 并发库存操作 | 低 | 使用数据库事务和锁 |
| 导入数据错误 | 中 | 导入前预览，记录错误日志 |

## 六、测试计划

### 6.1 功能测试

| 模块 | 测试点 | 预期结果 |
|------|--------|----------|
| 供应商管理 | 添加供应商 | 成功添加并返回列表 |
| 供应商管理 | 编辑供应商 | 成功修改并更新列表 |
| 库存记录 | 入库操作 | 库存数量增加，日志记录 |
| 库存记录 | 出库操作 | 库存数量减少，不足时提示 |
| 库存记录 | 库存预警 | 低于预警值时高亮显示 |
| 库存记录 | 库存查询 | 支持按商品名称和条码搜索 |
| 库存导入 | Excel导入 | 成功批量导入数据 |

### 6.2 数据一致性测试

| 测试场景 | 操作 | 验证点 |
|----------|------|--------|
| 入库操作 | 添加入库记录 | 库存增加，日志记录 |
| 出库操作 | 添加出库记录 | 库存减少，日志记录 |
| 库存盘点 | 调整库存 | 库存数量正确更新，日志记录 |

---

## 七、文件清单

| 文件路径 | 文件类型 | 说明 |
|----------|----------|------|
| app/admin/model/ShopSupplier.php | 模型 | 供应商数据模型 |
| app/admin/model/ShopProduct.php | 模型 | 商品数据模型 |
| app/admin/model/ShopStock.php | 模型 | 库存数据模型 |
| app/admin/model/ShopStockLog.php | 模型 | 库存日志模型 |
| app/admin/controller/ShopSupplier.php | 控制器 | 供应商管理控制器 |
| app/admin/controller/ShopStockRecord.php | 控制器 | 库存记录管理控制器 |
| app/admin/controller/ShopStockImport.php | 控制器 | 库存导入控制器 |
| app/admin/view/shop_supplier/index.html | 视图 | 供应商列表页 |
| app/admin/view/shop_supplier/index_search.html | 视图 | 供应商搜索表单 |
| app/admin/view/shop_supplier/form.html | 视图 | 供应商表单页 |
| app/admin/view/shop_stock_record/index.html | 视图 | 库存列表页 |
| app/admin/view/shop_stock_record/index_search.html | 视图 | 库存搜索表单 |
| app/admin/view/shop_stock_record/inbound.html | 视图 | 入库表单页 |
| app/admin/view/shop_stock_record/outbound.html | 视图 | 出库表单页 |
| app/admin/view/shop_stock_record/adjust.html | 视图 | 盘点表单页 |
| app/admin/view/shop_stock_record/log.html | 视图 | 库存日志页 |
| app/admin/view/shop_stock_import/index.html | 视图 | 导入首页 |
| app/admin/view/shop_stock_import/preview.html | 视图 | 数据预览页 |