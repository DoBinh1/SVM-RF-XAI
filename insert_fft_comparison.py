import base64
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Reconfigure stdout for UTF-8 to prevent encoding errors on Windows
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(r"d:\[Lab] HUST\nhà máy")
html_path = base_dir / "slides" / "BaiGiang_CWRU_v2.html"
img_path = base_dir / "figures" / "fft_comparison_normal_fault.png"

if not html_path.exists():
    print(f"Error: HTML slide source not found at {html_path}")
    sys.exit(1)

if not img_path.exists():
    print(f"Error: Image not found at {img_path}")
    sys.exit(1)

# Encode image to base64
print(f"Encoding CWRU comparative plot: {img_path}")
img_data = img_path.read_bytes()
base64_str = base64.b64encode(img_data).decode("utf-8")

# Read HTML slide source
print(f"Reading HTML source file: {html_path}")
html_content = html_path.read_text(encoding="utf-8")
soup = BeautifulSoup(html_content, "html.parser")

# Find Slide 15 (Ưu điểm & Hạn chế)
sections = soup.find_all("section", class_="slide")
target_slide = None
for sec in sections:
    h2_tag = sec.find("h2")
    if h2_tag and "Ưu điểm & Hạn chế" in h2_tag.text:
        target_slide = sec
        break

if target_slide is None:
    print("Error: Could not find Slide 'Ưu điểm & Hạn chế của biến đổi Fourier (FFT)' in HTML")
    sys.exit(1)

# Find the image tag inside Slide 15 and replace its src with the comparative plot base64
img_tag = target_slide.find("img", class_="ill")
if img_tag:
    print("Found image tag in Slide 15, replacing src with 2x2 comparison plot...")
    img_tag["src"] = f"data:image/png;base64,{base64_str}"
else:
    print("Warning: Image tag not found in Slide 15")

# Save the updated HTML content back to file
print(f"Writing updated HTML back to: {html_path}")
html_path.write_text(str(soup), encoding="utf-8")

print("[SUCCESS] HTML slide source updated successfully with 2x2 comparative plot!")
