<?php

declare(strict_types=1);

namespace app\admin\model;

use think\admin\Model;

class ShopSupplier extends Model
{
    protected $table = 'shop_supplier';
    protected $pk = 'id';
    protected $autoWriteTimestamp = true;
    protected $createTime = 'create_at';
    protected $updateTime = false;
}
