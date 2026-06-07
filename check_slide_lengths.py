import os
import sys
import re

# Ensure UTF-8 output to prevent Cp1252 print errors
sys.stdout.reconfigure(encoding='utf-8')

current_dir = os.path.dirname(os.path.abspath(__file__))
slides_path = os.path.join(current_dir, 'slides', 'BaiGiang_CWRU.html')

if not os.path.exists(slides_path):
    print("Slides file not found.")
    sys.exit(1)

with open(slides_path, 'r', encoding='utf-8') as f:
    content = f.read()

slides = re.findall(r'<section[^>]*>(.*?)</section>', content, re.DOTALL)

print("Analyzing slide density (visible text character count, elements, and images):")
print(f"Total Slides: {len(slides)}\n")

for idx, slide_html in enumerate(slides, 1):
    # Remove speaker notes and base64 images for fair text count
    clean_slide = re.sub(r'<aside class=["\']notes["\'].*?</aside>', '', slide_html, flags=re.DOTALL)
    clean_slide = re.sub(r'src=["\']data:image/[^;]+;base64,[A-Za-z0-9+/=]+["\']', 'src="[BASE64]"', clean_slide)
    
    # Visible text (remove all HTML tags)
    visible_text = re.sub(r'<[^>]+>', ' ', clean_slide)
    visible_text = re.sub(r'\s+', ' ', visible_text).strip()
    char_len = len(visible_text)
    
    # Check elements
    headings = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', clean_slide, re.DOTALL)
    lists = re.findall(r'<li[^>]*>(.*?)</li>', clean_slide, re.DOTALL)
    keyideas = re.findall(r'<div class=["\']keyidea["\'][^>]*>(.*?)</div>', clean_slide, re.DOTALL)
    images = re.findall(r'<img[^>]+>', clean_slide)
    formulas = re.findall(r'class=["\']formula["\']', clean_slide)
    
    has_image = "Yes" if images else "No"
    has_formula = "Yes" if formulas else "No"
    
    # Identify empty/low density slides (e.g. text length < 250 characters and no image/formula)
    status = "OK"
    if char_len < 200 and not images and not formulas:
        status = "⚠️ VERY EMPTY"
    elif char_len < 100:
        status = "⚠️ EXTREMELY EMPTY"
        
    print(f"Slide {idx:02d}: Headings: {', '.join([re.sub('<[^<]+?>', '', h).strip() for h in headings])[:40]} | Text Len: {char_len} | Image: {has_image} | Formula: {has_formula} | Status: {status}")
