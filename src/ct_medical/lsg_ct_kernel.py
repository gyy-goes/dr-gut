python
"""
层级截面几何(LSG V2.0) - CT影像基础解析内核示例
Layered Section Geometry V2.0 - Basic CT Analysis Kernel Demo
对应论文：第3章 双尺度核心定义
Corresponding to Chapter 3: Core Definitions of Dual-Scale Architecture
"""

import numpy as np
import pydicom
import os
from matplotlib import pyplot as plt
from scipy.ndimage import label

# ==================================================
# 1. 加载DICOM断层序列，构建四维像素单元 (对应定义1)
# 1. Load DICOM series, build 4D pixel units (Definition 1)
# ==================================================
def load_dicom_4d(dicom_dir):
    """
    输入: DICOM文件夹路径
    输出: 四维像素张量 P(x,y,z,I) + 层间距dz
    """
    slices = []
    for f in sorted(os.listdir(dicom_dir)):
        if f.endswith('.dcm'):
            ds = pydicom.dcmread(os.path.join(dicom_dir, f))
            slices.append(ds)
    # 按轴向z排序
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    dz = float(slices[1].ImagePositionPatient[2]) - float(slices[0].ImagePositionPatient[2])
    
    # 构建三维灰度体数据 I(x,y,z)
    volume = np.stack([s.pixel_array for s in slices], axis=-1)
    # 四维像素单元: 坐标(x,y,z) + 属性I
    # 4D pixel unit: coordinate (x,y,z) + attribute I
    return volume, dz

# ==================================================
# 2. 像素级空间刻度梯度计算 (对应定义2)
# 2. Pixel-level spatial scale gradient calculation (Definition 2)
# ==================================================
def calc_pixel_gradients(volume, dz):
    """
    逐像素计算轴向一阶梯度g1、二阶梯度g2
    g1: 组织密度变化率 = 局部空间拉伸程度
    g2: 梯度变化曲率 = 局部畸变剧烈程度
    """
    # 一阶梯度 (一阶差分)
    g1 = np.gradient(volume, dz, axis=2)
    # 二阶梯度 (二阶差分)
    g2 = np.gradient(g1, dz, axis=2)
    return g1, g2

# ==================================================
# 3. 跨层连通域聚合 - 基础版 (对应定义3)
# 3. Cross-layer connected domain aggregation - basic (Definition 3)
# ==================================================
def segment_connected_domains(volume, g1, density_threshold, grad_threshold):
    """
    基于密度阈值+梯度阈值，识别连续组织结构单元
    输出: 标记后的连通域掩码
    """
    # 筛选满足材质条件的像素
    mask = (volume > density_threshold) & (np.abs(g1) > grad_threshold)
    # 三维连通域标记
    labeled, num_domains = label(mask)
    return labeled, num_domains

# ==================================================
# 4. 单层可视化: 原始影像 + 梯度热力图
# 4. Single-slice visualization: raw image + gradient heatmap
# ==================================================
def visualize_slice(volume, g1, slice_idx):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].imshow(volume[:, :, slice_idx], cmap='gray')
    axes[0].set_title('原始CT断层 / Raw CT Slice')
    axes[0].axis('off')
    
    im = axes[1].imshow(g1[:, :, slice_idx], cmap='jet', vmin=-50, vmax=50)
    axes[1].set_title('像素级一阶梯度(空间形变强度) / Pixel 1st Gradient')
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], label='梯度值 / Gradient Value')
    
    plt.tight_layout()
    plt.show()

# ==================================================
# 主程序示例
# ==================================================
if __name__ == '__main__':
    # 替换为你的DICOM文件夹路径
    DICOM_PATH = './ct_dicom_data'
    
    # 1. 加载四维数据
    vol, dz = load_dicom_4d(DICOM_PATH)
    print(f"四维像素张量尺寸 / 4D tensor shape: {vol.shape}")
    
    # 2. 计算像素级梯度
    g1, g2 = calc_pixel_gradients(vol, dz)
    
    # 3. 识别异常高梯度连通域(疑似病灶)
    labeled, n_domains = segment_connected_domains(vol, g1, 
                                                    density_threshold=100, 
                                                    grad_threshold=20)
    print(f"识别到高梯度结构单元数 / Detected high-gradient domains: {n_domains}")
    
    # 4. 可视化第z层
    visualize_slice(vol, g1, slice_idx=vol.shape[2]//2)
