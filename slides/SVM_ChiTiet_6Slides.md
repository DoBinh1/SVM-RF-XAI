# SVM CHI TIẾT — 6 SLIDE BỔ SUNG
# Bài giảng: Chẩn đoán lỗi ổ lăn bằng Machine Learning (dữ liệu CWRU)

> **Đối tượng:** Kỹ sư cơ khí / bảo trì — có nền tảng kỹ thuật, không chuyên ML  
> **Thời lượng:** ~15–20 phút  
> **Ngôn ngữ:** Tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh  
> **Màu sắc xuyên suốt:** Xanh dương `#1f77b4` = Bình thường (Normal) · Đỏ `#d62728` = Lỗi (Fault)

---

## Slide 1: Hard Margin SVM — Ôn lại nhanh

**Mục tiêu truyền đạt:** Kỹ sư nắm được 3 khái niệm nền tảng — siêu phẳng quyết định (decision hyperplane), margin, và support vectors — trước khi mở rộng sang các trường hợp phức tạp hơn.

**Bố cục:** 2 cột — Trái: nội dung bullet (40%) · Phải: hình minh hoạ 2D (60%)

### Nội dung chính

- **Bài toán:** Cho tập dữ liệu 2 lớp tách biệt hoàn toàn → tìm đường phân tách "tốt nhất"
- **Siêu phẳng quyết định (Decision Hyperplane):** Đường/mặt chia không gian thành 2 vùng — một bên là "Bình thường", bên kia là "Lỗi"
- **Margin:** Khoảng cách từ siêu phẳng đến điểm dữ liệu gần nhất mỗi bên
- **Support Vectors:** Các điểm dữ liệu nằm đúng trên ranh giới margin — chỉ chúng quyết định vị trí đường phân tách
- **Mục tiêu tối ưu:** Tìm siêu phẳng sao cho margin **lớn nhất** → mô hình tổng quát hoá tốt nhất

> 💡 *Tương tự thực tế:* Khi bạn kẻ vạch an toàn giữa khu vực vận hành và khu vực nguy hiểm trong nhà máy — vạch càng xa hai bên, xác suất "lấn tuyến" càng thấp.

### Hình minh hoạ

**Mô tả chi tiết:**
- Không gian 2D, trục X: đặc trưng 1 (ví dụ "RMS"), trục Y: đặc trưng 2 (ví dụ "Kurtosis")
- **Đám mây xanh dương** (`#1f77b4`): ~30 điểm tròn, nằm phía trái-dưới → lớp "Bình thường"
- **Đám mây đỏ** (`#d62728`): ~30 điểm tam giác, nằm phía phải-trên → lớp "Lỗi"
- Hai đám mây tách biệt hoàn toàn, không có điểm nào xen lẫn
- **Đường liền nét đen đậm**: decision hyperplane, nằm giữa hai đám mây
- **Hai đường nét đứt**: song song với decision hyperplane, đi qua support vectors
- **Vùng giữa hai đường nét đứt**: tô màu xám nhạt (alpha=0.15) — chú thích "Margin"
- **Support vectors**: 2–3 điểm ở mỗi bên, được khoanh tròn đen lớn (marker size lớn hơn, viền đậm)
- **Mũi tên** hai đầu nối hai đường nét đứt, ghi nhãn "Margin = 2/‖w‖"
- Title: "Hard Margin SVM — Tối đa hoá khoảng cách an toàn"
- Legend: "⚫ Support Vectors", "● Normal", "▲ Fault"

**Thông điệp hình:** Chỉ có vài điểm (support vectors) quyết định toàn bộ đường biên — phần còn lại không ảnh hưởng.

### Code minh hoạ

```python
# === Slide 1: Hard Margin SVM ===
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_blobs

# Tạo dữ liệu 2 lớp tách biệt hoàn toàn
X, y = make_blobs(n_samples=60, centers=2, cluster_std=0.8,
                  center_box=(-3, 3), random_state=42)

# Huấn luyện Hard Margin SVM (C rất lớn = không cho phép vi phạm)
svm = SVC(kernel='linear', C=1e6)
svm.fit(X, y)

# Vẽ hình
fig, ax = plt.subplots(figsize=(8, 6))

# Vùng quyết định
xx, yy = np.meshgrid(np.linspace(X[:,0].min()-1, X[:,0].max()+1, 300),
                     np.linspace(X[:,1].min()-1, X[:,1].max()+1, 300))
Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

# Vẽ decision boundary + margin
ax.contour(xx, yy, Z, levels=[-1, 0, 1],
           linestyles=['--', '-', '--'], colors='k', linewidths=[1, 2, 1])
ax.contourf(xx, yy, Z, levels=[-1, 1], colors=['gray'], alpha=0.15)

# Dữ liệu: Normal (xanh, tròn) và Fault (đỏ, tam giác)
ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o',
           s=60, edgecolors='k', linewidths=0.5, label='Normal', zorder=3)
ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^',
           s=60, edgecolors='k', linewidths=0.5, label='Fault', zorder=3)

# Khoanh tròn support vectors
sv = svm.support_vectors_
ax.scatter(sv[:, 0], sv[:, 1], s=200, facecolors='none',
           edgecolors='k', linewidths=2, label='Support Vectors', zorder=4)

ax.set_xlabel('Đặc trưng 1 (RMS)', fontsize=13)
ax.set_ylabel('Đặc trưng 2 (Kurtosis)', fontsize=13)
ax.set_title('Hard Margin SVM — Tối đa hoá khoảng cách an toàn',
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.tick_params(labelsize=12)
plt.tight_layout()
plt.savefig('slide1_hard_margin_svm.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Ghi chú cho người trình bày

> "Ở đây dữ liệu 'sạch' — hai lớp tách biệt hoàn toàn, SVM tìm được đường biên hoàn hảo. Nhưng thực tế dữ liệu rung ổ lăn có nhiễu, đo lường sai, ngoại lệ — slide tiếp theo sẽ cho thấy Hard Margin không còn khả thi."

---

## Slide 2: Soft Margin SVM — Thực tế có nhiễu

**Mục tiêu truyền đạt:** Kỹ sư hiểu tại sao thực tế không dùng hard margin, cơ chế slack variables cho phép "tha" một số điểm lỗi, và vai trò của tham số C trong kiểm soát sự cân bằng giữa margin rộng và sai số nhỏ.

**Bố cục:** 2 cột — Trái: nội dung bullet + bảng nhỏ (45%) · Phải: hình minh hoạ 2D với annotation (55%)

### Nội dung chính

- **Thực tế:** Dữ liệu rung ổ lăn luôn có nhiễu cảm biến, điều kiện vận hành thay đổi, ngoại lệ → hai lớp không tách biệt hoàn toàn
- **Soft Margin:** Cho phép một số điểm **vi phạm margin** — mỗi điểm vi phạm bị phạt bởi biến slack $\xi_i \geq 0$
- **Hàm mục tiêu:** Tối thiểu $\frac{1}{2}\|w\|^2 + C \sum_i \xi_i$ — cân bằng giữa margin rộng và tổng lỗi nhỏ
- **Tham số C — "Mức độ nghiêm khắc":**

| C lớn (ví dụ 100) | C nhỏ (ví dụ 0.01) |
|---|---|
| Phạt nặng lỗi → margin hẹp | Chấp nhận nhiều lỗi → margin rộng |
| Ôm sát dữ liệu train | Tổng quát hoá tốt hơn |
| Dễ overfitting | Có thể bỏ sót lỗi thật |

- **Với dữ liệu ổ lăn:** C thường chọn qua cross-validation (ví dụ `GridSearchCV`)

> 💡 *Analog:* C nhỏ giống đặt ngưỡng rung ISO cao (4.5 mm/s) — ít cảnh báo giả nhưng bỏ sót lỗi nhẹ. C lớn giống ngưỡng thấp (1.5 mm/s) — phát hiện hết nhưng báo động liên tục.

### Hình minh hoạ

**Mô tả chi tiết:**
- Cùng layout 2D như Slide 1, nhưng **dữ liệu có nhiễu** — 2–3 điểm xanh lọt sang vùng đỏ và ngược lại
- Đường decision boundary (đen, nét liền) cắt qua vùng "xen lẫn"
- Hai đường margin (nét đứt) — margin rộng hơn Slide 1
- Các điểm vi phạm margin (nằm sai phía hoặc trong vùng margin):
  - Được đánh dấu bằng **dấu X đen lớn** chồng lên
  - Có **mũi tên nhỏ** chỉ từ điểm vi phạm đến đường margin gần nhất, ghi nhãn "$\xi_i$"
- Chú thích: "Điểm vi phạm — bị phạt bởi $\xi$"
- Title: "Soft Margin SVM — Chấp nhận lỗi để tổng quát hoá"

**Thông điệp hình:** Margin rộng hơn, đổi lại chấp nhận vài điểm "sai" — đây là sự thỏa hiệp cần thiết cho dữ liệu thực.

### Code minh hoạ

```python
# === Slide 2: Soft Margin SVM — Ảnh hưởng của C ===
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_blobs

# Tạo dữ liệu có nhiễu (cluster_std lớn → hai lớp chồng lấp)
X, y = make_blobs(n_samples=80, centers=2, cluster_std=1.8,
                  center_box=(-3, 3), random_state=42)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

for ax, C_val, title in zip(axes, [100, 0.1],
        ['C = 100 (nghiêm khắc → margin hẹp)',
         'C = 0.1 (khoan dung → margin rộng)']):
    svm = SVC(kernel='linear', C=C_val)
    svm.fit(X, y)

    # Lưới vùng quyết định
    xx, yy = np.meshgrid(np.linspace(X[:,0].min()-2, X[:,0].max()+2, 300),
                         np.linspace(X[:,1].min()-2, X[:,1].max()+2, 300))
    Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    # Decision boundary + margin
    ax.contour(xx, yy, Z, levels=[-1, 0, 1],
               linestyles=['--', '-', '--'], colors='k', linewidths=[1, 2, 1])
    ax.contourf(xx, yy, Z, levels=[-1, 1], colors=['gray'], alpha=0.15)

    # Dữ liệu
    ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o',
               s=50, edgecolors='k', linewidths=0.5, label='Normal', zorder=3)
    ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^',
               s=50, edgecolors='k', linewidths=0.5, label='Fault', zorder=3)

    # Đánh dấu điểm vi phạm margin
    decision = svm.decision_function(X)
    violations = np.where((y == 0) & (decision > -1) | (y == 1) & (decision < 1))[0]
    # Chỉ đánh dấu điểm thực sự vi phạm (nằm sai phía hoặc trong margin)
    margin_violators = np.where(np.abs(decision) < 1)[0]
    ax.scatter(X[margin_violators, 0], X[margin_violators, 1],
               marker='x', c='black', s=120, linewidths=2,
               label=f'Vi phạm margin ({len(margin_violators)} điểm)', zorder=5)

    # Support vectors
    sv = svm.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], s=180, facecolors='none',
               edgecolors='k', linewidths=1.5, zorder=4)

    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel('Đặc trưng 1', fontsize=12)
    ax.set_ylabel('Đặc trưng 2', fontsize=12)
    ax.legend(fontsize=10, loc='upper left')
    ax.tick_params(labelsize=11)

plt.suptitle('Soft Margin SVM — Tham số C kiểm soát sự cân bằng',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('slide2_soft_margin_svm.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Ghi chú cho người trình bày

> "Hãy nhìn hình bên phải (C nhỏ) — margin rộng nhưng có vài điểm bị phân loại sai. Trong thực tế nhà máy, đây thường là lựa chọn tốt hơn vì mô hình tổng quát hoá tốt hơn trên dữ liệu mới. Tham số C thường được chọn tự động bằng cross-validation, kỹ sư không cần chọn tay."

---

## Slide 3: Giới hạn của SVM tuyến tính

**Mục tiêu truyền đạt:** Kỹ sư thấy rõ ràng rằng cả Hard lẫn Soft Margin đều bất lực khi dữ liệu phân bố phi tuyến — tạo "nhu cầu" tự nhiên cho giải pháp kernel ở slide sau.

**Bố cục:** 2 cột — Trái: nội dung + ví dụ thực tế (40%) · Phải: hình minh hoạ dữ liệu đồng tâm (60%)

### Nội dung chính

- **Giả định của SVM tuyến tính:** Tồn tại một siêu phẳng (đường thẳng / mặt phẳng) chia được hai lớp
- **Thực tế dữ liệu ổ lăn:**
  - Ổ lăn bình thường: RMS thấp, kurtosis thấp → tập trung ở trung tâm
  - Ổ lăn lỗi: RMS có thể thấp hoặc cao, kurtosis biến thiên → **bao quanh** vùng bình thường
  - Không có đường thẳng nào phân tách được!
- **Ví dụ trực quan:** Dữ liệu dạng vòng tròn đồng tâm — lớp bên trong (Normal) bị lớp bên ngoài (Fault) bao quanh
- **Hậu quả:** Bất kể chọn C bao nhiêu, SVM tuyến tính chỉ đạt ~50% accuracy → không tốt hơn tung đồng xu
- ➡️ **Cần một cách tiếp cận hoàn toàn khác** → Kernel (slide tiếp theo)

### Hình minh hoạ

**Mô tả chi tiết:**
- Không gian 2D, trục X: "Đặc trưng 1", trục Y: "Đặc trưng 2"
- **Lớp xanh dương (Normal):** ~50 điểm tròn, phân bố thành cụm tròn nhỏ ở trung tâm (bán kính nhỏ)
- **Lớp đỏ (Fault):** ~50 điểm tam giác, phân bố thành vòng tròn bao quanh cụm xanh (bán kính lớn)
- **Nhiều đường thẳng nét đứt xám** kẻ qua — tất cả đều cắt nhầm cả hai lớp → ghi chú "✗ Không phân tách được!"
- Có thể thêm: một đường thẳng nét đứt đỏ đậm nhất với accuracy ~50% ghi bên cạnh
- **Đường tròn nét chấm xanh lá** phác hoạ boundary lý tưởng → ghi chú "✓ Cần boundary phi tuyến"
- Title: "Giới hạn SVM tuyến tính — Không có đường thẳng nào chia được"
- Font size lớn, rõ ràng

**Thông điệp hình:** Đường thẳng bất lực trước dữ liệu phi tuyến — cần "thay đổi cách nhìn".

### Code minh hoạ

```python
# === Slide 3: Giới hạn SVM tuyến tính ===
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_circles

# Tạo dữ liệu vòng tròn đồng tâm
X, y = make_circles(n_samples=200, noise=0.08, factor=0.4, random_state=42)

# SVM tuyến tính — thử phân tách
svm_linear = SVC(kernel='linear', C=10)
svm_linear.fit(X, y)
acc_linear = svm_linear.score(X, y)

fig, ax = plt.subplots(figsize=(8, 7))

# Vùng quyết định
xx, yy = np.meshgrid(np.linspace(-1.5, 1.5, 300),
                     np.linspace(-1.5, 1.5, 300))
Z = svm_linear.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
ax.contourf(xx, yy, Z, levels=[-10, 0, 10],
            colors=['#d62728', '#1f77b4'], alpha=0.12)
ax.contour(xx, yy, Z, levels=[0], colors='k',
           linewidths=2, linestyles='--')

# Dữ liệu
ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o',
           s=50, edgecolors='k', linewidths=0.5, label='Normal (trong)', zorder=3)
ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^',
           s=50, edgecolors='k', linewidths=0.5, label='Fault (ngoài)', zorder=3)

# Đường tròn boundary lý tưởng
circle = plt.Circle((0, 0), 0.68, fill=False, color='green',
                     linewidth=2, linestyle=':', label='Boundary lý tưởng (phi tuyến)')
ax.add_patch(circle)

# Chú thích accuracy
ax.text(0.02, 0.98, f'Accuracy SVM tuyến tính: {acc_linear:.0%}\n(≈ tung đồng xu!)',
        transform=ax.transAxes, fontsize=13, fontweight='bold',
        va='top', ha='left', color='red',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

ax.set_xlabel('Đặc trưng 1', fontsize=13)
ax.set_ylabel('Đặc trưng 2', fontsize=13)
ax.set_title('Giới hạn SVM tuyến tính — Không đường thẳng nào chia được',
             fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='lower left')
ax.set_aspect('equal')
ax.tick_params(labelsize=12)
plt.tight_layout()
plt.savefig('slide3_linear_svm_limitation.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Ghi chú cho người trình bày

> "Mời các anh/chị nhìn hình: dù vẽ đường thẳng theo hướng nào, nó cũng cắt nhầm cả hai nhóm. Accuracy chỉ ~50% — tệ hơn cả đoán mò! Vậy phải làm sao? Chúng ta cần thay đổi 'cách nhìn' dữ liệu — đó chính là ý tưởng kernel ở slide tiếp."

---

## Slide 4: Ý tưởng Kernel — Nâng chiều dữ liệu

**Mục tiêu truyền đạt:** Kỹ sư hiểu trực quan rằng "nâng dữ liệu lên không gian cao hơn" biến bài toán phi tuyến thành tuyến tính — không cần hiểu công thức, chỉ cần thấy hình.

**Bố cục:** 2 hình cạnh nhau — Trái: dữ liệu 2D ban đầu · Phải: dữ liệu 3D sau khi thêm chiều z

### Nội dung chính

- **Quan sát:** Dữ liệu 2D không tách được → thử thêm thông tin mới
- **Phép biến đổi $\Phi$:** Thêm chiều thứ 3: $z = x_1^2 + x_2^2$ (khoảng cách bình phương đến gốc toạ độ)
- **Kết quả trong không gian 3D:**
  - Normal (ở gần gốc): $z$ nhỏ → nằm **thấp**
  - Fault (ở xa gốc): $z$ lớn → nằm **cao**
  - → Một mặt phẳng nằm ngang dễ dàng chia tách!
- **Chiếu ngược về 2D:** Mặt phẳng cắt ngang trong 3D trở thành **đường tròn** trong 2D → đúng boundary phi tuyến cần tìm
- 💡 **Điểm mấu chốt:** Kernel tự động làm việc này — kỹ sư không cần tự tính $\Phi(x)$

### Hình minh hoạ

**Mô tả chi tiết — 2 hình cạnh nhau:**

**Hình trái (2D — "Trước"):**
- Giống hệt Slide 3: dữ liệu vòng tròn đồng tâm, không tách được
- Có dấu ✗ đỏ và text "Không tách được bằng đường thẳng"
- Mũi tên cong lớn từ hình trái → hình phải, ghi "$\Phi: (x_1, x_2) \rightarrow (x_1, x_2, x_1^2 + x_2^2)$"

**Hình phải (3D — "Sau"):**
- Cùng dữ liệu nhưng trong không gian 3D
- Trục X: $x_1$, trục Y: $x_2$, trục Z: $z = x_1^2 + x_2^2$
- **Điểm xanh (Normal):** nằm thấp (z nhỏ), tạo thành "đĩa" phẳng gần z=0
- **Điểm đỏ (Fault):** nằm cao (z lớn), tạo thành "vòng" ở trên
- **Mặt phẳng ngang** (bán trong suốt, alpha=0.25, màu xanh lá) cắt giữa → chia 2 nhóm rõ ràng
- Có dấu ✓ xanh lá và text "Tách được bằng mặt phẳng!"
- Góc nhìn 3D: `elev=25, azim=45`
- Màu xanh/đỏ nhất quán với toàn bài

**Thông điệp hình:** Thêm chiều = thay đổi góc nhìn → bài toán khó trở nên dễ.

### Code minh hoạ

```python
# === Slide 4: Ý tưởng Kernel — Nâng chiều dữ liệu ===
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from mpl_toolkits.mplot3d import Axes3D

# Tạo dữ liệu vòng tròn đồng tâm
X, y = make_circles(n_samples=200, noise=0.08, factor=0.4, random_state=42)

fig = plt.figure(figsize=(15, 6))

# --- Hình trái: 2D (không tách được) ---
ax1 = fig.add_subplot(121)
ax1.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o',
            s=50, edgecolors='k', linewidths=0.5, label='Normal')
ax1.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^',
            s=50, edgecolors='k', linewidths=0.5, label='Fault')
ax1.set_title('2D — Không tách được ✗', fontsize=14, fontweight='bold', color='red')
ax1.set_xlabel('$x_1$', fontsize=13)
ax1.set_ylabel('$x_2$', fontsize=13)
ax1.legend(fontsize=11)
ax1.set_aspect('equal')
ax1.tick_params(labelsize=12)

# --- Hình phải: 3D (thêm chiều z = x₁² + x₂²) ---
ax2 = fig.add_subplot(122, projection='3d')
z = X[:, 0]**2 + X[:, 1]**2  # Phép biến đổi Φ

ax2.scatter(X[y==0, 0], X[y==0, 1], z[y==0], c='#1f77b4', marker='o',
            s=50, edgecolors='k', linewidths=0.3, label='Normal (z thấp)')
ax2.scatter(X[y==1, 0], X[y==1, 1], z[y==1], c='#d62728', marker='^',
            s=50, edgecolors='k', linewidths=0.3, label='Fault (z cao)')

# Mặt phẳng phân tách nằm ngang
xx_plane, yy_plane = np.meshgrid(np.linspace(-1.5, 1.5, 10),
                                  np.linspace(-1.5, 1.5, 10))
z_plane = np.full_like(xx_plane, 0.5)  # Mặt phẳng z = 0.5
ax2.plot_surface(xx_plane, yy_plane, z_plane,
                 alpha=0.25, color='green', edgecolor='green', linewidth=0.5)

ax2.set_title('3D — Tách được bằng mặt phẳng ✓',
              fontsize=14, fontweight='bold', color='green')
ax2.set_xlabel('$x_1$', fontsize=12)
ax2.set_ylabel('$x_2$', fontsize=12)
ax2.set_zlabel('$z = x_1^2 + x_2^2$', fontsize=12)
ax2.legend(fontsize=10, loc='upper left')
ax2.view_init(elev=25, azim=45)

plt.suptitle('Ý tưởng Kernel: Nâng chiều dữ liệu biến phi tuyến → tuyến tính',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('slide4_kernel_intuition.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Ghi chú cho người trình bày

> "Nhìn hình bên trái: hai lớp bao quanh nhau, không có đường thẳng nào chia được. Nhưng chỉ cần thêm một chiều z — khoảng cách đến tâm — thì Normal nằm thấp, Fault nằm cao, và một mặt phẳng ngang tách chúng dễ dàng. Đây là ý tưởng cốt lõi của kernel — biến bài toán khó thành bài toán dễ bằng cách thay đổi góc nhìn."

---

## Slide 5: Kernel Trick — Tại sao không tốn chi phí

**Mục tiêu truyền đạt:** Kỹ sư hiểu rằng kernel trick là cách tính toán thông minh — không cần tính toạ độ trong không gian cao chiều mà vẫn cho kết quả tương đương, nhờ đó có thể dùng không gian vô hạn chiều mà máy tính vẫn chạy được.

**Bố cục:** 1 cột — nội dung giải thích ngắn + sơ đồ so sánh 2 cách tính + code minh hoạ

### Nội dung chính

- **Vấn đề:** Nếu $\Phi(x)$ ánh xạ vào không gian hàng triệu / vô hạn chiều → tính tường minh là **bất khả thi** (tốn bộ nhớ & thời gian)
- **Quan sát then chốt:** SVM chỉ cần **tích vô hướng** giữa các cặp điểm: $\Phi(x_i)^T \Phi(x_j)$ — không cần biết toạ độ cụ thể của từng $\Phi(x)$
- **Kernel trick:** Hàm $k(x_i, x_j)$ tính trực tiếp tích vô hướng đó **từ dữ liệu gốc** — không bao giờ phải tính $\Phi(x)$ tường minh!

| | Cách "thật thà" | Kernel Trick |
|---|---|---|
| Bước 1 | Tính $\Phi(x_i)$ cho mỗi điểm | *(bỏ qua)* |
| Bước 2 | Nhân $\Phi(x_i)^T \Phi(x_j)$ | Tính $k(x_i, x_j)$ trực tiếp |
| Chi phí | $O(d')$ — $d'$ có thể vô hạn | $O(d)$ — chỉ phụ thuộc chiều gốc |
| Kết quả | Giống nhau ✓ | Giống nhau ✓ |

- **Ví dụ cụ thể:** Polynomial kernel bậc 2: $k(x, z) = (x^T z + 1)^2$
  - Kết quả bằng đúng $\Phi(x)^T \Phi(z)$ trong không gian 6 chiều
  - Nhưng chỉ tốn 1 phép nhân + 1 phép bình phương!

### Hình minh hoạ

**Mô tả chi tiết — Sơ đồ dạng flowchart:**
- **Hàng trên:** "Cách thật thà" — 3 ô:
  - Ô 1: "Dữ liệu gốc $x \in \mathbb{R}^2$"
  - Mũi tên → Ô 2: "$\Phi(x) \in \mathbb{R}^{6}$" (tô đỏ nhạt, viền đỏ — tốn chi phí)
  - Mũi tên → Ô 3: "$\Phi(x_i)^T \Phi(x_j) = ?$"
- **Hàng dưới:** "Kernel Trick" — 2 ô:
  - Ô 1: "Dữ liệu gốc $x \in \mathbb{R}^2$"
  - Mũi tên thẳng → Ô 2: "$k(x_i, x_j) = (x_i^T x_j + 1)^2$" (tô xanh lá nhạt, viền xanh — hiệu quả)
- **Dấu "="** lớn nối Ô 3 hàng trên với Ô 2 hàng dưới → "Kết quả giống nhau!"
- Ghi chú bên phải: "✗ Tốn bộ nhớ" (hàng trên), "✓ Nhanh & gọn" (hàng dưới)

### Code minh hoạ

```python
# === Slide 5: Kernel Trick — Chứng minh bằng code ===
import numpy as np

# Hai điểm dữ liệu trong không gian 2D gốc
x = np.array([1.0, 2.0])
z = np.array([3.0, 4.0])

# ======================================
# CÁCH 1: Tính Φ(x) tường minh, rồi nhân
# ======================================
# Polynomial kernel bậc 2: Φ(x) = [1, √2·x₁, √2·x₂, x₁², √2·x₁x₂, x₂²]
def phi_explicit(v):
    """Ánh xạ tường minh vào không gian 6 chiều"""
    return np.array([1,
                     np.sqrt(2)*v[0],
                     np.sqrt(2)*v[1],
                     v[0]**2,
                     np.sqrt(2)*v[0]*v[1],
                     v[1]**2])

phi_x = phi_explicit(x)   # Vector 6 chiều
phi_z = phi_explicit(z)   # Vector 6 chiều
result_explicit = np.dot(phi_x, phi_z)  # Nhân hai vector 6 chiều

# ======================================
# CÁCH 2: Kernel trick — tính trực tiếp
# ======================================
def kernel_poly2(a, b):
    """Polynomial kernel bậc 2: k(a,b) = (aᵀb + 1)²"""
    return (np.dot(a, b) + 1)**2

result_kernel = kernel_poly2(x, z)  # Chỉ 1 phép nhân + 1 bình phương

# So sánh kết quả
print(f"Cách 1 (tường minh, 6 chiều):  {result_explicit:.4f}")
print(f"Cách 2 (kernel trick, 2 chiều): {result_kernel:.4f}")
print(f"Giống nhau? {np.isclose(result_explicit, result_kernel)}")
# Output:
# Cách 1 (tường minh, 6 chiều):  144.0000
# Cách 2 (kernel trick, 2 chiều): 144.0000
# Giống nhau? True

# → Kernel trick cho kết quả GIỐNG HỆT nhưng không cần tính Φ(x)!
# → Với RBF kernel: Φ(x) có VÔ HẠN chiều — chỉ kernel trick mới khả thi.
```

### Ghi chú cho người trình bày

> "Đây là phần 'ma thuật' toán học của SVM. Các anh/chị không cần nhớ công thức — chỉ cần nhớ: kernel giúp SVM làm việc trong không gian rất cao mà không tốn chi phí tính toán. Chạy code sẽ thấy hai cách cho kết quả y hệt nhau, nhưng cách 2 nhanh hơn nhiều lần."

---

## Slide 6: Chọn Kernel nào? — Hướng dẫn thực chiến

**Mục tiêu truyền đạt:** Kỹ sư biết ngay nên bắt đầu với kernel nào cho bài toán ổ lăn, hiểu trực quan ảnh hưởng của γ, và có thể áp dụng ngay sau buổi học.

**Bố cục:** 3 phần — Bảng so sánh (trên) · 3 hình decision boundary cạnh nhau (giữa) · Khuyến nghị thực chiến (dưới)

### Nội dung chính

**Bảng so sánh 3 kernel phổ biến:**

| Kernel | Công thức | Ý nghĩa trực quan | Khi nào dùng |
|---|---|---|---|
| **Linear** | $k(x,z) = x^T z$ | Đường thẳng / mặt phẳng | Dữ liệu tuyến tính, feature nhiều (NLP, text) |
| **Polynomial** | $k(x,z) = (x^T z + 1)^d$ | Đường cong bậc $d$ | Feature ít, quan hệ đa thức rõ |
| **RBF (Gaussian)** | $k(x,z) = \exp(-\gamma \|x-z\|^2)$ | "Vùng ảnh hưởng" quanh mỗi điểm | **Mặc định tốt cho hầu hết bài toán** |

**Khuyến nghị cho bài toán ổ lăn:**
- 🏆 **RBF là điểm xuất phát mặc định** — linh hoạt, xử lý tốt dữ liệu phi tuyến
- Tham số $\gamma$ (gamma) — "bán kính nhìn":
  - $\gamma$ **nhỏ** = mỗi điểm "nhìn xa" → boundary mượt mại, tổng quát
  - $\gamma$ **lớn** = mỗi điểm "chỉ nhìn gần" → boundary ôm sát dữ liệu, dễ overfitting
- **Quy trình thực tế:** `GridSearchCV` trên `C` × `gamma`, dùng 5-fold CV

### Hình minh hoạ

**Mô tả chi tiết — 3 hình cạnh nhau trên cùng tập dữ liệu:**

- Cùng dữ liệu `make_circles` với noise
- **Hình 1:** Linear kernel → boundary thẳng → tách sai hoàn toàn, vùng quyết định chia 50/50
- **Hình 2:** Polynomial kernel (degree=3) → boundary cong nhẹ → tách được phần lớn nhưng không hoàn hảo
- **Hình 3:** RBF kernel (gamma=2) → boundary tròn mượt → tách hoàn hảo, accuracy ~98%
- Mỗi hình có:
  - Vùng quyết định tô nền (xanh nhạt / đỏ nhạt, alpha=0.2)
  - Dữ liệu chấm rõ (xanh/đỏ)
  - Title ghi tên kernel + accuracy
  - Support vectors được khoanh tròn
- Ghi chú dưới hình: "✗ Thất bại" · "△ Tạm ổn" · "✓ Tốt nhất"

**Thông điệp hình:** RBF kernel là lựa chọn linh hoạt nhất cho dữ liệu phi tuyến.

### Code minh hoạ

```python
# === Slide 6: So sánh 3 kernel trên cùng dữ liệu ===
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_circles

# Dữ liệu vòng tròn đồng tâm
X, y = make_circles(n_samples=200, noise=0.08, factor=0.4, random_state=42)

# 3 kernel cần so sánh
kernels = [
    ('Linear', SVC(kernel='linear', C=10)),
    ('Polynomial (degree=3)', SVC(kernel='poly', degree=3, C=10, coef0=1)),
    ('RBF (γ=2)', SVC(kernel='rbf', gamma=2, C=10)),
]
markers = ['✗ Thất bại', '△ Tạm ổn', '✓ Tốt nhất']
colors_title = ['red', 'orange', 'green']

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

for ax, (name, svm), note, c_title in zip(axes, kernels, markers, colors_title):
    svm.fit(X, y)
    acc = svm.score(X, y)

    # Lưới vùng quyết định
    xx, yy = np.meshgrid(np.linspace(-1.5, 1.5, 300),
                         np.linspace(-1.5, 1.5, 300))
    Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    # Vùng quyết định
    ax.contourf(xx, yy, Z, levels=[-10, 0, 10],
                colors=['#d62728', '#1f77b4'], alpha=0.15)
    ax.contour(xx, yy, Z, levels=[0], colors='k', linewidths=2)

    # Dữ liệu
    ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o',
               s=40, edgecolors='k', linewidths=0.5, label='Normal')
    ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^',
               s=40, edgecolors='k', linewidths=0.5, label='Fault')

    # Support vectors
    sv = svm.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], s=150, facecolors='none',
               edgecolors='k', linewidths=1.5, zorder=4)

    ax.set_title(f'{name}\nAccuracy: {acc:.0%} — {note}',
                 fontsize=13, fontweight='bold', color=c_title)
    ax.set_xlabel('$x_1$', fontsize=12)
    ax.set_ylabel('$x_2$', fontsize=12)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=11)
    if ax == axes[0]:
        ax.legend(fontsize=10, loc='lower left')

plt.suptitle('So sánh 3 Kernel trên dữ liệu phi tuyến — RBF là lựa chọn mặc định',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('slide6_kernel_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Ghi chú cho người trình bày

> "Trong bài toán ổ lăn CWRU, chúng ta dùng RBF kernel làm mặc định. Hình giữa (Polynomial) tách được phần lớn nhưng không mượt, RBF bên phải tách hoàn hảo. Trong thực tế, các anh/chị chỉ cần nhớ: bắt đầu với RBF, rồi dùng GridSearchCV để tìm C và gamma tối ưu."

---

## Gợi ý thứ tự trình bày

1. **Mở đầu (Slide 1):** Ôn nhanh Hard Margin — nhắc lại khái niệm margin và support vectors từ phần trước. Hỏi: "Nếu dữ liệu không sạch thì sao?"
2. **Mở rộng (Slide 2):** Giới thiệu Soft Margin — giải thích tham số C bằng analog ngưỡng rung ISO. Cho kỹ sư thảo luận: C lớn hay nhỏ phù hợp hơn với dữ liệu nhà máy?
3. **Tạo vấn đề (Slide 3):** Cho thấy SVM tuyến tính thất bại hoàn toàn trên dữ liệu phi tuyến. Dừng lại, hỏi: "Các anh/chị có ý tưởng gì không?"
4. **Giải pháp trực quan (Slide 4):** Trình bày ý tưởng kernel bằng hình — chỉ cần "nâng dữ liệu lên" là tách được. Không cần đi sâu vào toán.
5. **Giải thích cơ chế (Slide 5):** Dành cho ai muốn hiểu sâu hơn — có thể bỏ qua nếu thời gian eo hẹp. Chạy code live để chứng minh hai cách cho kết quả giống nhau.
6. **Thực chiến (Slide 6):** Kết thúc bằng hướng dẫn chọn kernel — RBF là mặc định, GridSearchCV để tìm tham số tối ưu. Chuyển tiếp sang phần tiếp theo (Random Forest hoặc SHAP).

---

## Những điểm kỹ sư thường hỏi

### 1. "Khi nào nên dùng SVM thay vì Random Forest cho bài toán ổ lăn?"

> **Gợi ý trả lời:** SVM phù hợp khi: (a) đã chọn lọc được bộ đặc trưng tinh gọn (10–15 features), (b) dữ liệu training nhỏ (<5000 mẫu — SVM tận dụng tốt ít mẫu nhờ maximum margin), (c) cần decision boundary rõ ràng. Trong thực tế nhà máy với dữ liệu nhiều feature và cần giải thích (SHAP), Random Forest thường là lựa chọn đầu tiên.

### 2. "Gamma nhỏ và gamma lớn ảnh hưởng thế nào? Tôi chọn giá trị bao nhiêu?"

> **Gợi ý trả lời:** Gamma kiểm soát "bán kính nhìn" của mỗi support vector. Gamma nhỏ = nhìn xa = boundary mềm mại (tổng quát hoá tốt, có thể bỏ sót lỗi nhẹ). Gamma lớn = nhìn gần = boundary ôm sát dữ liệu (chính xác trên train, dễ overfitting). **Không cần chọn tay** — dùng `GridSearchCV` với `gamma = [0.001, 0.01, 0.1, 1, 10]` kết hợp `C = [0.1, 1, 10, 100]`, sklearn tự tìm cặp tối ưu qua 5-fold CV.

### 3. "SVM có thể dùng cho hệ thống giám sát online (real-time) không?"

> **Gợi ý trả lời:** Có — SVM **dự đoán rất nhanh** (chỉ tính khoảng cách đến support vectors, thường vài chục điểm). Vấn đề là ở **huấn luyện** — chậm với dữ liệu lớn. Quy trình thực tế: huấn luyện offline trên workstation → deploy mô hình lên edge device → dự đoán online mỗi khi có segment mới. Thời gian dự đoán 1 mẫu (22 features) thường <1ms — dư sức cho monitoring real-time với chu kỳ lấy mẫu 1–5 giây.
