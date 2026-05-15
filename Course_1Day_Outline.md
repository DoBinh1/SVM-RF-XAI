# 🏭 KHÓA ĐÀO TẠO 1 NGÀY: Chẩn Đoán Lỗi Ổ Lăn Bằng AI & SHAP

> **Đối tượng:** Kỹ sư bảo trì + kỹ sư IT/Data  
> **Mục tiêu:** Từ tín hiệu rung → Phát hiện lỗi → Giải thích tại sao  
> **Hình thức:** Hands-on (100% code chạy)  
> **Thời gian:** 3.5 giờ (tính Q&A linh hoạt)

---

## 📅 **LỊCH TRÌNH BUỔI DẠY**

### **Phần I: Mở đầu (10 phút)**
**Mục tiêu:** Hiểu bài toán + Dữ liệu

- **Vấn đề thực tế nhà máy:** Ổ lăn bị hỏng → máy dừng → mất sản xuất
- **Giải pháp:** Phát hiện sớm từ tín hiệu rung trước khi hỏng
- **Dataset CWRU:** 4 trạng thái (Normal, IR, OR, Ball) × 10 RPM → 48 kB/s
- **Dòng chảy:** Tín hiệu thô → Phân tích envelope → 22 đặc trưng → Mô hình AI → SHAP giải thích

**Code chạy:** Load 1 file audio → Visualize waveform (5 giây)

---

### **Phần II: Envelope Analysis — Phát Hiện Lỗi Ổ Lăn (45 phút)**
**Mục tiêu:** Kỹ sư hiểu "tại sao lỗi lại xuất hiện ở 107 Hz (BPFO)?"

#### **1. Tại sao FFT thô không đủ? (5 phút)**
```
❌ FFT thô: Peak ở 30 Hz (1X quay) + noise nhiều → khó thấy lỗi ổ lăn
✅ Envelope: Peak rõ ràng ở 107 Hz (BPFO) → dễ phát hiện
```

#### **2. Công thức BPFO/BPFI/BSF (5 phút)**
```
BPFO = (Nb/2) × fr × (1 - (d/D) × cos(α))
BPFI = (Nb/2) × fr × (1 + (d/D) × cos(α))
BSF = (D/2d) × fr × (1 - (d/D)² × cos²(α))

Với CWRU @1797 RPM (no load):
  Nb = 16 (số bi)
  d = 12.7 mm (đường kính bi)
  D = 71.5 mm (pitch diameter)
  α = 15.17° (contact angle)
  fr = 29.95 Hz (tần số quay)

→ BPFO ≈ 107 Hz, BPFI ≈ 162 Hz, BSF ≈ 141 Hz
```

#### **3. Envelope Analysis Step-by-step (35 phút)**
**Code chạy live:**

```python
# Step 1: Bandpass filter (2000-6000 Hz) — vùng cộng hưởng kết cấu
filtered = butterworth_bandpass(signal, 2000, 6000)

# Step 2: Hilbert transform → lấy đường bao biên độ
envelope = np.abs(scipy.signal.hilbert(filtered))

# Step 3: FFT của envelope → xem peak ở tần số lỗi
env_fft = np.fft.fft(envelope)
freqs = np.fft.fftfreq(len(envelope), 1/fs)

# Kết quả:
# Normal: flat, no peak
# IR (Inner Race): peak rõ ở 162 Hz + sidebands (162±30, 162±60, ...)
# OR (Outer Race): peak ở 107 Hz (không có sidebands nếu ở vị trí 6h)
# Ball: peak ở 141 Hz
```

**Visualization:** So sánh 4 trạng thái (Normal vs IR vs OR vs Ball)
- Cột 1: Waveform thô
- Cột 2: FFT thô
- Cột 3: Envelope (sau bandpass + Hilbert)
- Cột 4: Envelope FFT (zoom 0-300 Hz)

**Vấn đề thường gặp:**
- Q: "Tín hiệu của tôi không có peak ở BPFO" → A: Check bandpass range, có thể cần 1500-5000 Hz
- Q: "Peak ở 107 Hz mà model vẫn nói Normal" → A: Phụ thuộc cường độ + context features khác

---

### **Phần III: Trích Đặc Trưng (25 phút)**
**Mục tiêu:** Hiểu 22 features → Đầu vào cho mô hình

#### **1. 3 nhóm đặc trưng (5 phút)**

**Time Domain (6 features):**
```
rms, peak, kurtosis, crest_factor, impulse_factor, shape_factor
```
- **rms:** Mức rung tổng thể (ISO 10816: <2.8 mm/s = OK)
- **kurtosis:** Nhạy xung va chạm (Pearson = 3 là bình thường; >6 cần theo dõi; >10 hành động ngay)
- **crest_factor:** Peak/RMS — nếu lớn = có xung (CF>6: theo dõi; CF>10: hành động)

**Frequency Domain (4 features):**
```
energy_0_500Hz, energy_500_2000Hz, energy_2000_6000Hz, spectral_centroid
```
- Phân chia năng lượng theo dải tần số
- BPFO/BPFI/BSF nằm ở dải 0-500 Hz

**Envelope Domain (6 features):** — ⭐ **CỐT LÕI**
```
env_energy_BPFO, env_energy_BPFI, env_energy_BSF,
envelope_kurtosis, envelope_rms, envelope_crest_factor
```
- Peak ở BPFO → `env_energy_BPFO` cao
- Peak ở BPFI → `env_energy_BPFI` cao
- Peak ở BSF → `env_energy_BSF` cao

#### **2. Tại sao WINDOW_SIZE=16384? (3 phút)**
```
WINDOW_SIZE = 16384 → df = 48000/16384 = 2.93 Hz/bin

Với df = 2.93 Hz:
  - BPFI window [152-172 Hz]: 7 bins → có cơ hội tách biệt
  - BSF window [131-151 Hz]: 7 bins → không chồng lấp với BPFI
  - BPFO window [97-117 Hz]: có riêng

⚠️ Nếu dùng WINDOW_SIZE=2048 → df=23.44 Hz:
  → 3 cửa sổ gần nhau (107, 141, 162 Hz) sẽ bị chồng lấp
  → env_energy_BPFI ≡ env_energy_BSF (không thể phân biệt)
  → Model accuracy chỉ 50-70%
```

#### **3. Code chạy (15 phút)**
```python
# Extract features từ 1 segment
features = extract_features(signal_segment)
# Output: dict 22 keys

# Heatmap: 10 segments × 4 class → thấy pattern
# Normal: tất cả features thấp
# IR: env_energy_BPFI cao + kurtosis cao
# OR: env_energy_BPFO cao + crest_factor cao
# Ball: env_energy_BSF cao
```

---

### **Phần IV: Model Training (20 phút)**
**Mục tiêu:** Huấn luyện 2 mô hình → So sánh

#### **1. Random Forest (10 phút)**
```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=200, max_depth=15, 
                            random_state=42)
rf.fit(X_train, y_train)
accuracy = rf.score(X_test, y_test)  # ~85-86%

# Feature importance
importances = rf.feature_importances_
→ env_energy_BPFI, env_energy_BSF, kurtosis là top 3
```

#### **2. SVM (5 phút)**
```python
from sklearn.svm import SVC
svm = SVC(kernel='rbf', C=10, gamma=0.01)
svm.fit(X_train, y_train)
accuracy = svm.score(X_test, y_test)  # ~82-83%
```

#### **3. So sánh (5 phút)**
| | RF | SVM |
|---|---|---|
| Accuracy | 85-86% | 82-83% |
| Training time | Nhanh | Chậm (nếu dùng probability=True) |
| Feature importance | Có sẵn | Khó |
| Giải thích (SHAP) | Nhanh | Chậm |

**Kết luận:** Cho factory, RF là lựa chọn tốt vì dễ giải thích + nhanh

---

### **Phần V: SHAP — Giải Thích Model ⭐ (40 phút)**
**Mục tiêu:** Kỹ sư hiểu "tại sao model lại chẩn đoán là Inner Race Fault?"

#### **1. SHAP là gì? (5 phút)**
```
Giả sử mô hình dự đoán: Inner Race Fault (xác suất 95%)

SHAP trả lời: Thứ gì đẩy mô hình về quyết định này?
  ✅ env_energy_BPFI = 0.85 → ủng hộ (+0.25)
  ✅ envelope_kurtosis = 14 → ủng hộ (+0.20)
  ✅ kurtosis = 12 → ủng hộ (+0.15)
  ❌ rms = 2.1 → phản bác (-0.08)
  ❌ crest_factor = 5 → phản bác (-0.05)
  
Base value (điểm xuất phát nếu không biết gì) = 0.25
Tổng: 0.25 + 0.25 + 0.20 + 0.15 - 0.08 - 0.05 = 0.72 (IR, xác suất ≈ 72%)
```

#### **2. Code chạy (30 phút)**

**A. TreeExplainer (rất nhanh cho Random Forest):**
```python
import shap

explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_test)
# Output shape: (n_samples=6170, n_features=22, n_classes=4)

# Summary plot: Feature importance toàn cục cho mỗi class
shap.summary_plot(shap_values[:, :, class_idx], X_test, 
                  plot_type='bar')
→ Cho IR: env_energy_BPFI, envelope_kurtosis, kurtosis là top 3
```

**B. Waterfall plot (Giải thích từng mẫu cụ thể):**
```python
# Lấy 1 mẫu IR
sample_idx = 100  # ví dụ
explanation = shap.Explanation(
    values=shap_values[sample_idx, :, class_idx_IR],  # ⭐ FIX indexing
    base_values=explainer.expected_value[class_idx_IR],
    data=X_test[sample_idx],
    feature_names=feature_names
)
shap.plots.waterfall(explanation)

→ Hiển thị:
  Base value: 0.25
  env_energy_BPFI = 0.85 → +0.25
  envelope_kurtosis = 14 → +0.20
  ... (đến dự đoán cuối cùng)
```

**C. Demo 4 class (4 mẫu):**
```
Mẫu 1 (Normal):
  → Base 0.25 → -0.20 (rms thấp) → -0.15 (kurtosis thấp) → ... → Dự đoán Normal ✓

Mẫu 2 (IR):
  → Base 0.25 → +0.25 (env_BPFI cao) → +0.20 (envelope_kurtosis cao) → ... → IR ✓

Mẫu 3 (OR):
  → Base 0.25 → +0.22 (env_BPFO cao) → ... → OR ✓

Mẫu 4 (Ball):
  → Base 0.25 → +0.18 (env_BSF cao) → ... → Ball ✓
```

#### **3. Kết nối với thực tế nhà máy (5 phút)**

| Nếu SHAP cho thấy | Ý nghĩa vật lý | Hành động khuyến nghị |
|---|---|---|
| **env_energy_BPFO cao** | Lỗi rãnh ngoài (OR) | ⚠️ Chuẩn bị thay ổ lăn, giám sát 2 tuần |
| **env_energy_BPFI cao** | Lỗi rãnh trong (IR) | 🔴 Dừng máy trong 1 tuần, sửa ngay |
| **env_energy_BSF cao** | Lỗi trên bi (Ball fault) | 🟡 Kiểm tra bôi trơn, giám sát 1 tuần |
| **kurtosis > 10** | Xung va chạm rõ ràng | Hành động ngay (không chờ) |
| **envelope_kurtosis cao** | Xung lặp nhiều → lỗi phát triển | Tăng tần suất giám sát |

**Câu hỏi thực tế:**
- Q: "SHAP nói OR nhưng kỹ sư nói phải IR, ai đúng?" → A: SHAP dựa trên mô hình; cần xác nhận bằng tay
- Q: "env_BPFI = 0.5 (không cao) nhưng model vẫn nói IR?" → A: Xem kurtosis + kurtosis + context

---

### **Phần VI: Hands-on Demo + Q&A (30 phút)**

#### **Scenario 1: Dữ liệu mới → Dự đoán + Giải thích**
```python
# Học viên chạy trên dữ liệu test khác
new_sample = X_test[random_idx]
prediction = rf_model.predict([new_sample])
proba = rf_model.predict_proba([new_sample])

# SHAP giải thích
explanation = shap.Explanation(
    values=shap_values[random_idx, :, predicted_class],
    base_values=explainer.expected_value[predicted_class],
    data=new_sample,
    feature_names=feature_names
)
shap.plots.waterfall(explanation)

# Kỹ sư IT/Data: "Feature nào mạnh nhất?"
# Kỹ sư bảo trì: "Cần hành động gì?"
```

#### **Scenario 2: Confusion cases**
```
Mẫu A: Model nói IR (xác suất 65%), SHAP chỉ env_BPFI = 0.6 (không cao)
→ Cần thêm features khác ủng hộ → kiểm tra kurtosis + envelope_kurtosis

Mẫu B: Model nói Normal nhưng RF uncertainty cao
→ Model không tự tin → cần double-check bằng tay
```

#### **Q&A mở (15 phút)**
- Sẽ trả lời bất kỳ câu hỏi nào từ học viên
- Troubleshooting thực tế

---

## 🎯 **THÀNH QUẢ DỰ KIẾN SAU BUỔI**

✅ Kỹ sư bảo trì biết:
- Tại sao cần giám sát envelope ở 107, 162, 141 Hz
- Khi nào cần dừng máy (kurtosis >10? OR vs IR?)
- Cách đọc SHAP waterfall plot → Hành động gì

✅ Kỹ sư IT/Data biết:
- Toàn bộ pipeline (từ load signal → train → explain)
- Tại sao envelope analysis quan trọng hơn FFT thô
- Cách sử dụng SHAP để debug mô hình

✅ Cả hai biết:
- Khi nào tin tưởng mô hình (accuracy 85% + SHAP rõ ràng)
- Khi nào cần double-check (uncertainty cao)
- Cách triển khai trên dữ liệu mới

---

## 📚 **TÀI LIỆU HỖ TRỢ**

1. **`Course_Integrated.ipynb`** — Notebook duy nhất, chạy toàn bộ (3.5h)
2. **`Handout_01_Envelope.md`** — BPFO/BPFI/BSF công thức + giải thích
3. **`Handout_02_Features_Guide.md`** — 22 features quick reference
4. **`Handout_03_SHAP_Explained.md`** — Cách đọc waterfall + decision tree
5. **`FAQ_Troubleshooting.md`** — Câu hỏi thường gặp + giải pháp

---

**Bắt đầu:** `jupyter notebook Course_Integrated.ipynb`

