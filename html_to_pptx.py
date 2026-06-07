"""
html_to_pptx.py
Dùng BeautifulSoup4 để parse file HTML slide (Reveal.js/custom)
rồi xuất ra PPTX bằng python-pptx.

Chạy:  python html_to_pptx.py
Output: slides/BaiGiang_CWRU.pptx
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
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ──────────────────────────────────────────────
#  CONSTANTS – Design System (dark-navy theme)
# ──────────────────────────────────────────────
W = Inches(13.33)          # 16:9 widescreen width
H = Inches(7.5)            # 16:9 widescreen height

# Colours  (R, G, B)
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
C_NORMAL    = RGBColor(0x2e, 0xcc, 0x71)   # normal class
C_IR        = RGBColor(0xe7, 0x4c, 0x3c)   # ir class
C_OR        = RGBColor(0x34, 0x98, 0xdb)   # or class
C_BALL      = RGBColor(0xf3, 0x9c, 0x12)   # ball class
C_HEADER_BG = RGBColor(0x1c, 0x2c, 0x44)   # table header bg
C_WHITE     = RGBColor(0xff, 0xff, 0xff)
C_CODE_BG   = RGBColor(0x0b, 0x13, 0x20)

FONT_BODY   = "Segoe UI"
FONT_MONO   = "Cascadia Code"

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
    from pptx.util import Pt as UPt
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
#  SLIDE BACKGROUND
# ──────────────────────────────────────────────

def set_slide_background(slide, color: RGBColor = C_BG):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


# ──────────────────────────────────────────────
#  COMMON SLIDE ELEMENTS
# ──────────────────────────────────────────────

def add_pill(slide, text: str, top=Inches(0.22)):
    """Small section label pill at the top."""
    if not text:
        return
    width = Inches(4.5)
    txb = slide.shapes.add_textbox(MAR_L, top, width, Inches(0.32))
    tf  = txb.text_frame
    p   = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(11)
    run.font.color.rgb = C_ACCENT
    run.font.name = FONT_BODY

def add_title(slide, text: str, is_h1=False, top=Inches(0.60)):
    """Main slide title (h1 or h2)."""
    font_size = 32 if is_h1 else 22
    color     = C_WHITE
    txb = slide.shapes.add_textbox(MAR_L, top, USABLE_W, Inches(0.72))
    tf  = txb.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    if not is_h1:
        p.alignment = PP_ALIGN.LEFT
    else:
        p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = True
    run.font.color.rgb = color
    run.font.name = FONT_BODY
    # Accent bar under h2
    if not is_h1:
        bar = add_rect(slide, MAR_L, top + Inches(0.68),
                       Inches(0.07), Inches(0.25), fill=C_ACCENT)
    return txb

def add_keyidea(slide, text: str, top=Inches(1.40)):
    """Highlighted key-idea box (teal-tinted)."""
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
    """Render an HTML <table> into a PPTX table."""
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
    """Render a .card div as a bordered rectangle + text."""
    # Background rect
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
        run.font.color.rgb = C_ACCENT2
        run.font.name  = FONT_BODY
        inner_top += Inches(0.38)

    # Bullet items
    lis = card_tag.find_all("li")
    if lis:
        items = [clean_text(li) for li in lis]
        add_bullet_list(slide, items, inner_left, inner_top,
                        inner_w, height - (inner_top - top) - Inches(0.1),
                        font_size=12)
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
    """Full-bleed gradient section break."""
    set_slide_background(slide, RGBColor(0x0b, 0x13, 0x22))
    pill_tag = sec_tag.find(class_="pill")
    pill_txt = clean_text(pill_tag) if pill_tag else ""

    h1 = sec_tag.find("h1")
    h2 = sec_tag.find("h2")
    title_tag = h1 or h2
    title_txt = clean_text(title_tag) if title_tag else ""

    # Vertical centering – place everything in the middle third
    mid_top = Inches(2.5)

    if pill_txt:
        add_textbox(slide, MAR_L, mid_top, USABLE_W, Inches(0.40),
                    text=pill_txt, font_size=14, color=C_ACCENT,
                    align=PP_ALIGN.CENTER)
        mid_top += Inches(0.45)

    if title_txt:
        add_textbox(slide, MAR_L, mid_top, USABLE_W, Inches(1.20),
                    text=title_txt, font_size=36, bold=True,
                    color=C_WHITE, align=PP_ALIGN.CENTER)

    # Accent line
    bar_w = Inches(2.0)
    bar_l = (W - bar_w) / 2
    add_rect(slide, bar_l, Inches(1.9), bar_w, Pt(3), fill=C_ACCENT)

    add_speaker_notes(slide, sec_tag.find("aside", class_="notes"))


# ──────────────────────────────────────────────
#  GENERIC CONTENT SLIDE
# ──────────────────────────────────────────────

def render_content_slide(slide, sec_tag):
    set_slide_background(slide, C_BG)

    # ── Pill & Title ──
    pill_tag = sec_tag.find(class_="pill")
    pill_txt = clean_text(pill_tag) if pill_tag else ""
    add_pill(slide, pill_txt)

    h1 = sec_tag.find("h1")
    h2 = sec_tag.find("h2")
    title_tag = h1 or h2
    is_h1 = h1 is not None
    title_txt = clean_text(title_tag) if title_tag else ""
    add_title(slide, title_txt, is_h1=is_h1)

    # ── Key idea ──
    keyidea_tag = sec_tag.find(class_="keyidea")
    content_top = Inches(1.38)
    if keyidea_tag:
        content_top = add_keyidea(slide, clean_text(keyidea_tag), top=content_top)

    content_height = H - content_top - Inches(0.20)

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
        img_w  = Inches(5.0)
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
    Render whatever text/list/table content exists in sec_tag
    (bullets, paragraphs, table, code blocks) into the given box.
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
                      color=C_ACCENT2)

        # ul / ol → bullets
        elif tag_name in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                _add_para(clean_text(li), prefix="• ")

        # table
        elif tag_name == "table":
            # Table inside textbox not possible – add separately
            # (will be clipped if already in two-col mode; acceptable trade-off)
            rows = child.find_all("tr")
            for ri, tr in enumerate(rows):
                cells = tr.find_all(["th", "td"])
                row_txt = "  |  ".join(clean_text(c) for c in cells)
                is_hdr  = any(c.name == "th" for c in cells)
                _add_para(row_txt, font_size=11,
                          bold=is_hdr,
                          color=C_ACCENT2 if is_hdr else C_INK)

        # <pre> code block
        elif tag_name == "pre" or "code" in cls_list:
            code_txt = clean_text(child)
            for line in code_txt.split("\n"):
                _add_para(line, font_size=10,
                          color=RGBColor(0x7d, 0xd3, 0xfc))
                # change font to mono for last added para
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
#  MAIN CONVERSION LOGIC
# ──────────────────────────────────────────────

def html_to_pptx(html_path: Path, out_path: Path):
    print(f"[INFO] Parsing HTML: {html_path}")
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    sections = soup.find_all("section", class_="slide")
    total = len(sections)
    print(f"[INFO] Found {total} slides")

    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H

    # Use blank layout (index 6)
    blank_layout = prs.slide_layouts[6]

    for i, sec in enumerate(sections, start=1):
        cls = sec.get("class", [])
        slide = prs.slides.add_slide(blank_layout)

        if "section" in cls:
            render_section_slide(slide, sec)
            print(f"  [{i:02d}/{total}] [SECTION] {clean_text(sec.find(['h1','h2']) or '')[:60]}")
        else:
            render_content_slide(slide, sec)
            t = sec.find(["h1","h2"])
            print(f"  [{i:02d}/{total}]          {clean_text(t)[:60] if t else '(no title)'}")

        add_slide_number(slide, i, total)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    print(f"\n[DONE] Saved → {out_path}")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    from pathlib import Path as _P

    # Auto-locate the HTML file
    base = _P("d:/[Lab] HUST")
    candidates = list(base.rglob("BaiGiang_CWRU.html"))
    if not candidates:
        raise FileNotFoundError("Không tìm thấy BaiGiang_CWRU.html")

    html_path = candidates[0]
    out_path  = html_path.parent / "BaiGiang_CWRU.pptx"
    html_to_pptx(html_path, out_path)
