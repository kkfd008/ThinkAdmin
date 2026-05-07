<?php

declare(strict_types=1);

namespace app\admin\controller;

use app\admin\model\ShopDelivery as ShopDeliveryModel;
use app\admin\model\ShopDeliveryItem;
use think\admin\Controller;
use think\admin\helper\QueryHelper;

class ShopDelivery extends Controller
{
    public function index()
    {
        ShopDeliveryModel::mQuery()->layTable(function () {
            $this->title = '库单管理';
        }, static function (QueryHelper $query) {
            $query->where(['is_deleted' => 0]);
            $query->like('supplier_name,remark')->dateBetween('delivery_date');
        });
    }

    public function detail()
    {
        $id = $this->request->get('id');
        $delivery = ShopDeliveryModel::mk()->findOrEmpty($id);
        if ($delivery->isEmpty()) {
            $this->error('库单不存在！');
        }
        $this->delivery = $delivery;
        $this->items = ShopDeliveryItem::mk()->where(['delivery_id' => $id])->select();
        $this->title = '入库单明细';
        $this->fetch();
    }

    public function remove()
    {
        ShopDeliveryModel::mDelete();
    }
}
