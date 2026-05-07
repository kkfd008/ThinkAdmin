<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopProduct extends Model
{
    protected $table = 'shop_product';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = 'update_at';
}
