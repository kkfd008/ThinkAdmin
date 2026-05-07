<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopStock extends Model
{
    protected $table = 'shop_stock';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = 'update_at';

    public function product()
    {
        return $this->hasOne(ShopProduct::class, 'id', 'product_id')
            ->bind([
                'product_barcode' => 'barcode',
                'product_name' => 'name',
                'product_box_spec' => 'box_spec',
                'product_cost_price' => 'cost_price',
                'product_price' => 'price',
            ]);
    }
}
