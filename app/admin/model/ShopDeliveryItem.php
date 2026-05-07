<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopDeliveryItem extends Model
{
    protected $table = 'shop_delivery_item';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = false;
}
