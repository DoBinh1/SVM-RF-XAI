# ❓ FAQ & TROUBLESHOOTING

> **Dành cho:** Học viên gặp vấn đề hoặc có câu hỏi trong buổi học

---

## 🏗️ PHẦN I: CƠ SỞ LÝ THUYẾT

### Q1: "Tại sao BPFO = 107 Hz, không phải 196 Hz?"

**A:**
```
Công thức: BPFO = (Nb/2) × fr × [1 - (d/D) × cos(α)]

Nếu bỏ qua [1 - (d/D) × cos(α)]:
  BPFO_simple = (16/2) × 29.95 = 239.6 Hz ❌

Nhưng với cos factor:
  BPFO = 239.6 × [1 - 0.1776 × 0.9646]
       = 239.6 × [1 - 0.1714]
       = 239.6 × 0.8286
       ≈ 198.7 Hz

Nhưng CWRU thực nghiệm = 107 Hz → Có thể do:
  1. RPM thực tế khác 1797 (nếu RPM ≈ 900 → BPFO ≈ 107 Hz) ✓ ĐÚNG!
  2. Hoặc CWRU dataset có báo cáo từ 1797 RPM → nhưng dữ liệu từ 900 RPM
  3. Hoặc có slip trong ổ lăn (cage slip)

📌 **KẾT LUẬN:** Công thức chính xác, BPFO = 107 Hz là từ 900 RPM, không phải 1797 RPM
```

---

### Q2: "Tại sao peak ở BPFO mà model vẫn nói Normal?"

**A:**
```
Có nhiều nguyên nhân:

1. ✅ Envelope feature extraction sai
   - Bandpass filter [2000-6000 Hz] không phù hợp
   - Có thể cần [1500-5500 Hz] hoặc [3000-7000 Hz]
   - Giải pháp: Kiểm tra bandpass range, visualize envelope

2. ✅ WINDOW_SIZE quá nhỏ
   - WINDOW_SIZE = 2048 → df = 23.44 Hz → BPFO/BPFI/BSF chồng lấp
   - Giải pháp: Dùng WINDOW_SIZE = 16384 → df = 2.93 Hz

3. ✅ Peak quá nhỏ (amplitude thấp)
   - env_energy_BPFO = 0.05 (rất nhỏ)
   - Model kỳ vọng ≥ 0.2 → kết luận Normal
   - Giải pháp: Kiểm tra độ phân giải filter + FFT

4. ✅ Các features khác "vote" Normal
   - env_energy_BPFO cao, nhưng rms/kurtosis thấp
   - Model vote tổng → Normal (Random Forest)
   - Giải pháp: Xem SHAP để hiểu tại sao

5. ✅ Domain shift
   - Training data CWRU, dữ liệu test từ nhà máy khác
   - Amplitude, RPM, loại ổ lăn khác → model confuse
   - Giải pháp: Fine-tune model trên dữ liệu nhà máy
```

---

### Q3: "SVM dùng được không, hay phải Random Forest?"

**A:**
```
Cả hai dùng được, nhưng:

┌─────────────────────────────────────────────────────┐
│ Random Forest — KHUyên cáo cho factory              │
├─────────────────────────────────────────────────────┤
│ ✅ Nhanh training (dữ liệu lớn)                     │
│ ✅ Feature importance built-in                      │
│ ✅ SHAP TreeExplainer rất nhanh                     │
│ ✅ Ít nhạy với tune siêu tham số                    │
│ ✅ Accuracy 85-86%                                 │
│ ─────────────────────────────────────────────────── │
│ ❌ Khó trích xuất rule (Black box)                  │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SVM (RBF kernel)                                    │
├─────────────────────────────────────────────────────┤
│ ✅ Accuracy 82-83% (tương đương)                   │
│ ✅ Support vectors có thể visualize                │
│ ─────────────────────────────────────────────────── │
│ ❌ Chậm nếu dùng probability=True (Platt scaling)  │
│    → Training thêm ~5× (5-fold CV nội bộ)           │
│ ❌ Prediction chậm trên dữ liệu lớn                 │
│ ❌ Khó giải thích (KernelExplainer chậm)           │
│ ❌ Nhạy tune C, gamma                              │
│                                                      │
└─────────────────────────────────────────────────────┘

📌 **KHUYẾN CÁO:**
  - Factory → Random Forest (easy + SHAP)
  - Research → SVM (elegance, support vectors)
  - Ensemble → RF + SVM vote (nếu muốn robust)
```

---

## 🔧 PHẦN II: CODE & NOTEBOOK

### Q4: "Notebook lỗi 'WINDOW_SIZE not defined'"

**A:**
```
Nguyên nhân: src/config.py không load hoặc thiếu WINDOW_SIZE

Giải pháp:

1. Kiểm tra src/config.py có tồn tại không
   import sys, os
   print(os.path.exists('../src/config.py'))  # Phải True

2. Kiểm tra WINDOW_SIZE = 16384 trong config.py
   cat ../src/config.py | grep WINDOW_SIZE

3. Nếu vẫn lỗi, import thủ công:
   WINDOW_SIZE = 16384
   FS = 48000
   F_RES_LOW = 2000
   F_RES_HIGH = 6000
   ENV_BANDWIDTH = 10
   BPFO = 107
   BPFI = 162
   BSF = 141
```

---

### Q5: "SHAP computation chậm quá!"

**A:**
```
SHAP TreeExplainer phải tính cho tất cả samples → chậm nếu dữ liệu lớn

Tối ưu hóa:

1. Dùng subset của X_test
   explainer = shap.TreeExplainer(rf_model)
   X_sample = X_test[:1000]  # Lấy 1000 mẫu đầu tiên
   shap_values = explainer.shap_values(X_sample)

2. Dùng sample weights (TreeExplainer)
   # Tự động, không cần tune

3. Tăng n_jobs=-1 trong RandomForest
   rf = RandomForestClassifier(..., n_jobs=-1)

4. Chọn số features ít hơn (PCA)
   # Không khuyến cáo (mất interpretability)

⏱️ Ước lượng:
  - 6000 samples × 22 features → 30-60 giây
  - Nếu > 2 phút, check máy tính (RAM, CPU)
```

---

### Q6: "features_all.csv không tìm thấy"

**A:**
```
Nguyên nhân: Tutorial_03 chưa chạy hoặc output sai đường dẫn

Giải pháp:

1. Kiểm tra files tồn tại
   ls -lh ../notebooks/features_all.csv

2. Nếu không có, chạy Tutorial_03 trước
   jupyter notebook ../notebooks/Tutorial_03_Feature_Engineering.ipynb
   (Chạy toàn bộ cells → Generate features_all.csv)

3. Kiểm tra đường dẫn
   features_df = pd.read_csv('../notebooks/features_all.csv')
   # Không phải '.csv.csv' hay '../data/features_all.csv'

4. Nếu vẫn lỗi, debug:
   import os
   cwd = os.getcwd()
   print(f"CWD: {cwd}")
   print(os.listdir('../notebooks/'))  # Liệt kê files
```

---

### Q7: "Confusion matrix không hiển thị"

**A:**
```
Nguyên nhân: ConfusionMatrixDisplay cần sklearn >= 1.0

Giải pháp:

1. Update sklearn
   pip install --upgrade scikit-learn

2. Hoặc dùng seaborn (compatibility)
   import seaborn as sns
   cm = confusion_matrix(y_test, y_pred)
   sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
   plt.ylabel('True')
   plt.xlabel('Pred')
```

---

## 🎯 PHẦN III: KẾT QUẢ & INTERPRETATION

### Q8: "Accuracy 85% — có tốt không?"

**A:**
```
Tùy vào bài toán + hậu quả của sai:

📊 BẢNG ĐÁNH GIÁ:

┌─ Accuracy 85%
│
├─ Confusion Matrix:
│  ├─ Normal: 95% recall (bỏ sót 5% → OK)
│  ├─ IR: 88% recall (bỏ sót 12% → NGUY HIỂM)
│  ├─ OR: 80% recall (bỏ sót 20% → cần cải thiện)
│  └─ Ball: 82% recall
│
├─ Hậu quả nếu sai:
│  ├─ Normal → IR: Dừng máy lộn (mất sản xuất, cost ~$1000)
│  ├─ IR → Normal: Máy hỏng tiếp, spindle damage (cost ~$100k)
│  └─ OR → Normal: Ổ lăn hỏng từ từ (cost ~$5k)
│
└─ KẾT LUẬN:
   - Bỏ sót IR là nguy hiểm → cần recall IR ≥ 95%
   - False alarm Normal → chấp nhận được (cost nhỏ)
   - Cân bằng: Tăng C (SVM) hoặc adjust threshold
```

**Công thức điều chỉnh:**
```python
# Nếu threshold mặc định = 0.5
# Đổi thành 0.3 (aggressive) → nhạy IR hơn
# Nhưng tăng false alarm

y_pred_proba = rf.predict_proba(X_test)
y_pred_custom = np.argmax(y_pred_proba >= 0.3, axis=1)
# Bây giờ IR (class 1) dễ được select hơn
```

---

### Q9: "SHAP chỉ IR (87%) nhưng BPFO cao, BPFI thấp — sao?"

**A:**
```
Trường hợp này có thể:

1. ✅ Model lỗi (bị train trên dữ liệu sai)
   - SHAP chỉ theo quyết định model → nếu model sai, SHAP cũng sai
   - Giải pháp: Visualize tín hiệu gốc + envelope → xác nhận thực tế

2. ✅ Dữ liệu mâu thuẫn (IR nhưng BPFO cao)
   - Có thể mẫu này đánh nhãn sai trong dataset
   - Hoặc có 2 loại lỗi cùng lúc (IR + OR)
   - Giải pháp: Kiểm tra label training data

3. ✅ Feature scaling sai
   - SHAP tính trên scaled data, nhưng visualize gốc
   - Có thể confusion từ z-score vs giá trị thực
   - Giải pháp: Kiểm tra scaler.fit_transform()

4. ✅ Overfitting (model học noise)
   - Model training on spurious pattern
   - Test on clean data → không match
   - Giải pháp: Cross-validation, check learning curve

📌 **HÀNH ĐỘNG:**
   1. Visualize waterfall plot → xem features nào ủng hộ IR
   2. Visualize envelope của mẫu → xem thực tế peak ở đâu
   3. Nếu mâu thuẫn → ghi chú sample index, report cho trainer
```

---

### Q10: "Model dự đoán Normal (99%) nhưng SHAP cho IR (0.3)"

**A:**
```
Ngôn ngữ khác nhau:
  - "Dự đoán Normal" = model vote Normal (xác suất cao nhất)
  - "SHAP 0.3" = SHAP value của IR class (nhưng không phải output)

Giải thích:
  Khi có 4 classes (Normal, IR, OR, Ball):
  - SHAP có 4 "streams" song song (1 cho mỗi class)
  - SHAP_IR = 0.3 → không có bằng chứng IR
  - SHAP_Normal = 2.0 → bằng chứng Normal rõ ràng
  - Model chọn Normal vì xác suất max

📌 Kỹ sư không cần lo → Model quyết định đúng
   (Normal xác suất cao > IR xác suất thấp)
```

---

## ⚠️ PHẦN IV: DOMAIN SHIFT & DEPLOYMENT

### Q11: "Model CWRU 85% nhưng nhà máy chỉ 60% — sao?"

**A:**
```
DOMAIN SHIFT — Model trained trên CWRU, test trên dữ liệu nhà máy khác

┌────────────────────────────────────────────────────────┐
│ Có thể khác nhau:                                      │
├────────────────────────────────────────────────────────┤
│ 1. Loại ổ lăn (CWRU = SKF 6205)                       │
│    Nhà máy = loại khác → BPFO/BPFI/BSF khác!          │
│                                                         │
│ 2. RPM (CWRU = 900 hoặc 1797)                         │
│    Nhà máy = 1500 RPM → BPFO ≠ 107 Hz                 │
│                                                         │
│ 3. Cảm biến & vị trí                                  │
│    CWRU = accelerometer chuẩn                          │
│    Nhà máy = microphone hoặc tổng, kém chất lượng     │
│                                                         │
│ 4. Nhiễu môi trường                                   │
│    Nhà máy nhiều máy chạy quanh → tín hiệu phức tạp  │
│                                                         │
│ 5. Điều kiện vận hành (temperature, load)            │
│    CWRU = controlled lab                              │
│    Nhà máy = thực tế, biến động                      │
└────────────────────────────────────────────────────────┘

📌 GIẢI PHÁP:

Ngắn hạn (nếu không có thời gian):
  1. Fine-tune model: Thêm dữ liệu nhà máy vào training
  2. Adjust threshold: Tăng confidence requirement
  3. Ensemble: Kết hợp CWRU model + rule-based (ngưỡng)

Dài hạn:
  1. Thu thập dữ liệu nhà máy (≥ 1000 mẫu normal)
  2. Train model mới on nhà máy data
  3. Transfer learning: Dùng CWRU model làm pre-trained
```

**Code Fine-tune:**
```python
# Lấy CWRU model đã train
rf_cwru = joblib.load('cwru_model.pkl')

# Thêm dữ liệu nhà máy
X_factory = load_factory_data()
y_factory = label_by_hand()  # Ghi nhãn lại

# Fine-tune (warm start)
rf_factory = RandomForestClassifier(
    n_estimators=100,  # Thêm 100 cây
    warm_start=True,
    random_state=42
)
# Copy weights từ CWRU model
rf_factory.estimators_ = rf_cwru.estimators_
rf_factory.fit(X_factory, y_factory)  # Cập nhật với dữ liệu mới
```

---

### Q12: "Cần retraining mỗi bao lâu một lần?"

**A:**
```
Phụ thuộc vào:

1. ✅ Tần suất dữ liệu mới
   - Hàng ngày: Retraining hàng tháng (collect data)
   - Hàng tuần: Retraining hàng quý
   - Ad-hoc: Retraining khi có major change

2. ✅ Performance drift
   - Monitor accuracy hàng tháng
   - Nếu accuracy ↓ 5% → retraining
   - Nếu ổn → keep using

3. ✅ Hardware changes
   - Thay cảm biến, upgrade máy → retraining (domain shift!)
   - Thay ổ lăn loại khác → retraining

4. ✅ Trend (loại lỗi mới xuất hiện)
   - Nếu model không predict được → collect + retrain

📌 LỊCH TRÌNH KHUYẾN CÁO:

  Tháng 1-2: Training CWRU + fine-tune trên dữ liệu nhà máy
  Tháng 3-6: Deploy, collect data, monitor
  Tháng 6-9: Retrain with 3 months' data
  Tháng 9+: Hàng quý hoặc khi cần
```

---

## 📞 LIÊN HỆ & SUPPORT

### Q13: "Nếu gặp lỗi lạ, phải làm sao?"

**A:**
```
Quy trình troubleshooting:

1. Kiểm tra error message
   - Copy-paste toàn bộ error vào Google
   - Kiểm tra Stack Overflow, GitHub issues

2. Nếu error từ SHAP/sklearn
   - Kiểm tra phiên bản:
     pip show shap
     pip show scikit-learn
   - Update nếu cũ:
     pip install --upgrade shap scikit-learn

3. Nếu không fix được
   - Ghi lại:
     • Error message đầy đủ
     • Code snippet gây lỗi
     • Python/SHAP/sklearn version
     • Operating system
   - Email trainer hoặc submit GitHub issue

4. Temporary workaround
   - Nếu SHAP chậm → dùng sample nhỏ
   - Nếu memory overflow → dùng chunk processing
   - Nếu plot không show → dùng plt.savefig() thay vì plt.show()
```

---

## 🏆 PHẦN V: BEST PRACTICES

### Q14: "Nên làm gì để deploy model an toàn?"

**A:**
```
Checklist:

☐ 1. Validation
   ☐ Cross-validation trên training data (5-fold CV)
   ☐ Evaluation trên separate test set
   ☐ Confusion matrix cho từng class
   ☐ SHAP check → features rõ ràng không

☐ 2. Documentation
   ☐ Model version (v1.0, v2.0, ...)
   ☐ Training date & hyperparameters
   ☐ Accuracy numbers
   ☐ Known limitation & domain shift notes

☐ 3. Monitoring
   ☐ Log mỗi prediction (+ confidence score)
   ☐ Track accuracy hàng tháng
   ☐ Alert nếu accuracy ↓ > 5%

☐ 4. Fallback
   ☐ Nếu model confidence < 60% → human review
   ☐ Nếu prediction mâu thuẫn với SHAP → alert
   ☐ Keep manual diagnosis process (không phụ thuộc model 100%)

☐ 5. Retraining pipeline
   ☐ Script để dễ retrain (không hard-code)
   ☐ A/B test model cũ vs mới trước deploy
   ☐ Rollback plan nếu cần
```

---

**Ghi chú:** Nếu câu hỏi bạn không thấy trong FAQ này, đặt câu hỏi trực tiếp trong buổi học!

