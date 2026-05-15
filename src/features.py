# src/features.py
"""
Trích đặc trưng cho chẩn đoán lỗi ổ lăn.
Chia thành 3 nhóm rõ ràng: thời gian, tần số, envelope.
"""
import numpy as np
from scipy import stats as sp_stats
from scipy.signal import butter, filtfilt, hilbert

from src.config import (FS, BPFO, BPFI, BSF,
                         F_RES_LOW, F_RES_HIGH, ENV_BANDWIDTH)


# ═══════════════════════════════════════════════════════════════
# 1. ĐẶC TRƯNG MIỀN THỜI GIAN
# ═══════════════════════════════════════════════════════════════

def time_domain_features(segment):
    """
    Đặc trưng miền thời gian — nhìn trực tiếp vào hình dạng sóng rung.
    Lưu ý: KHÔNG có feature 'mean' vì tín hiệu rung AC-coupled → mean ≈ 0.
    """
    rms = np.sqrt(np.mean(segment**2))
    peak = np.max(np.abs(segment))
    mean_abs = np.mean(np.abs(segment)) + 1e-10

    features = {
        'rms': rms,
        # RMS = mức rung tổng thể. ISO 10816: < 2.8 mm/s cho máy loại II

        'std': np.std(segment),

        'peak': peak,

        'peak_to_peak': np.max(segment) - np.min(segment),

        'kurtosis': sp_stats.kurtosis(segment),
        # Kurtosis > 3: có xung nhọn → va chạm từ điểm lỗi
        # Kurtosis > 6: cần chú ý; > 10: cần hành động ngay

        'skewness': sp_stats.skew(segment),

        'crest_factor': peak / rms if rms > 0 else 0,
        # Peak/RMS — nhạy xung đột biến. CF > 6: theo dõi; > 10: hành động

        'impulse_factor': peak / mean_abs,
        # Peak / mean(|x|) — nhạy hơn crest factor với xung nhỏ

        'shape_factor': rms / mean_abs,
        # RMS / mean(|x|) — phản ánh "độ nhọn" phân phối biên độ

        'spectral_entropy': _spectral_entropy(segment),
        # Entropy cao = phổ trải đều (noise); thấp = có đỉnh nổi bật
    }
    return features


# ═══════════════════════════════════════════════════════════════
# 2. ĐẶC TRƯNG MIỀN TẦN SỐ
# ═══════════════════════════════════════════════════════════════

def frequency_domain_features(segment, fs=FS):
    """
    Đặc trưng miền tần số — dựa trên FFT tín hiệu thô.
    QUAN TRỌNG: BPFO=107Hz, BPFI=162Hz, BSF=141Hz đều ở dải 0-500 Hz.
    """
    n = len(segment)
    fft_vals = np.abs(np.fft.fft(segment)[:n//2]) * 2 / n
    freqs    = np.fft.fftfreq(n, 1/fs)[:n//2]

    def energy_band(f_low, f_high):
        mask = (freqs >= f_low) & (freqs < f_high)
        return np.sum(fft_vals[mask]**2)

    total_energy = np.sum(fft_vals**2) + 1e-10

    features = {
        # Dải thấp: chứa tần số lỗi CƠ BẢN (BPFO, BPFI, BSF, 1X)
        'energy_low_0_500Hz': energy_band(0, 500),
        # BPFO≈107Hz, BPFI≈162Hz, BSF≈141Hz, 1X≈30Hz đều ở đây

        # Dải trung: harmonics và sidebands (2×BPFO, 3×BPFO...)
        'energy_mid_500_2000Hz': energy_band(500, 2000),
        # KHÔNG phải dải tần lỗi cơ bản — chỉ chứa bội số bậc cao

        # Dải cao: vùng cộng hưởng kết cấu — bandpass cho envelope
        'energy_high_2000_6000Hz': energy_band(2000, 6000),

        # Tỷ lệ năng lượng dải thấp
        'energy_ratio_low_total': energy_band(0, 500) / total_energy,

        # Tần số trung tâm — dịch cao khi có lỗi ổ lăn
        'spectral_centroid': np.sum(freqs * fft_vals**2) / total_energy,

        # Tần số có biên độ lớn nhất
        'dominant_freq': freqs[np.argmax(fft_vals)] if len(fft_vals) > 0 else 0,
    }
    return features


# ═══════════════════════════════════════════════════════════════
# 3. ĐẶC TRƯNG MIỀN ENVELOPE — CỐT LÕI CHẨN ĐOÁN Ổ LĂN
# ═══════════════════════════════════════════════════════════════

def envelope_features(segment, fs=FS,
                      f_res_low=F_RES_LOW, f_res_high=F_RES_HIGH,
                      bpfo=BPFO, bpfi=BPFI, bsf=BSF,
                      bandwidth_hz=ENV_BANDWIDTH):
    """
    Đặc trưng từ Envelope Analysis.

    Tại sao quan trọng hơn FFT thông thường?
    → Lỗi ổ lăn tạo xung lặp tuần hoàn, nhưng xung bị "chôn" trong
      tín hiệu cộng hưởng kết cấu tần số cao.
    → Envelope analysis "giải điều chế" để bộc lộ tần số lặp (BPFO/BPFI/BSF).
    """
    # Bước 1: Bandpass filter quanh vùng cộng hưởng kết cấu
    nyq = fs / 2
    b, a = butter(4, [f_res_low/nyq, f_res_high/nyq], btype='band')
    filtered = filtfilt(b, a, segment)

    # Bước 2: Hilbert transform → đường bao biên độ
    envelope = np.abs(hilbert(filtered))

    # Bước 3: FFT của envelope
    n = len(envelope)
    env_fft = np.abs(np.fft.fft(envelope - np.mean(envelope))[:n//2]) * 2 / n
    env_freqs = np.fft.fftfreq(n, 1/fs)[:n//2]
    df = fs / n  # Độ phân giải tần số

    def energy_around(center_freq):
        bw = max(bandwidth_hz, 3*df)
        mask = (env_freqs >= center_freq - bw) & (env_freqs <= center_freq + bw)
        return np.sum(env_fft[mask]**2) if mask.any() else 0.0

    env_rms = np.sqrt(np.mean(envelope**2)) + 1e-10

    features = {
        'env_energy_BPFO': energy_around(bpfo),
        # Năng lượng envelope tại 107 Hz → mạnh nếu lỗi rãnh ngoài (OR)

        'env_energy_BPFI': energy_around(bpfi),
        # Năng lượng envelope tại 162 Hz → mạnh nếu lỗi rãnh trong (IR)

        'env_energy_BSF': energy_around(bsf),
        # Năng lượng envelope tại 141 Hz → mạnh nếu lỗi bi (Ball)

        'envelope_kurtosis': sp_stats.kurtosis(envelope),
        # Kurtosis envelope — rất nhạy với xung lặp lại

        'envelope_rms': env_rms,
        # Mức rung trong vùng cộng hưởng

        'envelope_crest_factor': np.max(envelope) / env_rms,
        # Crest factor envelope — đo độ đột biến xung
    }
    return features


# ═══════════════════════════════════════════════════════════════
# HÀM TỔNG HỢP
# ═══════════════════════════════════════════════════════════════

def extract_features(segment, fs=FS):
    """Trích tất cả đặc trưng từ 1 segment tín hiệu."""
    feats = {}
    feats.update(time_domain_features(segment))
    feats.update(frequency_domain_features(segment, fs))
    feats.update(envelope_features(segment, fs))
    return feats


# ── Hàm nội bộ ──────────────────────────────────────────────────

def _spectral_entropy(segment, fs=FS):
    """Shannon entropy của PSD — đo mức "trải đều" của phổ."""
    n = len(segment)
    fft_vals = np.abs(np.fft.fft(segment)[:n//2])**2
    psd = fft_vals / (np.sum(fft_vals) + 1e-10)
    return -np.sum(psd * np.log(psd + 1e-10))
