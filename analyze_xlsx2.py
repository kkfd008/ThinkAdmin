import os
import zipfile
import xml.etree.ElementTree as ET
import re

xlsx_path = r"d:\dev\project\ThinkAdmin\resoure\2025.5月翰林送货明细.xlsx"

def parse_xlsx(filepath):
    with zipfile.ZipFile(filepath, 'r') as z:
        # Read shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    texts = []
                    for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                        if t.text:
                            texts.append(t.text)
                    shared_strings.append(''.join(texts))

        # Read each worksheet
        sheet_num = 1
        while f'xl/worksheets/sheet{sheet_num}.xml' in z.namelist():
            with z.open(f'xl/worksheets/sheet{sheet_num}.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                rows = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
                print(f"\n{'=' * 60}")
                print(f"Sheet {sheet_num}: {len(rows)} rows")
                print(f"{'=' * 60}")

                # Get dimension
                dim = root.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}dimension')
                if dim is not None:
                    print(f"Dimension: {dim.get('ref', '')}")

                row_limit = 120
                row_count = 0
                for row in rows:
                    if row_count >= row_limit:
                        print(f"\n... (showing {row_limit} of {len(rows)} rows)")
                        break

                    row_num = row.get('r')
                    cells = []
                    for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.get('r', '')
                        cell_type = c.get('t', '')
                        value_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        value = ''
                        if value_elem is not None:
                            if cell_type == 's':
                                idx = int(value_elem.text)
                                if 0 <= idx < len(shared_strings):
                                    value = shared_strings[idx]
                            elif cell_type == 'b':
                                value = value_elem.text
                            else:
                                value = value_elem.text or ''
                        cells.append((ref, value))
                    
                    cells.sort(key=lambda x: x[0])
                    values = [v for _, v in cells]
                    
                    if any(v for v in values):
                        line = ' | '.join(str(v) if v is not None else '' for v in values)
                        print(f"  Row {row_num}: {line}")
                    
                    row_count += 1

            sheet_num += 1

        # Also check for sheet8 onwards
        for name in z.namelist():
            m = re.match(r'xl/worksheets/sheet(\d+)\.xml', name)
            if m:
                sn = int(m.group(1))
                if sn >= sheet_num:
                    print(f"\nAdditional file found: {name}")

if __name__ == '__main__':
    parse_xlsx(xlsx_path)
