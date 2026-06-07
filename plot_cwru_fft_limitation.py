import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Thiết lập đường dẫn cơ sở
base_dir = Path(r"d:\[Lab] HUST\nhà máy")
data_path = base_dir / "CWRU Data" / "0HP" / "IR_007.mat"

# Đọc dữ liệu từ file .mat của CWRU (Lỗi rãnh trong 7mils, 0HP)
# Biến chứa dữ liệu gia tốc Drive End là 'X109_DE_time'
try:
    mat = scipy.io.loadmat(str(data_path))
    # Phẳng hóa mảng dữ liệu 1D
    raw_data = mat['X109_DE_time'].flatten()
    rpm = float(mat['X109RPM'][0][0])
except Exception as e:
    print(f"Lỗi khi đọc file .mat: {e}")
    sys.exit(1)

# Thông số vật lý của tín hiệu CWRU
fs = 12000  # Tần số lấy mẫu (Hz)
duration = 0.5  # Thời gian lấy phân đoạn phân tích (s)
N = int(fs * duration)  # 6000 mẫu
data_segment = raw_data[:N]
t = np.arange(N) / fs  # Miền thời gian (s)

# Tính toán các tần số lý thuyết đặc trưng
f_rotor = rpm / 60.0  # Tần số quay của rotor (1X) ≈ 30 Hz
# Vòng bi SKF 6205 tại 0HP có hệ số nhân BPFI ≈ 5.415
f_bpfi = 5.4152 * f_rotor  # ≈ 162.2 Hz

# Tính toán biến đổi Fourier nhanh (FFT) thô
fft_vals = np.fft.rfft(data_segment)
freqs = np.fft.rfftfreq(N, 1/fs)
fft_amps = np.abs(fft_vals) / N * 2

# Cài đặt style đồ thị cho slide nền sáng
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#111827'
plt.rcParams['axes.labelcolor'] = '#111827'
plt.rcParams['xtick.color'] = '#111827'
plt.rcParams['ytick.color'] = '#111827'

# Vẽ đồ thị
fig = plt.figure(figsize=(12.5, 6), dpi=150, facecolor='white')
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.25], wspace=0.25)

# --- PANEL TRÁI: MIỀN THỜI GIAN THỰC TẾ (CWRU) ---
ax_time = fig.add_subplot(gs[0])
ax_time.set_facecolor('#f9fafb')
ax_time.plot(t * 1000, data_segment, color='#1e3a8a', linewidth=0.8)
ax_time.set_title('Tín Hiệu Rung Thật (Miền Thời Gian CWRU - IR_007)', fontsize=12, fontweight='bold', pad=10, color='#d4232a')
ax_time.set_xlabel('Thời gian (ms)', fontsize=10, labelpad=5)
ax_time.set_ylabel('Gia tốc rung động (g)', fontsize=10)
ax_time.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
ax_time.set_xlim(0, duration * 1000)
ax_time.set_ylim(-3, 3)

# Chú thích về đặc trưng miền thời gian của lỗi rãnh trong
ax_time.text(20, 2.5, f'Tốc độ motor: {rpm:.1f} RPM\nTần số quay 1X: {f_rotor:.2f} Hz', 
             fontsize=9, color='#1e3a8a', bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))

# --- PANEL PHẢI: MIỀN TẦN SỐ (PHỔ FFT THÔ THỰC TẾ) ---
ax_freq = fig.add_subplot(gs[1])
ax_freq.set_facecolor('#f9fafb')
ax_freq.plot(freqs, fft_amps, color='#0f766e', linewidth=0.8)
ax_freq.set_title('Phổ FFT Thô Thực Tế từ Dữ Liệu CWRU', fontsize=12, fontweight='bold', pad=10, color='#d4232a')
ax_freq.set_xlabel('Tần số (Hz)', fontsize=10, labelpad=5)
ax_freq.set_ylabel('Biên độ phổ (g)', fontsize=10)
ax_freq.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
ax_freq.set_xlim(0, 5000)
ax_freq.set_ylim(0, 0.055)

# Đánh dấu vùng tần số cộng hưởng của bệ máy bị kích thích bởi xung va đập ổ lăn
ax_freq.axvspan(2000, 4000, color='#fbbf24', alpha=0.15)
ax_freq.text(3000, 0.045, 'Vùng cộng hưởng bệ máy\nbị kích thích (2 - 4 kHz)', color='#b45309', 
             fontsize=9, ha='center', fontweight='bold')

# Đánh dấu nền phổ dâng cao
ax_freq.annotate('Nền phổ dâng cao\ndo va đập & nhiễu', xy=(4500, 0.005), xytext=(3800, 0.018),
                 arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.2),
                 fontsize=9, color='#475569', ha='center')

# --- INSET ZOOM: HẠN CHẾ CỦA FFT THÔ (0 - 300 HZ) ---
ax_inset = ax_freq.inset_axes([0.42, 0.45, 0.55, 0.48])
ax_inset.set_facecolor('#ffffff')
ax_inset.plot(freqs, fft_amps, color='#0f766e', linewidth=1.0)
ax_inset.set_xlim(0, 300)
ax_inset.set_ylim(0, 0.045)
ax_inset.set_title('Phóng to vùng tần số thấp 0 - 300 Hz', fontsize=8, fontweight='bold', pad=3, color='#475569')
ax_inset.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
ax_inset.tick_params(labelsize=8)

# Tìm và đánh dấu các đỉnh tần số rotor
ax_inset.annotate(f'Rotor 1X ({f_rotor:.1f}Hz)', xy=(f_rotor, 0.0065), xytext=(f_rotor + 15, 0.015),
                  arrowprops=dict(arrowstyle='->', color='#1e3a8a', lw=0.8), fontsize=7, color='#1e3a8a')
ax_inset.annotate(f'Rotor 2X ({f_rotor*2:.1f}Hz)', xy=(f_rotor*2, 0.0028), xytext=(f_rotor*2 + 25, 0.008),
                  arrowprops=dict(arrowstyle='->', color='#1e3a8a', lw=0.8), fontsize=7, color='#1e3a8a')

# Đánh dấu vị trí lỗi rãnh trong lý thuyết BPFI (162.2 Hz)
ax_inset.annotate(f'BPFI lý thuyết ({f_bpfi:.1f}Hz)?\n(Bị chôn vùi trong phổ thô)', xy=(f_bpfi, 0.033), xytext=(f_bpfi + 20, 0.038),
                  arrowprops=dict(arrowstyle='->', color='#ef4444', lw=1.2),
                  fontsize=8, color='#ef4444', fontweight='bold')

# Vẽ khung nét đứt chỉ thị vùng phóng to
rect_x = [0, 300, 300, 0, 0]
rect_y = [0, 0, 0.045, 0.045, 0]
ax_freq.plot(rect_x, rect_y, color='#ef4444', linestyle='--', linewidth=1)

# Lưu đồ thị ra thư mục figures
figures_dir = base_dir / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_img_path = figures_dir / "fft_limitation_real_cwru.png"
plt.savefig(str(output_img_path), facecolor='white', bbox_inches='tight', dpi=200)
print(f"[SUCCESS] Đồ thị phân tích dữ liệu thật CWRU đã được lưu thành công tại: {output_img_path}")
plt.close()
