<?php

declare(strict_types=1);

namespace app\admin\controller;

use app\admin\model\ShopProduct;
use app\admin\model\ShopStock;
use think\admin\Controller;
use think\admin\service\AdminService;

class ShopStockImport extends Controller
{
    public function index()
    {
        $this->title = '库存导入';
        $this->fetch();
    }

    public function preview()
    {
        $file = $this->request->file('file');
        if (empty($file)) {
            $this->error('请选择要导入的文件！');
        }

        $ext = strtolower(pathinfo($file->getOriginalName(), PATHINFO_EXTENSION));
        if (!in_array($ext, ['xlsx', 'xls'])) {
            $this->error('只允许上传 .xlsx 或 .xls 格式的文件！');
        }

        $info = $file->move(sysconf('storage.local.root') ?: syspath('runtime'));
        if (!$info) {
            $this->error('文件上传失败！');
        }

        $filePath = $info->getRealPath();
        $data = $this->readExcel($filePath);
        
        if (empty($data)) {
            $this->error('文件内容为空！');
        }
        
        $this->data = $data;
        $this->title = '导入预览';
        $this->fetch();
    }

    public function import()
    {
        $data = $this->request->post('data');
        if (empty($data)) {
            $this->error('没有要导入的数据！');
        }
        
        $data = json_decode($data, true);
        $success = 0;
        $failed = 0;
        $errors = [];
        
        foreach ($data as $row) {
            try {
                $product = ShopProduct::mk()->where(function ($q) use ($row) {
                    $q->where('barcode', $row['barcode'])->whereOr('code', $row['code']);
                })->find();
                
                if (!$product) {
                    $product = ShopProduct::mk()->insertGetId([
                        'code' => $row['code'],
                        'barcode' => $row['barcode'],
                        'name' => $row['name'],
                        'category' => $row['category'],
                        'unit' => $row['unit'] ?: '件',
                        'status' => 1
                    ]);
                }
                
                $stock = ShopStock::mk()->where(['product_id' => $product['id'] ?? $product])->find();
                if ($stock) {
                    $stock->save(['stock' => $row['stock']]);
                } else {
                    ShopStock::mk()->insert([
                        'product_id' => $product['id'] ?? $product,
                        'stock' => $row['stock'],
                        'min_stock' => $row['min_stock'] ?: 10
                    ]);
                }
                $success++;
            } catch (\Exception $e) {
                $failed++;
                $errors[] = "第{$row['row']}行: " . $e->getMessage();
            }
        }
        
        sysoplog('库存管理', "批量导入库存，成功{$success}条，失败{$failed}条");
        
        if ($failed > 0) {
            $this->success("导入完成！成功{$success}条，失败{$failed}条", '', ['errors' => $errors]);
        } else {
            $this->success("全部导入成功！共{$success}条");
        }
    }

    public function template()
    {
        $headers = ['商品编码', '商品条码', '商品名称', '商品分类', '计量单位', '库存数量', '预警数量'];
        $data = [
            ['P001', '6901234567890', '商品示例1', '食品', '件', 100, 10],
            ['P002', '6901234567891', '商品示例2', '日用品', '个', 50, 5],
        ];
        
        $this->exportExcel($headers, $data, '库存导入模板');
    }

    private function readExcel($filePath)
    {
        $extension = pathinfo($filePath, PATHINFO_EXTENSION);
        
        if ($extension === 'xlsx') {
            $zip = new \ZipArchive();
            if ($zip->open($filePath) === true) {
                $xmlContent = $zip->getFromName('xl/sharedStrings.xml');
                $sheetContent = $zip->getFromName('xl/worksheets/sheet1.xml');
                $zip->close();
                
                $strings = [];
                preg_match_all('/<t>(.*?)<\/t>/', $xmlContent, $matches);
                if (isset($matches[1])) {
                    $strings = $matches[1];
                }
                
                preg_match_all('/<c.*?>(.*?)<\/c>/', $sheetContent, $cellMatches);
                $cells = [];
                foreach ($cellMatches[1] as $cell) {
                    if (preg_match('/<v>(\d+)<\/v>/', $cell, $vMatch)) {
                        $cells[] = $strings[intval($vMatch[1])] ?? '';
                    } elseif (preg_match('/<t>(.*?)<\/t>/', $cell, $tMatch)) {
                        $cells[] = $tMatch[1];
                    } else {
                        $cells[] = '';
                    }
                }
                
                $rows = array_chunk($cells, 7);
                array_shift($rows);
                
                $result = [];
                $rowNum = 2;
                foreach ($rows as $row) {
                    if (empty(array_filter($row))) continue;
                    $result[] = [
                        'row' => $rowNum++,
                        'code' => $row[0] ?? '',
                        'barcode' => $row[1] ?? '',
                        'name' => $row[2] ?? '',
                        'category' => $row[3] ?? '',
                        'unit' => $row[4] ?? '',
                        'stock' => intval($row[5] ?? 0),
                        'min_stock' => intval($row[6] ?? 10)
                    ];
                }
                return $result;
            }
        }
        
        return [];
    }

    private function exportExcel($headers, $data, $filename)
    {
        $xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>';
        $xml .= '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
        $xml .= '<sheet name="Sheet1"><row>';
        
        foreach ($headers as $header) {
            $xml .= '<c><t>' . htmlspecialchars($header) . '</t></c>';
        }
        $xml .= '</row>';
        
        foreach ($data as $row) {
            $xml .= '<row>';
            foreach ($row as $cell) {
                $xml .= '<c><t>' . htmlspecialchars((string)$cell) . '</t></c>';
            }
            $xml .= '</row>';
        }
        
        $xml .= '</sheet></workbook>';
        
        header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        header('Content-Disposition: attachment;filename="' . $filename . '.xlsx"');
        header('Cache-Control: max-age=0');
        
        $zip = new \ZipArchive();
        $zip->open('php://output', \ZipArchive::CREATE);
        $zip->addFromString('xl/worksheets/sheet1.xml', $xml);
        $zip->addFromString('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>');
        $zip->addFromString('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/worksheets/sheet1.xml"/></Relationships>');
        $zip->close();
        exit;
    }
}
