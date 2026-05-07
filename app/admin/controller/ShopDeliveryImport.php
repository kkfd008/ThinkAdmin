<?php

declare(strict_types=1);

namespace app\admin\controller;

use app\admin\model\ShopDelivery;
use app\admin\model\ShopDeliveryItem;
use app\admin\model\ShopProduct;
use app\admin\model\ShopStock;
use app\admin\model\ShopStockLog;
use think\admin\Controller;
use think\admin\service\AdminService;

class ShopDeliveryImport extends Controller
{
    private $headerMap = [
        'barcode' => null, 'name' => null, 'box_spec' => null, 'box_count' => null,
        'quantity' => null, 'unit' => null, 'cost_price' => null, 'retail_price' => null,
    ];
    private $fieldKeys = ['barcode', 'name', 'box_spec', 'box_count', 'quantity', 'unit', 'cost_price', 'retail_price'];

    public function index()
    {
        $this->title = '入库单导入';
        $this->fetch();
    }

    public function preview()
    {
        $file = $this->request->file('file');
        if (empty($file)) $this->error('请选择要导入的文件！');

        $ext = strtolower(pathinfo($file->getOriginalName(), PATHINFO_EXTENSION));
        if (!in_array($ext, ['xlsx', 'xls'])) $this->error('只允许上传 .xlsx 或 .xls 格式的文件！');

        $info = $file->move(sysconf('storage.local.root') ?: syspath('runtime'));
        if (!$info) $this->error('文件上传失败！');

        $sheets = $this->parseExcel($info->getRealPath());
        if (empty($sheets)) $this->error('文件内容为空或格式不正确！');

        $this->app->session->set('delivery_import_data', $sheets);

        $this->sheets = $sheets;
        $this->title = '导入预览';
        $this->fetch();
    }

    public function import()
    {
        $sheets = $this->app->session->get('delivery_import_data');
        if (empty($sheets)) $this->error('会话已过期，请重新上传文件！');

        $selected = $this->request->post('sheet_ids/a', []);
        if (empty($selected)) $this->error('请至少选择一个入库单！');

        $success = 0;
        $failed = 0;
        $errors = [];

        foreach ($selected as $idx) {
            if (!isset($sheets[$idx])) continue;
            $sheet = $sheets[$idx];
            try {
                $totalAmount = 0;
                $totalQuantity = 0;
                foreach ($sheet['items'] as $it) {
                    $totalAmount += floatval($it['cost_price'] ?? 0) * intval($it['quantity'] ?? 0);
                    $totalQuantity += intval($it['quantity'] ?? 0);
                }

                $deliveryId = ShopDelivery::mk()->insertGetId([
                    'supplier_name' => $sheet['customer'] ?: '',
                    'delivery_date' => $sheet['delivery_date'] ?: date('Y-m-d'),
                    'order_type' => '入库',
                    'item_count' => count($sheet['items']),
                    'total_quantity' => $totalQuantity,
                    'total_amount' => round($totalAmount, 2),
                    'remark' => $sheet['title'],
                ]);

                foreach ($sheet['items'] as $item) {
                    $item['delivery_id'] = $deliveryId;
                    $item['price'] = $item['retail_price'] ?? '0';
                    unset($item['retail_price']);
                    ShopDeliveryItem::mk()->insert($item);

                    $qty = intval($item['quantity'] ?? 0);
                    $barcode = $item['barcode'] ?? '';
                    $name = $item['name'] ?? '';
                    if ($qty > 0) {
                        $this->syncProductAndStock($barcode, $name, $item, $qty);
                    }
                }
                $success++;
            } catch (\Exception $e) {
                $failed++;
                $errors[] = "【{$sheet['sheet_name']}】: " . $e->getMessage();
            }
        }

        $this->app->session->delete('delivery_import_data');

        sysoplog('入库单管理', "导入库单，成功{$success}个，失败{$failed}个");

        if ($failed > 0) {
            $this->success("导入完成！成功{$success}个，失败{$failed}个", '', ['errors' => array_slice($errors, 0, 10)]);
        } else {
            $this->success("全部导入成功！共{$success}个库单");
        }
    }

    private function syncProductAndStock(string $barcode, string $name, array $item, int $qty): void
    {
        $product = null;
        if (!empty($barcode)) {
            $product = ShopProduct::mk()->where('barcode', $barcode)->find();
        }
        if (!$product && !empty($name)) {
            $product = ShopProduct::mk()->where('name', $name)->find();
        }
        $productData = [
            'barcode' => $barcode,
            'name' => $name,
            'box_spec' => floatval($item['box_spec'] ?? 0),
            'cost_price' => floatval($item['cost_price'] ?? 0),
            'price' => floatval($item['retail_price'] ?? floatval($item['cost_price'] ?? 0) * 1.15),
        ];
        if ($product) {
            $product->save($productData);
            $productId = intval($product['id']);
        } else {
            $productId = intval(ShopProduct::mk()->insertGetId($productData));
        }

        $stock = ShopStock::mk()->where(['product_id' => $productId])->find();
        if ($stock) {
            $stock->save(['stock' => intval($stock['stock']) + $qty]);
        } else {
            ShopStock::mk()->insert(['product_id' => $productId, 'stock' => $qty]);
        }

        ShopStockLog::mk()->insert([
            'barcode' => $barcode, 'name' => $name,
            'type' => 1, 'quantity' => $qty,
        ]);
    }

    // ====== Excel 解析（不变） ======

    private function parseExcel(string $filePath): array
    {
        if (!class_exists('\\ZipArchive')) throw new \Exception('缺少ZipArchive扩展');
        $zip = new \ZipArchive();
        if ($zip->open($filePath) !== true) return [];
        $sharedStrings = $this->readSharedStrings($zip);
        $result = [];
        $sheetNum = 1;
        while ($zip->locateName("xl/worksheets/sheet{$sheetNum}.xml") !== false) {
            $rows = $this->parseSheetRows($zip->getFromName("xl/worksheets/sheet{$sheetNum}.xml"), $sharedStrings);
            if (count($rows) < 4) { $sheetNum++; continue; }
            $sheetName = $rows[0][1] ?? $rows[0][0] ?? "Sheet{$sheetNum}";
            $customer = $this->extractCustomer($rows[0], $rows[1] ?? []);
            $deliveryDate = $this->extractDate($rows[0], $rows[1] ?? []);
            $headerIndex = $this->buildHeaderIndex($rows[2] ?? []);
            $items = [];
            for ($i = 3; $i < count($rows); $i++) {
                $vals = array_values($rows[$i]);
                if (stripos($vals[0] ?? '', '金额小计') !== false) continue;
                if (stripos($vals[0] ?? '', '核准人') !== false) continue;
                if (!$this->looksLikeDataRow($rows[$i], $headerIndex)) continue;
                $item = $this->mapRowToItem($rows[$i], $headerIndex);
                if (!empty($item['name']) || !empty($item['barcode'])) $items[] = $item;
            }
            $result[] = ['sheet_name' => $sheetName, 'title' => $sheetName, 'customer' => $customer, 'delivery_date' => $deliveryDate, 'items' => $items, 'summary' => $this->calculateSummary($items)];
            $sheetNum++;
        }
        $zip->close();
        return $result;
    }

    private function readSharedStrings(\ZipArchive $zip): array
    {
        $strings = [];
        $ssContent = $zip->getFromName('xl/sharedStrings.xml');
        if (empty($ssContent)) return $strings;
        $ssContent = preg_replace('/\sxmlns[=][\"][^\"]*[\"]/', '', $ssContent, 1);
        $doc = new \DOMDocument();
        @$doc->loadXML($ssContent);
        foreach ($doc->getElementsByTagName('si') as $si) {
            $ts = '';
            foreach ($si->getElementsByTagName('t') as $t) $ts .= $t->textContent;
            $strings[] = $ts;
        }
        return $strings;
    }

    private function parseSheetRows(string $xml, array $sharedStrings): array
    {
        $xml = preg_replace('/\sxmlns[=][\"][^\"]*[\"]/', '', $xml, 1);
        $doc = new \DOMDocument();
        @$doc->loadXML($xml);
        $rows = [];
        foreach ($doc->getElementsByTagName('row') as $rowNode) {
            $cells = [];
            foreach ($rowNode->getElementsByTagName('c') as $cellNode) {
                $ref = $cellNode->getAttribute('r');
                $type = $cellNode->getAttribute('t');
                $vNode = $cellNode->getElementsByTagName('v')->item(0);
                $value = '';
                if ($vNode) {
                    $raw = $vNode->textContent;
                    if ($type === 's') { $idx = intval($raw); $value = $sharedStrings[$idx] ?? ''; }
                    elseif ($type === 'b') $value = $raw === '1' ? 'true' : 'false';
                    else $value = $raw;
                }
                $isNode = $cellNode->getElementsByTagName('is')->item(0);
                if ($isNode) {$value=''; foreach ($isNode->getElementsByTagName('t') as $tNode) $value.=$tNode->textContent;}
                $cells[$ref] = $value;
            }
            if (!empty($cells)) $rows[] = $cells;
        }
        return $rows;
    }

    private function extractCustomer(array $row0, array $row1): string
    {
        $combined = array_merge(array_values($row0), array_values($row1));
        foreach ($combined as $i => $v) {
            if (stripos((string)$v, '客户') !== false && isset($combined[$i+1])) {
                $c = trim((string)$combined[$i+1]);
                if (!empty($c) && stripos($c, '日期') === false) return $c;
            }
        }
        foreach ($row1 as $v) {if(stripos((string)$v,'汇得行')!==false||stripos((string)$v,'翰林')!==false) return trim((string)$v);}
        return '';
    }

    private function extractDate(array $row0, array $row1): string
    {
        $combined = array_merge(array_values($row0), array_values($row1));
        foreach ($combined as $i => $v) {
            if (stripos(trim((string)$v), '日期') !== false && isset($combined[$i+1])) {
                $d = trim((string)$combined[$i+1]);
                if (is_numeric($d) && strlen($d) <= 5) return $this->excelSerialToDate(intval($d));
                if (preg_match('/^\d{4}[-\/]\d{1,2}[-\/]\d{1,2}$/', $d)) return date('Y-m-d', strtotime($d));
                return $d;
            }
        }
        foreach ($combined as $v) {$v=trim((string)$v); if(is_numeric($v)&&strlen($v)===5&&intval($v)>40000&&intval($v)<60000) return $this->excelSerialToDate(intval($v));}
        return '';
    }

    private function excelSerialToDate(int $serial): string { return (new \DateTime('1899-12-30'))->modify("+{$serial} days")->format('Y-m-d'); }

    private function buildHeaderIndex(array $headers): array
    {
        $index = $this->headerMap;
        $values = array_values($headers);
        $patterns = [
            'barcode' => ['货号', '条码'], 'name' => ['商品名称', '名称', '品名'],
            'box_spec' => ['箱规', '规格'], 'box_count' => ['箱数'],
            'quantity' => ['数量'], 'unit' => ['单位'],
            'cost_price' => ['供货价', '进价', '成本价'], 'retail_price' => ['建议售价', '售价', '零售价'],
        ];
        foreach ($values as $col => $header) {
            $header = trim((string)$header);
            foreach ($patterns as $field => $pats) {
                if ($index[$field] === null) {
                    foreach ($pats as $p) {if(stripos($header,$p)!==false){$index[$field]=$col;break;}}
                }
            }
        }
        foreach (array_keys($this->headerMap) as $pos => $field) {if($index[$field]===null)$index[$field]=$pos;}
        return $index;
    }

    private function looksLikeDataRow(array $row, array $headerIndex): bool
    {
        $values = array_values($row);
        if (empty($values)) return false;
        $name = trim((string)($values[$headerIndex['name'] ?? 2] ?? ''));
        $barcode = trim((string)($values[$headerIndex['barcode'] ?? 1] ?? ''));
        return !empty($name) || (is_numeric($barcode) && strlen($barcode) >= 8);
    }

    private function mapRowToItem(array $row, array $headerIndex): array
    {
        $values = array_values($row);
        $item = [];
        foreach ($this->fieldKeys as $key) {
            $col = $headerIndex[$key] ?? null;
            $item[$key] = $col !== null ? trim((string)($values[$col] ?? '')) : '';
        }
        if (empty($item['unit'])) $item['unit'] = '个';
        return $item;
    }

    private function calculateSummary(array $items): array
    {
        $totalAmount = 0; $totalQuantity = 0;
        foreach ($items as $item) {$totalAmount += floatval($item['cost_price']??0)*intval($item['quantity']??0); $totalQuantity += intval($item['quantity']??0);}
        return ['item_count' => count($items), 'total_quantity' => $totalQuantity, 'total_amount' => round($totalAmount, 2)];
    }
}
