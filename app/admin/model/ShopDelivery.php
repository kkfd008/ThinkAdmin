<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopDelivery extends Model
{
    protected $table = 'shop_delivery';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = 'update_at';

    public function items()
    {
        return $this->hasMany(ShopDeliveryItem::class, 'delivery_id', 'id');
    }
}
