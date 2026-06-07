import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find "Mỗi lỗi một" and get the surrounding slide comments
title_str = 'Mỗi lỗi một'
title_idx = content.find(title_str)
if title_idx != -1:
    # Look backwards for the slide start comment <!-- \d+ ... -->
    preceding = content[max(0, title_idx - 1000):title_idx]
    start_matches = list(re.finditer(r'<!-- \d+ [A-Z0-9 ]+ -->', preceding))
    if start_matches:
        start_comment = start_matches[-1].group(0)
        start_idx = content.find(start_comment)
        print(f"Start comment: {start_comment} at index {start_idx}")
        
        # Look forwards for the next slide start comment
        following = content[title_idx:]
        next_matches = list(re.finditer(r'<!-- \d+ [A-Z0-9 ]+ -->', following))
        if next_matches:
            next_comment = next_matches[0].group(0)
            end_idx = title_idx + next_matches[0].start()
            print(f"End comment: {next_comment} at index {end_idx}")
            
            # Print slide content
            slide_text = content[start_idx:end_idx]
            clean_text = re.sub(r'src="data:image/png;base64,[^"]+"', 'src="data:image/png;base64,..."', slide_text)
            print("MATCHED SLIDE 16 CONTENT:")
            print(clean_text)
        else:
            print("Could not find next slide comment!")
    else:
        print("Could not find start comment!")
else:
    print("Could not find title string!")
