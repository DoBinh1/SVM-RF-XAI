import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Thiết lập bảng mã UTF-8 cho console Windows
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn
base_dir = Path(r"d:\[Lab] HUST\nhà máy")
csv_path = base_dir / "notebooks" / "features_all.csv"
figures_dir = base_dir / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)

# Đọc dữ liệu đặc trưng CWRU
if not csv_path.exists():
    print(f"Lỗi: Không tìm thấy file {csv_path}")
    sys.exit(1)

df = pd.read_csv(csv_path)

# Map nhãn lớp sang tiếng Việt cho trực quan và khớp với slide
label_mapping = {
    'Normal': 'Normal',
    'IR': 'IR (Lỗi Rãnh Trong)',
    'OR': 'OR (Lỗi Rãnh Ngoài)',
    'B': 'Ball (Lỗi Bi)'
}
df['label_vi'] = df['label'].map(label_mapping)
class_order = ['Normal', 'IR (Lỗi Rãnh Trong)', 'OR (Lỗi Rãnh Ngoài)', 'Ball (Lỗi Bi)']

# Cấu hình thẩm mỹ phong cách tối giản, cao cấp
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Calibri', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 15,
    'figure.dpi': 200
})
sns.set_style("whitegrid", {
    "grid.color": "#e2e8f0",
    "grid.linestyle": "--",
    "axes.edgecolor": "#cbd5e1"
})

# ==============================================================================
# HÌNH 1: BOXPLOT 2x2 CỦA 4 ĐẶC TRƯNG MIỀN THỜI GIAN CHỦ CHỐT
# (RMS, Peak, Crest Factor, Kurtosis)
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
axes = axes.flatten()

features_to_plot = [
    ('rms', 'RMS (Mức rung tổng thể - g)', 'rms'),
    ('peak', 'Peak (Biên độ đỉnh - g)', 'peak'),
    ('crest_factor', 'Crest Factor (Hệ số đỉnh)', 'crest_factor'),
    ('kurtosis', 'Kurtosis (Độ nhọn)', 'kurtosis')
]

for idx, (col_name, title, key) in enumerate(features_to_plot):
    ax = axes[idx]
    # Vẽ boxplot sử dụng bảng màu Set2 đồng bộ với boxplot Kurtosis trước đó của người dùng
    sns.boxplot(
        data=df,
        x='label_vi',
        y=col_name,
        order=class_order,
        palette='Set2',
        width=0.55,
        linewidth=1.2,
        showfliers=True,
        fliersize=3,
        flierprops=dict(marker='o', markerfacecolor='gray', markersize=3, markeredgecolor='none', alpha=0.4),
        ax=ax
    )
    
    ax.set_title(title, pad=10, fontweight='bold', color='#1e293b')
    ax.set_xlabel('')
    ax.set_ylabel('')
    # Xoay nhãn trục X nhẹ để tránh chồng chéo
    ax.set_xticklabels(class_order, rotation=10, ha='right', color='#475569')
    ax.tick_params(colors='#475569')

# Thêm tiêu đề chung cho hình vẽ
fig.suptitle('So sánh các đặc trưng thời gian đo lường mức độ rung ổ lăn', 
             y=0.98, fontweight='bold', fontsize=16, color='#0f172a')

plt.tight_layout(rect=[0, 0, 1, 0.95])
boxplot_output = figures_dir / "time_domain_features_comparison.png"
plt.savefig(boxplot_output, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Đã lưu hình Boxplot 2x2 vào: {boxplot_output}")


# ==============================================================================
# HÌNH 2: SCATTER PLOT 2D - KHÔNG GIAN ĐẶC TRƯNG RMS vs KURTOSIS
# Minh họa vì sao cần Machine Learning để phân loại
# ==============================================================================
plt.figure(figsize=(10, 6.5))

# Vẽ scatter plot với màu sắc Set2
ax_scatter = sns.scatterplot(
    data=df,
    x='rms',
    y='kurtosis',
    hue='label_vi',
    hue_order=class_order,
    palette='Set2',
    alpha=0.85,
    edgecolor='w',
    linewidth=0.5,
    s=50
)

# Cấu hình tiêu đề và nhãn
plt.title('Không gian đặc trưng 2D: RMS vs Kurtosis', pad=15, fontweight='bold', fontsize=15, color='#0f172a')
plt.xlabel('Trị hiệu dụng RMS (Biểu thị tổng năng lượng rung)', labelpad=10, fontweight='bold', color='#1e293b')
plt.ylabel('Độ nhọn Kurtosis (Nhạy với xung va đập)', labelpad=10, fontweight='bold', color='#1e293b')

# Cấu hình grid và chú thích
plt.legend(title='Trạng thái ổ lăn', title_fontsize=11, loc='upper right', frameon=True, facecolor='white', edgecolor='#e2e8f0')
plt.xlim(-0.05, 1.25)
plt.ylim(0, 18)

# Chú giải thêm thông tin khoa học trực quan trên hình
plt.text(0.08, 1.5, 'Normal\n(Rung động thấp, phân bố Gauss)', fontsize=9, color='#334155', style='italic', weight='bold')
plt.text(0.12, 11.5, 'Ball (Lỗi Bi)\n(Rung động vừa, Kurtosis vừa)', fontsize=9, color='#334155', style='italic', weight='bold')
plt.text(0.38, 5.0, 'IR (Lỗi Rãnh Trong)\n(Rung động cao, Kurtosis cao)', fontsize=9, color='#334155', style='italic', weight='bold')
plt.text(0.68, 14.5, 'OR (Lỗi Rãnh Ngoài)\n(Xung va đập mạnh & liên tục)', fontsize=9, color='#334155', style='italic', weight='bold')

plt.tight_layout()
scatter_output = figures_dir / "feature_space_scatter_2d.png"
plt.savefig(scatter_output, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Đã lưu hình Scatter 2D vào: {scatter_output}")
