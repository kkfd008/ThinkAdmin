# ThinkAdmin 项目技术文档

## 一、项目概述

### 1.1 项目简介
ThinkAdmin 是一款基于 ThinkPHP 的应用开发框架，专注于快速构建企业级后台管理系统。项目采用模块化架构设计，提供完善的权限管理、微信集成、文件存储等核心功能。

### 1.2 项目架构
```
ThinkAdmin/
├── app/                    # 应用目录
│   ├── admin/              # 后台管理模块
│   ├── index/              # 前台入口模块
│   └── wechat/             # 微信模块
├── config/                 # 配置文件
├── public/                 # 静态资源
├── runtime/                # 运行时缓存
└── vendor/                 # 第三方依赖
```

### 1.3 技术栈
| 分类 | 技术 | 版本 |
|------|------|------|
| 语言 | PHP | >= 7.1 |
| 框架 | ThinkPHP | ^6.0 |
| ORM | think-orm | ^2.0\|^3.0 |
| 核心库 | think-library | ^6.1 |
| 数据库 | MySQL / SQLite | - |

---

## 二、核心模块

### 2.1 后台管理模块 (admin)

#### 2.1.1 控制器清单

| 控制器 | 功能描述 | 文件路径 |
|--------|----------|----------|
| Index | 后台首页入口 | `app/admin/controller/Index.php` |
| User | 系统用户管理 | `app/admin/controller/User.php` |
| Auth | 系统权限管理 | `app/admin/controller/Auth.php` |
| Config | 系统参数配置 | `app/admin/controller/Config.php` |
| Menu | 菜单管理 | `app/admin/controller/Menu.php` |
| File | 文件管理 | `app/admin/controller/File.php` |
| Oplog | 操作日志 | `app/admin/controller/Oplog.php` |
| Queue | 任务队列 | `app/admin/controller/Queue.php` |
| Login | 登录处理 | `app/admin/controller/Login.php` |

#### 2.1.2 用户管理功能

**用户列表** (`User::index`)
- 支持状态筛选（启用/禁用）
- 支持用户类型筛选
- 支持关键词搜索（用户名、手机号、邮箱）
- 支持日期范围筛选

**用户表单** (`User::add` / `User::edit`)
- 用户名验证（唯一性检查）
- 权限配置（RBAC节点绑定）
- 初始密码与账号相同

**密码修改** (`User::pass`)
- 新旧密码验证
- 密码加密存储（MD5）
- 密码修改事件触发

#### 2.1.3 权限管理功能

**权限列表** (`Auth::index`)
- 权限名称搜索
- 权限类型筛选
- 状态切换

**权限配置** (`Auth::add` / `Auth::edit`)
- 权限节点树展示
- 插件权限集成
- 权限节点批量保存

---

### 2.2 微信模块 (wechat)

#### 2.2.1 控制器清单

| 控制器 | 功能描述 | 文件路径 |
|--------|----------|----------|
| Config | 微信配置管理 | `app/wechat/controller/Config.php` |
| Fans | 粉丝管理 | `app/wechat/controller/Fans.php` |
| Menu | 微信菜单 | `app/wechat/controller/Menu.php` |
| News | 图文素材 | `app/wechat/controller/News.php` |
| Keys | 自动回复 | `app/wechat/controller/Keys.php` |
| Auto | 自动任务 | `app/wechat/controller/Auto.php` |
| payment/Record | 支付记录 | `app/wechat/controller/payment/Record.php` |
| payment/Refund | 退款管理 | `app/wechat/controller/payment/Refund.php` |
| api/Login | 微信登录 | `app/wechat/controller/api/Login.php` |
| api/Push | 消息推送 | `app/wechat/controller/api/Push.php` |

#### 2.2.2 核心服务

**WechatService** (`app/wechat/service/WeChatService.php`)

提供微信接口统一调度：

| 方法 | 功能 | 对应类 |
|------|------|--------|
| `WeChatOauth()` | 网页授权 | `\WeChat\Oauth` |
| `WeChatUser()` | 粉丝管理 | `\WeChat\User` |
| `WeChatMenu()` | 菜单管理 | `\WeChat\Menu` |
| `WeChatTemplate()` | 模板消息 | `\WeChat\Template` |
| `WeChatMedia()` | 素材管理 | `\WeChat\Media` |
| `WePayOrder()` | 支付订单 | `\WePay\Order` |
| `WePayRefund()` | 退款处理 | `\WePay\Refund` |
| `WeMiniUser()` | 小程序用户 | `\WeMini\User` |

#### 2.2.3 数据模型

**WechatFans** (`app/wechat/model/WechatFans.php`)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| openid | string | 粉丝唯一标识 |
| unionid | string | 开放平台唯一标识 |
| nickname | string | 用户昵称 |
| sex | int | 性别(1男/2女/0未知) |
| headimgurl | string | 头像URL |
| subscribe | int | 关注状态 |
| subscribe_time | int | 关注时间 |
| appid | string | 公众号APPID |
| country | string | 国家 |
| province | string | 省份 |
| city | string | 城市 |

---

## 三、配置管理

### 3.1 应用配置 (`config/app.php`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| app_namespace | 应用命名空间 | - |
| app_express | 快速访问 | true |
| with_route | 启用路由 | true |
| super_user | 超级用户 | admin |
| default_timezone | 默认时区 | Asia/Shanghai |
| cors_on | 跨域开启 | true |
| cors_methods | 允许方法 | GET,PUT,POST,PATCH,DELETE |
| rbac_ignore | 忽略RBAC | ['index'] |

### 3.2 数据库配置 (`config/database.php`)

**MySQL 配置**
```php
[
    'type' => 'mysql',
    'hostname' => env('DB_MYSQL_HOST', '127.0.0.1'),
    'hostport' => env('DB_MYSQL_PORT', '3306'),
    'database' => env('DB_MYSQL_DATABASE', 'thinkadmin'),
    'username' => env('DB_MYSQL_USERNAME', 'root'),
    'password' => env('DB_MYSQL_PASSWORD', ''),
    'prefix' => env('DB_MYSQL_PREFIX', ''),
    'charset' => 'utf8mb4',
]
```

**SQLite 配置**（默认）
```php
[
    'type' => 'sqlite',
    'database' => syspath('database/sqlite.db'),
    'charset' => 'utf8',
]
```

### 3.3 路由配置 (`config/route.php`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| url_html_suffix | URL后缀 | html |
| url_route_must | 强制路由 | false |
| route_complete_match | 完全匹配 | true |
| default_app | 默认应用 | index |
| default_controller | 默认控制器 | Index |
| default_action | 默认方法 | index |

---

## 四、核心功能

### 4.1 用户认证体系

**登录流程**
```
请求 → Login::index → 验证码验证 → 账号密码验证 → 会话建立 → 跳转首页
```

**权限控制**
- 使用 `@auth true` 注解标记需登录操作
- 使用 `@menu true` 注解标记菜单显示
- RBAC 权限节点动态加载

### 4.2 文件存储系统

支持多种存储驱动：

| 驱动 | 说明 | 配置类 |
|------|------|--------|
| Local | 本地存储 | LocalStorage |
| AliOSS | 阿里云OSS | AliossStorage |
| Qiniu | 七牛云存储 | QiniuStorage |
| Txcos | 腾讯云COS | TxcosStorage |
| Upyun | 又拍云 | UpyunStorage |

**存储配置** (`Config::storage`)
- 允许文件扩展名白名单
- 禁止可执行文件上传（sh, asp, bat, cmd, exe, php）

### 4.3 任务队列

**队列管理** (`Queue`)
- 任务列表展示
- 任务状态监控
- 任务重试机制

### 4.4 微信支付

**支付配置** (`Config::payment`)
- 商户号配置
- 证书管理（PEM/P12格式）
- API密钥配置

**支付流程**
```
下单 → WePayOrder::create → 统一下单接口 → 返回支付参数 → 前端调起支付
```

**退款流程**
```
申请退款 → WePayRefund::create → 退款接口 → 回调通知 → 更新订单状态
```

---

## 五、安全机制

### 5.1 输入验证

使用 `_vali()` 方法进行表单验证：

```php
$this->_vali([
    'username.require' => '账号不能为空',
    'password.require' => '密码不能为空',
    'password.confirm:repassword' => '两次密码不一致',
]);
```

### 5.2 防CSRF攻击

- 表单令牌验证 (`_applyFormToken`)
- 请求来源检查

### 5.3 文件上传安全

- 扩展名白名单过滤
- 禁止可执行文件上传
- 文件类型校验

### 5.4 错误处理

**异常页面配置**
```php
'http_exception_template' => [
    404 => syspath('public/static/theme/err/404.html'),
    500 => syspath('public/static/theme/err/500.html'),
]
```

---

## 六、部署指南

### 6.1 环境要求

| 依赖 | 版本 |
|------|------|
| PHP | >= 7.1 |
| MySQL | >= 5.7 或 SQLite |
| Composer | >= 2.0 |

### 6.2 安装步骤

```bash
# 克隆项目
git clone https://gitee.com/zoujingli/ThinkAdmin.git

# 安装依赖
composer install

# 复制环境配置
cp .env.example .env

# 配置数据库连接
# 编辑 .env 文件

# 启动服务
php think run
```

### 6.3 目录权限

```bash
chmod -R 755 runtime/
chmod -R 755 public/static/
```

---

## 七、扩展开发

### 7.1 新增控制器

```php
namespace app\admin\controller;

use think\admin\Controller;

class Example extends Controller
{
    public function index()
    {
        $this->title = '示例页面';
        $this->fetch();
    }
}
```

### 7.2 新增模型

```php
namespace app\admin\model;

use think\admin\Model;

class Example extends Model
{
    protected $table = 'example';
}
```

### 7.3 新增视图

视图文件放置于 `app/{module}/view/{controller}/{action}.html`

---

## 八、附录

### 8.1 项目地址

| 平台 | 地址 |
|------|------|
| Gitee | https://gitee.com/zoujingli/ThinkAdmin |
| GitHub | https://github.com/zoujingli/ThinkAdmin |
| 官网 | https://thinkadmin.top |

### 8.2 开源协议

MIT License

### 8.3 联系方式

- 作者：Anyon
- 邮箱：zoujingli@qq.com