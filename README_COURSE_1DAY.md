# 🏭 KHÓA ĐÀO TẠO 1 NGÀY: CHẨN ĐOÁN LỖI Ổ LĂN BẰNG AI & SHAP

**Trainer:** Nhà máy  
**Audience:** Kỹ sư bảo trì + Kỹ sư IT/Data  
**Format:** 100% Hands-on (code chạy từ đầu)  
**Duration:** 3.5-4 giờ (tính Q&A linh hoạt)

---

## 📚 CÁC TÀI LIỆU KHÓA

### **1. Main Course Outline** ← **BẮT ĐẦU TỪ ĐÂY**
📄 [`Course_1Day_Outline.md`](Course_1Day_Outline.md)
- Lịch trình buổi dạy (6 phần)
- Mục tiêu từng phần
- Nội dung chi tiết

### **2. Integrated Notebook** ← **CODE CHẠY**
📓 [`notebooks/Course_Integrated_1Day.ipynb`](notebooks/Course_Integrated_1Day.ipynb)
- Notebook duy nhất, chạy toàn bộ pipeline
- Cô đọng nhưng đầy đủ nội dung
- Tất cả code lready được test ✅

### **3. Handout Materials** ← **THAM KHẢO NHANH**
📘 [`Handout_01_Envelope_Analysis.md`](Handout_01_Envelope_Analysis.md)
- BPFO/BPFI/BSF công thức & tính toán
- Tại sao WINDOW_SIZE=16384
- Sidebands và amplitude modulation

📗 [`Handout_02_Features_Guide.md`](Handout_02_Features_Guide.md)
- Chi tiết 22 features (time/frequency/envelope)
- Bảng tra cứu nhanh
- Bài tập xác định loại lỗi

📕 [`Handout_03_SHAP_Explained.md`](Handout_03_SHAP_Explained.md)
- Cách đọc waterfall plot
- Feature importance toàn cục
- Ví dụ 4 loại lỗi + quyết định hành động

### **4. FAQ & Troubleshooting** ← **KHI CÓ VẤN ĐỀ**
❓ [`FAQ_Troubleshooting.md`](FAQ_Troubleshooting.md)
- 14 câu hỏi thường gặp
- Troubleshooting code lỗi
- Domain shift & deployment best practices

---

## 🎯 LỊCH TRÌNH BUỔI DẠY (3.5 giờ)

| Phần | Nội dung | Thời gian | Output |
|---|---|---|---|
| **I** | Mở đầu: Bài toán & Dataset | 10 phút | Hiểu problem |
| **II** | Envelope Analysis (BPFO/BPFI/BSF) | 45 phút | Thấy peak lỗi ổ lăn |
| **III** | Trích 22 features | 25 phút | Heatmap 4 classes |
| **IV** | Training RF + SVM | 20 phút | Accuracy 85% |
| **V** | SHAP — Giải thích 🌟 | 40 phút | Waterfall plots × 4 |
| **VI** | Demo + Q&A | 30 phút | Học viên hiểu hết |
| **TỔNG** | | **3.5h** | |

---

## 🚀 CÁCH SỬ DỤNG

### **Trainer Chuẩn Bị:**
```bash
1. Kiểm tra Python packages
   pip install -r requirements.txt
   # hoặc install thủ công:
   pip install numpy pandas matplotlib scipy scikit-learn shap jupyter

2. Kiểm tra dữ liệu
   ls notebooks/features_all.csv  # Phải tồn tại từ Tutorial_03
   
3. Test notebook (optional)
   jupyter notebook notebooks/Course_Integrated_1Day.ipynb
   # Chạy 1 cell → kiểm tra setup
```

### **Buổi Học:**
```bash
1. Mở notebook
   cd "d:\[Lab] HUST\nhà máy"
   jupyter notebook notebooks/Course_Integrated_1Day.ipynb

2. Chạy từng phần (cell by cell)
   - Phần I: Cell [0-2]
   - Phần II: Cell [3-6]
   - Phần III: Cell [7-10]
   - Phần IV: Cell [11-14]
   - Phần V: Cell [15-19]
   - Phần VI: Cell [20-23]

3. Pause để Q&A sau mỗi phần
   - Học viên có thể chạy code lại
   - Hỏi câu hỏi → Trainer giải thích
   - Xem handout nếu cần detail
```

---

## 📝 CÓ GÌ TRONG TỪ HỎI COURSE

### **Kỹ sư bảo trì sẽ biết:**
```
✅ Tại sao cần giám sát envelope ở 107, 162, 141 Hz (BPFO/BPFI/BSF)
✅ Cách đọc SHAP waterfall plot → Hành động gì
✅ Ngưỡng cảnh báo: kurtosis >6 (theo dõi), >10 (hành động ngay)
✅ IR (Inner Race) nguy hiểm nhất → dừng ngay
✅ OR (Outer Race) → theo dõi 2 tuần
✅ Ball Fault → kiểm tra bôi trơn
✅ Khi nào tin model, khi nào không tin (confidence < 60%)
```

### **Kỹ sư IT/Data sẽ biết:**
```
✅ Toàn bộ pipeline (load → bandpass → envelope → FFT → features → train → SHAP)
✅ Tại sao WINDOW_SIZE=16384 (df=2.93 Hz → tách biệt BPFO/BPFI/BSF)
✅ Cách trích 22 features (time/freq/envelope domain)
✅ Envelope analysis quan trọng hơn FFT thô 10x
✅ Random Forest > SVM cho factory (dễ + nhanh + SHAP)
✅ SHAP interpretation (waterfall + summary plots)
✅ Domain shift issue & fine-tuning strategy
```

### **Cả hai sẽ biết:**
```
✅ Khi nào tin model (accuracy 85% + SHAP rõ ràng)
✅ Khi nào cần double-check (uncertainty cao)
✅ Cách kết hợp model + engineer knowledge
✅ Deployment strategy & monitoring
```

---

## 🛠️ REQUIREMENTS

### **Software:**
- Python 3.7+
- Jupyter Notebook
- scikit-learn >= 0.24
- SHAP >= 0.41
- matplotlib, scipy, pandas, numpy

### **Hardware:**
- RAM ≥ 4 GB
- CPU: Dual core (SHAP computation chạy single-threaded)
- ~30 phút để training + SHAP

### **Data:**
- `features_all.csv` (2750 samples × 22 features) — từ Tutorial_03
- Hoặc dữ liệu raw CWRU (nếu muốn envelope visualization)

---

## ❓ CÓ NGHI VẤN GÌ?

### **Câu hỏi về nội dung → Xem handouts:**
- "BPFO là gì?" → [`Handout_01_Envelope_Analysis.md`](Handout_01_Envelope_Analysis.md)
- "22 features nào quan trọng?" → [`Handout_02_Features_Guide.md`](Handout_02_Features_Guide.md)
- "Cách đọc SHAP?" → [`Handout_03_SHAP_Explained.md`](Handout_03_SHAP_Explained.md)

### **Vấn đề kỹ thuật → Xem FAQ:**
- "Notebook lỗi" → [`FAQ_Troubleshooting.md`](FAQ_Troubleshooting.md) — Q4-7
- "Accuracy thấp" → [`FAQ_Troubleshooting.md`](FAQ_Troubleshooting.md) — Q8-11
- "Deploy sao?" → [`FAQ_Troubleshooting.md`](FAQ_Troubleshooting.md) — Q12-14

### **Runtime errors → Debug steps:**
1. Kiểm tra error message (ghi lại)
2. Google error + "shap" hoặc "sklearn"
3. Kiểm tra phiên bản package: `pip show PACKAGE_NAME`
4. Update nếu cũ: `pip install --upgrade PACKAGE_NAME`
5. Nếu vẫn lỗi → email trainer with error message + code snippet

---

## 📊 KỲ VỌNG KẾT QUẢSAU BUỔI

```
┌──────────────────────────────────────────────────────────────┐
│ MỤC TIÊU: Học viên có thể độc lập                           │
│                                                              │
│ ✅ Phân tích tín hiệu rung của ổ lăn bất kỳ                 │
│ ✅ Áp dụng envelope analysis → xác định loại lỗi            │
│ ✅ Dùng SHAP để giải thích quyết định model                 │
│ ✅ Liên kết model output → hành động bảo trì                │
│ ✅ Nhận biết khi nào model sai → cảnh báo                   │
│ ✅ Retrain model khi có dữ liệu mới                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎓 NEXT STEPS SAU KHÓA

### **Tuần 1-2:**
- Triển khai model trên 1 máy test (không quan trọng)
- Collect dữ liệu thực (30 ngày = ~1000 signals)
- Monitor accuracy & false alarm rate

### **Tháng 1-2:**
- Fine-tune model trên dữ liệu nhà máy
- A/B test model CWRU vs model mới
- Rollout dần (2-3 máy → cả nhà máy)

### **Tháng 3+:**
- Monitoring hàng tháng (accuracy, false alarm)
- Retrain quarterly
- Document lessons learned

---

## 📞 CONTACT

**Trainer:** Nhà máy  
**Email:** [Liên hệ qua Slack/Email của nhà máy]  
**Office hours:** [Sau buổi học, hoặc theo lịch hẹn]

---

**Phiên bản:** 1.0 | **Ngày cập nhật:** 2026-05-15  
**Status:** ✅ Ready for 1-day workshop

