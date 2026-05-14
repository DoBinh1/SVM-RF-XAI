# Ứng dụng Machine Learning trong chẩn đoán thiết bị quay (CWRU Bearing Fault Diagnosis)

Repository này chứa toàn bộ tài liệu lý thuyết và mã nguồn thực hành (Jupyter Notebook) phục vụ cho khóa đào tạo 5 ngày về **"Ứng dụng AI/ML trong chẩn đoán và giám sát tình trạng máy móc"**, thiết kế dành riêng cho các kỹ sư bảo trì và vận hành nhà máy.

## 🎯 Mục tiêu khóa học
Giúp các kỹ sư nhà máy:
1. Hiểu bản chất tín hiệu rung động (waveform, phổ FFT) từ góc độ trực quan.
2. Nắm vững cách chuyển đổi tín hiệu thô thành các đặc trưng toán học (RMS, Kurtosis, Peak...).
3. Tự huấn luyện các mô hình Machine Learning cơ bản (SVM, Random Forest) để chẩn đoán hư hỏng vòng bi ổ lăn.
4. "Mở hộp đen" mô hình AI bằng phương pháp XAI (SHAP) để đưa ra quyết định bảo trì thực tế và an toàn.

---

## 📂 Cấu trúc Repository

### 1. Tài liệu lý thuyết (Handouts)
Được viết bằng ngôn ngữ của kỹ sư, tối giản công thức toán học, tập trung vào ý nghĩa vật lý và ứng dụng thực tiễn, kèm theo sơ đồ minh họa trực quan:
- **`PhanA_MoTa_PhanTich_DuLieu.md`**: Giới thiệu bộ dữ liệu CWRU (Case Western Reserve University), sơ đồ thiết bị, cách đọc tín hiệu thời gian và tần số của các loại lỗi.
- **`PhanB_GiaiThich_SVM_RandomForest.md`**: Giải thích trực giác về Support Vector Machine (tìm đường biên an toàn) và Random Forest (hội đồng nhiều chuyên gia biểu quyết).
- **`PhanD_GiaiThich_SHAP.md`**: Giải thích eXplainable AI (XAI) và Shapley Values, giúp kỹ sư hiểu lý do đằng sau các dự đoán của mô hình để ra quyết định bảo trì.
- **`images/`**: Chứa các hình ảnh, sơ đồ chất lượng cao được sử dụng trong các tài liệu trên.

### 2. Thực hành (CWRU_Tutorials/)
Gồm 5 file Jupyter Notebook tự chứa (self-contained), đi theo pipeline từ xử lý dữ liệu đến giải thích mô hình:
- **`Tutorial_01_KhamPha_TinHieu.ipynb`**: Khám phá tín hiệu rung, vẽ waveform.
- **`Tutorial_02_FFT_Spectrogram.ipynb`**: Áp dụng biến đổi Fourier (FFT) và vẽ phổ thời gian - tần số (Spectrogram).
- **`Tutorial_03_TrichDacTrung_EDA.ipynb`**: Trích xuất 19 đặc trưng toán học, phân tích hộp (Boxplot).
- **`Tutorial_04_SVM_RandomForest.ipynb`**: Huấn luyện, đánh giá mô hình Support Vector Machine và Random Forest.
- **`Tutorial_05_SHAP_GiaiThich.ipynb`**: Dùng biểu đồ SHAP Summary và Waterfall để giải thích lý do mô hình chẩn đoán lỗi.
- **`data/`**: Thư mục chứa tín hiệu độ rung gốc của CWRU đã được tối ưu lại thành định dạng `.npy` (NumPy array) giúp tải cực nhanh và dễ sử dụng cho người mới học Python.

### 3. File tổng hợp và tham khảo
- `CWRU_SVM_RF_SHAP.ipynb`: Notebook tổng hợp đầy đủ chu trình thành 1 file duy nhất.
- `Đề cương chi tiết cho khóa đào tạo 5 ngày.docx`: Khung chương trình đào tạo.
- Các file PDF/Docx tài liệu mở rộng.

---

## 🚀 Hướng dẫn sử dụng

### 1. Yêu cầu hệ thống (Requirements)
Bạn cần cài đặt Python (khuyến nghị bản 3.9+) và các thư viện phân tích dữ liệu cơ bản:
```bash
pip install numpy pandas matplotlib seaborn scipy scikit-learn shap jupyter
```

### 2. Chạy thử các bài học
Mở terminal/command prompt tại thư mục clone về, gõ lệnh:
```bash
jupyter notebook
```
Sau đó truy cập vào thư mục `CWRU_Tutorials` và mở chạy lần lượt các Notebook từ `01` đến `05`.

---
*Dự án thực hành thuộc chương trình Lab HUST - Dữ liệu minh họa lấy từ [CWRU Bearing Data Center](https://engineering.case.edu/bearingdatacenter).*
