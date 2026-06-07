import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert
from pathlib import Path
import sys

# Thiết lập đường dẫn
base_dir = Path(r"d:\[Lab] HUST\nhà máy")
fault_path = base_dir / "CWRU Data" / "0HP" / "OR_007@6.mat"

# 1. Đọc dữ liệu từ file .mat CWRU
try:
    mat_fault = scipy.io.loadmat(str(fault_path))
    fault_data = mat_fault['X135_DE_time'].flatten()
    rpm_fault = float(mat_fault['X135RPM'][0][0])
except Exception as e:
    print(f"Lỗi khi đọc file .mat CWRU: {e}")
    sys.exit(1)

# Các thông số vật lý tín hiệu
fs = 12000  # Tần số lấy mẫu mặc định của CWRU (Hz)
duration = 0.5  # Độ dài phân đoạn phân tích (s)
N = int(fs * duration)  # 6000 mẫu

t = np.arange(N) / fs  # Miền thời gian (s)
fault_segment = fault_data[:N]

# Khử DC offset bằng cách trừ đi giá trị trung bình (Detrend)
fault_segment = fault_segment - np.mean(fault_segment)

# Tính toán các tần số lý thuyết đặc trưng
f_rotor = rpm_fault / 60.0  # Tần số rotor 1X (~29.93 Hz)
f_bpfo = 3.5848 * f_rotor   # Tần số lỗi BPFO rãnh ngoài (~107.3 Hz)

# 2. Xử lý tín hiệu qua 4 bước của Envelope Analysis

# Bước 1: Lọc băng thông (Bandpass) quanh vùng cộng hưởng chính (600 - 3000 Hz)
f_low = 600.0
f_high = 3000.0
nyq = fs / 2
b, a = butter(4, [f_low/nyq, f_high/nyq], btype='band')
filtered_signal = filtfilt(b, a, fault_segment)

# Bước 2: Giải điều chế biên độ qua phép biến đổi Hilbert để trích xuất đường bao (envelope)
analytic_signal = hilbert(filtered_signal)
amplitude_envelope = np.abs(analytic_signal)

# Bước 3: Tính phổ FFT thô của tín hiệu thô ban đầu
fft_raw = np.fft.rfft(fault_segment)
freqs_raw = np.fft.rfftfreq(N, 1/fs)
amps_raw = np.abs(fft_raw) / N * 2

# Bước 4: Tính phổ FFT của đường bao (Envelope Spectrum) sau khi đã khử DC của đường bao
env_detrend = amplitude_envelope - np.mean(amplitude_envelope)
fft_env = np.fft.rfft(env_detrend)
freqs_env = np.fft.rfftfreq(N, 1/fs)
amps_env = np.abs(fft_env) / N * 2

# Thiết lập style đồ thị slide nền sáng
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Calibri', 'Arial', 'DejaVu Sans']
plt.rcParams['text.color'] = '#1e293b'
plt.rcParams['axes.labelcolor'] = '#1e293b'
plt.rcParams['xtick.color'] = '#1e293b'
plt.rcParams['ytick.color'] = '#1e293b'

# Vẽ đồ thị 2x2
fig, axs = plt.subplots(2, 2, figsize=(14, 8.5), dpi=150, facecolor='white')
fig.suptitle('Quy trình phân tích bao hình (Envelope Analysis) cho tín hiệu lỗi vòng ngoài (Outer Race)', 
             fontsize=14, fontweight='bold', color='#1e3a8a', y=0.96)

# --- HÀNG 1: MIỀN THỜI GIAN (ZOOM 50 MS ĐỂ RÕ CÁC XUNG VA ĐẬP) ---
t_ms = t * 1000
zoom_ms = 50.0  # Phóng to dải 0 - 50 ms
zoom_N = int(fs * (zoom_ms / 1000.0))

# Trái: Tín hiệu rung thô
axs[0, 0].set_facecolor('#f8fafc')
axs[0, 0].plot(t_ms[:zoom_N], fault_segment[:zoom_N], color='#0f172a', linewidth=0.7)
axs[0, 0].set_title('① Tín hiệu rung động thô (Miền thời gian - Zoom 50 ms)', fontsize=11, fontweight='bold', color='#0f172a', pad=8)
axs[0, 0].set_ylabel('Gia tốc rung động (g)', fontsize=9)
axs[0, 0].set_xlabel('Thời gian (ms)', fontsize=9)
axs[0, 0].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[0, 0].set_xlim(0, zoom_ms)
raw_zoom_max = np.max(np.abs(fault_segment[:zoom_N]))
axs[0, 0].set_ylim(-raw_zoom_max * 1.15, raw_zoom_max * 1.15) # Tự động điều chỉnh để không bị cắt cụt

# Phải: Sau lọc băng thông + Trích đường bao Hilbert
axs[0, 1].set_facecolor('#f8fafc')
axs[0, 1].plot(t_ms[:zoom_N], filtered_signal[:zoom_N], color='#94a3b8', linewidth=0.5, alpha=0.7, label='Tín hiệu sau lọc 0.6-3 kHz')
axs[0, 1].plot(t_ms[:zoom_N], amplitude_envelope[:zoom_N], color='#dc2626', linewidth=1.2, label='Đường bao (Envelope)')
axs[0, 1].set_title('② Giải điều chế: Tín hiệu sau lọc băng thông & Đường bao', fontsize=11, fontweight='bold', color='#dc2626', pad=8)
axs[0, 1].set_xlabel('Thời gian (ms)', fontsize=9)
axs[0, 1].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[0, 1].set_xlim(0, zoom_ms)
env_zoom_max = np.max(amplitude_envelope[:zoom_N])
axs[0, 1].set_ylim(-env_zoom_max * 1.15, env_zoom_max * 1.15) # Tự động điều chỉnh phóng to đường bao
axs[0, 1].legend(loc='upper right', fontsize=8)


# --- HÀNG 2: MIỀN TẦN SỐ (0 - 500 HZ ĐỂ SO SÁNH PHỔ FFT THÔ VS PHỔ BAO) ---

# Trái: Phổ FFT thô dải thấp (0 - 500 Hz)
axs[1, 0].set_facecolor('#f8fafc')
axs[1, 0].plot(freqs_raw, amps_raw, color='#64748b', linewidth=0.7)
axs[1, 0].set_title('③ Phổ FFT thô: Không thể hiện rõ tần số lỗi', fontsize=11, fontweight='bold', color='#475569', pad=8)
axs[1, 0].set_xlabel('Tần số (Hz)', fontsize=9)
axs[1, 0].set_ylabel('Biên độ phổ (g)', fontsize=9)
axs[1, 0].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[1, 0].set_xlim(0, 500)
axs[1, 0].set_ylim(0, 0.03)

# Đánh dấu vị trí BPFO lý thuyết
axs[1, 0].axvline(f_bpfo, color='#dc2626', linestyle='--', linewidth=1.0, alpha=0.7)
axs[1, 0].text(f_bpfo + 5, 0.025, f'BPFO lý thuyết ({f_bpfo:.1f} Hz)', color='#dc2626', fontsize=8, fontweight='bold')


# Phải: Phổ Bao (Envelope Spectrum) dải thấp (0 - 500 Hz)
axs[1, 1].set_facecolor('#f8fafc')
axs[1, 1].plot(freqs_env, amps_env, color='#7c3aed', linewidth=0.8)
axs[1, 1].set_title('④ Phổ bao (Envelope Spectrum): Xác định rõ tần số lỗi BPFO', fontsize=11, fontweight='bold', color='#7c3aed', pad=8)
axs[1, 1].set_xlabel('Tần số (Hz)', fontsize=9)
axs[1, 1].set_ylabel('Biên độ phổ bao (g)', fontsize=9)
axs[1, 1].grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
axs[1, 1].set_xlim(0, 500)

# Cấu hình tự động giới hạn Y-axis để hiển thị các đỉnh phổ bao rõ nét
max_amp_env = np.max(amps_env[(freqs_env >= 10) & (freqs_env <= 500)])
axs[1, 1].set_ylim(0, max_amp_env * 1.25)

# Đánh dấu đỉnh lỗi BPFO và các hài của nó
axs[1, 1].axvline(f_bpfo, color='#7c3aed', linestyle='--', linewidth=1.0, alpha=0.7)
axs[1, 1].text(f_bpfo + 5, max_amp_env * 1.05, f'BPFO ({f_bpfo:.1f} Hz)', color='#7c3aed', fontsize=8, fontweight='bold')

# Đánh dấu hài 2X BPFO
f_bpfo_2x = 2 * f_bpfo
if f_bpfo_2x <= 500:
    axs[1, 1].axvline(f_bpfo_2x, color='#7c3aed', linestyle=':', linewidth=0.8, alpha=0.7)
    axs[1, 1].text(f_bpfo_2x + 5, max_amp_env * 0.9, f'2×BPFO ({f_bpfo_2x:.1f} Hz)', color='#7c3aed', fontsize=8)

# Đánh dấu hài 3X BPFO
f_bpfo_3x = 3 * f_bpfo
if f_bpfo_3x <= 500:
    axs[1, 1].axvline(f_bpfo_3x, color='#7c3aed', linestyle=':', linewidth=0.8, alpha=0.7)
    axs[1, 1].text(f_bpfo_3x + 5, max_amp_env * 0.95, f'3×BPFO ({f_bpfo_3x:.1f} Hz)', color='#7c3aed', fontsize=8)

# Chỉnh sửa layout chung
plt.tight_layout()
fig.subplots_adjust(top=0.90)

# Lưu đồ thị ra thư mục figures
figures_dir = base_dir / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_img_path = figures_dir / "envelope_comparison_4steps.png"
plt.savefig(str(output_img_path), facecolor='white', bbox_inches='tight', dpi=200)
print(f"[SUCCESS] Plot saved to: {output_img_path}")
plt.close()
