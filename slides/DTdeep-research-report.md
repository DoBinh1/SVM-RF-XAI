# Tóm tắt  
Decision Tree là mô hình phân lớp/tuyến tính cây, mỗi nút phân chia dữ liệu dựa vào điều kiện lên đặc trưng nhằm thuần hóa tập con (stop khi tất cả mẫu cùng nhãn hoặc không cải thiện). Chỉ số Gini đo độ “loang lổ” của nút: \(Gini=1-\sum p_i^2\) (nhỏ = tốt). Random Forest tạo tập hợp nhiều cây (bagging + bootstrap) với ngẫu nhiên hóa dữ liệu và đặc trưng, rồi gộp kết quả bằng phiếu đa số. Mô hình đánh giá sử dụng các chỉ số (accuracy, precision, recall, F1, AUC, ma trận nhầm lẫn), lựa chọn chỉ số tùy mục tiêu lỗi loại I/II của nhà máy. Cuối cùng, Feature Importance (dựa trên giảm độ nhiễu Gini hoặc thay đổi accuracy khi đảo permute) được đọc theo biểu đồ cột và cần lưu ý bias hay tương quan giữa đặc trưng.

## Decision Tree – khái niệm và cách hoạt động  
Một Decision Tree là mô hình cây phân lớp, trong đó các nút nội bộ (node điều kiện) xét điều kiện về đặc trưng và chia dữ liệu thành hai nhánh, tới khi phân đến nút lá (leaf) dùng nhãn chia của dữ liệu tại đó. Thuật toán xây dựng cây phân tách đệ quy (top-down), tại mỗi bước chọn điều kiện tách tối ưu (ví dụ theo Gini) và chia đến khi tập con thuần nhất hoặc không cải thiện thêm (dừng khi mọi dữ liệu trong node cùng nhãn, hoặc độ sâu tối đa, hoặc node quá nhỏ). Tree dễ quan sát và giải thích (trực quan, minh bạch), hỗ trợ cả phân loại và hồi quy.  
- **Các thành phần:** Node gốc (root) chứa toàn bộ dữ liệu; node điều kiện phân nhánh; node lá đưa ra nhãn cuối cùng.  
- **Quy trình dự đoán:** Với mẫu mới, đi từ root xuống leaf qua các điều kiện, trả nhãn của leaf cuối cùng.  
- **Chia nhánh (splitting):** Mỗi node thử các điều kiện (thuộc tính, ngưỡng) để tối đa hóa độ thuần nhất của hai node con (ví dụ dùng chỉ số Gini).  
- **Ví dụ đơn giản:** Với dữ liệu có 2 lớp, điều kiện \(x_1>5\) chia thành 2 nhóm, mục tiêu là nhóm con có Gini thấp nhất (thuần nhất nhất).  

## Chỉ số Gini và ví dụ tính toán  
Gini là chỉ số đo độ hỗn loạn của nhãn trong một node: \(Gini = 1 - \sum_{i=1}^C p_i^2\) với \(p_i\) là tần suất lớp thứ i. Gini = 0 khi node chỉ chứa một lớp; lớn nhất khi lớp cân bằng nhất.  
- **Gini index:** Để đánh giá một phép tách, tính \(Gini_{index} = Gini(p) - \sum_{k} \frac{m_k}{M} Gini(c_k)\) (chênh lệch Gini cha và tổng Gini con được weighted). Tách tốt khi Gini index lớn.  
- **Ví dụ số:** Giả sử node cha có 20 mẫu: 5 nhãn 0 và 15 nhãn 1, thì \(Gini_{cha}=1-(0.25^2+0.75^2)=0.375\). Nếu tách thành 2 node con mỗi 10 mẫu, một bên thuần lớp 1 (Gini=0), một bên có 10 mẫu (5 nhãn 0, 5 nhãn 1) Gini=0.5. Khi đó \(Gini\_index=0.375-(10/20*0 + 10/20*0.5)=0.125\). Gini index càng cao (hỗn hợp giảm mạnh) càng tốt.  
- **Dừng tách:** Giới hạn độ sâu tối đa, chỉ số mẫu tối thiểu tại node, hoặc dừng khi không còn cải thiện Gini đáng kể.  
- **Ưu/nhược điểm:** Dễ hiểu, không cần giả định tuyến tính, xử lý tốt cả dữ liệu có nhiều loại đặc trưng. Tuy nhiên cây sâu sẽ **overfitting** dữ liệu huấn luyện (độ lệch phương sai cao). Khắc phục bằng giới hạn độ sâu, số mẫu tối thiểu hoặc pruning.

## Random Forest – ý tưởng và thuật toán  
Random Forest là tổ hợp của nhiều Decision Tree với phương pháp bagging: mỗi cây được xây dựng trên tập con dữ liệu bootstrap khác nhau và tập con đặc trưng ngẫu nhiên, rồi kết hợp kết quả dự đoán (đa số phiếu). Khi huấn luyện, cho mỗi cây:  
- Lấy ngẫu nhiên \(n\) mẫu từ tập dữ liệu (bootstrap sampling).  
- Chọn ngẫu nhiên \(k\) thuộc tính (k < d) ở mỗi bước phân tách.  
- Xây dựng cây quyết định trên tập mẫu và thuộc tính này.  
Nhờ tính ngẫu nhiên (dữ liệu + đặc trưng) mỗi cây khác nhau, giảm tương quan giữa các cây. Khi dự đoán, với mẫu mới mỗi cây ra dự đoán, Random Forest cộng phiếu (vote) để quyết định nhãn chung. Ví dụ nếu 5/6 cây dự đoán lớp 1 thì kết quả cuối cùng là 1.  

```mermaid
flowchart LR
  Data[Dữ liệu gốc] -->|Bootstrap| BS1(Mẫu 1)
  Data -->|Bootstrap| BS2(Mẫu 2)
  Data -->|...\| BSk(Mẫu k)
  BS1 --> Tree1[Cây QĐ 1]
  BS2 --> Tree2[Cây QĐ 2]
  BSk --> Treek[Cây QĐ k]
  Tree1 -->|Dự đoán| Voting[Tổng hợp (vote đa số)]
  Tree2 --> Voting
  Treek --> Voting
```  

## Tham số chính và ứng dụng Random Forest  
Các tham số quan trọng bao gồm: số cây \(n\_estimators\), số thuộc tính xem xét tại mỗi node (\(max\_features\)), độ sâu tối đa, số mẫu tối thiểu cho node, v.v. (scikit-learn: `n_estimators`, `max_features`, `max_depth`, `min_samples_leaf`). Random Forest thường chuẩn hoá ngẫu nhiên với `bootstrap=True`. Ưu điểm: độ chính xác cao, giảm overfitting so với một cây đơn, tự ước lượng OOB error, ổn định trên nhiều tập khác nhau. Nhược điểm: Mất trực quan (khó giải thích từng cây), thời gian huấn luyện/tính toán lớn hơn, có thể đưa ra tầm quan trọng sai lệch nếu đặc trưng nhiều giá trị hoặc tương quan cao. *Khi dùng:* phù hợp cho bài toán phức tạp có nhiều biến và muốn cải thiện hiệu suất (đặc biệt khi một cây đơn dễ quá khớp).

## Đánh giá mô hình – Chỉ số và ma trận nhầm lẫn  
Các chỉ số phân loại phổ biến:  
- **Accuracy (Độ chính xác tổng quát):** tỉ lệ dự đoán đúng so với tổng mẫu. \(\frac{TP+TN}{TP+TN+FP+FN}\). Dùng khi tập cân bằng và chi phí lỗi tương đối như nhau; không khuyến khích khi dữ liệu mất cân bằng.  
- **Precision (Độ chính xác) và Recall (Tỉ lệ phát hiện):** Precision = \(\frac{TP}{TP+FP}\), đo tỉ lệ dự đoán dương đúng trong tổng dự đoán dương. Recall = \(\frac{TP}{TP+FN}\), đo khả năng phát hiện tất cả dương tính. Precision và Recall cân bằng với F1 score = \(2\frac{P\cdot R}{P+R}\), phù hợp với dữ liệu mất cân bằng.  
- **ROC-AUC:** AUC đo diện tích dưới ROC curve (TPR vs FPR). AUC là xác suất model xếp một mẫu dương ngẫu nhiên cao hơn mẫu âm ngẫu nhiên. AUC=1.0 là hoàn hảo, 0.5 tương đương dự đoán ngẫu nhiên.  
- **Ma trận nhầm lẫn:** Bảng đếm (TP, TN, FP, FN) giúp hiểu rõ các loại sai sót. Từ ma trận có thể tính bất kỳ chỉ số trên.  
- **Lựa chọn chỉ số theo ngữ cảnh:** Cân nhắc lỗi loại I/II: nếu bỏ sót (FN) tốn kém (ví dụ bỏ sót lỗi máy), ưu tiên **Recall**; nếu báo lỗi sai (FP) tốn kém (ví dụ ngừng dây chuyền không cần thiết), ưu tiên **Precision**. Bảng hướng dẫn: Độ thu hồi khi FN đắt, Độ đặc hiệu (ngược FPR) khi FP đắt, Độ chính xác khi cần dự đoán dương cụ thể chính xác.  
- **Biểu đồ đánh giá:** Nên vẽ cả **ROC curve** (TPR-FPR) hoặc **Precision-Recall curve** để đánh giá qua các ngưỡng. Với dữ liệu mất cân bằng, đường PR có thể phù hợp hơn. Ma trận nhầm lẫn thường được trực quan hóa dưới dạng heatmap.

## Đánh giá mô hình – Cross-validation và OOB  
Để ước lượng hiệu năng chính xác hơn, áp dụng **Cross-validation (CV)** như k-fold: chia dữ liệu thành k nhóm (fold), luân phiên dùng k–1 nhóm train và 1 nhóm test. Ví dụ, KFold chia đều dữ liệu thành k phần, mỗi lần huấn luyện trên k–1 phần và đo trên phần còn lại. CV cho điểm trung bình và độ lệch chuẩn của chỉ số, giảm phụ thuộc vào phân chia train/test cố định. Ngoài ra, Random Forest có thể dùng **OOB error**: mỗi mẫu bỏ vào OOB (không dùng) cho các cây đã không dùng nó khi xây dựng, sau đó đo lỗi trung bình trên các dự đoán của cây đó. OOB error giúp ước lượng chính xác mô hình mà không cần tách tập test.  
- **Thực hành CV:** Sử dụng hàm `cross_val_score` hoặc `cross_validate` trong scikit-learn, thử nhiều chỉ số (accuracy, F1, v.v.).  
- **Đồ thị cần có:** Hình ROC, biểu đồ hỗn hợp (precision-recall), đồ thị learning curve hoặc validation curve (if cần). Confusion matrix heatmap giúp phân tích chi tiết sai sót.

## Giải thích kết quả – Độ quan trọng đặc trưng (Feature Importance)  
Feature Importance đo mức ảnh hưởng của mỗi đặc trưng lên mô hình. Với Random Forest, có hai loại:  
- **Gini Importance (MDI):** tính tổng giảm impurity (Gini) trên tất cả nút cây do đặc trưng đó gây ra, bình thường hoá. Giá trị cho biết ảnh hưởng trung bình của đặc trưng đến phân tách. (Trong scikit-learn: `feature_importances_` tính bằng cách cộng giảm Gini).  
- **Permutation Importance:** đo độ giảm chỉ số đánh giá (ví dụ accuracy) khi hoán vị giá trị của một đặc trưng trên tập kiểm thử, nghĩa là ức chế thông tin đặc trưng đó. Phù hợp hơn khi đặc trưng phân phối đa dạng hoặc có tương quan.  
- **Cách đọc:** Đặc trưng có giá trị lớn hơn (MDI hoặc permutation) là quan trọng hơn. Tuy nhiên, MDI có thể ưu tiên biến số lượng giá trị lớn (bias) và có thể chia sẻ quan trọng nếu biến tương quan. Permutation kém hiệu quả khi tính toán nhưng không thiên lệch nhiều.  
- **Minh họa:** Vẽ **biểu đồ cột (bar chart)** xếp hạng các biến theo độ quan trọng (giá trị MDI hay giảm accuracy), ưu tiên hiển thị top features.  
- **Ví dụ ngắn:** Nếu `feature_importances_ = [0.4, 0.3, 0.3]` cho 3 biến thì biến 1 có ảnh hưởng lớn nhất (0.4). Trong biểu đồ cột, thanh của biến 1 cao nhất.  
- **Cảnh báo:** Nếu các đặc trưng có tương quan cao, chúng có thể chia sẻ thông tin và làm giảm giá trị importance từng biến. MDI còn thiên vị biến có nhiều giá trị rời rạc (ví dụ biến số ID). Nên kiểm tra qua permutation và ý nghĩa nghiệp vụ.

 *Hình: Ví dụ biểu đồ cột thể hiện độ quan trọng các đặc trưng (theo Gini importance) của mô hình Random Forest. Biểu đồ xếp hạng tính năng giảm impurity trung bình (Mean decrease in impurity).*

