# 超市管理系统 - 实现计划

## 一、需求分析

### 1.1 业务概述

根据用户需求，需要在后台添加一个超市管理系统，包含三个核心子模块：

* **库存管理**：商品库存的增删改查、库存预警

* **商品管理**：商品信息的管理，包括分类、价格、规格等

* **销售记录**：销售订单的记录和查询

### 1.2 功能需求

| 模块   | 功能   | 说明              |
| ---- | ---- | --------------- |
| 商品管理 | 商品列表 | 展示所有商品信息，支持搜索筛选 |
| 商品管理 | 添加商品 | 添加新商品信息         |
| 商品管理 | 编辑商品 | 修改商品信息          |
| 商品管理 | 删除商品 | 删除商品记录          |
| 库存管理 | 库存列表 | 展示库存信息，支持预警提示   |
| 库存管理 | 入库操作 | 商品入库，增加库存       |
| 库存管理 | 出库操作 | 商品出库，减少库存       |
| 库存管理 | 库存盘点 | 调整库存数量          |
| 销售记录 | 销售列表 | 展示销售记录，支持时间筛选   |
| 销售记录 | 添加销售 | 记录销售订单          |
| 销售记录 | 销售统计 | 按时间维度统计销售数据     |

## 二、技术方案

### 2.1 架构设计

**模块结构**

```
app/admin/
├── controller/
│   ├── ShopProduct.php    # 商品管理控制器
│   ├── ShopStock.php      # 库存管理控制器
│   └── ShopSale.php       # 销售记录控制器
├── model/
│   ├── ShopProduct.php    # 商品模型
│   ├── ShopStock.php      # 库存模型
│   └── ShopSale.php       # 销售模型
└── view/
    ├── shop_product/      # 商品管理视图
    ├── shop_stock/        # 库存管理视图
    └── shop_sale/         # 销售记录视图
```

### 2.2 数据库设计

#### 2.2.1 商品表 (shop\_product)

| 字段名         | 类型            | 说明   | 约束               |
| ----------- | ------------- | ---- | ---------------- |
| id          | int           | 主键   | AUTO\_INCREMENT  |
| code        | varchar(50)   | 商品编码 | NOT NULL, UNIQUE |
| name        | varchar(100)  | 商品名称 | NOT NULL         |
| category    | varchar(50)   | 商品分类 | <br />           |
| price       | decimal(10,2) | 售价   | NOT NULL         |
| cost\_price | decimal(10,2) | 成本价  | <br />           |
| unit        | varchar(20)   | 计量单位 | 默认'件'            |
| specs       | varchar(200)  | 规格描述 | <br />           |
| image       | varchar(255)  | 商品图片 | <br />           |
| status      | tinyint(1)    | 状态   | 0禁用/1启用          |
| sort        | int           | 排序权重 | 默认0              |
| create\_at  | datetime      | 创建时间 | <br />           |
| update\_at  | datetime      | 更新时间 | <br />           |

#### 2.2.2 库存表 (shop\_stock)

| 字段名         | 类型           | 说明   | 约束                    |
| ----------- | ------------ | ---- | --------------------- |
| id          | int          | 主键   | AUTO\_INCREMENT       |
| product\_id | int          | 商品ID | NOT NULL, FOREIGN KEY |
| stock       | int          | 当前库存 | DEFAULT 0             |
| min\_stock  | int          | 预警库存 | DEFAULT 10            |
| warehouse   | varchar(50)  | 仓库名称 | <br />                |
| location    | varchar(100) | 存放位置 | <br />                |
| create\_at  | datetime     | 创建时间 | <br />                |
| update\_at  | datetime     | 更新时间 | <br />                |

#### 2.2.3 销售记录表 (shop\_sale)

| 字段名            | 类型            | 说明   | 约束                    |
| -------------- | ------------- | ---- | --------------------- |
| id             | int           | 主键   | AUTO\_INCREMENT       |
| order\_no      | varchar(50)   | 订单编号 | NOT NULL, UNIQUE      |
| product\_id    | int           | 商品ID | NOT NULL, FOREIGN KEY |
| quantity       | int           | 销售数量 | NOT NULL              |
| unit\_price    | decimal(10,2) | 单价   | NOT NULL              |
| total\_amount  | decimal(10,2) | 总金额  | NOT NULL              |
| customer\_name | varchar(50)   | 客户名称 | <br />                |
| sale\_time     | datetime      | 销售时间 | NOT NULL              |
| create\_at     | datetime      | 创建时间 | <br />                |

### 2.3 控制器设计

#### 2.3.1 ShopProduct 控制器

| 方法名            | 功能     | 权限注解                  |
| -------------- | ------ | --------------------- |
| index          | 商品列表   | @auth true @menu true |
| add            | 添加商品   | @auth true            |
| edit           | 编辑商品   | @auth true            |
| state          | 修改状态   | @auth true            |
| remove         | 删除商品   | @auth true            |
| \_form\_filter | 表单数据处理 | -                     |

#### 2.3.2 ShopStock 控制器

| 方法名            | 功能     | 权限注解                  |
| -------------- | ------ | --------------------- |
| index          | 库存列表   | @auth true @menu true |
| inbound        | 入库操作   | @auth true            |
| outbound       | 出库操作   | @auth true            |
| adjust         | 库存调整   | @auth true            |
| \_form\_filter | 表单数据处理 | -                     |

#### 2.3.3 ShopSale 控制器

| 方法名            | 功能     | 权限注解                  |
| -------------- | ------ | --------------------- |
| index          | 销售列表   | @auth true @menu true |
| add            | 添加销售   | @auth true            |
| statistics     | 销售统计   | @auth true            |
| \_form\_filter | 表单数据处理 | -                     |

## 三、实现步骤

### 3.1 创建模型文件

**步骤1**: 创建商品模型

```bash
文件路径: app/admin/model/ShopProduct.php
```

**步骤2**: 创建库存模型

```bash
文件路径: app/admin/model/ShopStock.php
```

**步骤3**: 创建销售模型

```bash
文件路径: app/admin/model/ShopSale.php
```

### 3.2 创建控制器文件

**步骤4**: 创建商品管理控制器

```bash
文件路径: app/admin/controller/ShopProduct.php
```

**步骤5**: 创建库存管理控制器

```bash
文件路径: app/admin/controller/ShopStock.php
```

**步骤6**: 创建销售记录控制器

```bash
文件路径: app/admin/controller/ShopSale.php
```

### 3.3 创建视图文件

**步骤7**: 创建商品管理视图

```bash
文件路径: app/admin/view/shop_product/index.html
文件路径: app/admin/view/shop_product/index_search.html
文件路径: app/admin/view/shop_product/form.html
```

**步骤8**: 创建库存管理视图

```bash
文件路径: app/admin/view/shop_stock/index.html
文件路径: app/admin/view/shop_stock/index_search.html
文件路径: app/admin/view/shop_stock/inbound.html
文件路径: app/admin/view/shop_stock/outbound.html
```

**步骤9**: 创建销售记录视图

```bash
文件路径: app/admin/view/shop_sale/index.html
文件路径: app/admin/view/shop_sale/index_search.html
文件路径: app/admin/view/shop_sale/form.html
文件路径: app/admin/view/shop_sale/statistics.html
```

### 3.4 初始化数据库

**步骤10**: 创建数据库表结构

```bash
使用 SQL 脚本创建三张表：shop_product, shop_stock, shop_sale
```

## 四、依赖与风险

### 4.1 依赖关系

| 依赖项                            | 说明            |
| ------------------------------ | ------------- |
| think\admin\Controller         | 基础控制器类        |
| think\admin\Model              | 基础模型类         |
| think\admin\helper\QueryHelper | 查询助手          |
| layui                          | 前端UI框架（已在项目中） |

### 4.2 风险评估

| 风险项     | 风险等级 | 应对措施         |
| ------- | ---- | ------------ |
| 数据库表不存在 | 高    | 首次访问时自动创建表结构 |
| 库存负数    | 中    | 出库时检查库存数量    |
| 商品不存在   | 中    | 入库/销售时校验商品ID |
| 并发库存操作  | 低    | 使用数据库事务和锁    |

## 五、测试计划

### 5.1 功能测试

| 模块   | 测试点  | 预期结果         |
| ---- | ---- | ------------ |
| 商品管理 | 添加商品 | 成功添加并返回列表    |
| 商品管理 | 编辑商品 | 成功修改并更新列表    |
| 商品管理 | 删除商品 | 成功删除并刷新列表    |
| 库存管理 | 入库操作 | 库存数量增加       |
| 库存管理 | 出库操作 | 库存数量减少，不足时提示 |
| 库存管理 | 库存预警 | 低于预警值时高亮显示   |
| 销售记录 | 添加销售 | 成功创建订单，库存减少  |
| 销售记录 | 销售统计 | 正确统计销售数据     |

### 5.2 数据一致性测试

| 测试场景 | 操作     | 验证点         |
| ---- | ------ | ----------- |
| 销售出库 | 添加销售记录 | 库存自动减少对应数量  |
| 库存盘点 | 调整库存   | 库存数量正确更新    |
| 删除商品 | 删除商品记录 | 关联库存和销售记录处理 |

***

## 六、文件清单

| 文件路径                                            | 文件类型 | 说明      |
| ----------------------------------------------- | ---- | ------- |
| app/admin/model/ShopProduct.php                 | 模型   | 商品数据模型  |
| app/admin/model/ShopStock.php                   | 模型   | 库存数据模型  |
| app/admin/model/ShopSale.php                    | 模型   | 销售数据模型  |
| app/admin/controller/ShopProduct.php            | 控制器  | 商品管理控制器 |
| app/admin/controller/ShopStock.php              | 控制器  | 库存管理控制器 |
| app/admin/controller/ShopSale.php               | 控制器  | 销售记录控制器 |
| app/admin/view/shop\_product/index.html         | 视图   | 商品列表页   |
| app/admin/view/shop\_product/index\_search.html | 视图   | 商品搜索表单  |
| app/admin/view/shop\_product/form.html          | 视图   | 商品表单页   |
| app/admin/view/shop\_stock/index.html           | 视图   | 库存列表页   |
| app/admin/view/shop\_stock/index\_search.html   | 视图   | 库存搜索表单  |
| app/admin/view/shop\_stock/inbound.html         | 视图   | 入库表单页   |
| app/admin/view/shop\_stock/outbound.html        | 视图   | 出库表单页   |
| app/admin/view/shop\_sale/index.html            | 视图   | 销售列表页   |
| app/admin/view/shop\_sale/index\_search.html    | 视图   | 销售搜索表单  |
| app/admin/view/shop\_sale/form.html             | 视图   | 销售表单页   |
| app/admin/view/shop\_sale/statistics.html       | 视图   | 销售统计页   |

