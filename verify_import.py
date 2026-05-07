import os
import sys
sys.path.insert(0, r'd:\dev\project\ThinkAdmin')

# Simulate the PHP logic to verify correctness
import zipfile
import xml.etree.ElementTree as ET
import re
import json
from datetime import datetime, timedelta

xlsx_path = r"d:\dev\project\ThinkAdmin\resoure\2025.5月翰林送货明细.xlsx"

def excel_serial_to_date(serial):
    """Excel date serial number to date string (PHP compatible)"""
    base = datetime(1899, 12, 30)
    return (base + timedelta(days=int(serial))).strftime('%Y-%m-%d')

def read_shared_strings(z):
    strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            content = f.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'<t[^>]*>(.*?)</t>', content)
        for m in matches:
            strings.append(m)
    return strings

def parse_sheet_rows(xml, shared_strings):
    """Parse rows from sheet XML, same logic as PHP"""
    row_matches = re.findall(r'<row[^>]*>(.*?)</row>', xml, re.DOTALL)
    rows = []
    
    for row_xml in row_matches:
        cell_matches = re.findall(r'<c[^>]*>(.*?)</c>', row_xml, re.DOTALL)
        cells = {}
        
        for cell_xml in cell_matches:
            cell_type = ''
            tm = re.search(r' t="([^"]*)"', cell_xml)
            if tm:
                cell_type = tm.group(1)
            
            ref = ''
            rm = re.search(r' r="([^"]*)"', cell_xml)
            if rm:
                ref = rm.group(1)
            
            value = ''
            vm = re.search(r'<v>(.*?)</v>', cell_xml)
            if vm:
                raw = vm.group(1)
                if cell_type == 's':
                    idx = int(raw)
                    value = shared_strings[idx] if 0 <= idx < len(shared_strings) else ''
                elif cell_type == 'b':
                    value = 'true' if raw == '1' else 'false'
                else:
                    value = raw
            else:
                im = re.search(r'<is><t>(.*?)</t></is>', cell_xml)
                if im:
                    value = im.group(1)
            
            cells[ref] = value
        
        if cells:
            rows.append(cells)
    
    return rows

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

def looks_like_data_row(values, header_index):
    name_idx = header_index.get('name', 2)
    barcode_idx = header_index.get('barcode', 1)
    qty_idx = header_index.get('quantity', 5)
    
    name = str(values[name_idx] if name_idx < len(values) else '').strip()
    barcode = str(values[barcode_idx] if barcode_idx < len(values) else '').strip()
    
    if name or (barcode.isdigit() and len(barcode) >= 8):
        return True
    return False

def build_header_index(headers):
    values = list(headers.values())
    index = {k: None for k in ['line_no','barcode','name','box_spec','box_count','quantity','unit','cost_price','total_amount','retail_price']}
    
    patterns = {
        'line_no': ['行号', '序号', 'No', 'Line'],
        'barcode': ['货号', '条码', '商品编码', 'Barcode', 'EAN'],
        'name': ['商品名称', '名称', 'Name', '品名'],
        'box_spec': ['箱规', '规格', '包络', 'Box'],
        'box_count': ['箱数', '箱', 'Carton'],
        'quantity': ['数量', 'Quantity', 'Qty'],
        'unit': ['单位', 'Unit'],
        'cost_price': ['供货价', '进价', '成本价', 'Cost'],
        'total_amount': ['金额汇总', '金额', '小计', 'Amount'],
        'retail_price': ['建议售价', '售价', '零售价', 'Price'],
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

# Main analysis
with zipfile.ZipFile(xlsx_path, 'r') as z:
    shared_strings = read_shared_strings(z)
    print(f"Shared strings: {len(shared_strings)}")
    
    sheet_num = 1
    while f'xl/worksheets/sheet{sheet_num}.xml' in z.namelist():
        sheet_xml = z.read(f'xl/worksheets/sheet{sheet_num}.xml').decode('utf-8', errors='ignore')
        rows = parse_sheet_rows(sheet_xml, shared_strings)
        
        print(f"\n{'='*70}")
        print(f"Sheet {sheet_num}: {len(rows)} rows parsed")
        print(f"{'='*70}")
        
        if len(rows) < 4:
            print("  SKIP: too few rows")
            sheet_num += 1
            continue
        
        # Row0 = title (field1)
        title = list(rows[0].values())[0] if rows[0] else ''
        # Also check if title is in 2nd cell
        r0_vals = list(rows[0].values())
        if len(r0_vals) > 1 and len(r0_vals[1]) > len(title):
            title = r0_vals[1]
        print(f"  Field1(Sheet名): {title}")
        
        # Row1 = customer + date
        customer = extract_customer(rows[0], rows[1] if len(rows) > 1 else {})
        delivery_date = extract_date(rows[0], rows[1] if len(rows) > 1 else {})
        print(f"  Field2(客户): {customer}")
        print(f"  Field3(日期): {delivery_date}")
        
        # Row2 = headers
        headers = rows[2] if len(rows) > 2 else {}
        header_vals = list(headers.values())
        print(f"  表头: {' | '.join(str(v) for v in header_vals)}")
        
        header_index = build_header_index(headers)
        print(f"  索引: {json.dumps(header_index, ensure_ascii=False)}")
        
        # Parse items from row3+
        items = []
        for i in range(3, len(rows)):
            vals = list(rows[i].values())
            
            # Skip summary & sign rows
            first_val = str(vals[0] if vals else '').strip()
            if '金额小计' in first_val:
                print(f"  SKIP row {i}: 金额小计")
                continue
            if '核准人' in first_val:
                print(f"  SKIP row {i}: 核准人")
                continue
            
            if looks_like_data_row(vals, header_index):
                item = map_row_to_item(vals, header_index)
                if item.get('name') or item.get('barcode'):
                    items.append(item)
        
        total_amount = sum(float(it.get('total_amount', 0) or 0) for it in items)
        total_qty = sum(int(it.get('quantity', 0) or 0) for it in items)
        print(f"  {len(items)} items | 总数量:{total_qty} | 总金额:¥{total_amount:.2f}")
        
        for it in items[:3]:
            print(f"    {it['line_no']:>3} | {it['barcode'][:16]:>16} | {it['name'][:30]:30} | {it['quantity']:>5} | {it['unit']:4} | ¥{it['cost_price']}")
        if len(items) > 3:
            print(f"    ... ({len(items)-3} more)")
        
        sheet_num += 1

print("\n" + "=" * 70)
print("VALIDATION COMPLETE!")
