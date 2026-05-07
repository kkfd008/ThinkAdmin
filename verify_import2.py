# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime, timedelta

xlsx_path = r"d:\dev\project\ThinkAdmin\resoure\2025.5月翰林送货明细.xlsx"

def excel_serial_to_date(serial):
    base = datetime(1899, 12, 30)
    return (base + timedelta(days=int(serial))).strftime('%Y-m-d')  # noqa: W605

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

def read_shared_strings(z):
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
        for si in tree.findall('.//{%s}si' % NS):
            texts = []
            for t in si.iter('{%s}t' % NS):
                if t.text:
                    texts.append(t.text)
            strings.append(''.join(texts))
    return strings

def parse_sheet_rows(z, sheet_num, shared_strings):
    fname = 'xl/worksheets/sheet%d.xml' % sheet_num
    if fname not in z.namelist():
        return []
    with z.open(fname) as f:
        tree = ET.parse(f)
    
    rows_out = []
    for row in tree.findall('.//{%s}row' % NS):
        cells = {}
        for c in row.findall('{%s}c' % NS):
            ref = c.get('r', '')
            cell_type = c.get('t', '')
            v_el = c.find('{%s}v' % NS)
            value = ''
            if v_el is not None and v_el.text is not None:
                if cell_type == 's':
                    idx = int(v_el.text)
                    value = shared_strings[idx] if 0 <= idx < len(shared_strings) else ''
                elif cell_type == 'b':
                    value = 'true' if v_el.text == '1' else 'false'
                else:
                    value = v_el.text
            cells[ref] = value
        if cells:
            rows_out.append(cells)
    return rows_out

def extract_customer(row0, row1):
    combined = list(row0.values()) + list(row1.values())
    for i, val in enumerate(combined):
        val = str(val)
        if '客户' in val and i + 1 < len(combined):
            customer = str(combined[i + 1]).strip()
            if customer and '日期' not in customer:
                return customer
    for v in row1.values():
        v = str(v).strip()
        if '汇得行' in v or '翰林' in v:
            return v
    return ''

def extract_date(row0, row1):
    combined = list(row0.values()) + list(row1.values())
    for i, val in enumerate(combined):
        val = str(val).strip()
        if '日期' in val and i + 1 < len(combined):
            date_val = str(combined[i + 1]).strip()
            if date_val.isdigit() and len(date_val) <= 5:
                return excel_serial_to_date(int(date_val))
    for v in combined:
        v = str(v).strip()
        if v.isdigit() and len(v) == 5 and 40000 < int(v) < 60000:
            return excel_serial_to_date(int(v))
    return ''

def build_header_index(headers):
    values = list(headers.values())
    index = {k: None for k in ['line_no','barcode','name','box_spec','box_count','quantity','unit','cost_price','total_amount','retail_price']}
    patterns = {
        'line_no': ['行号', '序号'],
        'barcode': ['货号', '条码'],
        'name': ['商品名称', '名称', '品名'],
        'box_spec': ['箱规', '规格'],
        'box_count': ['箱数'],
        'quantity': ['数量'],
        'unit': ['单位'],
        'cost_price': ['供货价', '进价', '成本价'],
        'total_amount': ['金额汇总', '金额', '小计'],
        'retail_price': ['建议售价', '售价', '零售价'],
    }
    for col, header in enumerate(values):
        header = str(header).strip()
        for field, pats in patterns.items():
            if index[field] is None:
                for p in pats:
                    if p in header:
                        index[field] = col
                        break
    default_order = list(index.keys())
    for pos, field in enumerate(default_order):
        if index[field] is None:
            index[field] = pos
    return index

def looks_like_data_row(values, header_index):
    name_idx = header_index.get('name', 2)
    barcode_idx = header_index.get('barcode', 1)
    name = str(values[name_idx] if name_idx < len(values) else '').strip()
    barcode = str(values[barcode_idx] if barcode_idx < len(values) else '').strip()
    return bool(name or (barcode.isdigit() and len(barcode) >= 8))

def map_row_to_item(values, header_index):
    field_keys = ['line_no','barcode','name','box_spec','box_count','quantity','unit','cost_price','total_amount','retail_price']
    item = {}
    for key in field_keys:
        col = header_index.get(key)
        val = str(values[col] if col is not None and col < len(values) else '').strip()
        item[key] = val
    if not item.get('line_no'):
        item['line_no'] = '0'
    if not item.get('unit'):
        item['unit'] = '个'
    return item

# ---- MAIN ----
with zipfile.ZipFile(xlsx_path, 'r') as z:
    shared_strings = read_shared_strings(z)
    print(f"Shared strings: {len(shared_strings)}")

    sheet_num = 1
    while True:
        rows = parse_sheet_rows(z, sheet_num, shared_strings)
        if not rows:
            break

        print(f"\n{'='*70}")
        print(f"Sheet {sheet_num}: {len(rows)} rows")
        print(f"{'='*70}")

        if len(rows) < 4:
            print("  SKIP: too few rows")
            sheet_num += 1
            continue

        # Row0 = title (field1)
        r0v = list(rows[0].values())
        title = r0v[0] if r0v else ''
        if len(r0v) > 1 and r0v[1] and len(str(r0v[1])) > len(str(title)):
            title = r0v[1]
        print(f"  [F1] Sheet: {title}")

        # Row1 = customer + date
        customer = extract_customer(rows[0], rows[1] if len(rows) > 1 else {})
        delivery_date = extract_date(rows[0], rows[1] if len(rows) > 1 else {})
        print(f"  [F2] 客户: {customer}")
        print(f"  [F3] 日期: {delivery_date}")

        # Row2 = headers
        headers = rows[2] if len(rows) > 2 else {}
        header_vals = list(headers.values())
        print(f"  表头: {' | '.join(str(v) for v in header_vals)}")

        header_index = build_header_index(headers)
        print(f"  索引: {json.dumps(header_index, ensure_ascii=False)}")

        # items from row3+
        items = []
        for i in range(3, len(rows)):
            vals = list(rows[i].values())
            first_val = str(vals[0] if vals else '').strip()
            if u'金额小计' in first_val:
                continue
            if u'核准人' in first_val:
                continue
            if looks_like_data_row(vals, header_index):
                item = map_row_to_item(vals, header_index)
                if item.get('name') or item.get('barcode'):
                    items.append(item)

        total_amount = sum(float(it.get('total_amount', 0) or 0) for it in items)
        total_qty = sum(int(it.get('quantity', 0) or 0) for it in items)
        print(f"  商品数: {len(items)} | 总数量: {total_qty} | 总金额: {total_amount:.2f}")

        for it in items[:3]:
            print(f"    {it['line_no']:>3} | {it['barcode'][:16]:>16} | {it['name'][:35]:35} | {it['quantity']:>5} | {it['unit']:4} | {it['cost_price']}")
        if len(items) > 3:
            print(f"    ... ({len(items)-3} more)")

        sheet_num += 1

print(f"\n{'='*70}")
print("Done! All sheets parsed successfully!")
