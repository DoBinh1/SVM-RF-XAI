# src/signal_utils.py
"""
Tiện ích xử lý tín hiệu: load dữ liệu, envelope analysis, vẽ hình.
"""
import os
import glob
import numpy as np
from scipy.signal import butter, filtfilt, hilbert

from src.config import (FS, WINDOW_SIZE, OVERLAP, DATA_DIR,
                         BPFO, BPFI, BSF, F_RES_LOW, F_RES_HIGH,
                         CLASS_NAMES, CLASS_COLORS, CLASS_DESC)


# ═══════════════════════════════════════════════════════════════
# LOAD DỮ LIỆU
# ═══════════════════════════════════════════════════════════════

def parse_label_from_filename(filename):
    """
    Xác định loại lỗi từ tên file .npy.
    Quy ước: Normal_DE.npy, IR_007_DE.npy, OR_007@6_DE.npy, B_007_DE.npy
    """
    base = os.path.basename(filename).replace('.npy', '').replace('_DE', '').lower()
    if 'normal' in base:
        return 'Normal'
    elif base.startswith('ir'):
        return 'IR'
    elif base.startswith('or'):
        return 'OR'
    elif base.startswith('b'):
        return 'B'
    return 'Unknown'


def load_cwru_data(data_dir=DATA_DIR, domains=None,
                   window_size=WINDOW_SIZE, overlap=OVERLAP):
    """
    Load tín hiệu CWRU (.npy), cắt thành segment với overlap.

    Returns:
        X_segments: np.array — shape (N, window_size)
        y_labels:   np.array — shape (N,) — nhãn lỗi
        file_ids:   np.array — shape (N,) — tên file gốc (dùng cho GroupShuffleSplit)
    """
    if domains is None:
        domains = ['0HP', '1HP', '2HP', '3HP']

    all_segments, all_labels, all_file_ids = [], [], []
    step = int(window_size * (1 - overlap))

    for domain in domains:
        domain_path = os.path.join(data_dir, domain)
        if not os.path.exists(domain_path):
            print(f"⚠️  Không tìm thấy thư mục: {domain_path}")
            continue

        npy_files = [os.path.join(domain_path, f) for f in os.listdir(domain_path) if f.endswith('.npy')]
        npy_files = sorted(npy_files)
        print(f"\n📂 {domain}: tìm thấy {len(npy_files)} file .npy")

        for fpath in npy_files:
            fname = os.path.basename(fpath)
            label = parse_label_from_filename(fname)

            if label == 'Unknown':
                print(f"   ⏭️  Bỏ qua: {fname}")
                continue

            signal = np.load(fpath)
            file_id = f"{domain}/{fname}"  # Unique file ID cho group split
            n_segments = (len(signal) - window_size) // step + 1

            for i in range(n_segments):
                seg = signal[i*step : i*step + window_size]
                if len(seg) == window_size:
                    all_segments.append(seg)
                    all_labels.append(label)
                    all_file_ids.append(file_id)

            print(f"   ✅ {fname}: {len(signal):,} mẫu → {n_segments} segments [{label}]")

    X = np.array(all_segments)
    y = np.array(all_labels)
    fids = np.array(all_file_ids)
    print(f"\n{'='*60}")
    print(f"TỔNG KẾT: {len(X)} segments, {len(np.unique(y))} lớp")
    for cls in CLASS_NAMES:
        if cls in y:
            print(f"  {cls}: {np.sum(y == cls)} segments")
    return X, y, fids


def load_one_sample_per_class(data_dir=DATA_DIR, domain='0HP'):
    """Load 1 tín hiệu dài cho mỗi loại lỗi (dùng cho visualization)."""
    domain_path = os.path.join(data_dir, domain)
    samples = {}
    npy_files = [os.path.join(domain_path, f) for f in os.listdir(domain_path) if f.endswith('.npy')]
    for fpath in sorted(npy_files):
        label = parse_label_from_filename(fpath)
        if label != 'Unknown' and label not in samples:
            samples[label] = np.load(fpath)
    return samples


# ═══════════════════════════════════════════════════════════════
# ENVELOPE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def envelope_spectrum(signal, fs=FS, f_low=F_RES_LOW, f_high=F_RES_HIGH):
    """
    Thực hiện Envelope Analysis 4 bước.

    Tại sao bandpass 2000–5000 Hz?
    → Vùng cộng hưởng kết cấu của thân ổ đỡ.
    → Xung va chạm từ lỗi ổ lăn "kích" vùng này.

    Returns: (freqs, env_fft, envelope, filtered)
    """
    nyq = fs / 2
    b, a = butter(4, [f_low/nyq, f_high/nyq], btype='band')
    filtered = filtfilt(b, a, signal)

    analytic = hilbert(filtered)
    envelope = np.abs(analytic)

    n = len(envelope)
    env_fft = np.abs(np.fft.fft(envelope - np.mean(envelope))[:n//2]) * 2 / n
    freqs   = np.fft.fftfreq(n, 1/fs)[:n//2]

    return freqs, env_fft, envelope, filtered
