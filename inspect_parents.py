import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for image tags and print their parent wrappers (up to 3 lines above them)
matches = re.finditer(r'<img[^>]+>', content)
for m in matches:
    start_idx = m.start()
    line_no = content.count('\n', 0, start_idx) + 1
    tag = m.group(0)
    clean_tag = re.sub(r'src="data:[^"]+"', 'src="data:image/png;base64,..."', tag)
    
    # Get preceding 300 characters to inspect the parent div
    preceding = content[max(0, start_idx - 300):start_idx]
    parent_divs = re.findall(r'<div[^>]+>', preceding)
    parent_info = parent_divs[-1] if parent_divs else "No parent div found"
    
    print(f"Line {line_no}:")
    print(f"  Parent: {parent_info}")
    print(f"  Img:    {clean_tag}")
