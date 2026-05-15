# 📕 HANDOUT 3: SHAP GIẢI THÍCH MÔ HÌNH

> **Đối tượng:** Kỹ sư muốn hiểu "tại sao model lại quyết định như vậy?"

---

## 1. SHAP LÀ GÌ?

### 1.1. Ví dụ trực quan
```
Mô hình dự đoán mẫu X:
  → Inner Race Fault (xác suất 87%)

SHAP trả lời: Thứ gì đẩy mô hình về quyết định này?

  Feature           | SHAP value | Ý nghĩa
  ─────────────────────────────────────────────────
  env_energy_BPFI   | +0.25      | ✅ Ủng hộ (xác suất tăng 25%)
  envelope_kurtosis | +0.20      | ✅ Ủng hộ (xác suất tăng 20%)
  kurtosis          | +0.15      | ✅ Ủng hộ
  rms               | -0.08      | ❌ Phản bác (xác suất giảm 8%)
  energy_0_500Hz    | -0.05      | ❌ Phản bác
  ─────────────────────────────────────────────────
  Base value        | 0.25       | Điểm xuất phát nếu không biết gì
  TỔNG              | 0.87       | Dự đoán cuối cùng (87%)
```

### 1.2. 3 khái niệm cốt lõi

**1️⃣ Base Value**
```
Nếu không biết gì về mẫu, model dự đoán xác suất bao nhiêu?

Ví dụ: Dataset có 60% IR, 30% OR, 10% Ball
→ Base value (IR) = 0.25 (từ tỷ lệ trong training data)

Nó là điểm xuất phát, từ đó các feature đẩy giá trị lên/xuống
```

**2️⃣ SHAP Value (+)**
```
Feature "ủng hộ" quyết định → SHAP dương

env_energy_BPFI = 0.85 → SHAP = +0.25
  → Giá trị cao của env_energy_BPFI đẩy xác suất IR tăng 25%
  → Mô hình "thấy" peak ở 162 Hz → tin rằng là IR
```

**3️⃣ SHAP Value (-)**
```
Feature "phản bác" quyết định → SHAP âm

rms = 2.1 (thấp) → SHAP = -0.08
  → Mô hình kỳ vọng IR có rms cao, nhưng không → tin tưởng giảm 8%
  → Nhưng đủ vì các features khác ủng hộ mạnh
```

---

## 2. WATERFALL PLOT — CÁC ĐỌCNH TỪ TRÁI SANG PHẢI

### 2.1. Ví dụ Inner Race Fault
```
                        ← Giá trị features
                         (scaled/normalized)

Base value: 0.25       ← Điểm xuất phát
    │
    ├─ env_energy_BPFI = +0.85  → SHAP +0.25  → 0.25 + 0.25 = 0.50 ✅
    │  (Peak rõ ở 162 Hz)
    │
    ├─ envelope_kurtosis = +0.88 → SHAP +0.20  → 0.50 + 0.20 = 0.70 ✅
    │  (Xung lặp rõ ràng)
    │
    ├─ kurtosis = +0.80          → SHAP +0.15  → 0.70 + 0.15 = 0.85 ✅
    │  (Xung va chạm rõ)
    │
    ├─ rms = -0.12              → SHAP -0.04  → 0.85 - 0.04 = 0.81 ❌
    │  (Thấp hơn kỳ vọng)
    │
    └─ [... other features thêm/bớt ...] → TỔNG = 0.87 = Inner Race Fault ✓
```

### 2.2. Cách đọc từng thành phần

```
┌──────────────────────────────────────────────────────────────┐
│ Waterfall Plot: Inner Race Fault — Sample #100               │
└──────────────────────────────────────────────────────────────┘

  Base value = 0.25
  
  ←─── Phía LEFT = phản bác/âm (kéo xuống)
  
  PHẢI:
  ├─ env_energy_BPFI ────────────────→ +0.25  (MÀNG ĐỎCAO)
  │  "Peak rõ ở 162 Hz, chắc là IR"
  │
  ├─ envelope_kurtosis ───────────→ +0.20
  │  "Xung lặp rõ ràng, confirm IR"
  │
  ├─ kurtosis ─────────────→ +0.15
  │  "Xung sắc nét, thêm bằng chứng"
  │
  TRÁI:
  ├─ rms ──→ -0.04
  │  "Hơi thấp, nhưng không quan trọng"
  │
  MODEL OUTPUT = 0.87 (87% = Inner Race Fault) ✓
  
  Threshold thường là 0.5 → > 0.5 = IR
```

### 2.3. 3 loại Waterfall plot

#### **Plot A: Confident Prediction (Bối bản IR)**
```
Base = 0.25
  + env_energy_BPFI +0.25
  + envelope_kurtosis +0.20
  + kurtosis +0.15
  - rms -0.04
───────────────
Output = 0.81 ← IR (xác suất cao, tin tưởng)
```

#### **Plot B: Uncertain Prediction (Giữa OR vs Ball)**
```
Base = 0.25
  + env_energy_BPFO +0.15 → 0.40
  + envelope_rms +0.10 → 0.50
  - env_energy_BPFI -0.05 → 0.45
  - env_energy_BSF -0.05 → 0.40
───────────────
Output = 0.40 ← OR? (xác suất thấp, không tin)

⚠️ Cảnh báo: Nếu output < 0.6, model không tự tin → cần double-check
```

#### **Plot C: Confident Normal**
```
Base = 0.25
  - env_energy_BPFO -0.12 → 0.13
  - env_energy_BPFI -0.10 → 0.03
  - envelope_kurtosis -0.08 → -0.05
  - kurtosis -0.06 → -0.11
  - rms -0.04 → -0.15
───────────────
Output = 0.05 ← Normal (hầu hết features phản bác)
```

---

## 3. SUMMARY PLOT — FEATURE IMPORTANCE TOÀN CỤC

### 3.1. Cách đọc
```
Feature Importance for IR (Inner Race Fault):

  env_energy_BPFI  ■■■■■■■■■ (rất quan trọng)
  envelope_kurtosis ■■■■■■■■
  kurtosis         ■■■■■■
  rms              ■■■
  spectral_entropy ■■
  
→ BPFI + envelope_kurtosis là "chữ ký" IR
→ Các feature khác phụ thuộc/phụ trợ
```

### 3.2. Ý nghĩa cho từng loại lỗi

**IR (Inner Race) Signature:**
```
✅ Top 3: env_energy_BPFI, envelope_kurtosis, kurtosis
   → Peak rõ ở 162 Hz + xung lặp rõ ràng
```

**OR (Outer Race) Signature:**
```
✅ Top 3: env_energy_BPFO, crest_factor, envelope_rms
   → Peak ở 107 Hz + xung có pha (không điều chế)
```

**Ball Fault Signature:**
```
✅ Top 3: env_energy_BSF, envelope_rms, spectral_centroid
   → Peak ở 141 Hz + rms envelope cao
```

**Normal Signature:**
```
✅ Tất cả features âm hoặc thấp
   → Không có peak ở BPFO/BPFI/BSF
   → Không có xung va chạm
```

---

## 4. SHAP → HÀNH ĐỘNG

### 4.1. Quy trình quyết định

```
┌───────────────────────────────────────────────────────┐
│ Model dự đoán + SHAP Waterfall                        │
└───────────────────────────────────────────────────────┘
            ↓
┌─── Kiểm tra prediction confidence (xác suất)
│    ├─ < 60%? → Không tin, cần double-check
│    └─ ≥ 60%? → Tiếp tục
│
├─── Loại lỗi là gì? (từ SHAP top features)
│    ├─ env_BPFO cao → Outer Race (OR)
│    ├─ env_BPFI cao → Inner Race (IR)
│    └─ env_BSF cao → Ball Fault (B)
│
├─── Cường độ lỗi? (từ envelope_kurtosis + kurtosis)
│    ├─ Kurtosis > 10 → Lỗi đã phát triển → Hành động ngay
│    ├─ Kurtosis 6-10 → Theo dõi
│    └─ Kurtosis < 6 → Có thể bình thường
│
└─── HÀNH ĐỘNG cuối cùng (xem bảng dưới)
```

### 4.2. Bảng hành động

| Dự đoán | Confidence | Kurtosis | Hành động |
|---|---|---|---|
| IR | ≥80% | >10 | 🔴 DỪNG MÁY NGAY (1-2 tuần) |
| IR | 60-80% | 6-10 | 🟠 DỪNG TRONG 1 TUẦN (kiểm tra chắc chắn) |
| OR | ≥80% | >10 | 🔴 DỪNG TRONG 1 TUẦN |
| OR | 60-80% | 6-10 | ⚠️ THEO DÕI 2 TUẦN (chuẩn bị phụ tùng) |
| OR | <60% | <6 | 🟡 THEO DÕI 1 THÁNG |
| Ball | ≥80% | >6 | 🟡 KIỂM TRA BÔI TRƠN, THEO DÕI 1 TUẦN |
| Ball | <80% | <6 | 🟢 TIẾP TỤC GIÁM SÁT |
| Normal | ≥70% | <6 | ✅ BÌNH THƯỜNG, GIÁM SÁT ĐỊNH KỲ |
| Normal | <70% | - | ⚠️ KHÔNG TỰ TIN, KIỂM TRA THỦ CÔng |

---

## 5. CÁC TRƯ VỤ THỰC TẾ

### Trường hợp 1: IR rõ ràng
```
Mẫu: Test_IR_100
Dự đoán: Inner Race Fault (95%)

SHAP Waterfall:
  Base = 0.25
  + env_energy_BPFI = +0.30  (peak rõ ở 162 Hz)
  + envelope_kurtosis = +0.25 (kurtosis = 14)
  + kurtosis = +0.15
  - rms = -0.02
  ───────────────
  Output = 0.93 → IR ✓

Hành động: 🔴 DỪNG MÁY NGAY
Lý do: Confidence 95% + kurtosis 14 > 10 = Lỗi đã phát triển
Thời gian sửa: 1-2 tuần
```

### Trường hợp 2: OR không rõ
```
Mẫu: Test_OR_050
Dự đoán: Outer Race Fault (68%)

SHAP Waterfall:
  Base = 0.25
  + env_energy_BPFO = +0.18  (peak 107 Hz nhưng không cao)
  + envelope_rms = +0.12
  - env_energy_BPFI = -0.05
  - kurtosis = -0.02
  ───────────────
  Output = 0.68 → OR? (không tự tin)

Hành động: ⚠️ THEO DÕI 1-2 TUẦN
Lý do: Confidence chỉ 68%, cần xác nhận bằng other methods
Kiểm tra: Xem lại FFT thô, kiểm tra align
```

### Trường hợp 3: Ball fault mờ nhạt
```
Mẫu: Test_Ball_030
Dự đoán: Ball Fault (62%)

SHAP Waterfall:
  Base = 0.25
  + env_energy_BSF = +0.15
  + envelope_rms = +0.10
  - env_energy_BPFO = -0.08
  - env_energy_BPFI = -0.08
  ───────────────
  Output = 0.62 → Ball? (mờ nhạt)

Hành động: 🟡 KIỂM TRA BÔI TRƠN, THEO DÕI
Lý do: Confidence thấp 62%, nhưng env_BSF có peak → có thể là Ball
Tiếp theo: Nếu sau 1 tuần envelope_kurtosis tăng → sửa sớm
```

### Trường hợp 4: Mẫu bình thường nhưng model nói có lỗi
```
Mẫu: Test_Normal_200
Dự đoán: Outer Race Fault (72%)

SHAP Waterfall:
  Base = 0.25
  + env_energy_BPFO = +0.20  (???không cao nhưng có)
  + crest_factor = +0.12
  - rms = -0.03
  - kurtosis = -0.04
  ───────────────
  Output = 0.72 → OR? (nghi ngờ)

⚠️ DOMAIN SHIFT — Dữ liệu nhà máy khác CWRU!

Kiểm tra:
  1. Envelope plot: Có peak rõ ở 107 Hz không?
  2. RPM: Khác 1797 RPM training data?
  3. Loại ổ lăn: Khác loại ổ lăn CWRU?
  4. Vị trí cảm biến: Khác vị trí training?

Giải pháp: Thu thập dữ liệu nhà máy (normal state) → fine-tune model
```

---

## 6. FAQ

**Q: SHAP value có thể là 0?**  
A: Có, nếu feature không ảnh hưởng (neutral)

**Q: Tại sao cùng feature, mẫu này SHAP +0.1, mẫu khác +0.3?**  
A: SHAP phụ thuộc vào giá trị feature và context của mẫu khác

**Q: Nếu tất cả SHAP đều âm, kết luận gì?**  
A: Model không tin quyết định → uncertainty cao → cần double-check

**Q: SHAP dương/âm có liên quan đến feature value (cao/thấp)?**  
A: Không đơn giản — phụ thuộc vào loại feature và dữ liệu training

**Q: Có thể tin SHAP hơn dự đoán?**  
A: Không — SHAP chỉ giải thích "vì sao" model quyết định. Nếu model sai, SHAP cũng sai

---

## 7. THỰC HÀNH

### Bài tập 1: Đọc Waterfall plot
```
Waterfall của 1 mẫu:

Base = 0.25
  + env_energy_BPFI = +0.08
  + envelope_kurtosis = +0.12
  + kurtosis = +0.05
  - rms = -0.15
  - energy_0_500Hz = -0.08
  ───────────────
  Output = 0.27 → ?

Câu hỏi:
  1. Dự đoán loại lỗi gì?
  2. Model tự tin không?
  3. Nên hành động gì?

Gợi ý: Output thấp (0.27) nhưng env_BPFI dương → mâu thuẫn
```

<details>
<summary>Đáp án</summary>

1. Dự đoán: Inner Race Fault (vì env_BPFI + envelope_kurtosis dương)
2. Model **KHÔNG tự tin** (Output = 0.27 << 0.6)
3. Hành động: **Không tin dự đoán** → Kiểm tra thủ công
   - Xem envelope plot: Có peak ở 162 Hz không?
   - Xem time-domain kurtosis: Có cao không?
   - Lý do mâu thuẫn: Rms quá thấp kéo output xuống → có thể là Normal nhưng có xung nhỏ

</details>

---

**Tài liệu tham khảo:** SHAP (SHapley Additive exPlanations) dựa trên game theory, giải thích cách mô hình machine learning đưa ra quyết định

