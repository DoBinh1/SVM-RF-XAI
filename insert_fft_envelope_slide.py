import base64
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Reconfigure stdout for UTF-8 to prevent encoding errors on Windows
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(r"d:\[Lab] HUST\nhà máy")
html_path = base_dir / "slides" / "BaiGiang_CWRU_v2.html"
img_path = base_dir / "figures" / "envelope_comparison_4steps.png"

if not html_path.exists():
    print(f"Error: HTML slide source not found at {html_path}")
    sys.exit(1)

if not img_path.exists():
    print(f"Error: Image not found at {img_path}")
    sys.exit(1)

# Encode image to base64
print(f"Encoding envelope comparative plot: {img_path}")
img_data = img_path.read_bytes()
base64_str = base64.b64encode(img_data).decode("utf-8")

# Read HTML slide source
print(f"Reading HTML source file: {html_path}")
html_content = html_path.read_text(encoding="utf-8")
soup = BeautifulSoup(html_content, "html.parser")

# Find Slide 20 (4 bước "bóc" tần số lỗi)
sections = soup.find_all("section", class_="slide")
target_slide = None
for sec in sections:
    h2_tag = sec.find("h2")
    if h2_tag and '4 bước "bóc" tần số lỗi' in h2_tag.text:
        target_slide = sec
        break

if target_slide is None:
    print("Error: Could not find Slide '4 bước \"bóc\" tần số lỗi' in HTML")
    sys.exit(1)

# Find the image tag inside Slide 20 and replace its src with the base64 envelope plot
img_tag = target_slide.find("img", class_="ill")
if img_tag:
    print("Found image tag in Slide 20, replacing src with base64 envelope plot...")
    img_tag["src"] = f"data:image/png;base64,{base64_str}"
    img_tag["alt"] = "FFT thô vs Phổ Bao (OR thực tế CWRU)"
else:
    print("Warning: Image tag not found in Slide 20")

# Update figcap
figcap_tag = target_slide.find("div", class_="figcap")
if figcap_tag:
    print("Updating figure caption...")
    figcap_tag.string = "Lỗi rãnh ngoài (OR) thực tế tại CWRU: Phổ FFT thô không rõ tần số lỗi ↔ Phổ Bao (Envelope) xác định chính xác tần số lỗi BPFO (107.3 Hz)"

# Update Step 1 and Step 4 text
steps = target_slide.find_all("div", class_="step")
for step in steps:
    if "Bước 1" in step.text:
        print("Updating Step 1 text...")
        step.clear()
        
        b_tag = soup.new_tag("b")
        b_tag.string = "Bước 1: Lọc băng thông (Bandpass)"
        step.append("🔍 ")
        step.append(b_tag)
        step.append(soup.new_tag("br"))
        
        span_tag = soup.new_tag("span", style="font-size: 0.85em; opacity: 0.8;")
        span_tag.string = "Lọc giữ lại dải tần số quanh vùng cộng hưởng chính (0.6 - 3 kHz)."
        step.append(span_tag)
        
    elif "Bước 4" in step.text:
        print("Updating Step 4 text...")
        # Recreate the step content with BPFO 107.3 Hz
        step.clear()
        
        b_tag = soup.new_tag("b")
        b_tag.string = "Bước 4: Đọc đỉnh tần số khuyết tật"
        step.append("🎯 ")
        step.append(b_tag)
        step.append(soup.new_tag("br"))
        
        span_tag = soup.new_tag("span", style="font-size: 0.85em; opacity: 0.8;")
        span_tag.string = "Đọc đỉnh tần số lỗi rõ nét: BPFO (107.3 Hz) và các bội số (2×, 3×...)."
        step.append(span_tag)

# Update Speaker Notes
notes_tag = target_slide.find("aside", class_="notes")
if notes_tag:
    print("Updating speaker notes...")
    notes_tag.clear()
    
    p1 = soup.new_tag("p")
    p1.string = ("Đây là phần minh chứng thực tế từ dữ liệu CWRU. Ở slide trước, ta thấy phổ FFT thô của ca lỗi "
                 "vòng ngoài OR gần như bất lực trong việc chỉ ra vạch lỗi 107.3 Hz. Nhưng ở đây, sau khi đi qua "
                 "4 bước của Envelope Analysis, vạch lỗi BPFO 107.3 Hz cùng các hài bậc cao hiện lên cực kỳ rõ nét.")
    
    p2 = soup.new_tag("p")
    p2.string = ("Nhắc lại 4 bước cốt lõi: lọc băng thông vùng cộng hưởng 0.6 - 3 kHz; biến đổi Hilbert để bóc tách "
                 "lấy đường bao; tính FFT trên đường bao đó; và cuối cùng là đối chiếu tần số lỗi đặc trưng. Phương "
                 "pháp này giải quyết triệt để điểm mù mất thông tin thời gian và chôn vùi tần số của FFT thô.")
    
    notes_tag.append(p1)
    notes_tag.append(p2)

# Save the updated HTML content back to file
print(f"Writing updated HTML back to: {html_path}")
html_path.write_text(str(soup), encoding="utf-8")

print("[SUCCESS] HTML slide source updated successfully with 2x2 envelope comparative plot!")
