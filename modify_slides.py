import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS .ill definition
old_css = """  .ill{width:100%;max-height:60vh;object-fit:contain;background:#fff;
    border:1px solid var(--line);border-radius:12px;padding:8px;display:block}"""

new_css = """  .ill{max-width:100%;width:auto;max-height:60vh;object-fit:contain;background:#fff;
    border:1px solid var(--line);border-radius:12px;padding:8px;display:block;margin:0 auto}"""

# Check if it was already modified in the previous run
if ".ill{max-width:100%" in content or "width:auto;max-height:60vh" in content:
    print("CSS of .ill was already successfully updated.")
else:
    if old_css in content:
        content = content.replace(old_css, new_css)
        print("Successfully updated CSS definition of .ill!")
    else:
        # Regex search
        css_pattern = r"\.ill\s*\{[^}]*\}"
        match = re.search(css_pattern, content)
        if match:
            print(f"Found existing CSS for .ill: {match.group(0)}")
            content = re.sub(css_pattern, new_css, content)
            print("Updated .ill CSS using regex!")
        else:
            print("Warning: CSS definition of .ill not found!")

# 2. Update inline styles of specific image tags
replacements = [
    (
        'alt="CWRU test stand" style="max-height: 44vh; width: 100%; object-fit: contain;">',
        'alt="CWRU test stand" style="max-height: 44vh; width: auto; max-width: 100%; object-fit: contain;">'
    ),
    (
        'alt="Cấu tạo ổ lăn" style="max-height: 44vh; width: 100%; object-fit: contain;">',
        'alt="Cấu tạo ổ lăn" style="max-height: 44vh; width: auto; max-width: 100%; object-fit: contain;">'
    ),
    (
        'alt="Waveform 4 trạng thái (thực tế CWRU)" style="max-height: 38vh; width: 95%; object-fit: contain;">',
        'alt="Waveform 4 trạng thái (thực tế CWRU)" style="max-height: 38vh; width: auto; max-width: 95%; object-fit: contain;">'
    ),
    (
        'alt="Waveform và FFT" style="max-height: 44vh; width: 100%; object-fit: contain;">',
        'alt="Waveform và FFT" style="max-height: 44vh; width: auto; max-width: 100%; object-fit: contain;">'
    ),
    (
        'alt="FFT thô vs Envelope (OR thực tế CWRU)" style="max-height: 44vh; width: 100%; object-fit: contain;">',
        'alt="FFT thô vs Envelope (OR thực tế CWRU)" style="max-height: 44vh; width: auto; max-width: 100%; object-fit: contain;">'
    ),
    (
        'alt="Spectrogram ví dụ" style="max-height: 44vh; width: 100%; object-fit: contain;">',
        'alt="Spectrogram ví dụ" style="max-height: 44vh; width: auto; max-width: 100%; object-fit: contain;">'
    )
]

for old_str, new_str in replacements:
    # Check if the replacement has already happened
    if new_str in content:
        print(f"Already updated image with alt: {new_str.split('style=')[0]}")
    elif old_str in content:
        content = content.replace(old_str, new_str)
        print(f"Successfully updated image with alt: {old_str.split('style=')[0]}")
    else:
        print(f"Could not find exact tag for replacement: {old_str[:50]}...")

# Save the updated content back to the file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modification complete!")
