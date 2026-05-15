# Ứng dụng Machine Learning trong chẩn đoán thiết bị quay (CWRU Bearing Fault Diagnosis)

Repository này chứa toàn bộ tài liệu lý thuyết và mã nguồn thực hành (Jupyter Notebook) phục vụ cho khóa đào tạo 5 ngày về **"Ứng dụng AI/ML trong chẩn đoán và giám sát tình trạng máy móc"**, thiết kế dành riêng cho các kỹ sư bảo trì và vận hành nhà máy.

## 🎯 Mục tiêu khóa học
Giúp các kỹ sư nhà máy:
1. Hiểu bản chất tín hiệu rung động (waveform, phổ FFT) từ góc độ trực quan.
2. Nắm vững **Envelope Analysis** (phân tích đường bao) — công cụ cốt lõi trong chẩn đoán lỗi ổ lăn.
3. Nắm vững cách chuyển đổi tín hiệu thô thành các đặc trưng toán học (RMS, Kurtosis, Envelope Energy...).
4. Tránh rò rỉ dữ liệu (Data Leakage) bằng cách chia dữ liệu chuẩn xác.
5. Tự huấn luyện các mô hình Machine Learning cơ bản (SVM, Random Forest) để chẩn đoán hư hỏng vòng bi ổ lăn.
6. "Mở hộp đen" mô hình AI bằng phương pháp XAI (SHAP) để đưa ra quyết định bảo trì thực tế và an toàn, liên kết chặt chẽ với cơ chế vật lý.

---

## 📂 Cấu trúc Repository (Cập nhật Mới)

```text
├── notebooks/                                    # Mã nguồn chính (8 bài giảng)
│   ├── Tutorial_01_Signal_EDA.ipynb              # Khám phá tín hiệu, "chữ ký" lỗi
│   ├── Tutorial_02_FFT_Spectrum.ipynb            # Biến đổi Fourier (FFT)
│   ├── Tutorial_02b_Envelope_Analysis.ipynb      # Envelope Analysis (Cốt lõi)
│   ├── Tutorial_03_Feature_Engineering.ipynb     # Trích đặc trưng thời gian, tần số, envelope
│   ├── Tutorial_04_SVM_RF_Training.ipynb         # Huấn luyện SVM & RF, đánh giá
│   ├── Tutorial_05_SHAP_Explanation.ipynb        # SHAP Waterfall & Summary
│   ├── Tutorial_06_Conclusions.ipynb             # Kết luận & Khuyến nghị nhà máy
│   └── Tutorial_07_Instructor_Guide.ipynb        # Hướng dẫn dành cho giảng viên
├── src/                                          # Thư viện dùng chung
│   ├── config.py                                 # Các hằng số (FS=48kHz, BPFO, BPFI...)
│   ├── features.py                               # Hàm trích đặc trưng
│   └── signal_utils.py                           # Hàm load data, tính envelope
├── figures/                                      # Hình ảnh xuất ra từ code
├── CWRU_Tutorials/data/                          # Dữ liệu gốc (.npy, 48kHz)
├── requirements.txt                              # Danh sách thư viện Python
└── README.md                                     # File giới thiệu (bạn đang đọc)
```

### Tài liệu lý thuyết (Handouts)
Được viết bằng ngôn ngữ của kỹ sư, tối giản công thức toán học, tập trung vào ý nghĩa vật lý:
- **`PhanA_MoTa_PhanTich_DuLieu.md`**: Giới thiệu bộ dữ liệu CWRU, sơ đồ thiết bị.
- **`PhanB_GiaiThich_SVM_RandomForest.md`**: Giải thích trực giác về SVM và Random Forest.
- **`PhanD_GiaiThich_SHAP.md`**: Giải thích XAI và ứng dụng SHAP trong bảo trì.
- **`images/`**: Chứa các hình ảnh, sơ đồ minh họa.

*(Lưu ý: Các notebook ở phiên bản cũ và file tổng hợp vẫn được giữ lại tại thư mục `CWRU_Tutorials` để tham khảo.)*

---

## 🚀 Hướng dẫn sử dụng

### 1. Yêu cầu hệ thống (Requirements)
Bạn cần cài đặt Python (khuyến nghị bản 3.10+) và cài đặt thư viện bằng `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Chạy thử các bài học
Mở terminal/command prompt tại thư mục clone về, gõ lệnh:
```bash
jupyter notebook
```
Sau đó truy cập vào thư mục `notebooks/` và chạy lần lượt các file từ `Tutorial_01` đến `Tutorial_06`. Chú ý phải chạy theo thứ tự do `Tutorial_04` dùng dữ liệu của `03`, và `05` dùng dữ liệu của `04`.

---
*Dự án thực hành thuộc chương trình Lab HUST - Dữ liệu minh họa lấy từ [CWRU Bearing Data Center](https://engineering.case.edu/bearingdatacenter).*
