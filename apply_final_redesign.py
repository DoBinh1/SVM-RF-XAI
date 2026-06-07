import re

file_path = r"d:\[Lab] HUST\nhà máy\slides\BaiGiang_CWRU.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# =========================================================================
# 1. Base selectors & Font Sizing
# =========================================================================

# Adjust h1 size
content = content.replace(
    'h1{font-size:3.0rem;line-height:1.15;margin-bottom:.6rem}',
    'h1{font-size:2.2rem;line-height:1.15;margin-bottom:.6rem}'
)
content = content.replace(
    '.section h1{font-size:3.4rem;color:#fff}',
    '.section h1{font-size:2.2rem;color:#fff}'
)

# Adjust h2 size
content = content.replace(
    'h2{font-size:2.15rem;color:#fff;margin-bottom:1.1rem;border-left:6px solid var(--accent);padding-left:.7rem}',
    'h2{font-size:1.75rem;color:#fff;margin-bottom:1.1rem;border-left:6px solid var(--accent);padding-left:.7rem}'
)

# Adjust h3 size
content = content.replace(
    'h3{font-size:1.35rem;color:var(--accent2);margin:.6rem 0 .4rem}',
    'h3{font-size:1.15rem;color:var(--accent2);margin:.6rem 0 .4rem}'
)

# Adjust p, li size
content = content.replace(
    'p,li{font-size:1.28rem;line-height:1.55;color:var(--ink)}',
    'p,li{font-size:1.05rem;line-height:1.55;color:var(--ink)}'
)

# =========================================================================
# 2. Slide Layout & Viewport Sizing
# =========================================================================

# Lock base .slide to overflow:hidden and adjust padding
old_slide = """  .slide{
    position:absolute;inset:0;display:none;overflow-y:auto;
    padding:5.0vh 6vw 7vh;flex-direction:column;
    animation:fade .35s ease;
  }"""

new_slide = """  .slide{
    position:absolute;inset:0;display:none;overflow:hidden;
    padding:3vh 4vw 4vh;flex-direction:column;
    animation:fade .35s ease;
  }"""

if old_slide in content:
    content = content.replace(old_slide, new_slide)
    print("Successfully replaced base .slide style!")
else:
    # Try with single line formatting
    old_slide_alt = ".slide{position:absolute;inset:0;display:none;overflow-y:auto;padding:5.0vh 6vw 7vh;flex-direction:column;animation:fade .35s ease;}"
    new_slide_alt = ".slide{position:absolute;inset:0;display:none;overflow:hidden;padding:3vh 4vw 4vh;flex-direction:column;animation:fade .35s ease;}"
    if old_slide_alt in content:
        content = content.replace(old_slide_alt, new_slide_alt)
        print("Successfully replaced base .slide style (alt)!")
    else:
        print("Warning: Base .slide style not matched precisely. Using regex to fix...")
        content = re.sub(
            r"\.slide\s*\{([^}]+)\}",
            lambda m: ".slide{position:absolute;inset:0;display:none;overflow:hidden;padding:3vh 4vw 4vh;flex-direction:column;animation:fade .35s ease;}",
            content,
            count=1
        )

# =========================================================================
# 3. Content flex constraints
# =========================================================================

# Add unified rule for .grid, .flow, table
flex_rule = """
  .grid, .flow, table {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }
"""
content = content.replace(
    '.g5{grid-template-columns:1.05fr .95fr}',
    '.g5{grid-template-columns:1.05fr .95fr}' + flex_rule
)

# =========================================================================
# 4. Card & Key Idea Sizing
# =========================================================================

# Adjust .card base styling (overflow:hidden, clamp font-size)
content = content.replace(
    '  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.1rem 1.3rem}',
    '  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:1.1rem 1.3rem;overflow:hidden;font-size:clamp(0.85rem, 1.5vh, 1.05rem)}'
)

# Adjust .keyidea base styling (font-size to 1.1rem)
old_keyidea = "padding:.65rem 1.1rem;margin:-.15rem 0 1rem;font-size:1.34rem;line-height:1.5;color:#eaf6ff"
new_keyidea = "padding:.65rem 1.1rem;margin:-.15rem 0 1rem;font-size:1.1rem;line-height:1.5;color:#eaf6ff"
content = content.replace(old_keyidea, new_keyidea)

# =========================================================================
# 5. Media Queries
# =========================================================================

# 1024px responsive query
content = content.replace(
    '.slide{padding:3vh 4vw 5vh}',
    '.slide{padding:3vh 4vw 4vh}'
)
content = content.replace(
    'h2{font-size:1.7rem}',
    'h2{font-size:1.75rem}'
)
content = content.replace(
    '.keyidea{font-size:1.15rem}',
    '.keyidea{font-size:1.1rem}'
)

# 768px responsive query
content = content.replace(
    '.slide{padding:2vh 3vw 4vh;overflow-y:auto}',
    '.slide{padding:2vh 3vw 4vh;overflow:hidden}'
)
content = content.replace(
    '.keyidea{font-size:1.05rem}',
    '.keyidea{font-size:1.1rem}'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Slide redesign successfully applied!")
