import os
import zipfile
import xml.etree.ElementTree as ET
import re

xlsx_path = r"d:\dev\project\ThinkAdmin\resoure\2025.5月翰林送货明细.xlsx"

def parse_xlsx(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"=== Analyzing: {os.path.basename(filepath)} ===")
    print(f"File size: {os.path.getsize(filepath)} bytes\n")

    with zipfile.ZipFile(filepath, 'r') as z:
        # List all files in archive
        print("Archive contents:")
        for f in z.namelist():
            print(f"  {f}")

        # Read shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in root.findall('.//ns:si', ns):
                    texts = []
                    for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                        if t.text:
                            texts.append(t.text)
                    shared_strings.append(''.join(texts))

        print(f"\nShared strings count: {len(shared_strings)}")

        # Read each worksheet
        sheet_num = 1
        while f'xl/worksheets/sheet{sheet_num}.xml' in z.namelist():
            with z.open(f'xl/worksheets/sheet{sheet_num}.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

                rows = root.findall('.//ns:row', ns)
                print(f"\n{'=' * 80}")
                print(f"Sheet {sheet_num}: {len(rows)} rows")
                print(f"{'=' * 80}")

                # Also try to read dimension
                dim = root.find('.//ns:dimension', ns)
                if dim is not None:
                    ref = dim.get('ref', '')
                    print(f"Dimension ref: {ref}")

                # Parse and print rows
                row_limit = 60
                row_count = 0
                for row in rows:
                    if row_count >= row_limit:
                        print(f"\n... (showing {row_limit} of {len(rows)} rows)")
                        break

                    row_num = row.get('r')
                    cells = []
                    max_col = 0
                    for c in row.findall('ns:c', ns):
                        ref = c.get('r', '')
                        cell_type = c.get('t', '')
                        value_elem = c.find('ns:v', ns)
                        value = ''
                        if value_elem is not None:
                            if cell_type == 's':  # shared string
                                idx = int(value_elem.text)
                                if 0 <= idx < len(shared_strings):
                                    value = shared_strings[idx]
                            elif cell_type == 'b':  # boolean
                                value = value_elem.text
                            else:
                                value = value_elem.text or ''

                        # Extract column letter
                        col_match = re.match(r'([A-Z]+)', ref)
                        if col_match:
                            col_letter = col_match.group(1)
                            col_num = 0
                            for ch in col_letter:
                                col_num = col_num * 26 + (ord(ch) - ord('A') + 1)
                            max_col = max(max_col, col_num)

                        cells.append((ref, value))

                    # Sort cells by column letter
                    cells.sort(key=lambda x: x[0])

                    values = [v for _, v in cells]
                    # Pad to max column
                    if max_col > len(values):
                        values.extend([''] * (max_col - len(values)))

                    if values:
                        line = ' | '.join(str(v) if v is not None else '' for v in values)
                        print(f"  Row {row_num}: {line}")

                    row_count += 1

            sheet_num += 1

        if sheet_num == 1:
            print("\nNo worksheets found!")

if __name__ == '__main__':
    parse_xlsx(xlsx_path)
    print("\n" + "=" * 80)
    print("Analysis complete!")
