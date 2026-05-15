# src/config.py
"""
Tất cả tham số cấu hình cho bộ notebook SVM-RF-XAI.
Thay đổi 1 chỗ → áp dụng cho toàn bộ pipeline.
"""
import os

# ── Đường dẫn dữ liệu ──────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'CWRU_Tutorials', 'data')

# ── Thông số ổ lăn SKF 6205 @ ~1797 RPM (không tải) ──────────
# Công thức (SKF 6205: nb=9 bi, bd=7.94mm, pd=38.5mm, contact_angle=0°, fr=29.95 Hz @ 1797RPM):
#   BPFO = nb * fr * (1 - bd/pd * cos(contact_angle)) / 2
#   BPFI = nb * fr * (1 + bd/pd * cos(contact_angle)) / 2
#   FTF = fr * (1 - bd/pd * cos(contact_angle)) / 2
#   BSF = (pd/2bd) * fr * (1 - (bd/pd)^2)
# Kết quả từ CWRU Bearing Data Center:
BPFO = 107.4    # Hz — Ball Pass Frequency Outer race
BPFI = 162.2    # Hz — Ball Pass Frequency Inner race
BSF  = 141.2    # Hz — 2× BSF cơ bản (~ 70.6 Hz). Trong thực tế, quan sát 2×BSF vì mỗi bi chạm rãnh 2 lần/vòng quay
FTF  = 11.9     # Hz — Fundamental Train Frequency (tần số lồng bi)
RPM  = 1797     # Tốc độ quay danh nghĩa

# ── Cảm biến & lấy mẫu ─────────────────────────────────────────
FS           = 48000   # Hz — Tần số lấy mẫu CWRU (DriveEnd, 48kHz)
WINDOW_SIZE  = 16384   # Số mẫu mỗi segment — được tăng từ 2048 để đạt độ phân giải tần số ~2.93 Hz/bin
                       # Điều này cho phép các tần số lỗi (BPFI, BSF, BPFO) được tách biệt trong envelope analysis
OVERLAP      = 0.5     # 50% overlap

# ── Envelope Analysis ──────────────────────────────────────────
F_RES_LOW   = 2000    # Hz — Giới hạn dưới bandpass (vùng cộng hưởng)
F_RES_HIGH  = 5000    # Hz — Giới hạn trên bandpass
ENV_BANDWIDTH = 10    # Hz — Bandwidth quanh BPFO/BPFI/BSF khi tính năng lượng

# ── Labels & màu sắc ───────────────────────────────────────────
CLASS_NAMES  = ['Normal', 'IR', 'OR', 'B']
CLASS_COLORS = {'Normal': '#2ecc71', 'IR': '#3498db', 'OR': '#e74c3c', 'B': '#f39c12'}
CLASS_DESC = {
    'Normal': 'Bình thường',
    'IR':     'Lỗi rãnh trong (Inner Race)',
    'OR':     'Lỗi rãnh ngoài (Outer Race)',
    'B':      'Lỗi bi (Ball)',
}

# ── Random seed ────────────────────────────────────────────────
RANDOM_STATE = 42
