<?php

declare(strict_types=1);

namespace app\admin\controller;

use app\admin\model\ShopSupplier;
use think\admin\Controller;
use think\admin\helper\QueryHelper;

class ShopSupplier extends Controller
{
    public function index()
    {
        ShopSupplier::mQuery()->layTable(function () {
            $this->title = '供应商管理';
        }, static function (QueryHelper $query) {
            $query->where(['is_deleted' => 0]);
            $query->like('code,name,phone')->dateBetween('create_at');
        });
    }

    public function add()
    {
        ShopSupplier::mForm('form');
    }

    public function edit()
    {
        ShopSupplier::mForm('form');
    }

    public function remove()
    {
        ShopSupplier::mDelete();
    }

    protected function _form_filter(array &$data)
    {
        if ($this->request->isPost()) {
            if (empty($data['name'])) {
                $this->error('供应商名称不能为空！');
            }
            if (empty($data['code'])) {
                $this->error('供应商ID不能为空！');
            }
            if (strlen($data['code']) < 4 || strlen($data['code']) > 12) {
                $this->error('供应商ID长度必须在4-12位之间！');
            }
            if (!preg_match('/^[a-zA-Z]+$/', $data['code'])) {
                $this->error('供应商ID只能包含英文字母！');
            }
            $data['code'] = strtoupper($data['code']);
            $map = [
                ['code', '=', $data['code']],
                ['is_deleted', '=', 0],
                ['id', '<>', $data['id'] ?? 0]
            ];
            if (ShopSupplier::mk()->where($map)->count() > 0) {
                $this->error('供应商ID已存在！');
            }
        }
    }
}
