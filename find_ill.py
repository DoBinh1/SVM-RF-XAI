import re
import sys

# Reconfigure stdout to use utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all <img tags and print their class and attribute info
matches = re.finditer(r'<img[^>]+>', content)
for m in matches:
    start_idx = m.start()
    # Find the line number
    line_no = content.count('\n', 0, start_idx) + 1
    tag = m.group(0)
    # Truncate the src attribute if it's base64 to keep print output clean
    clean_tag = re.sub(r'src="data:[^"]+"', 'src="data:image/png;base64,..."', tag)
    print(f"Line {line_no}: {clean_tag}")
