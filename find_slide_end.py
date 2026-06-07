import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "<!-- 11 WAVEFORM -->"
start_idx = content.find(start_marker)
if start_idx != -1:
    # Find the next slide comment, which starts with <!-- followed by a number
    next_slide_match = re.search(r'<!-- \d+ [A-Z ]+ -->', content[start_idx + len(start_marker):])
    if next_slide_match:
        end_idx = start_idx + len(start_marker) + next_slide_match.start()
        slide_text = content[start_idx:end_idx]
        # Strip the long base64 string to keep stdout readable
        clean_text = re.sub(r'src="data:image/png;base64,[^"]+"', 'src="data:image/png;base64,..."', slide_text)
        print("MATCHED SLIDE CONTENT:")
        print(clean_text)
        print("\nNEXT SLIDE COMMENT:")
        print(next_slide_match.group(0))
    else:
        print("Could not find the next slide comment!")
else:
    print("Could not find start marker!")
