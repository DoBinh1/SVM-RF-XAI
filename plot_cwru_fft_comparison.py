import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Thiết lập đường dẫn
base_dir = Path(r"d:\[Lab] HUST\nhà máy")
normal_path = base_dir / "CWRU Data" / "0HP" / "Normal.mat"
fault_path = base_dir / "CWRU Data" / "0HP" / "OR_007@6.mat"

# 1. Đọc dữ liệu từ file .mat CWRU
try:
    # Trạng thái bình thường (Normal)
    mat_normal = scipy.io.loadmat(str(normal_path))
    normal_data = mat_normal['X097_DE_time'].flatten()
    rpm_normal = float(mat_normal['X097RPM'][0][0])
    
    # Trạng thái lỗi vòng ngoài (Outer Race Fault)
    mat_fault = scipy.io.loadmat(str(fault_path))
    fault_data = mat_fault['X135_DE_time'].flatten()
    rpm_fault = float(mat_fault['X135RPM'][0][0])
except Exception as e:
    print(f"Lỗi khi đọc file .mat: {e}")
    sys.exit(1)

# Các thông số vật lý tín hiệu
fs = 12000  # Tần số lấy mẫu mặc định của CWRU (Hz)
duration = 0.5  # Độ dài phân đoạn phân tích (s)
N = int(fs * duration)  # 6000 mẫu

t = np.arange(N) / fs  # Miền thời gian (s)
normal_segment = normal_data[:N]
fault_segment = fault_data[:N]

# Loại bỏ DC offset bằng cách trừ đi giá trị trung bình (Detrend)
normal_segment = normal_segment - np.mean(normal_segment)
fault_segment = fault_segment - np.mean(fault_segment)

# Tính toán tần số lý thuyết của lỗi
f_rotor = rpm_fault / 60.0  # Tần số rotor 1X (~29.93 Hz)
f_bpfo = 3.5848 * f_rotor  # Tần số lỗi BPFO lý thuyết (~107.3 Hz)

# 2. Tính toán phổ FFT thô cho cả 2 trạng thái
fft_normal = np.fft.rfft(normal_segment)
fft_fault = np.fft.rfft(fault_segment)
freqs = np.fft.rfftfreq(N, 1/fs)

amps_normal = np.abs(fft_normal) / N * 2
amps_fault = np.abs(fft_fault) / N * 2

# Thiết lập style đồ thị slide nền sáng
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#1e293b'
plt.rcParams['axes.labelcolor'] = '#1e293b'
plt.rcParams['xtick.color'] = '#1e293b'
plt.rcParams['ytick.color'] = '#1e293b'

# Vẽ đồ thị so sánh 2x2
fig, axs = plt.subplots(2, 2, figsize=(14, 8.5), dpi=150, facecolor='white')
fig.suptitle('So sánh tín hiệu rung động thực tế CWRU: Bình thường vs Lỗi vòng ngoài (Outer Race)', 
             fontsize=14, fontweight='bold', color='#1e3a8a', y=0.96)

# --- HÀNG 1: MIỀN THỜI GIAN ---
# Trái: Normal Time Domain
axs[0, 0].set_facecolor('#f8fafc')
axs[0, 0].plot(t * 1000, normal_segment, color='#059669', linewidth=0.7)
axs[0, 0].set_title('① Tín hiệu rung động thô (Trạng thái bình thường)', fontsize=11, fontweight='bold', color='#059669', pad=8)
axs[0, 0].set_ylabel('Gia tốc rung động (g)', fontsize=9)
axs[0, 0].set_xlabel('Thời gian (ms)', fontsize=9)
axs[0, 0].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[0, 0].set_xlim(0, duration * 1000)
axs[0, 0].set_ylim(-7, 7) # Đồng bộ thang đo Y để so sánh mức độ dao động

# Phải: Fault Time Domain
axs[0, 1].set_facecolor('#f8fafc')
axs[0, 1].plot(t * 1000, fault_segment, color='#0f172a', linewidth=0.7)
axs[0, 1].set_title('② Tín hiệu rung động thô (Lỗi vòng ngoài - Outer Race)', fontsize=11, fontweight='bold', color='#0f172a', pad=8)
axs[0, 1].set_xlabel('Thời gian (ms)', fontsize=9)
axs[0, 1].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[0, 1].set_xlim(0, duration * 1000)
axs[0, 1].set_ylim(-7, 7)


# --- HÀNG 2: MIỀN TẦN SỐ (PHỔ FFT THÔ) ---
# Trái: Normal FFT
axs[1, 0].set_facecolor('#f8fafc')
axs[1, 0].plot(freqs, amps_normal, color='#059669', linewidth=0.7)
axs[1, 0].set_title('③ Phổ FFT thô (Trạng thái bình thường)', fontsize=11, fontweight='bold', color='#059669', pad=8)
axs[1, 0].set_xlabel('Tần số (Hz)', fontsize=9)
axs[1, 0].set_ylabel('Biên độ phổ (g)', fontsize=9)
axs[1, 0].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[1, 0].set_xlim(0, 5000)
axs[1, 0].set_ylim(0, 0.7) # Nâng thang đo Y để hiển thị đầy đủ đỉnh phổ 0.62g của Outer Race

# Phải: Fault FFT
axs[1, 1].set_facecolor('#f8fafc')
axs[1, 1].plot(freqs, amps_fault, color='#64748b', linewidth=0.7)
axs[1, 1].set_title('④ Phổ FFT thô (Lỗi vòng ngoài - Outer Race)', fontsize=11, fontweight='bold', color='#475569', pad=8)
axs[1, 1].set_xlabel('Tần số (Hz)', fontsize=9)
axs[1, 1].set_ylabel('Biên độ phổ (g)', fontsize=9)
axs[1, 1].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[1, 1].set_xlim(0, 5000)
axs[1, 1].set_ylim(0, 0.7)


# --- INSET ZOOM VÙNG TẦN SỐ THẤP (0 - 300 HZ) ---
# Inset Normal (Trái)
ax_ins_norm = axs[1, 0].inset_axes([0.42, 0.45, 0.55, 0.48])
ax_ins_norm.set_facecolor('#ffffff')
ax_ins_norm.plot(freqs, amps_normal, color='#059669', linewidth=0.9)
ax_ins_norm.set_xlim(0, 300)
ax_ins_norm.set_ylim(0, 0.05)
ax_ins_norm.set_title('Phóng to dải thấp 0 - 300 Hz', fontsize=8, fontweight='bold', pad=3, color='#475569')
ax_ins_norm.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
ax_ins_norm.tick_params(labelsize=7)
ax_ins_norm.axvline(f_rotor, color='#0284c7', linestyle='--', linewidth=0.8, alpha=0.7)
ax_ins_norm.text(f_rotor + 5, 0.04, f'Rotor 1X ({f_rotor:.1f} Hz)', color='#0284c7', fontsize=7)

# Inset Fault (Phải)
ax_ins_fault = axs[1, 1].inset_axes([0.42, 0.45, 0.55, 0.48])
ax_ins_fault.set_facecolor('#ffffff')
ax_ins_fault.plot(freqs, amps_fault, color='#64748b', linewidth=0.9)
ax_ins_fault.set_xlim(0, 300)
ax_ins_fault.set_ylim(0, 0.05)
ax_ins_fault.set_title('Phóng to dải thấp 0 - 300 Hz', fontsize=8, fontweight='bold', pad=3, color='#475569')
ax_ins_fault.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
ax_ins_fault.tick_params(labelsize=7)

# Đánh dấu rotor 1X và 2X ở phổ lỗi
ax_ins_fault.axvline(f_rotor, color='#0284c7', linestyle='--', linewidth=0.8, alpha=0.7)
ax_ins_fault.text(f_rotor + 5, 0.04, f'1X ({f_rotor:.1f} Hz)', color='#0284c7', fontsize=7)

# Đánh dấu vị trí lỗi rãnh ngoài lý thuyết BPFO (107.3 Hz)
ax_ins_fault.axvline(f_bpfo, color='#dc2626', linestyle='--', linewidth=1.0, alpha=0.7)
ax_ins_fault.text(f_bpfo + 5, 0.03, f'BPFO lý thuyết ({f_bpfo:.1f} Hz)', color='#dc2626', fontsize=7, fontweight='bold')

# Vẽ khung nét đứt chỉ thị vùng phóng to trên biểu đồ chính
for ax in [axs[1, 0], axs[1, 1]]:
    rect_x = [0, 300, 300, 0, 0]
    rect_y = [0, 0, 0.05, 0.05, 0]
    ax.plot(rect_x, rect_y, color='#dc2626', linestyle='--', linewidth=0.8)

# Chỉnh sửa layout chung
plt.tight_layout()
fig.subplots_adjust(top=0.90)

# Lưu đồ thị ra thư mục figures
figures_dir = base_dir / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_img_path = figures_dir / "fft_comparison_normal_fault.png"
plt.savefig(str(output_img_path), facecolor='white', bbox_inches='tight', dpi=200)
print(f"[SUCCESS] FFT comparison plot saved to: {output_img_path}")
plt.close()
