# 📗 HANDOUT 2: 22 FEATURES QUICK REFERENCE

> **Dùng cho:** Kỹ sư muốn nhanh chóng tra cứu ý nghĩa từng feature

---

## 🎯 TÓNG HỢP 22 FEATURES

```
┌─────────────────────────────────────────────────────────────┐
│ THỜI GIAN (Time Domain) — 6 features                        │
│ ─────────────────────────────────────────────────────────── │
│ 1. rms ✅           — Mức rung tổng thể (ISO 10816)          │
│ 2. peak             — Biên độ cực đại                        │
│ 3. kurtosis ✅      — Nhạy xung va chạm (normal ≈ 3)        │
│ 4. crest_factor ✅  — Peak/RMS (CF>6: nguy hiểm)            │
│ 5. impulse_factor   — Peak/mean(|x|) (nhạy xung nhỏ)       │
│ 6. shape_factor     — RMS/mean(|x|) (phân phối biên độ)    │
│                                                              │
│ TẦN SỐ (Frequency Domain) — 4 features                       │
│ ─────────────────────────────────────────────────────────── │
│ 7. energy_0_500Hz ✅        — Dải thấp (BPFO/BPFI/BSF)     │
│ 8. energy_500_2000Hz        — Dải trung (harmonics)         │
│ 9. energy_2000_6000Hz       — Dải cao (cộng hưởng kết cấu) │
│ 10. spectral_centroid       — Trung tâm phổ (Hz)            │
│                                                              │
│ ENVELOPE (Envelope Domain) — 6 features ⭐ CỐT LÕI          │
│ ─────────────────────────────────────────────────────────── │
│ 11. env_energy_BPFO ✅      — Peak ở 107 Hz → Outer Race   │
│ 12. env_energy_BPFI ✅      — Peak ở 162 Hz → Inner Race   │
│ 13. env_energy_BSF ✅       — Peak ở 141 Hz → Ball Fault   │
│ 14. envelope_kurtosis ✅    — Nhạy xung lặp                │
│ 15. envelope_rms            — RMS đường bao                 │
│ 16. envelope_crest_factor   — Peak envelope / RMS envelope  │
│                                                              │
│ PHẦN TỬ KHÁC — 6 features                                    │
│ ─────────────────────────────────────────────────────────── │
│ 17. std                     — Độ lệch chuẩn                 │
│ 18. peak_to_peak            — Max - Min                     │
│ 19. skewness                — Độ lệch phân phối (< 0: trái) │
│ 20. spectral_entropy        — Entropy phổ (noise ↑)        │
│ 21. dominant_freq           — Tần số có biên độ cao nhất    │
│ 22. energy_ratio_low_total  — Tỷ lệ energy_0_500Hz / total │
└─────────────────────────────────────────────────────────────┘

✅ = CỐT LÕI — kỹ sư nên nhớ
```

---

## 🔍 CHI TIẾT 22 FEATURES

### **TIME DOMAIN (6)**

| Feature | Công thức | Ý nghĩa | Khi cao | Khi thấp |
|---|---|---|---|---|
| **rms** | √(mean(x²)) | Mức rung tổng thể | Rung mạnh, có lỗi | Bình thường |
| **peak** | max(\|x\|) | Biên độ cực đại | Xung va chạm | Bình thường |
| **std** | √(mean((x-μ)²)) | Độ lệch chuẩn | Rung không ổn định | Ổn định |
| **peak_to_peak** | max(x) - min(x) | Khoảng max-min | Xung lớn | Rung nhỏ |
| **kurtosis (Pearson)** | E[(x-μ)⁴]/σ⁴ | Nhạy xung va chạm | ❌ Lỗi ổ lăn (>6, >10) | ✅ Bình thường (≈3) |
| **skewness** | E[(x-μ)³]/σ³ | Độ lệch phân phối | ➡️ Phân phối nghiêng trái | ⬅️ Nghiêng phải |
| **crest_factor** | peak / rms | Peak/RMS | ❌ Xung đột ngột (CF>8) | ✅ Rung mịn (CF≈3-4) |
| **impulse_factor** | peak / mean(\|x\|) | Peak/mean(abs) | Xung nhỏ rõ ràng | Rung phân tán |
| **shape_factor** | rms / mean(\|x\|) | RMS/mean(abs) | Phân phối nhọn | Phân phối bằng phẳng |

**💡 Kỹ sư cần nhớ:**
- **rms < 2.8 mm/s** = Bình thường (ISO 10816 loại II)
- **kurtosis > 6** = Cần theo dõi; **> 10** = Hành động ngay
- **crest_factor > 8** = Nguy hiểm; **> 10** = Sửa chữa sớm

---

### **FREQUENCY DOMAIN (4)**

| Feature | Ý nghĩa | Khi cao | Khi thấp |
|---|---|---|---|
| **energy_0_500Hz** ✅ | Năng lượng dải 0-500 Hz | Lỗi ổ lăn (BPFO/BPFI/BSF đều ở đây) | Bình thường |
| **energy_500_2000Hz** | Năng lượng dải 500-2000 Hz | Harmonics, bội số bậc cao | Ổn định |
| **energy_2000_6000Hz** | Năng lượng dải 2000-6000 Hz | Vùng cộng hưởng kết cấu | Không có lỗi |
| **spectral_centroid** | Trung tâm phổ (Hz) | Năng lượng dịch sang tần số cao | Năng lượng ở tần số thấp |

**💡 Kỹ sư cần nhớ:**
- **energy_0_500Hz cao** = Có peak ở BPFO/BPFI/BSF → Lỗi ổ lăn
- **energy_2000_6000Hz cao** = Cộng hưởng kết cấu (cần bandpass filter)
- FFT thô **không** giúp phân loại IR vs OR (dùng envelope!)

---

### **ENVELOPE DOMAIN (6)** ⭐ **CỐT LÕI**

| Feature | Ý nghĩa | IR | OR | Ball | Normal |
|---|---|---|---|---|---|
| **env_energy_BPFO** | Năng lượng envelope ở 107 Hz | Low | ❌ Cao | Medium | Very Low |
| **env_energy_BPFI** | Năng lượng envelope ở 162 Hz | ❌ Cao | Low | Low | Very Low |
| **env_energy_BSF** | Năng lượng envelope ở 141 Hz | Low | Low | ❌ Cao | Very Low |
| **envelope_kurtosis** | Kurtosis đường bao | ❌ Rất cao (>10) | Cao (6-10) | Cao | Thấp (≈3) |
| **envelope_rms** | RMS đường bao | ❌ Cao | Cao | Cao | Thấp |
| **envelope_crest_factor** | Peak envelope / RMS | ❌ Cao (>8) | Cao | Cao | Thấp |

**🎯 Cách phân loại từ Envelope:**
```
┌─ Normal: Tất cả envelope features thấp
│
├─ Inner Race Fault (IR):
│  ✓ env_energy_BPFI cao (peak rõ ở 162 Hz)
│  ✓ envelope_kurtosis rất cao (>10)
│  ✓ envelope_rms cao
│
├─ Outer Race Fault (OR):
│  ✓ env_energy_BPFO cao (peak rõ ở 107 Hz)
│  ✓ envelope_kurtosis cao (6-10)
│  ✓ envelope_rms cao
│
└─ Ball Fault (B):
   ✓ env_energy_BSF cao (peak rõ ở 141 Hz)
   ✓ envelope_kurtosis cao
   ✓ envelope_rms cao
```

**💡 Kỹ sư cần nhớ:**
- **Envelope features = "chữ ký" lỗi ổ lăn**
- **env_energy_BPFO > env_energy_BPFI** → OR
- **env_energy_BPFI > env_energy_BPFO** → IR
- **envelope_kurtosis > 6** → Chắc chắn có vấn đề

---

## 📊 BẢNG THỰC HÀNH

### Bài 1: Xác định loại lỗi từ features

**Mẫu A:**
```
env_energy_BPFO = 0.95 (cao)
env_energy_BPFI = 0.12 (thấp)
env_energy_BSF = 0.10 (thấp)
envelope_kurtosis = 8.5

→ Dự đoán: ___________________
```

<details>
<summary>Đáp án</summary>

→ Dự đoán: **Outer Race Fault (OR)**

Lý do: env_energy_BPFO cao (0.95) >> các features khác, envelope_kurtosis = 8.5 (6-10 range)
</details>

---

**Mẫu B:**
```
env_energy_BPFO = 0.15
env_energy_BPFI = 0.88 (cao)
env_energy_BSF = 0.16
envelope_kurtosis = 13.2 (rất cao)

→ Dự đoán: ___________________
```

<details>
<summary>Đáp án</summary>

→ Dự đoán: **Inner Race Fault (IR)**

Lý do: env_energy_BPFI cao (0.88), envelope_kurtosis rất cao (13.2 > 10) = xung rõ ràng
</details>

---

**Mẫu C:**
```
env_energy_BPFO = 0.08
env_energy_BPFI = 0.06
env_energy_BSF = 0.82 (cao)
envelope_kurtosis = 7.1
rms = 1.2
kurtosis = 3.1

→ Dự đoán: ___________________
```

<details>
<summary>Đáp án</summary>

→ Dự đoán: **Ball Fault (B)**

Lý do: env_energy_BSF cao (0.82), envelope_kurtosis = 7.1, nhưng rms + kurtosis (time domain) thấp
</details>

---

### Bài 2: Hành động từ features

**Tình huống 1:**
```
Mô hình dự đoán: Inner Race Fault
SHAP chỉ cao: env_energy_BPFI, envelope_kurtosis, kurtosis

→ Hành động: ___________________
```

<details>
<summary>Đáp án</summary>

→ Hành động: **🔴 DỪNG MÁY NGAY**

Lý do: IR là fault nguy hiểm nhất, phát triển nhanh, không thể chờ
</details>

---

**Tình huống 2:**
```
Mô hình dự đoán: Outer Race Fault
SHAP chỉ: env_energy_BPFO = 0.6 (tương đối cao)
           kurtosis = 5.8 (sát ngưỡng)

→ Hành động: ___________________
```

<details>
<summary>Đáp án</summary>

→ Hành động: **⚠️ THEO DÕI 2 TUẦN**

Nếu sau 1 tuần:
- kurtosis ≥ 10 → Dừng máy sửa
- env_energy_BPFO tăng tiếp → Sửa sớm
- Ổn định → Tiếp tục giám sát
</details>

---

## 🚨 NGƯỠNG CẢNH BÁO

| Chỉ số | Bình thường | Theo dõi | Hành động ngay |
|---|---|---|---|
| **rms (mm/s)** | < 2.8 | 2.8-4.5 | > 4.5 |
| **kurtosis (Pearson)** | ≈ 3 | 6-10 | > 10 |
| **crest_factor** | 3-4 | 6-8 | > 8 |
| **env_energy_BPFO** | < 0.1 | 0.1-0.5 | > 0.5 |
| **env_energy_BPFI** | < 0.1 | 0.1-0.5 | > 0.5 |
| **env_energy_BSF** | < 0.1 | 0.1-0.5 | > 0.5 |
| **envelope_kurtosis** | ≈ 3 | 6-10 | > 10 |

---

## 📌 TÓM TẮT

**✅ Kỹ sư bảo trì cần nhớ:**
1. **rms < 2.8 mm/s** → Bình thường
2. **kurtosis (time) > 6** → Cần theo dõi
3. **Envelope features (BPFO/BPFI/BSF)** → Loại lỗi cụ thể
4. **envelope_kurtosis > 10** → Hành động ngay

**✅ Kỹ sư IT/Data cần nhớ:**
1. **env_energy_BPFO, env_energy_BPFI, env_energy_BSF** = Top 3 features quan trọng
2. **Envelope features = "chữ ký" lỗi** → Model học từ đó
3. **WINDOW_SIZE=16384** → df=2.93 Hz → tách biệt BPFO/BPFI/BSF
4. **Nếu accuracy thấp** → Kiểm tra envelope feature extraction

