import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PyPDF2 import PdfReader

reader = PdfReader(r'd:\[Lab] HUST\nhà máy\slides\tong hop\Tổng hợp slide.pdf')
print(f'Total pages: {len(reader.pages)}')
print('='*80)

for i, page in enumerate(reader.pages):
    text = page.extract_text()
    print(f'\n--- PAGE {i+1} ---')
    if text and text.strip():
        # Print first 300 chars of each page
        print(text[:300])
    else:
        print('[No text extracted / Image-based slide]')
