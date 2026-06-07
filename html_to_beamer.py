#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html_to_beamer.py  (v2 – Overleaf/XeLaTeX compatible)
======================================================
BeautifulSoup4  → parse HTML slides
python-pptx-free → xuất LaTeX Beamer 16:9

Chạy:   python html_to_beamer.py
Output: slides/BaiGiang_CWRU.tex  +  slides/images/*.{png,jpg}

Compiler khuyến nghị: XeLaTeX
  Overleaf → Menu (☰) → Compiler → XeLaTeX
"""

from __future__ import annotations
import re, sys, io, base64, textwrap
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString

# ── UTF-8 console ──────────────────────────────────────────────────────────
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ══════════════════════════════════════════════════════════════════════════
#  LATEX ESCAPE & TEXT UTILITIES
# ══════════════════════════════════════════════════════════════════════════

_LATEX_ESCAPE = str.maketrans({
    '&':  r'\&',
    '%':  r'\%',
    '$':  r'\$',
    '#':  r'\#',
    '_':  r'\_',
    '{':  r'\{',
    '}':  r'\}',
    '~':  r'\textasciitilde{}',
    '^':  r'\textasciicircum{}',
    '\\': r'\textbackslash{}',
    '<':  r'\textless{}',
    '>':  r'\textgreater{}',
    '|':  r'\textbar{}',
    '"':  r"''",
    '\u2013': '--',
    '\u2014': '---',
    '\u00d7': r'$\times$',
    '\u2192': r'$\rightarrow$',
    '\u2190': r'$\leftarrow$',
    '\u2264': r'$\leq$',
    '\u2265': r'$\geq$',
    '\u2260': r'$\neq$',
    '\u00b1': r'$\pm$',
    '\u03b1': r'$\alpha$',
    '\u03b2': r'$\beta$',
    '\u03c6': r'$\varphi$',
    '\u03c0': r'$\pi$',
    '\u2248': r'$\approx$',
    # Strip emoji (cannot render reliably in Beamer without special setup)
    '\u26a0': '[!]',    # ⚠
    '\U0001f6a8': '[!]',
    '\u2705': '[OK]',   # ✅
    '\u274c': '[X]',    # ❌
    '\u2714': '[OK]',   # ✔
    '\u2716': '[X]',    # ✖
    '\U0001f534': '[IR]',
    '\U0001f7e0': '[OR]',
    '\U0001f7e1': '[Ball]',
    '\U0001f7e2': '[Normal]',
    '\U0001f6a7': '[!]',
    '\U0001f527': '[tool]',
})

# Strip all remaining emoji (codepoints outside BMP and common symbol blocks)
_EMOJI_RE = re.compile(
    r'[\U0001F000-\U0001FFFF'   # supplemental symbols
    r'\U00002600-\U000027FF'    # misc symbols
    r'\U00002B00-\U00002BFF'    # misc symbols & arrows
    r'\U0001F300-\U0001F9FF'    # emoji
    r'\uFE00-\uFE0F'            # variation selectors
    r'\u200D'                   # zero-width joiner
    r']+',
    flags=re.UNICODE
)

def esc(text: str) -> str:
    """Escape a plain string for LaTeX, stripping unrenderable emoji."""
    if not text:
        return ''
    text = _EMOJI_RE.sub('', text)
    return text.translate(_LATEX_ESCAPE)

def clean_text(tag, escape=True) -> str:
    """Recursively extract text from a BS4 tag, handling sub/sup/strong/em."""
    if tag is None:
        return ''
    if isinstance(tag, NavigableString):
        return esc(str(tag)) if escape else str(tag)
    parts = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            t = str(child)
            parts.append(esc(t) if escape else t)
        elif child.name == 'br':
            parts.append(r'\\')
        elif child.name == 'sub':
            inner = clean_text(child, escape)
            parts.append(f'$_{{{inner}}}$')
        elif child.name == 'sup':
            inner = clean_text(child, escape)
            parts.append(f'$^{{{inner}}}$')
        elif child.name in ('strong', 'b'):
            inner = clean_text(child, escape)
            parts.append(f'\\textbf{{{inner}}}')
        elif child.name in ('em', 'i'):
            inner = clean_text(child, escape)
            parts.append(f'\\textit{{{inner}}}')
        elif child.name == 'code':
            raw = child.get_text()
            parts.append(f'\\texttt{{{esc(raw)}}}')
        elif child.name == 'aside':
            pass   # skip speaker notes
        else:
            parts.append(clean_text(child, escape))
    return ''.join(parts).strip()


# ══════════════════════════════════════════════════════════════════════════
#  SAVE EMBEDDED IMAGES
# ══════════════════════════════════════════════════════════════════════════

_img_counter = 0

def save_image(img_tag, img_dir: Path) -> str | None:
    """Save base64-embedded image; return relative path for \\includegraphics."""
    global _img_counter
    if img_tag is None:
        return None
    src = img_tag.get('src', '')
    m = re.match(r'data:image/([^;]+);base64,(.+)', src, re.S)
    if not m:
        return None
    ext  = m.group(1).replace('jpeg', 'jpg')
    data = base64.b64decode(m.group(2))
    name = img_tag.get('data-img', '')
    if not name:
        _img_counter += 1
        name = f'img_{_img_counter:03d}'
    fpath = img_dir / f'{name}.{ext}'
    fpath.write_bytes(data)
    return f'images/{name}'     # NO extension → LaTeX picks best available


# ══════════════════════════════════════════════════════════════════════════
#  PREAMBLE  (XeLaTeX + Overleaf-safe)
# ══════════════════════════════════════════════════════════════════════════

PREAMBLE = r"""\documentclass[aspectratio=169,10pt]{beamer}

%% ════════════════════════════════════════════════════════════════════════════
%%  COMPILER: pdfLaTeX  (mac dinh cua Overleaf — KHONG can doi compiler)
%%  Cung hoat dong voi XeLaTeX va LuaLaTeX.
%% ════════════════════════════════════════════════════════════════════════════

%% ─── Encoding (pdfLaTeX + tieng Viet) ───────────────────────────────────────
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}          %% T5 = VnTeX — ho tro day du ky tu tieng Viet
\usepackage[vietnamese]{babel}

%% ─── Graphics & Colour ───────────────────────────────────────────────────────
\usepackage{graphicx}
\graphicspath{{images/}}          %% thu muc chua anh, cung cap cung file .tex
\usepackage{xcolor}
\usepackage{tikz}

%% ─── Tables ──────────────────────────────────────────────────────────────────
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{multirow}
%% Khong dung enumitem — xung dot voi Beamer

%% ─── Code listings ───────────────────────────────────────────────────────────
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small\color{caccent2},
  backgroundcolor=\color{cbg},
  frame=single,
  framesep=4pt,
  rulecolor=\color{cline},
  breaklines=true,
  breakatwhitespace=false,
  showstringspaces=false,
  keywordstyle=\color{caccent},
  commentstyle=\color{cmuted},
  stringstyle=\color{cgood},
  language=Python,
  upquote=true,
  literate=
    {->}{{\ensuremath{\rightarrow}}}2
    {<-}{{\ensuremath{\leftarrow}}}2
    {>=}{{\ensuremath{\geq}}}2
    {<=}{{\ensuremath{\leq}}}2
}

%% ─── Math & Misc ─────────────────────────────────────────────────────────────
\usepackage{amsmath,amssymb}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}

%% ═══════════════════════════════════════════════════════════════════════════
%%  COLOUR PALETTE
%% ═══════════════════════════════════════════════════════════════════════════
\definecolor{cbg}{HTML}{0E1726}
\definecolor{cpanel}{HTML}{152133}
\definecolor{cink}{HTML}{EAF0F7}
\definecolor{cmuted}{HTML}{9FB3C8}
\definecolor{caccent}{HTML}{2DD4BF}
\definecolor{caccent2}{HTML}{38BDF8}
\definecolor{cline}{HTML}{2A3A52}
\definecolor{cwarn}{HTML}{FBBF24}
\definecolor{cgood}{HTML}{34D399}
\definecolor{cbad}{HTML}{EF4444}
\definecolor{cheader}{HTML}{1C2C44}
\definecolor{cpaneldk}{HTML}{0B1320}

%% ═══════════════════════════════════════════════════════════════════════════
%%  BEAMER CUSTOMISATION
%% ═══════════════════════════════════════════════════════════════════════════
\usetheme{default}
\usecolortheme{default}
\usefonttheme{professionalfonts}

\setbeamercolor{background canvas}{bg=cbg}
\setbeamercolor{normal text}{fg=cink,bg=cbg}
\setbeamercolor{alerted text}{fg=cwarn}
\setbeamercolor{example text}{fg=cgood}
\setbeamercolor{frametitle}{fg=white,bg=cbg}
\setbeamerfont{frametitle}{size=\large,series=\bfseries}
\setbeamertemplate{navigation symbols}{}

\setbeamertemplate{footline}{%
  \hfill\textcolor{cmuted}{\scriptsize\insertframenumber\,/\,\inserttotalframenumber}%
  \hspace{8pt}\vspace{5pt}%
}

\setbeamertemplate{itemize item}{\textcolor{caccent}{\textbullet}}
\setbeamertemplate{itemize subitem}{\textcolor{caccent2}{$\circ$}}
\setbeamertemplate{enumerate item}{\textcolor{caccent}{\insertenumlabel.}}

\setbeamercolor{block title}{fg=white,bg=cheader}
\setbeamercolor{block body}{fg=cink,bg=cpanel}
\setbeamercolor{block title alerted}{fg=cpaneldk,bg=cwarn}
\setbeamercolor{block body alerted}{fg=cink,bg=cpanel}
\setbeamercolor{block title example}{fg=cpaneldk,bg=cgood}
\setbeamercolor{block body example}{fg=cink,bg=cpanel}

\setbeamertemplate{frametitle}{%
  \vskip4pt
  \begin{tikzpicture}[remember picture, overlay]
    \fill[caccent] (0,0) rectangle (0.07,0.52);
  \end{tikzpicture}%
  \hspace{6pt}\insertframetitle
  \vskip2pt
}

%% ─── Custom commands ──────────────────────────────────────────────────────────
\newcommand{\slidepill}[1]{%
  \textcolor{caccent}{\scriptsize\textsc{#1}}\par\vspace{1pt}%
}

\newcommand{\keyidea}[1]{%
  \begin{tikzpicture}
    \node[
      draw=caccent, fill=cpanel,
      inner xsep=6pt, inner ysep=5pt,
      rounded corners=4pt,
      text width=\dimexpr\textwidth-16pt\relax,
      text=cink, font=\small
    ] {#1};
  \end{tikzpicture}%
  \vspace{3pt}%
}

\newcommand{\warnbox}[1]{%
  \begin{beamercolorbox}[sep=4pt,rounded=true]{block title alerted}%
    \small\textbf{[!]\enskip}#1%
  \end{beamercolorbox}%
}
\newcommand{\goodbox}[1]{%
  \begin{beamercolorbox}[sep=4pt,rounded=true]{block title example}%
    \small\textbf{[OK]\enskip}#1%
  \end{beamercolorbox}%
}
\newcommand{\badbox}[1]{%
  \begin{beamercolorbox}[sep=4pt,rounded=true]{block title alerted}%
    \small\textbf{[X]\enskip}#1%
  \end{beamercolorbox}%
}

\newcommand{\formulabox}[1]{%
  \begin{center}
  \colorbox{cpanel}{\parbox{0.88\textwidth}{%
    \centering\color{cink}\small#1%
  }}
  \end{center}%
}

\begin{document}
"""

POSTAMBLE = r"""
\end{document}
"""



# ══════════════════════════════════════════════════════════════════════════
#  SLIDE GENERATORS
# ══════════════════════════════════════════════════════════════════════════

def gen_section_slide(sec: Tag) -> str:
    pill  = sec.find(class_='pill')
    h     = sec.find(['h1', 'h2'])
    sub   = sec.find('p', class_='muted')
    notes = sec.find('aside', class_='notes')

    pill_txt  = clean_text(pill)  if pill  else ''
    title_txt = clean_text(h)     if h     else ''
    sub_txt   = clean_text(sub)   if sub   else ''
    notes_txt = clean_text(notes) if notes else ''

    lines = ['\\begin{frame}[plain]']
    lines.append('  \\begin{center}')
    lines.append('    \\vfill')
    if pill_txt:
        lines.append(f'    \\textcolor{{caccent}}{{\\small\\textsc{{{pill_txt}}}}}\\\\[6pt]')
    lines.append(f'    {{\\Huge\\bfseries\\color{{white}} {title_txt}}}\\\\[8pt]')
    lines.append('    \\textcolor{caccent}{\\rule{4cm}{1.5pt}}\\\\[8pt]')
    if sub_txt:
        lines.append(f'    {{\\small\\color{{cmuted}} {sub_txt}}}')
    lines.append('    \\vfill')
    lines.append('  \\end{center}')
    if notes_txt:
        lines.append(f'  \\note{{{notes_txt[:600]}}}')
    lines.append('\\end{frame}')
    return '\n'.join(lines)


def gen_content_slide(sec: Tag, img_dir: Path) -> str:
    pill  = sec.find(class_='pill')
    h     = sec.find(['h1', 'h2'])
    ki    = sec.find(class_='keyidea')
    notes = sec.find('aside', class_='notes')

    pill_txt  = clean_text(pill) if pill  else ''
    title_txt = clean_text(h)    if h     else ''
    ki_txt    = clean_text(ki)   if ki    else ''
    notes_txt = clean_text(notes) if notes else ''

    lines = ['\\begin{frame}{' + title_txt + '}']
    if pill_txt:
        lines.append(f'  \\slidepill{{{pill_txt}}}')
    if ki_txt:
        lines.append(f'  \\keyidea{{{ki_txt}}}')
        lines.append('  \\vspace{2pt}')

    images   = [i for i in sec.find_all('img', class_='ill')
                if i.get('src', '').startswith('data:')]
    cards    = sec.find_all(class_='card')
    table    = sec.find('table')
    ul_root  = _find_top_ul(sec)
    formula  = sec.find(class_='formula')
    pre      = sec.find('pre')
    flow     = sec.find(class_='flow')
    warn     = sec.find(class_='warn')
    good     = sec.find(class_='good')
    bad      = sec.find(class_='bad')

    img_paths = []
    for img in images:
        rp = save_image(img, img_dir)
        if rp:
            img_paths.append((rp, img.get('alt', ''), img.get('data-img', '')))

    # ── Layout decision ──────────────────────────────────────────────────────
    if len(img_paths) >= 2:
        lines.append('  \\begin{columns}[T]')
        for rp, alt, _ in img_paths[:2]:
            lines.append('    \\begin{column}{0.48\\textwidth}')
            lines.append(f'      \\centering\\includegraphics[width=\\textwidth,height=0.52\\textheight,keepaspectratio]{{{rp}}}')
            if alt:
                lines.append(f'      \\par{{\\tiny\\color{{cmuted}} {esc(alt)}}}')
            lines.append('    \\end{column}')
        lines.append('  \\end{columns}')

    elif len(img_paths) == 1 and (cards or ul_root or table or formula):
        rp, alt, _ = img_paths[0]
        lines.append('  \\begin{columns}[T]')
        lines.append('    \\begin{column}{0.44\\textwidth}')
        lines.append(f'      \\centering\\includegraphics[width=\\textwidth,height=0.5\\textheight,keepaspectratio]{{{rp}}}')
        if alt:
            lines.append(f'      \\par{{\\tiny\\color{{cmuted}} {esc(alt)}}}')
        lines.append('    \\end{column}')
        lines.append('    \\begin{column}{0.54\\textwidth}')
        lines += _render_body(sec, img_dir, skip_images=True)
        lines.append('    \\end{column}')
        lines.append('  \\end{columns}')

    elif len(img_paths) == 1:
        rp, alt, _ = img_paths[0]
        lines.append(f'  \\centering\\includegraphics[width=0.9\\textwidth,height=0.62\\textheight,keepaspectratio]{{{rp}}}')
        if alt:
            lines.append(f'  \\par{{\\tiny\\color{{cmuted}} {esc(alt)}}}')

    elif len(cards) >= 2:
        n = min(len(cards), 3)
        w = round(0.92 / n, 3)
        lines.append('  \\begin{columns}[T]')
        for card in cards[:n]:
            lines.append(f'    \\begin{{column}}{{{w}\\textwidth}}')
            lines += _render_card(card)
            lines.append('    \\end{column}')
        lines.append('  \\end{columns}')

    elif table:
        lines += _render_table(table)

    elif flow:
        lines += _render_flow(flow)

    elif formula:
        lines.append(f'  \\formulabox{{{clean_text(formula)}}}')

    elif pre:
        code = pre.get_text()
        lines.append('  \\begin{lstlisting}')
        lines.append(code.rstrip())
        lines.append('  \\end{lstlisting}')

    else:
        lines += _render_body(sec, img_dir)

    if warn:
        lines.append(f'  \\warnbox{{{clean_text(warn)}}}')
    if good:
        lines.append(f'  \\goodbox{{{clean_text(good)}}}')
    if bad:
        lines.append(f'  \\badbox{{{clean_text(bad)}}}')

    if notes_txt:
        lines.append(f'  \\note{{{notes_txt[:800]}}}')
    lines.append('\\end{frame}')
    return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────────────────
def _find_top_ul(sec: Tag):
    grow = sec.find(class_='grow')
    container = grow or sec
    for child in container.children:
        if isinstance(child, Tag) and child.name in ('ul', 'ol'):
            return child
    return container.find(['ul', 'ol'])


def _render_body(sec: Tag, img_dir: Path, skip_images=False) -> list[str]:
    result: list[str] = []
    grow = sec.find(class_='grow') or sec

    def _walk(node: Tag):
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            cls  = child.get('class', [])
            name = child.name

            if 'pill' in cls or 'keyidea' in cls:
                continue
            if name == 'aside':
                continue
            if 'warn' in cls or 'good' in cls or 'bad' in cls:
                continue

            if name in ('h3', 'h4'):
                result.append(f'  \\textcolor{{caccent2}}{{\\bfseries {clean_text(child)}}}\\\\')

            elif name in ('ul', 'ol'):
                env = 'enumerate' if name == 'ol' else 'itemize'
                result.append(f'  \\begin{{{env}}}')
                for li in child.find_all('li', recursive=False):
                    result.append(f'    \\item {clean_text(li)}')
                result.append(f'  \\end{{{env}}}')

            elif name == 'p':
                txt = clean_text(child)
                if txt:
                    result.append(f'  {txt}\\\\[2pt]')

            elif name == 'pre':
                code = child.get_text()
                result.append('  \\begin{lstlisting}')
                result.append(code.rstrip())
                result.append('  \\end{lstlisting}')

            elif 'formula' in cls:
                result.append(f'  \\formulabox{{{clean_text(child)}}}')

            elif 'flow' in cls:
                result.extend(_render_flow(child))

            elif 'card' in cls:
                result.extend(_render_card(child))

            elif name == 'table':
                result.extend(_render_table(child))

            elif name == 'img' and not skip_images:
                rp = save_image(child, img_dir)
                if rp:
                    alt = esc(child.get('alt', ''))
                    result.append(f'  \\centering\\includegraphics[width=0.8\\textwidth,height=0.45\\textheight,keepaspectratio]{{{rp}}}')
                    if alt:
                        result.append(f'  \\par{{\\tiny\\color{{cmuted}} {alt}}}')

            elif name == 'div':
                _walk(child)

    _walk(grow)
    return result


def _render_card(card: Tag) -> list[str]:
    lines = []
    h3 = card.find(['h3', 'h4'])
    title = clean_text(h3) if h3 else ''
    lines.append(f'  \\begin{{block}}{{{title}}}')
    lis = card.find_all('li')
    if lis:
        lines.append('    \\begin{itemize}')
        for li in lis:
            lines.append(f'      \\item {clean_text(li)}')
        lines.append('    \\end{itemize}')
    else:
        for p in card.find_all('p'):
            txt = clean_text(p)
            if txt:
                lines.append(f'    {txt}\\\\[2pt]')
    lines.append('  \\end{block}')
    return lines


def _render_table(table: Tag) -> list[str]:
    rows = table.find_all('tr')
    if not rows:
        return []
    first_cells = rows[0].find_all(['th', 'td'])
    n_cols = len(first_cells)
    if n_cols == 0:
        return []
    col_spec = 'l' + ('X' * (n_cols - 1))
    lines = [
        '  \\begin{center}',
        f'  \\begin{{tabularx}}{{\\textwidth}}{{{col_spec}}}',
        '  \\toprule',
    ]
    for ri, tr in enumerate(rows):
        cells = tr.find_all(['th', 'td'])
        is_hdr = any(c.name == 'th' for c in cells)
        row_parts = []
        for cell in cells[:n_cols]:
            txt = clean_text(cell)
            if is_hdr:
                txt = f'\\textbf{{\\color{{white}}{txt}}}'
            row_parts.append(txt)
        lines.append('    ' + ' & '.join(row_parts) + ' \\\\')
        if is_hdr:
            lines.append('  \\midrule')
    lines += ['  \\bottomrule',
              '  \\end{tabularx}',
              '  \\end{center}']
    return lines


def _render_flow(flow: Tag) -> list[str]:
    steps = flow.find_all(class_='step')
    if not steps:
        return []
    parts = [f'\\textcolor{{caccent2}}{{{clean_text(s)}}}' for s in steps]
    return ['  ' + ' $\\rightarrow$ '.join(parts) + '\\\\[4pt]']


# ══════════════════════════════════════════════════════════════════════════
#  TITLE SLIDE
# ══════════════════════════════════════════════════════════════════════════

def gen_title_from_slide1(sec: Tag) -> str:
    h    = sec.find('h1') or sec.find('h2')
    pill = sec.find(class_='pill')
    sub  = sec.find('p', class_='muted')
    title    = clean_text(h)    if h    else 'Bai Giang'
    pill_txt = clean_text(pill) if pill else ''
    sub_txt  = clean_text(sub)  if sub  else ''
    title_clean = title.replace(r'\\', ' --- ')
    lines = [
        '\\begin{frame}[plain]',
        '  \\begin{center}',
        '    \\vfill',
        f'    {{\\Huge\\bfseries\\color{{white}} {title_clean}}}\\\\[10pt]',
        '    \\textcolor{caccent}{\\rule{5cm}{1.5pt}}\\\\[8pt]',
    ]
    if pill_txt:
        lines.append(f'    {{\\small\\color{{caccent}} {pill_txt}}}\\\\[4pt]')
    if sub_txt:
        lines.append(f'    {{\\footnotesize\\color{{cmuted}} {sub_txt}}}')
    lines += ['    \\vfill', '  \\end{center}', '\\end{frame}']
    return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def html_to_beamer(html_path: Path, out_path: Path, img_dir: Path):
    print(f'[INFO] Parsing: {html_path}')
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    sections = soup.find_all('section', class_='slide')
    total = len(sections)
    print(f'[INFO] Found {total} slides')

    img_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for i, sec in enumerate(sections, 1):
        cls   = sec.get('class', [])
        h     = sec.find(['h1', 'h2'])
        title = clean_text(h)[:60] if h else '(no title)'

        if i == 1:
            frame = gen_title_from_slide1(sec)
            print(f'  [{i:02d}/{total}] [TITLE]   {title}')
        elif 'section' in cls:
            frame = gen_section_slide(sec)
            print(f'  [{i:02d}/{total}] [SECTION] {title}')
        else:
            frame = gen_content_slide(sec, img_dir)
            print(f'  [{i:02d}/{total}]           {title}')

        frames.append(frame)

    tex = PREAMBLE + '\n\n'.join(frames) + POSTAMBLE
    out_path.write_text(tex, encoding='utf-8')

    n_imgs = len(list(img_dir.iterdir()))
    print(f'\n[DONE] LaTeX  → {out_path}')
    print(f'[INFO] Images → {img_dir}  ({n_imgs} files)')
    print()
    print('Upload len Overleaf:')
    print('  1. New project → Upload Project → chon .zip')
    print('  2. Zip gom: BaiGiang_CWRU.tex  +  folder images/')
    print('  3. Menu (top-left) → Compiler → XeLaTeX → Recompile')


if __name__ == '__main__':
    base = Path('d:/[Lab] HUST')
    candidates = list(base.rglob('BaiGiang_CWRU.html'))
    if not candidates:
        raise FileNotFoundError('Khong tim thay BaiGiang_CWRU.html')

    html_path = candidates[0]
    slide_dir = html_path.parent
    out_path  = slide_dir / 'BaiGiang_CWRU.tex'
    img_dir   = slide_dir / 'images'

    html_to_beamer(html_path, out_path, img_dir)
