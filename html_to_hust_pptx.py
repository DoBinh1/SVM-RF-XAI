"""
html_to_hust_pptx.py
Dùng BeautifulSoup4 để parse file HTML slide (Reveal.js/custom)
và bổ sung các slide tiếp theo vào template HUST chính thức (phong cách tối - Dark Theme, font Calibri).

Chạy:  python html_to_hust_pptx.py
Output: slides/BaiGiang_CWRU_HUST.pptx
"""

from __future__ import annotations
import base64, io, re, sys
from pathlib import Path
from bs4 import BeautifulSoup, Tag

# Fix Windows console UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ──────────────────────────────────────────────
#  CONSTANTS – Design System (Dark Navy HUST theme)
# ──────────────────────────────────────────────
W = Inches(13.33)          # 16:9 widescreen width
H = Inches(7.5)            # 16:9 widescreen height

# Colours  (R, G, B) - Dark Scheme matching previous style
C_BG        = RGBColor(0x0e, 0x17, 0x26)   # --bg
C_PANEL     = RGBColor(0x15, 0x21, 0x33)   # --panel
C_INK       = RGBColor(0xea, 0xf0, 0xf7)   # --ink  (white-ish)
C_MUTED     = RGBColor(0x9f, 0xb3, 0xc8)   # --muted
C_ACCENT    = RGBColor(0x2d, 0xd4, 0xbf)   # --accent (teal)
C_ACCENT2   = RGBColor(0x38, 0xbd, 0xf8)   # --accent2 (sky)
C_LINE      = RGBColor(0x2a, 0x3a, 0x52)   # --line
C_WARN      = RGBColor(0xfb, 0xbf, 0x24)   # --warn (amber)
C_GOOD      = RGBColor(0x34, 0xd3, 0x99)   # --good (green)
C_BAD       = RGBColor(0xef, 0x44, 0x44)   # --bad  (red)

# Fault colors (Dark theme compatible)
C_NORMAL    = RGBColor(0x2e, 0xcc, 0x71)   # normal class
C_IR        = RGBColor(0xe7, 0x4c, 0x3c)   # ir class
C_OR        = RGBColor(0x34, 0x98, 0xdb)   # or class
C_BALL      = RGBColor(0xf3, 0x9c, 0x12)   # ball class

C_HEADER_BG = RGBColor(0x1c, 0x2c, 0x44)   # table header bg
C_WHITE     = RGBColor(0xff, 0xff, 0xff)
C_CODE_BG   = RGBColor(0x0b, 0x13, 0x20)

FONT_BODY   = "Calibri" # Đổi sang Calibri theo yêu cầu của user
FONT_MONO   = "Consolas" # Đổi sang Consolas cho code

# Layout margins
MAR_L   = Inches(0.55)
MAR_T   = Inches(0.35)
MAR_R   = Inches(0.55)
USABLE_W = W - MAR_L - MAR_R       # ~12.23 in


# ──────────────────────────────────────────────
#  HELPERS – python-pptx low-level
# ──────────────────────────────────────────────

def solid_fill(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color

def no_fill(shape):
    shape.fill.background()

def add_textbox(slide, left, top, width, height,
                text="", font_size=20, bold=False, italic=False,
                color: RGBColor = C_INK, font_name=FONT_BODY,
                align=PP_ALIGN.LEFT, word_wrap=True) -> object:
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = word_wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return txb

def add_rect(slide, left, top, width, height, fill: RGBColor = None,
             line_color: RGBColor = None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    if fill:
        solid_fill(shape, fill)
    else:
        no_fill(shape)
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape

def rgb_from_hex(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def clean_text(tag) -> str:
    """Extract clean text from a BS4 tag, preserving newlines at block elements."""
    if tag is None:
        return ""
    if isinstance(tag, str):
        return tag
    parts = []
    for child in tag.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.name in ("br",):
            parts.append("\n")
        elif child.name in ("p", "li", "div", "tr"):
            parts.append(clean_text(child) + "\n")
        else:
            parts.append(clean_text(child))
    return "".join(parts).strip()

def extract_base64_image(img_tag) -> bytes | None:
    """Return raw bytes from a data:image/... base64 src, or None."""
    if img_tag is None:
        return None
    src = img_tag.get("src", "")
    m = re.match(r"data:image/[^;]+;base64,(.+)", src, re.S)
    if not m:
        return None
    try:
        return base64.b64decode(m.group(1))
    except Exception:
        return None

def add_image_from_bytes(slide, img_bytes: bytes,
                         left, top, width, height):
    """Insert an image from raw bytes into a slide."""
    stream = io.BytesIO(img_bytes)
    try:
        slide.shapes.add_picture(stream, left, top, width, height)
    except Exception as e:
        print(f"  [WARN] Could not add image: {e}")


# ──────────────────────────────────────────────
#  COMMON SLIDE ELEMENTS
# ──────────────────────────────────────────────

def add_pill(slide, text: str, top=Inches(0.22)):
    """Small section label pill at the top."""
    if not text:
        return
    width = Inches(5.5)
    txb = slide.shapes.add_textbox(MAR_L, top, width, Inches(0.32))
    tf  = txb.text_frame
    p   = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(11)
    run.font.color.rgb = C_ACCENT # Teal màu nổi bật
    run.font.name = FONT_BODY
    run.font.bold = True

def add_keyidea(slide, text: str, top=Inches(1.40)):
    """Highlighted key-idea box (Teal-tinted for dark theme)."""
    height = Inches(0.55)
    rect = add_rect(slide, MAR_L, top, USABLE_W, height,
                    fill=RGBColor(0x0b, 0x22, 0x20),
                    line_color=C_ACCENT)
    txb = slide.shapes.add_textbox(MAR_L + Inches(0.15), top + Inches(0.08),
                                   USABLE_W - Inches(0.30), height - Inches(0.12))
    tf  = txb.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(13)
    run.font.bold = False
    run.font.color.rgb = C_INK
    run.font.name = FONT_BODY
    return top + height + Inches(0.12)   # return next Y

def add_speaker_notes(slide, html_tag):
    """Populate the PPTX notes placeholder from <aside class='notes'>."""
    if html_tag is None:
        return
    text = clean_text(html_tag)
    if not text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


# ──────────────────────────────────────────────
#  BULLET LIST RENDERER
# ──────────────────────────────────────────────

def add_bullet_list(slide, items: list[str], left, top, width, height,
                    font_size=14, color=C_INK):
    """Add a bulleted list textbox."""
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.level = 0
        run = p.add_run()
        run.text = "• " + item.strip()
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.name = FONT_BODY


# ──────────────────────────────────────────────
#  TABLE RENDERER
# ──────────────────────────────────────────────

def add_html_table(slide, table_tag, left, top, width, height):
    """Render an HTML <table> into a PPTX table (Dark Theme style)."""
    rows_html = table_tag.find_all("tr")
    if not rows_html:
        return

    # Count columns from first row
    first_cells = rows_html[0].find_all(["th", "td"])
    n_cols = len(first_cells)
    n_rows = len(rows_html)
    if n_cols == 0 or n_rows == 0:
        return

    tbl = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl_obj = tbl.table

    for ri, tr in enumerate(rows_html):
        cells = tr.find_all(["th", "td"])
        is_header = any(c.name == "th" for c in cells)
        for ci, cell in enumerate(cells[:n_cols]):
            tc = tbl_obj.cell(ri, ci)
            tc.text = clean_text(cell)
            tf = tc.text_frame
            tf.word_wrap = True
            for para in tf.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(12)
                    run.font.name = FONT_BODY
                    if is_header:
                        run.font.bold  = True
                        run.font.color.rgb = C_WHITE
                    else:
                        run.font.color.rgb = C_INK
            # Cell background
            fill = tc.fill
            fill.solid()
            if is_header:
                fill.fore_color.rgb = C_HEADER_BG
            elif ri % 2 == 0:
                fill.fore_color.rgb = C_PANEL
            else:
                fill.fore_color.rgb = C_BG


# ──────────────────────────────────────────────
#  CARD / PANEL RENDERER
# ──────────────────────────────────────────────

def add_card(slide, card_tag, left, top, width, height):
    """Render a .card div as a bordered rectangle + text (Dark theme)."""
    # Background rect - dark navy panel
    add_rect(slide, left, top, width, height,
             fill=C_PANEL, line_color=C_LINE)

    # h3 title inside card
    h3 = card_tag.find("h3")
    inner_top = top + Inches(0.12)
    inner_left = left + Inches(0.15)
    inner_w    = width - Inches(0.30)

    if h3:
        txb = slide.shapes.add_textbox(inner_left, inner_top,
                                       inner_w, Inches(0.36))
        tf  = txb.text_frame
        p   = tf.paragraphs[0]
        run = p.add_run()
        run.text = clean_text(h3)
        run.font.size  = Pt(13)
        run.font.bold  = True
        run.font.color.rgb = C_ACCENT2 # Sky blue cho tiêu đề
        run.font.name  = FONT_BODY
        inner_top += Inches(0.38)

    # Bullet items
    lis = card_tag.find_all("li")
    if lis:
        items = [clean_text(li) for li in lis]
        add_bullet_list(slide, items, inner_left, inner_top,
                        inner_w, height - (inner_top - top) - Inches(0.1),
                        font_size=12, color=C_INK)
    else:
        # Plain paragraphs
        paras = card_tag.find_all("p")
        if paras:
            text = "\n".join(clean_text(p) for p in paras)
            txb = slide.shapes.add_textbox(
                inner_left, inner_top, inner_w,
                height - (inner_top - top) - Inches(0.1))
            tf  = txb.text_frame
            tf.word_wrap = True
            para = tf.paragraphs[0]
            run  = para.add_run()
            run.text = text
            run.font.size = Pt(12)
            run.font.color.rgb = C_INK
            run.font.name = FONT_BODY


# ──────────────────────────────────────────────
#  SECTION DIVIDER SLIDE
# ──────────────────────────────────────────────

def render_section_slide(slide, sec_tag):
    """Full-bleed gradient section break - Adapt to HUST Section Header Layout."""
    # Keep the default background of HUST Section Header Layout (Index 1)
    
    pill_tag = sec_tag.find(class_="pill")
    pill_txt = clean_text(pill_tag) if pill_tag else ""

    h1 = sec_tag.find("h1")
    h2 = sec_tag.find("h2")
    title_tag = h1 or h2
    title_txt = clean_text(title_tag) if title_tag else ""

    # Gán Title vào placeholder và định dạng màu tối vì nền của nửa phải Section slide là màu trắng
    title_shape = None
    try:
        title_shape = slide.shapes.title
    except Exception:
        pass
        
    if title_shape and title_txt:
        title_shape.text = title_txt
        for p in title_shape.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.name = FONT_BODY
                r.font.bold = True
                r.font.size = Pt(36)
                r.font.color.rgb = RGBColor(0x11, 0x18, 0x27) # Màu đen sẫm
    elif title_txt:
        add_textbox(slide, MAR_L, Inches(3.0), USABLE_W, Inches(1.20),
                    text=title_txt, font_size=36, bold=True,
                    color=RGBColor(0x11, 0x18, 0x27), align=PP_ALIGN.CENTER)

    # Trích xuất các gạch đầu dòng mục tiêu bài học từ HTML
    goals = []
    ul = sec_tag.find(["ul", "ol"])
    if ul:
        for li in ul.find_all("li"):
            goals.append(clean_text(li))

    # Xác định subtitle tương ứng dựa trên tiêu đề phần
    subtitle_txt = ""
    if "Tutorial 02" in pill_txt or "tần số" in title_txt.lower():
        subtitle_txt = "FFT · Envelope Analysis"
    elif "Tutorial 03" in pill_txt or "trích đặc trưng" in title_txt.lower():
        subtitle_txt = "Feature Engineering & EDA"
    elif "Phần B" in pill_txt or "svm" in title_txt.lower():
        subtitle_txt = "SVM & Random Forest"
    elif "Tutorial 04" in pill_txt or "huấn luyện" in title_txt.lower():
        subtitle_txt = "Model Training & Evaluation"
    elif "Tutorial 05" in pill_txt or "shap" in title_txt.lower():
        subtitle_txt = "SHAP · Explainable AI"
    elif "Kết thúc" in pill_txt or "cảm ơn" in title_txt.lower():
        subtitle_txt = "Cảm ơn & Hỏi đáp"

    # Duyệt và thay thế nội dung các shape tĩnh được kế thừa từ layout
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        txt = shape.text.strip()
        
        # 1. Thay thế subtitle mẫu
        if "FFT · Envelope Analysis" in txt or (shape.is_placeholder and shape.placeholder_format.idx == 13):
            shape.text = subtitle_txt if subtitle_txt else pill_txt
            for p in shape.text_frame.paragraphs:
                p.alignment = PP_ALIGN.CENTER
                for r in p.runs:
                    r.font.name = FONT_BODY
                    r.font.italic = True
                    r.font.size = Pt(14)
                    r.font.color.rgb = RGBColor(0x4b, 0x55, 0x63) # Xám vừa
                    
        # 2. Thay thế 4 gạch đầu dòng mục tiêu mẫu
        elif "Cấu tạo CWRU" in txt and len(goals) > 0:
            shape.text = goals[0]
        elif "Phân loại 4 trạng thái" in txt and len(goals) > 1:
            shape.text = goals[1]
        elif "Tần số lấy mẫu" in txt and len(goals) > 2:
            shape.text = goals[2]
        elif "Công thức & tần số" in txt and len(goals) > 3:
            shape.text = goals[3]
            
        # Định dạng lại các textbox mục tiêu bài học vừa thay thế sang màu tối và font Calibri
        if any(k in txt for k in ["Cấu tạo CWRU", "Phân loại 4 trạng thái", "Tần số lấy mẫu", "Công thức & tần số"]):
            for p in shape.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = FONT_BODY
                    r.font.size = Pt(14)
                    r.font.color.rgb = RGBColor(0x11, 0x18, 0x27) # Đen xám

    # Notes
    add_speaker_notes(slide, sec_tag.find("aside", class_="notes"))


# ──────────────────────────────────────────────
#  GENERIC CONTENT SLIDE
# ──────────────────────────────────────────────

def render_content_slide(slide, sec_tag):
    # Keep HUST template layout background (picture background)
    
    # ── Pill & Title ──
    pill_tag = sec_tag.find(class_="pill")
    pill_txt = clean_text(pill_tag) if pill_tag else ""
    if pill_txt:
        add_pill(slide, pill_txt, top=Inches(0.15))

    h1 = sec_tag.find("h1")
    h2 = sec_tag.find("h2")
    title_tag = h1 or h2
    title_txt = clean_text(title_tag) if title_tag else ""
    
    title_shape = None
    try:
        title_shape = slide.shapes.title
    except Exception:
        pass
        
    if title_shape and title_txt:
        title_shape.text = title_txt
        for p in title_shape.text_frame.paragraphs:
            p.alignment = PP_ALIGN.LEFT
            for r in p.runs:
                r.font.name = FONT_BODY
                r.font.bold = True
                r.font.size = Pt(22)
                # Hãy để nguyên màu mặc định của title placeholder của HUST hoặc set màu trắng
                r.font.color.rgb = C_WHITE 
    elif title_txt:
        # Fallback textbox
        txb = add_textbox(slide, MAR_L, Inches(0.45), USABLE_W, Inches(0.72),
                          text=title_txt, font_size=22, bold=True,
                          color=C_WHITE, font_name=FONT_BODY)
        # Accent bar under title
        add_rect(slide, MAR_L, Inches(0.45) + Inches(0.68),
                 Inches(0.07), Inches(0.25), fill=C_ACCENT)

    # ── Key idea ──
    keyidea_tag = sec_tag.find(class_="keyidea")
    content_top = Inches(1.38)
    if keyidea_tag:
        content_top = add_keyidea(slide, clean_text(keyidea_tag), top=content_top)

    content_height = H - content_top - Inches(0.40) # margin bottom

    # ── Decide layout based on HTML structure ──

    # Does it have an image?
    img_tag  = sec_tag.find("img", class_="ill")
    img_bytes = extract_base64_image(img_tag)

    # Does it have cards?
    cards    = sec_tag.find_all(class_="card")

    # Does it have a table?
    table_tag = sec_tag.find("table")

    # Top-level ul / ol
    ul_tag   = sec_tag.find(["ul", "ol"], recursive=False)
    if not ul_tag:
        # search one level deeper (e.g. inside .grow div)
        grow = sec_tag.find(class_="grow")
        if grow:
            ul_tag = grow.find(["ul", "ol"])

    # ── IMAGE + TEXT (two-column) ──
    if img_bytes and (cards or ul_tag or table_tag or
                      sec_tag.find("p")):
        img_w  = Inches(5.2)
        img_h  = content_height
        txt_w  = USABLE_W - img_w - Inches(0.3)
        img_left = MAR_L
        txt_left = img_left + img_w + Inches(0.3)

        add_image_from_bytes(slide, img_bytes,
                             img_left, content_top, img_w, img_h)
        _render_text_content(slide, sec_tag,
                             txt_left, content_top, txt_w, content_height,
                             skip_img=True)

    # ── IMAGE ONLY ──
    elif img_bytes:
        img_w = min(USABLE_W, Inches(9.0))
        img_l = MAR_L + (USABLE_W - img_w) / 2
        add_image_from_bytes(slide, img_bytes,
                             img_l, content_top, img_w, content_height)

    # ── CARDS (grid layout) ──
    elif cards:
        n = len(cards)
        card_w = (USABLE_W - Inches(0.2) * (n - 1)) / n
        for i, card in enumerate(cards):
            cl = MAR_L + i * (card_w + Inches(0.2))
            add_card(slide, card, cl, content_top, card_w, content_height)

    # ── TABLE ──
    elif table_tag:
        add_html_table(slide, table_tag,
                       MAR_L, content_top, USABLE_W, content_height)

    # ── BULLETS / TEXT ──
    else:
        _render_text_content(slide, sec_tag,
                             MAR_L, content_top, USABLE_W, content_height)

    add_speaker_notes(slide, sec_tag.find("aside", class_="notes"))


# ──────────────────────────────────────────────
#  TEXT CONTENT HELPER
# ──────────────────────────────────────────────

def _render_text_content(slide, sec_tag, left, top, width, height,
                         skip_img=False):
    """
    Render whatever text/list/table/code exists in sec_tag (Dark theme colors).
    """
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    first_para = True

    def _add_para(text, font_size=14, bold=False, italic=False,
                  color=C_INK, prefix=""):
        nonlocal first_para
        if first_para:
            p = tf.paragraphs[0]
            first_para = False
        else:
            p = tf.add_paragraph()
        run = p.add_run()
        run.text = (prefix + text).strip()
        run.font.size  = Pt(font_size)
        run.font.bold  = bold
        run.font.italic = italic
        run.font.color.rgb = color
        run.font.name  = FONT_BODY
        return p

    # Walk through direct children of .grow or sec_tag
    grow = sec_tag.find(class_="grow") or sec_tag
    for child in grow.children:
        if not isinstance(child, Tag):
            continue
        tag_name = child.name
        cls_list = child.get("class", [])

        # Skip images if requested
        if skip_img and tag_name == "img":
            continue
        # Skip aside notes
        if tag_name == "aside":
            continue
        # Skip pill / keyidea (already handled)
        if "pill" in cls_list or "keyidea" in cls_list:
            continue
        # Skip card (handled separately)
        if "card" in cls_list:
            continue

        # h3 sub-heading
        if tag_name == "h3":
            _add_para(clean_text(child), font_size=15, bold=True,
                      color=C_ACCENT2) # Sky blue heading

        # ul / ol → bullets
        elif tag_name in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                _add_para(clean_text(li), prefix="• ")

        # table fallback
        elif tag_name == "table":
            rows = child.find_all("tr")
            for ri, tr in enumerate(rows):
                cells = tr.find_all(["th", "td"])
                row_txt = "  |  ".join(clean_text(c) for c in cells)
                is_hdr  = any(c.name == "th" for c in cells)
                _add_para(row_txt, font_size=11,
                          bold=is_hdr,
                          color=C_ACCENT2 if is_hdr else C_INK)

        # <pre> code block (Consolas font, light cyan color on dark background)
        elif tag_name == "pre" or "code" in cls_list:
            code_txt = clean_text(child)
            for line in code_txt.split("\n"):
                _add_para(line, font_size=10,
                          color=RGBColor(0x7d, 0xd3, 0xfc)) # Light cyan code text
                last_p = tf.paragraphs[-1]
                for run in last_p.runs:
                    run.font.name = FONT_MONO

        # .warn / .good / .bad callout
        elif any(c in cls_list for c in ("warn", "good", "bad", "keyidea")):
            icon = {"warn": "⚠ ", "good": "✓ ", "bad": "✗ "}.get(
                next((c for c in cls_list if c in ("warn","good","bad")), ""), "")
            color = {"warn": C_WARN, "good": C_GOOD, "bad": C_BAD}.get(
                next((c for c in cls_list if c in ("warn","good","bad")), ""), C_INK)
            _add_para(clean_text(child), prefix=icon, color=color, font_size=13)

        # .flow steps (pipeline arrow diagram)
        elif "flow" in cls_list:
            steps = child.find_all(class_="step")
            flow_txt = " → ".join(clean_text(s) for s in steps)
            _add_para(flow_txt, color=C_ACCENT, font_size=13)

        # Generic <p>
        elif tag_name == "p":
            txt = clean_text(child)
            if txt:
                _add_para(txt)

        # Generic div – recurse one level
        elif tag_name == "div":
            for sub in child.children:
                if not isinstance(sub, Tag):
                    continue
                if sub.name in ("ul", "ol"):
                    for li in sub.find_all("li", recursive=False):
                        _add_para(clean_text(li), prefix="• ")
                elif sub.name == "p":
                    txt = clean_text(sub)
                    if txt:
                        _add_para(txt)
                elif sub.name == "h3":
                    _add_para(clean_text(sub), font_size=15, bold=True,
                              color=C_ACCENT2)


# ──────────────────────────────────────────────
#  SLIDE NUMBER FOOTER
# ──────────────────────────────────────────────

def add_slide_number(slide, number: int, total: int):
    txt = f"{number} / {total}"
    add_textbox(slide,
                W - Inches(1.2), H - Inches(0.35),
                Inches(1.0), Inches(0.30),
                text=txt, font_size=10, color=C_MUTED,
                align=PP_ALIGN.RIGHT)


# ──────────────────────────────────────────────
#  DELETE SLIDE HELPER
# ──────────────────────────────────────────────

def delete_slide(prs, index):
    """Safely delete a slide by its index in the Presentation."""
    id_list = prs.slides._sldIdLst
    if index < 0 or index >= len(id_list):
        return
    rId = id_list[index].rId
    prs.part.drop_rel(rId)
    del id_list[index]


# ──────────────────────────────────────────────
#  MAIN CONVERSION LOGIC
# ──────────────────────────────────────────────

def generate_hust_slides(html_path: Path, template_path: Path, out_path: Path):
    print(f"[INFO] Loading template: {template_path}")
    prs = Presentation(str(template_path))
    
    n_slides_in_template = len(prs.slides)
    print(f"[INFO] Slides in template originally: {n_slides_in_template}")
    
    # We keep slides 0 to 10. Slide 11 is the old "THANK YOU!" slide which we delete.
    if n_slides_in_template > 11:
        print(f"[INFO] Deleting slide index 11 (THANK YOU!): {prs.slides[11].name}")
        delete_slide(prs, 11)
        
    print(f"[INFO] Parsing HTML: {html_path}")
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    sections = soup.find_all("section", class_="slide")
    total_html_slides = len(sections)
    print(f"[INFO] Found {total_html_slides} slides in HTML source")

    # Layout indexes from HUST template:
    # Index 1: Section Header (nền đỏ/logo chìm)
    # Index 5: Title Only (nền tối/tiêu đề trắng)
    # Index 6: 2_Comparison (Dành cho slide có ảnh + text để "chọn đúng layout")
    # Index 3: Comparison (Dành cho slide có cards/bullets thông thường)
    
    section_layout = prs.slide_layouts[1]
    content_layout_title_only = prs.slide_layouts[5]
    content_layout_comparison = prs.slide_layouts[3]
    content_layout_2col = prs.slide_layouts[6]

    # Slide 14 is index 13 in the HTML file
    import_start_index = 13
    
    new_slides_to_import = sections[import_start_index:]
    n_imported = len(new_slides_to_import)
    print(f"[INFO] Importing {n_imported} slides from HTML (Slides {import_start_index+1} to {total_html_slides})")

    current_slide_num = len(prs.slides) + 1
    
    for i, sec in enumerate(new_slides_to_import, start=1):
        cls = sec.get("class", [])
        
        # Decide layout based on slide elements to implement "chọn đúng layout"
        img_tag  = sec.find("img", class_="ill")
        img_bytes = extract_base64_image(img_tag)
        cards    = sec.find_all(class_="card")
        table_tag = sec.find("table")
        
        if "section" in cls:
            # Use Section Header layout (Index 1)
            slide = prs.slides.add_slide(section_layout)
            render_section_slide(slide, sec)
            print(f"  [Import {i:02d}/{n_imported}] [SECTION] {clean_text(sec.find(['h1','h2']) or '')[:50]}")
        else:
            # Choose layout based on content
            if img_bytes and (cards or table_tag or sec.find("p") or sec.find(["ul", "ol"])):
                # Image + Text structure -> Use 2_Comparison Layout (Index 6)
                slide = prs.slides.add_slide(content_layout_2col)
            elif cards or table_tag:
                # Grid of cards or Table -> Use Comparison Layout (Index 3)
                slide = prs.slides.add_slide(content_layout_comparison)
            else:
                # Text list or Image only -> Use Title Only Layout (Index 5)
                slide = prs.slides.add_slide(content_layout_title_only)
                
            render_content_slide(slide, sec)
            t = sec.find(["h1","h2"])
            print(f"  [Import {i:02d}/{n_imported}]          {clean_text(t)[:50] if t else '(no title)'}")

        # Update slide number footer
        add_slide_number(slide, current_slide_num, 11 + n_imported)
        current_slide_num += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    print(f"\n[SUCCESS] Completed! Saved HUST slide deck to → {out_path}")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    base = Path("d:/[Lab] HUST/nhà máy")
    html_path = base / "slides" / "BaiGiang_CWRU_v2.html"
    template_path = base / "slides" / "HUST_PPT_template_2022_RED_16x9_567042.pptx"
    out_path = base / "slides" / "BaiGiang_CWRU_HUST_v3.pptx"
    
    if not html_path.exists():
        print(f"[ERROR] HTML file not found: {html_path}")
        sys.exit(1)
        
    if not template_path.exists():
        print(f"[ERROR] HUST Template file not found: {template_path}")
        sys.exit(1)
        
    generate_hust_slides(html_path, template_path, out_path)
