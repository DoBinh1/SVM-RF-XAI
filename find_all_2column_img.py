import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all slides
slides = re.split(r'<!-- \d+ [A-Z0-9 /]+ -->', content)
slide_comments = re.findall(r'<!-- \d+ [A-Z0-9 /]+ -->', content)

for i, slide in enumerate(slides[1:]):
    comment = slide_comments[i] if i < len(slide_comments) else "UNKNOWN"
    if 'imgwrap' in slide and ('g2' in slide or 'g5' in slide):
        print(f"Slide: {comment}")
        # Print first few lines of the slide content
        clean_slide = re.sub(r'src="data:image/png;base64,[^"]+"', 'src="data:image/png;base64,..."', slide)
        lines_printed = 0
        for line in clean_slide.split('\n'):
            if line.strip():
                print(f"  {line.strip()}")
                lines_printed += 1
                if lines_printed >= 10:
                    break
        print("-" * 50)
