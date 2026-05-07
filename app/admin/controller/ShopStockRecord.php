<?php

declare(strict_types=1);

namespace app\admin\controller;

use app\admin\model\ShopProduct;
use app\admin\model\ShopStock;
use app\admin\model\ShopStockLog;
use think\admin\Controller;
use think\admin\helper\QueryHelper;
use think\admin\service\AdminService;

class ShopStockRecord extends Controller
{
    public function index()
    {
        ShopStock::mQuery()->layTable(function () {
            $this->title = '库存记录管理';
        }, static function (QueryHelper $query) {
            $query->where(['shop_stock.is_deleted' => 0]);
            $query->with('product');
            $query->like('product_name,product_barcode')->dateBetween('update_at');
        });
    }

    /**
     * 入库、出库、售出通用弹出表单
     */
    public function inbound()
    {
        $this->_opForm(1, '入库');
    }

    public function outbound()
    {
        $this->_opForm(2, '出库');
    }

    public function sold()
    {
        $this->_opForm(3, '售出');
    }

    private function _opForm(int $type, string $title): void
    {
        if ($this->request->isGet()) {
            $this->title = $title;
            $this->opType = $type;
            $this->opTitle = $title;
            $this->products = ShopProduct::mk()->where(['is_deleted' => 0])->select();
            $this->fetch('inbound');
        } else {
            $data = $this->_vali([
                'product_id.require' => '请选择商品！',
                'quantity.require' => '数量不能为空！',
                'quantity.integer' => '数量必须是整数！',
                'quantity.gt:0' => '数量必须大于0！',
            ]);
            $product = ShopProduct::mk()->find($data['product_id']);
            if (empty($product)) $this->error('商品不存在！');

            $stock = ShopStock::mk()->where(['product_id' => $data['product_id']])->find();
            $nowStock = $stock ? $stock['stock'] : 0;
            $qty = intval($data['quantity']);

            if ($type === 1) { // 入库：增加
                if ($stock) $stock->save(['stock' => $nowStock + $qty]);
                else ShopStock::mk()->insert(['product_id' => $data['product_id'], 'stock' => $qty]);
            } elseif ($type === 2 || $type === 3) { // 出库/售出：减少
                if (!$stock || $nowStock < $qty) {
                    $this->error('库存不足！当前库存：' . $nowStock);
                }
                $stock->save(['stock' => $nowStock - $qty]);
            }

            ShopStockLog::mk()->insert([
                'barcode' => $product['barcode'],
                'name' => $product['name'],
                'type' => $type,
                'quantity' => $qty,
            ]);

            sysoplog('库存管理', "商品【{$product['name']}】{$title} {$qty} 件");
            $this->success($title . '成功！');
        }
    }

    /**
     * 库存盘点
     */
    public function adjust()
    {
        if ($this->request->isGet()) {
            $this->title = '库存盘点';
            $this->opType = 0;
            $this->opTitle = '盘点';
            $this->products = ShopProduct::mk()->where(['is_deleted' => 0])->select();
            $this->fetch('inbound');
        } else {
            $data = $this->_vali([
                'product_id.require' => '请选择商品！',
                'quantity.require' => '盘点数量不能为空！',
                'quantity.integer' => '盘点数量必须是整数！',
                'quantity.gte:0' => '盘点数量不能为负数！',
            ]);
            $product = ShopProduct::mk()->find($data['product_id']);
            if (empty($product)) $this->error('商品不存在！');

            $stock = ShopStock::mk()->where(['product_id' => $data['product_id']])->find();
            $nowStock = $stock ? $stock['stock'] : 0;
            $newStock = intval($data['quantity']);
            if ($stock) $stock->save(['stock' => $newStock]);
            else ShopStock::mk()->insert(['product_id' => $data['product_id'], 'stock' => $newStock]);

            sysoplog('库存管理', "商品【{$product['name']}】盘点，原库存 {$nowStock}，新库存 {$newStock}");
            $this->success('盘点成功！');
        }
    }

    public function log()
    {
        ShopStockLog::mQuery()->layTable(function () {
            $this->title = '库存变化记录';
        }, static function (QueryHelper $query) {
            $query->where(['is_deleted' => 0]);
            $query->like('barcode,name')->equal('type')->dateBetween('create_at');
        });
    }
}
