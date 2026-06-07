import sys
from pathlib import Path
from pptx import Presentation

# Reconfigure stdout for UTF-8 to prevent encoding errors on Windows
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = Path(r"d:\[Lab] HUST\nhà máy")
pptx_path = base_dir / "slides" / "BaiGiang_CWRU_HUST_v3.pptx"

if not pptx_path.exists():
    print(f"Error: PPTX file not found at {pptx_path}")
    sys.exit(1)

prs = Presentation(str(pptx_path))
print(f"Total slides in generated presentation: {len(prs.slides)}\n")

# Slide 15 should be at index 14 (11 template slides + 4 imported slides, index 14)
slide_idx = 14
if len(prs.slides) <= slide_idx:
    print(f"Error: Slide index {slide_idx} out of range.")
    sys.exit(1)

slide = prs.slides[slide_idx]
print(f"--- DETAILED INSPECTION OF SLIDE {slide_idx + 1} ---")

# Determine slide title
slide_title = ""
if slide.shapes.title:
    slide_title = slide.shapes.title.text
else:
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text:
            slide_title = shape.text
            break
print(f"Title: {slide_title.strip()}")

# Iterate over shapes
print(f"\nShapes found on slide:")
pic_count = 0
for idx, shape in enumerate(slide.shapes):
    shape_type = shape.shape_type
    # Shape types: 13 represents MSO_SHAPE_TYPE.PICTURE, 17 represents MSO_SHAPE_TYPE.TEXT_BOX, etc.
    type_name = str(shape_type)
    if shape_type == 13:
        type_name = "PICTURE"
        pic_count += 1
    elif shape_type == 17:
        type_name = "TEXT_BOX"
    elif shape_type == 1:
        type_name = "RECTANGLE"
        
    text_snippet = ""
    if shape.has_text_frame and shape.text:
        text_snippet = shape.text.replace("\n", " | ")[:120]
        
    # Get shape geometry details (in inches)
    l_in = shape.left.inches
    t_in = shape.top.inches
    w_in = shape.width.inches
    h_in = shape.height.inches
    
    print(f"  [{idx:02d}] Type: {type_name:<10} | Pos: ({l_in:.2f}\", {t_in:.2f}\") | Size: {w_in:.2f}\" x {h_in:.2f}\" | Text: {text_snippet}")

print(f"\nTotal pictures on Slide 15: {pic_count}")
if pic_count > 0:
    print("[VERIFICATION SUCCESS] The image was successfully compiled into Slide 15 of the PPTX file!")
else:
    print("[VERIFICATION FAILED] No pictures found on Slide 15. Please check the image extraction.")
