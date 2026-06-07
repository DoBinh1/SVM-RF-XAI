import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Định nghĩa đường dẫn cơ sở
base_dir = Path(r"d:\[Lab] HUST\nhà máy")

# Thiết lập font chữ và style đẹp cho slide nền sáng
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#111827'
plt.rcParams['axes.labelcolor'] = '#111827'
plt.rcParams['xtick.color'] = '#111827'
plt.rcParams['ytick.color'] = '#111827'

# 1. Khởi tạo dữ liệu giả lập tín hiệu lỗi ổ lăn
fs = 10000  # Tần số lấy mẫu (Hz)
duration = 0.4  # Thời gian thu mẫu (s)
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
N = len(t)

# Tín hiệu rotor thông thường (tần số thấp 30Hz - 1X và 60Hz - 2X)
rotor_signal = 0.25 * np.sin(2 * np.pi * 30 * t) + 0.1 * np.sin(2 * np.pi * 60 * t)

# Tần số lỗi ổ lăn lý thuyết (BPFI hoặc BPFO)
f_defect = 120  # 120 Hz (Tần số va đập lý thuyết)
f_resonance = 2200  # Tần số cộng hưởng của bệ máy (Hz)
decay_factor = 700  # Hệ số dập tắt xung va đập

# Tạo các xung va đập tuần hoàn
impact_signal = np.zeros_like(t)
impact_period = 1.0 / f_defect
impact_times = np.arange(0, duration, impact_period)

for t_start in impact_times:
    mask = t >= t_start
    t_diff = t[mask] - t_start
    # Xung va đập kích thích tần số cộng hưởng của máy
    impact_signal[mask] += 0.8 * np.exp(-decay_factor * t_diff) * np.sin(2 * np.pi * f_resonance * t_diff)

# Nhiễu nền trắng ngẫu nhiên đại diện cho môi trường công nghiệp
np.random.seed(42)
noise = np.random.normal(0, 0.15, N)

# Tín hiệu tổng hợp thu được từ cảm biến gia tốc vỏ máy
raw_signal = rotor_signal + impact_signal + noise

# 2. Tính toán biến đổi Fourier (FFT) thô
fft_vals = np.fft.rfft(raw_signal)
freqs = np.fft.rfftfreq(N, 1/fs)
fft_amps = np.abs(fft_vals) / N * 2

# 3. Vẽ đồ thị
fig = plt.figure(figsize=(12, 5.5), dpi=150, facecolor='white')
gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2], wspace=0.25)

# --- PANEL TRÁI: MIỀN THỜI GIAN ---
ax_time = fig.add_subplot(gs[0])
ax_time.set_facecolor('#f9fafb')
ax_time.plot(t * 1000, raw_signal, color='#1e3a8a', linewidth=1, label='Tín hiệu rung thô x(t)')
ax_time.set_title('Miền Thời Gian: Xung Va Đập Lỗi Ổ Lăn', fontsize=12, fontweight='bold', pad=10, color='#d4232a')
ax_time.set_xlabel('Thời gian (ms)', fontsize=10, labelpad=5)
ax_time.set_ylabel('Biên độ gia tốc (g)', fontsize=10)
ax_time.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
ax_time.set_xlim(0, duration * 1000)
ax_time.set_ylim(-1.5, 1.5)

# Đánh dấu các chu kỳ va đập lỗi
for i, t_start in enumerate(impact_times[:4]):
    ax_time.annotate('', xy=(t_start * 1000, 1.1), xytext=((t_start + impact_period) * 1000, 1.1),
                     arrowprops=dict(arrowstyle='<->', color='#d4232a', lw=1.2))
    if i == 1:
        ax_time.text((t_start + impact_period/2) * 1000, 1.2, f'Chu kỳ lỗi T = {impact_period*1000:.2f} ms\n(f = {f_defect} Hz)',
                     color='#d4232a', fontsize=8, ha='center', fontweight='bold')

# --- PANEL PHẢI: MIỀN TẦN SỐ (PHỔ FFT THÔ) ---
ax_freq = fig.add_subplot(gs[1])
ax_freq.set_facecolor('#f9fafb')
ax_freq.plot(freqs, fft_amps, color='#0f766e', linewidth=1, label='Phổ FFT thô X(f)')
ax_freq.set_title('Miền Tần Số: Phổ FFT Thô của Tín Hiệu', fontsize=12, fontweight='bold', pad=10, color='#d4232a')
ax_freq.set_xlabel('Tần số (Hz)', fontsize=10, labelpad=5)
ax_freq.set_ylabel('Biên độ phổ (g)', fontsize=10)
ax_freq.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
ax_freq.set_xlim(0, 4000)
ax_freq.set_ylim(0, 0.25)

# Tô màu làm nổi bật vùng cộng hưởng cơ học
ax_freq.axvspan(1800, 2600, color='#fbbf24', alpha=0.15, label='Vùng cộng hưởng bệ máy (kích thích bởi xung)')
ax_freq.text(2200, 0.20, 'Kích thích cộng hưởng\n(Năng lượng cao dải 2 kHz)', color='#b45309', 
             fontsize=9, ha='center', fontweight='bold')

# Đánh dấu nền phổ dâng cao do va đập và nhiễu
ax_freq.annotate('Nền phổ dâng cao\n(Nhiễu trắng + Xung lực rộng)', xy=(3500, 0.03), xytext=(2800, 0.08),
                 arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.2),
                 fontsize=9, color='#475569', ha='center')

# --- INSET ZOOM: VÙNG TẦN SỐ THẤP (HẠN CHẾ CỦA FFT THÔ) ---
# Tạo một vùng đồ thị nhỏ nằm bên trong panel phải để phóng to dải tần thấp 0 - 300 Hz
ax_inset = ax_freq.inset_axes([0.45, 0.45, 0.52, 0.48])
ax_inset.set_facecolor('#ffffff')
ax_inset.plot(freqs, fft_amps, color='#0f766e', linewidth=1.2)
ax_inset.set_xlim(0, 300)
ax_inset.set_ylim(0, 0.15)
ax_inset.set_title('Phóng to 0 - 300 Hz', fontsize=8, fontweight='bold', pad=3, color='#475569')
ax_inset.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
ax_inset.tick_params(labelsize=8)

# Đánh dấu tần số quay rotor 1X và 2X
ax_inset.annotate('1X (30Hz)', xy=(30, 0.125), xytext=(50, 0.13),
                  arrowprops=dict(arrowstyle='->', color='#1e3a8a', lw=1), fontsize=7, color='#1e3a8a')
ax_inset.annotate('2X (60Hz)', xy=(60, 0.05), xytext=(80, 0.06),
                  arrowprops=dict(arrowstyle='->', color='#1e3a8a', lw=1), fontsize=7, color='#1e3a8a')

# Đánh dấu vị trí lỗi lý thuyết BPFO (120 Hz) bị chôn vùi dưới nền nhiễu
ax_inset.annotate('Lỗi 120Hz ?\n(Bị nhiễu che khuất)', xy=(120, 0.02), xytext=(150, 0.08),
                  arrowprops=dict(arrowstyle='->', color='#ef4444', lw=1.2),
                  fontsize=8, color='#ef4444', ha='center', fontweight='bold')

# Vẽ khung chỉ thị vùng phóng to trên đồ thị chính
rect_x = [0, 300, 300, 0, 0]
rect_y = [0, 0, 0.15, 0.15, 0]
ax_freq.plot(rect_x, rect_y, color='#ef4444', linestyle='--', linewidth=1)
ax_freq.annotate('', xy=(150, 0.085), xytext=(1800, 0.12),
                 arrowprops=dict(arrowstyle='-', color='#ef4444', linestyle=':', alpha=0.5))

# Lưu đồ thị ra thư mục figures làm tài liệu slide
figures_dir = base_dir / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_img_path = figures_dir / "fft_limitation_bearing.png"
plt.savefig(str(output_img_path), facecolor='white', bbox_inches='tight', dpi=200)
print(f"[SUCCESS] Đồ thị phân tích FFT lỗi đã được lưu thành công tại: {output_img_path}")
plt.close()
