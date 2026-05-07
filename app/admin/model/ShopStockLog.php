<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopStockLog extends Model
{
    protected $table = 'shop_stock_log';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = false;
}
