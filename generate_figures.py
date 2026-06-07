# -*- coding: utf-8 -*-
"""
Chương trình sinh toàn bộ 6 figure minh hoạ bài giảng SVM.
Sinh ra các file PNG trong thư mục 'slides' tương ứng với mỗi slide.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_blobs, make_circles
from mpl_toolkits.mplot3d import Axes3D

# Cấu hình font hiển thị tiếng Việt trên đồ thị (nếu máy có sẵn font Unicode)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Tạo thư mục output nếu chưa tồn tại
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'slides')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def get_save_path(filename):
    return os.path.join(output_dir, filename)


def plot_slide1():
    """Slide 1: Hard Margin SVM"""
    # 2 lớp tách biệt hoàn toàn
    X, y = make_blobs(n_samples=60, centers=2, cluster_std=0.8, center_box=(-3, 3), random_state=42)
    
    # Huấn luyện Hard Margin (C rất lớn)
    svm = SVC(kernel='linear', C=1e6)
    svm.fit(X, y)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Thiết lập lưới
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500))
    Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    preds = svm.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    
    # Tô màu phân vùng quyết định
    ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5], colors=['#aec7e8', '#ffb09c'], alpha=0.25)
    
    # Vẽ decision boundary + margin lines
    ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
    ax.contour(xx, yy, Z, levels=[-1, 1], colors='black', linestyles='--', linewidths=1)
    
    # Tô vùng margin xám nhạt
    ax.contourf(xx, yy, Z, levels=[-1, 1], colors=['gray'], alpha=0.1)
    
    # Vẽ các điểm dữ liệu
    ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o', s=60, edgecolors='k', linewidths=0.5, label='Normal')
    ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^', s=60, edgecolors='k', linewidths=0.5, label='Fault')
    
    # Khoanh tròn Support Vectors
    sv = svm.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], facecolors='none', edgecolors='black', linewidths=2, s=180, label='Support Vectors')
    
    # Vẽ mũi tên Margin vuông góc với boundary
    w = svm.coef_[0]
    b = svm.intercept_[0]
    x0_x = np.mean(X[:, 0])
    x0_y = -(w[0] * x0_x + b) / w[1]
    x0 = np.array([x0_x, x0_y])
    w_norm_sq = np.dot(w, w)
    p1 = x0 + w / w_norm_sq
    p2 = x0 - w / w_norm_sq
    ax.annotate('', xy=p1, xytext=p2, arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text((p1[0]+p2[0])/2 + 0.15, (p1[1]+p2[1])/2 + 0.15, 'Margin', fontsize=11, fontweight='bold', color='black')
    
    # Decorate
    ax.set_title('Hard Margin SVM — Tối đa hoá khoảng cách an toàn', fontsize=14, fontweight='bold')
    ax.set_xlabel('Đặc trưng 1 (RMS)', fontsize=12)
    ax.set_ylabel('Đặc trưng 2 (Kurtosis)', fontsize=12)
    ax.tick_params(labelsize=11)
    ax.legend(fontsize=11, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(get_save_path('slide1_hard_margin.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide1_hard_margin.png")


def plot_slide2():
    """Slide 2: Soft Margin SVM"""
    # 2 lớp có nhiễu, chồng lấn nhau
    X, y = make_blobs(n_samples=80, centers=2, cluster_std=1.8, center_box=(-3, 3), random_state=42)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    
    for ax, C_val, title_note in zip(axes, [100, 0.1], 
                                     ['C = 100 → margin hẹp, ít lỗi', 
                                      'C = 0.1 → margin rộng, chấp nhận lỗi']):
        svm = SVC(kernel='linear', C=C_val)
        svm.fit(X, y)
        
        # Lưới
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500))
        Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        preds = svm.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        
        # Tô màu phân vùng quyết định
        ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5], colors=['#aec7e8', '#ffb09c'], alpha=0.25)
        
        # Vẽ decision boundary + margin lines
        ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
        ax.contour(xx, yy, Z, levels=[-1, 1], colors='black', linestyles='--', linewidths=1)
        
        # Vẽ các điểm dữ liệu
        ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o', s=50, edgecolors='k', linewidths=0.5, label='Normal')
        ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^', s=50, edgecolors='k', linewidths=0.5, label='Fault')
        
        # Khoanh tròn Support Vectors
        sv = svm.support_vectors_
        ax.scatter(sv[:, 0], sv[:, 1], facecolors='none', edgecolors='black', linewidths=1.5, s=150)
        
        # Tìm và đánh dấu các điểm vi phạm margin (y_val * dec < 1.0)
        y_val = 2 * y - 1
        dec = svm.decision_function(X)
        violators = np.where(y_val * dec < 1.0)[0]
        ax.scatter(X[violators, 0], X[violators, 1], facecolors='none', edgecolors='#ff7f0e', linewidths=2, s=200, label='Vi phạm margin')
        
        # Decorate
        ax.set_title(title_note, fontsize=13, fontweight='bold')
        ax.set_xlabel('Đặc trưng 1', fontsize=12)
        ax.set_ylabel('Đặc trưng 2', fontsize=12)
        ax.tick_params(labelsize=11)
        if C_val == 100:
            ax.legend(fontsize=10, loc='upper left')
            
    plt.suptitle('Soft Margin SVM — Tham số C kiểm soát sự cân bằng', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(get_save_path('slide2_soft_margin.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide2_soft_margin.png")


def plot_slide3():
    """Slide 3: Nonlinear Problem"""
    # Dữ liệu đồng tâm phi tuyến
    X, y = make_circles(n_samples=200, noise=0.07, factor=0.4, random_state=42)
    
    # Huấn luyện thử một tuyến tính SVM
    svm_linear = SVC(kernel='linear', C=1)
    svm_linear.fit(X, y)
    acc = svm_linear.score(X, y)
    
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Lưới
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500))
    Z = svm_linear.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    preds = svm_linear.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    
    # Tô màu phân vùng quyết định
    ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5], colors=['#aec7e8', '#ffb09c'], alpha=0.25)
    ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
    
    # Vẽ dữ liệu
    ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o', s=50, edgecolors='k', linewidths=0.5, label='Normal (Bình thường)')
    ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^', s=50, edgecolors='k', linewidths=0.5, label='Fault (Lỗi)')
    
    # Vẽ 2-3 đường thẳng thử nghiệm nét đứt xám
    x_vals = np.linspace(-1.3, 1.3, 100)
    ax.plot(x_vals, 0.4 * x_vals + 0.1, color='gray', linestyle=':', alpha=0.7, lw=1.5)
    ax.plot(x_vals, -0.6 * x_vals - 0.2, color='gray', linestyle=':', alpha=0.7, lw=1.5)
    ax.plot(x_vals, 0.0 * x_vals - 0.35, color='gray', linestyle=':', alpha=0.7, lw=1.5)
    ax.text(-1.2, -0.7, 'Thử nghiệm các đường thẳng khác nhau...', color='gray', fontsize=10, fontstyle='italic')
    
    # Ghi chú thất bại của SVM tuyến tính
    ax.annotate('SVM tuyến tính thất bại ở đây\n(Accuracy ≈ {:.0%})'.format(acc), 
                xy=(-0.1, 0.4), xytext=(-1.4, 0.8),
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5),
                fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.8))
    
    # Decorate
    ax.set_title('Giới hạn SVM tuyến tính — Không thể phân chia', fontsize=14, fontweight='bold')
    ax.set_xlabel('Đặc trưng 1', fontsize=12)
    ax.set_ylabel('Đặc trưng 2', fontsize=12)
    ax.legend(fontsize=11, loc='lower left')
    ax.set_aspect('equal')
    ax.tick_params(labelsize=11)
    
    plt.tight_layout()
    plt.savefig(get_save_path('slide3_nonlinear_problem.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide3_nonlinear_problem.png")


def plot_slide4():
    """Slide 4: Kernel Idea"""
    # Dữ liệu đồng tâm phi tuyến
    X, y = make_circles(n_samples=200, noise=0.07, factor=0.4, random_state=42)
    
    fig = plt.figure(figsize=(14, 6))
    
    # Subplot 1: 2D không phân tách được
    ax1 = fig.add_subplot(121)
    ax1.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o', s=50, edgecolors='k', linewidths=0.5, label='Normal')
    ax1.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^', s=50, edgecolors='k', linewidths=0.5, label='Fault')
    ax1.text(0, 0, '✗ Không tách được', color='red', fontsize=12, fontweight='bold', ha='center')
    ax1.set_title('Không gian 2D ban đầu (Phi tuyến)', fontsize=13, fontweight='bold')
    ax1.set_xlabel('$x_1$', fontsize=12)
    ax1.set_ylabel('$x_2$', fontsize=12)
    ax1.set_aspect('equal')
    ax1.legend(loc='lower left')
    
    # Subplot 2: 3D nâng chiều dữ liệu
    ax2 = fig.add_subplot(122, projection='3d')
    z = X[:, 0]**2 + X[:, 1]**2  # z = x1^2 + x2^2
    
    ax2.scatter(X[y==0, 0], X[y==0, 1], z[y==0], c='#1f77b4', marker='o', s=40, edgecolors='k', linewidths=0.3, label='Normal')
    ax2.scatter(X[y==1, 0], X[y==1, 1], z[y==1], c='#d62728', marker='^', s=40, edgecolors='k', linewidths=0.3, label='Fault')
    
    # Vẽ mặt phẳng cắt ngang tại z = 0.45 phân tách hai nhóm
    grid_x, grid_y = np.meshgrid(np.linspace(-1.2, 1.2, 10), np.linspace(-1.2, 1.2, 10))
    grid_z = np.full_like(grid_x, 0.45)
    ax2.plot_surface(grid_x, grid_y, grid_z, alpha=0.3, color='yellow', edgecolor='orange', linewidth=0.5)
    
    ax2.set_title('Không gian 3D nâng chiều (Tách tuyến tính ✓)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('$x_1$', fontsize=11)
    ax2.set_ylabel('$x_2$', fontsize=11)
    ax2.set_zlabel('$z = x_1^2 + x_2^2$', fontsize=11)
    ax2.view_init(elev=20, azim=45)
    
    # Vẽ mũi tên và nhãn trung gian chuyển đổi giữa 2 hình
    fig.text(0.48, 0.5, 'Ánh xạ $\\Phi$\n$z = x_1^2 + x_2^2$', fontsize=12, fontweight='bold', 
             ha='center', va='center', color='darkblue', 
             bbox=dict(boxstyle='rarrow,pad=0.4', fc='#aec7e8', ec='blue', lw=1.5))
             
    plt.suptitle('Ý tưởng Kernel: Nâng chiều dữ liệu để tách bằng mặt phẳng', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(get_save_path('slide4_kernel_idea.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide4_kernel_idea.png")


def plot_slide5():
    """Slide 5: Kernel Trick"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # ----------------------------------------------------
    # Subplot 1: Cách thông thường (Explicit mapping)
    # ----------------------------------------------------
    ax = axes[0]
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_title('Cách 1: Ánh xạ tường minh (Explicit Mapping)', fontsize=13, fontweight='bold', color='#d62728')
    
    # Box 1
    ax.text(1.8, 3.2, 'Dữ liệu gốc\n$x, z \\in \\mathbb{R}^2$', ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.5', fc='#aec7e8', ec='black', lw=1))
    
    # Arrow 1
    ax.annotate('', xy=(3.6, 3.2), xytext=(2.7, 3.2), arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(3.15, 3.5, 'Ánh xạ $\\Phi$', ha='center', fontsize=10, fontstyle='italic')
    
    # Box 2
    ax.text(5.0, 3.2, 'Không gian mới\n$\\Phi(x), \\Phi(z) \\in \\mathbb{R}^6$', ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.5', fc='#ffb09c', ec='black', lw=1))
    
    # Arrow 2
    ax.annotate('', xy=(7.0, 3.2), xytext=(6.4, 3.2), arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(6.7, 3.5, 'Tích vô hướng', ha='center', fontsize=9, fontstyle='italic')
    
    # Box 3
    ax.text(8.5, 3.2, 'Kết quả\n$\\Phi(x)^T \\Phi(z)$', ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.5', fc='#e2e2e2', ec='black', lw=1))
    
    # Cảnh báo tốn kém
    ax.text(5.0, 1.2, '✗ TỐN CHI PHÍ CHI TIẾT\nÁnh xạ Φ(x) có thể có chiều vô hạn,\ntốn bộ nhớ & năng lực CPU.',
            ha='center', va='center', fontsize=10, fontweight='bold', color='#d62728',
            bbox=dict(boxstyle='round,pad=0.4', fc='#ffebe9', ec='#d62728', lw=1))

    # ----------------------------------------------------
    # Subplot 2: Kernel Trick
    # ----------------------------------------------------
    ax = axes[1]
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_title('Cách 2: Kernel Trick (Tính trực tiếp)', fontsize=13, fontweight='bold', color='green')
    
    # Box 1
    ax.text(2.2, 3.2, 'Dữ liệu gốc\n$x, z \\in \\mathbb{R}^2$', ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.5', fc='#aec7e8', ec='black', lw=1))
    
    # Arrow 1
    ax.annotate('', xy=(4.8, 3.2), xytext=(3.5, 3.2), arrowprops=dict(arrowstyle="->", color="black", lw=2))
    ax.text(4.15, 3.5, 'Kernel $k(x,z)$', ha='center', fontsize=10, fontstyle='italic')
    
    # Box 2
    ax.text(6.8, 3.2, 'Tính trực tiếp\n$k(x,z) = (x^T z + 1)^2$', ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round,pad=0.5', fc='#c1f0c1', ec='green', lw=1.5))
    
    # Kết quả
    ax.text(9.0, 3.2, '= $\\Phi(x)^T \\Phi(z)$ ✓', ha='center', va='center', fontsize=12, fontweight='bold', color='green')
    
    # Lợi ích nhanh gọn
    ax.text(5.5, 1.2, '✓ NHANH & GỌN NHẸ\nKhông bao giờ cần tính toán Φ(x) cụ thể,\ntính toán trực tiếp từ dữ liệu gốc.',
            ha='center', va='center', fontsize=10, fontweight='bold', color='green',
            bbox=dict(boxstyle='round,pad=0.4', fc='#e6ffe6', ec='green', lw=1))
            
    plt.suptitle('Kernel Trick: Giải pháp tính tích vô hướng thông minh', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(get_save_path('slide5_kernel_trick.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide5_kernel_trick.png")


def plot_slide6():
    """Slide 6: Kernel Comparison"""
    # Dữ liệu đồng tâm phi tuyến
    X, y = make_circles(n_samples=200, noise=0.07, factor=0.4, random_state=42)
    
    # Định nghĩa 3 kernel
    models = [
        ('Linear Kernel', SVC(kernel='linear', C=10), '✗ Thất bại', 'red'),
        ('Polynomial Kernel (d=3)', SVC(kernel='poly', degree=3, C=10, coef0=1), '△ Tạm ổn', 'orange'),
        ('RBF Kernel (γ=2)', SVC(kernel='rbf', gamma=2, C=10), '✓ Tốt nhất', 'green')
    ]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    
    for ax, (name, svm, status, s_color) in zip(axes, models):
        svm.fit(X, y)
        acc = svm.score(X, y)
        
        # Lưới phân vùng
        x_min, x_max = X[:, 0].min() - 0.3, X[:, 0].max() + 0.3
        y_min, y_max = X[:, 1].min() - 0.3, X[:, 1].max() + 0.3
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 500), np.linspace(y_min, y_max, 500))
        Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        preds = svm.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        
        # Tô màu phân vùng quyết định
        ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5], colors=['#aec7e8', '#ffb09c'], alpha=0.25)
        ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
        
        # Vẽ dữ liệu
        ax.scatter(X[y==0, 0], X[y==0, 1], c='#1f77b4', marker='o', s=45, edgecolors='k', linewidths=0.5, label='Normal')
        ax.scatter(X[y==1, 0], X[y==1, 1], c='#d62728', marker='^', s=45, edgecolors='k', linewidths=0.5, label='Fault')
        
        # Vẽ support vectors
        sv = svm.support_vectors_
        ax.scatter(sv[:, 0], sv[:, 1], facecolors='none', edgecolors='black', linewidths=1.5, s=120)
        
        # Decorate
        ax.set_title('{}\nAccuracy: {:.0%} — {}'.format(name, acc, status), fontsize=13, fontweight='bold', color=s_color)
        ax.set_xlabel('$x_1$', fontsize=11)
        ax.set_ylabel('$x_2$', fontsize=11)
        ax.set_aspect('equal')
        ax.tick_params(labelsize=10)
        if name == 'Linear Kernel':
            ax.legend(fontsize=9, loc='lower left')
            
    plt.suptitle('So sánh khả năng phân tách của các loại Kernel', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(get_save_path('slide6_kernel_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide6_kernel_comparison.png")


def plot_slide8():
    """Slide 8: Summary — So sanh 3 dang SVM (Hard Margin / Soft Margin / RBF Kernel)"""

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # ---------------------------------------------------------------
    # Panel 1: Hard Margin SVM (du lieu sach, 2 lop tach biet)
    # ---------------------------------------------------------------
    X1, y1 = make_blobs(n_samples=60, centers=2, cluster_std=0.8,
                        center_box=(-3, 3), random_state=42)
    svm1 = SVC(kernel='linear', C=1e6)
    svm1.fit(X1, y1)

    ax = axes[0]
    x_min, x_max = X1[:, 0].min() - 1, X1[:, 0].max() + 1
    y_min, y_max = X1[:, 1].min() - 1, X1[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                         np.linspace(y_min, y_max, 300))
    Z = svm1.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    preds = svm1.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5],
                colors=['#aec7e8', '#ffb09c'], alpha=0.25)
    ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
    ax.contour(xx, yy, Z, levels=[-1, 1], colors='black',
               linestyles='--', linewidths=1)
    ax.contourf(xx, yy, Z, levels=[-1, 1], colors=['gray'], alpha=0.08)
    ax.scatter(X1[y1==0, 0], X1[y1==0, 1], c='#1f77b4', marker='o',
               s=45, edgecolors='k', linewidths=0.5, label='Normal')
    ax.scatter(X1[y1==1, 0], X1[y1==1, 1], c='#d62728', marker='^',
               s=45, edgecolors='k', linewidths=0.5, label='Fault')
    sv = svm1.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], facecolors='none', edgecolors='black',
               linewidths=2, s=180)
    ax.set_title('Hard-Margin SVM\nDu lieu sach, phan tach tuyen tinh',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Dac trung 1 (RMS)', fontsize=12)
    ax.set_ylabel('Dac trung 2 (Kurtosis)', fontsize=12)
    ax.legend(fontsize=10, loc='upper left')
    ax.tick_params(labelsize=11)
    # Hop chu thich uu/nhuoc
    ax.text(0.02, 0.02,
            u'+  Bien an toan toi da\n+  Ly thuyet vung chac\n-  Khong chiu duoc nhieu',
            transform=ax.transAxes, fontsize=9, va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', fc='#e8f4e8', ec='green', lw=1))

    # ---------------------------------------------------------------
    # Panel 2: Soft Margin SVM (du lieu co nhieu)
    # ---------------------------------------------------------------
    X2, y2 = make_blobs(n_samples=80, centers=2, cluster_std=1.8,
                        center_box=(-3, 3), random_state=42)
    svm2 = SVC(kernel='linear', C=0.5)
    svm2.fit(X2, y2)
    acc2 = svm2.score(X2, y2)

    ax = axes[1]
    x_min, x_max = X2[:, 0].min() - 1, X2[:, 0].max() + 1
    y_min, y_max = X2[:, 1].min() - 1, X2[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                         np.linspace(y_min, y_max, 300))
    Z = svm2.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    preds = svm2.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5],
                colors=['#aec7e8', '#ffb09c'], alpha=0.25)
    ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
    ax.contour(xx, yy, Z, levels=[-1, 1], colors='black',
               linestyles='--', linewidths=1)
    ax.scatter(X2[y2==0, 0], X2[y2==0, 1], c='#1f77b4', marker='o',
               s=45, edgecolors='k', linewidths=0.5)
    ax.scatter(X2[y2==1, 0], X2[y2==1, 1], c='#d62728', marker='^',
               s=45, edgecolors='k', linewidths=0.5)
    # Danh dau diem vi pham margin
    y_val = 2 * y2 - 1
    dec = svm2.decision_function(X2)
    violators = np.where(y_val * dec < 1.0)[0]
    ax.scatter(X2[violators, 0], X2[violators, 1], facecolors='none',
               edgecolors='#ff7f0e', linewidths=2, s=180,
               label='Vi pham margin')
    ax.set_title('Soft-Margin SVM (C=0.5)\nDu lieu co nhieu, cho phep sai so',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Dac trung 1 (RMS)', fontsize=12)
    ax.set_ylabel('Dac trung 2 (Kurtosis)', fontsize=12)
    ax.legend(fontsize=10, loc='upper left')
    ax.tick_params(labelsize=11)
    ax.text(0.02, 0.02,
            u'+  Chiu duoc nhieu tot\n+  Bein rong, tong quat\n-  Can chon C phu hop',
            transform=ax.transAxes, fontsize=9, va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', fc='#e8f4e8', ec='green', lw=1))

    # ---------------------------------------------------------------
    # Panel 3: RBF Kernel SVM (du lieu phi tuyen, dong tam)
    # ---------------------------------------------------------------
    X3, y3 = make_circles(n_samples=200, noise=0.07, factor=0.4, random_state=42)
    svm3 = SVC(kernel='rbf', gamma=2, C=10)
    svm3.fit(X3, y3)
    acc3 = svm3.score(X3, y3)

    ax = axes[2]
    x_min, x_max = X3[:, 0].min() - 0.3, X3[:, 0].max() + 0.3
    y_min, y_max = X3[:, 1].min() - 0.3, X3[:, 1].max() + 0.3
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                         np.linspace(y_min, y_max, 300))
    Z = svm3.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    preds = svm3.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5],
                colors=['#aec7e8', '#ffb09c'], alpha=0.25)
    ax.contour(xx, yy, Z, levels=[0], colors='black', linewidths=2)
    ax.scatter(X3[y3==0, 0], X3[y3==0, 1], c='#1f77b4', marker='o',
               s=45, edgecolors='k', linewidths=0.5, label='Normal')
    ax.scatter(X3[y3==1, 0], X3[y3==1, 1], c='#d62728', marker='^',
               s=45, edgecolors='k', linewidths=0.5, label='Fault')
    sv = svm3.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], facecolors='none', edgecolors='black',
               linewidths=2, s=180)
    ax.set_title('RBF Kernel SVM (gamma=2)\nDu lieu phi tuyen, Accuracy={:.0%}'.format(acc3),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Dac trung 1', fontsize=12)
    ax.set_ylabel('Dac trung 2', fontsize=12)
    ax.legend(fontsize=10, loc='lower left')
    ax.set_aspect('equal')
    ax.tick_params(labelsize=11)
    ax.text(0.02, 0.02,
            u'+  Xu ly phi tuyen tot\n+  Linh hoat, mac dinh tot\n-  Can chon C va gamma',
            transform=ax.transAxes, fontsize=9, va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', fc='#e8f4e8', ec='green', lw=1))

    # Tieu de chung
    plt.suptitle(
        'Ket luan: Ba bien the SVM cho ba tinh huong du lieu khac nhau',
        fontsize=15, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig(get_save_path('slide8_summary.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: slide8_summary.png")


if __name__ == '__main__':
    # Chay tuan tu sinh 7 hinh
    plot_slide1()
    plot_slide2()
    plot_slide3()
    plot_slide4()
    plot_slide5()
    plot_slide6()
    plot_slide8()
