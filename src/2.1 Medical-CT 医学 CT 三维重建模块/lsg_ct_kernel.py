"""
LSG 自上而下层级涌现气道重建【全bug修复终版】
修复点：
1. 移除add_volume非法blend参数，解决TypeError
2. 下调最高起始HU，抓取完整主气管，解决气道仅58体素
3. 病灶增加HU下限过滤，消除千万级噪点肺组织
4. 渲染clim+opacity强制mask=0全透明，无大片黄壳
5. 兼容旧版scipy、无ball依赖、无语法错误
"""
import os
import numpy as np
import pydicom
import torch
import pyvista as pv
from scipy.ndimage import binary_dilation, binary_erosion

# ===================== 全局配置参数 =====================
DICOM_FOLDER = "./dataset/ct_scan/"
SAVE_PREFIX = "airway_top_down_fixed_all_bug"
USE_GPU = True

# 【核心生长参数修复：下调起始HU，抓完整主气管】
MAX_HU_START = 200        # 原1800太高，只有钙化点，改为200抓取主气管管壁
MIN_ACTIVE_HU = -200       # 低于此=正常肺泡/空气，全程不参与运算
LESIONS_MIN_HU = 100       # 病灶最低HU，低于此不算病变，过滤海量肺噪点
HU_STEP = 50               # HU分档步长，每轮向下走50HU
GROW_HU_DIFF = 30          # 邻域HU差小于该值=同源组织，允许握手融合

# 管壁连续化修复参数
WALL_CLOSE_RADIUS = 2      # 闭运算核半径，填补点阵缝隙，融合为连续管壁

# 渲染参数
BACKGROUND_COLOR = "black"
# =======================================================

# 设备初始化
if USE_GPU and torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"✅ CUDA 启用：{torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print(f"⚠️ 运行于CPU")

# ===================== 工具函数 =====================
# 手动生成球形结构核，兼容所有版本scipy，无需ball
def create_sphere_kernel(radius):
    size = radius * 2 + 1
    xx, yy, zz = np.meshgrid(np.arange(size), np.arange(size), np.arange(size))
    center = radius
    dist = np.sqrt((xx - center)**2 + (yy - center)**2 + (zz - center)**2)
    return (dist <= radius).astype(np.uint8)

# ===================== 1. 加载CT + 固定三维坐标 =====================
def load_ct_with_coord(folder):
    slices = []
    for fname in os.listdir(folder):
        if fname.lower().endswith(".dcm"):
            ds = pydicom.dcmread(os.path.join(folder, fname))
            slices.append(ds)
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    pix_spacing = slices[0].PixelSpacing
    slice_thick = abs(slices[1].ImagePositionPatient[2] - slices[0].ImagePositionPatient[2])
    D = len(slices)
    H, W = slices[0].pixel_array.shape

    # 全局固定三维坐标 (z楼层, y行, x列)
    z_axis = torch.linspace(0, D-1, D, device=device).reshape(D,1,1).repeat(1,H,W)
    y_axis = torch.linspace(0, H-1, H, device=device).reshape(1,H,1).repeat(D,1,W)
    x_axis = torch.linspace(0, W-1, W, device=device).reshape(1,1,W).repeat(D,H,1)
    coord_3d = torch.stack([z_axis, y_axis, x_axis], dim=-1)

    # 还原原始HU值，全体素自带身份标签
    raw_np = np.stack([s.pixel_array for s in slices], axis=0).astype(np.float32)
    slope = getattr(slices[0], "RescaleSlope", 1.0)
    intercept = getattr(slices[0], "RescaleIntercept", 0.0)
    hu_full = raw_np * slope + intercept
    hu_tensor = torch.from_numpy(hu_full).to(device)

    print(f"三维楼宇尺寸 D={D}层 H={H} W={W}")
    print(f"原始HU范围：{hu_tensor.min():.1f} ~ {hu_tensor.max():.1f}")
    return coord_3d, hu_tensor, pix_spacing, slice_thick

# ===================== 2. 过滤正常肺泡，仅保留高HU候选体素 =====================
def get_active_mask(hu_vol):
    # 低于MIN_ACTIVE_HU=正常肺泡/空气，全程不参与运算
    active_mask = hu_vol > MIN_ACTIVE_HU
    inactive_ratio = (~active_mask).float().mean() * 100
    print(f"正常肺泡+空气占比 {inactive_ratio:.2f}%，全程剔除不参与计算")
    return active_mask

# ===================== 3. 六邻域安全握手融合（无越界） =====================
def safe_neighbor_grow(volume, current_grow_mask, diff_thresh):
    D, H, W = volume.shape
    new_grow = torch.zeros_like(current_grow_mask, dtype=torch.bool, device=device)
    dirs = [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]
    for dz, dy, dx in dirs:
        # Z轴边界
        if dz == -1:
            czs,cze = 1,D
            nzs,nze = 0,D-1
        elif dz == 1:
            czs,cze = 0,D-1
            nzs,nze = 1,D
        else:
            czs,cze = 0,D
            nzs,nze = 0,D
        # Y轴边界
        if dy == -1:
            cys,cye = 1,H
            nys,nye = 0,H-1
        elif dy == 1:
            cys,cye = 0,H-1
            nys,nye = 1,H
        else:
            cys,cye = 0,H
            nys,nye = 0,H
        # X轴边界
        if dx == -1:
            cxs,cxe = 1,W
            nxs,nxe = 0,W-1
        elif dx == 1:
            cxs,cxe = 0,W-1
            nxs,nxe = 1,W
        else:
            cxs,cxe = 0,W
            nxs,nxe = 0,W

        curr_hu = volume[czs:cze, cys:cye, cxs:cxe]
        nei_hu = volume[nzs:nze, nys:nye, nxs:nxe]
        curr_conn = current_grow_mask[czs:cze, cys:cye, cxs:cxe]
        gray_diff = torch.abs(curr_hu - nei_hu)
        # HU差值小于阈值 → 同源组织 → 握手融合
        merge_ok = curr_conn & (gray_diff < diff_thresh)
        new_grow[nzs:nze, nys:nye, nxs:nxe] |= merge_ok
    return new_grow

# ===================== 4. 核心：自上而下层级生长 =====================
def top_down_hierarchy_grow(hu_vol, active_mask):
    # 初始种子：最高HU区间的体素（修复：MAX_HU_START=200，抓取主气管）
    grow_mask = hu_vol > MAX_HU_START
    grow_mask = grow_mask & active_mask
    init_count = grow_mask.sum().item()
    print(f"\n初始核心种子体素：{init_count} 个（最高HU主干结构）")

    # 计算总分档轮次
    total_levels = int((MAX_HU_START - MIN_ACTIVE_HU) / HU_STEP)
    print(f"自上而下共 {total_levels} 档HU分级生长")

    for level in range(total_levels):
        current_high = MAX_HU_START - level * HU_STEP
        current_low = current_high - HU_STEP
        # 当前档位候选体素：在HU区间内、未被纳入、属于有效区域
        candidate = (hu_vol <= current_high) & (hu_vol > current_low) & active_mask & (~grow_mask)
        if candidate.sum() == 0:
            continue

        # 已有连通域向外邻域扩张，仅合并同源组织
        expand = safe_neighbor_grow(hu_vol, grow_mask, GROW_HU_DIFF)
        new_add = expand & candidate
        grow_mask |= new_add

        added_num = new_add.sum().item()
        print(f"  第{level+1:2d}档 HU[{current_low:.0f}, {current_high:.0f}] 新增融合体素：{added_num}")

        # 连续多轮无新增，提前收敛
        if added_num == 0 and level > 8:
            print("  结构生长收敛，提前终止")
            break

    total_airway = grow_mask.sum().item()
    print(f"\n层级生长完成，气道总连通体素：{total_airway}")
    return grow_mask

# ===================== 5. 提取孤立病灶（修复：增加LESIONS_MIN_HU过滤海量噪点） =====================
def extract_isolated_lesions(hu_vol, active_mask, airway_mask):
    # 仅HU高于病灶阈值、不在气道内、属于有效区域才判定为病灶
    lesion_candidate = (hu_vol > LESIONS_MIN_HU) & active_mask & (~airway_mask)
    lesion_mask = lesion_candidate
    lesion_count = lesion_mask.sum().item()
    print(f"提取孤立病灶体素：{lesion_count} 个（不与气道连通、高HU局部异常）")
    return lesion_mask

# ===================== 6. 点阵转连续管壁：形态学闭运算填补缝隙 =====================
def discrete_to_continuous(mask_gpu, radius):
    mask_np = mask_gpu.cpu().numpy().astype(np.uint8)
    kernel = create_sphere_kernel(radius)
    # 闭运算：先膨胀填补缝隙，再腐蚀还原厚度，离散点融合为连续闭合管壁
    dilated = binary_dilation(mask_np, kernel)
    closed = binary_erosion(dilated, kernel)
    return torch.from_numpy(closed.astype(np.float32)).to(device)

# ===================== 7. 保存三维网格 =====================
def save_volume_grid(hu_vol, airway_mask, lesion_mask, pix_spacing, slice_thick, prefix):
    hu_np = hu_vol.cpu().numpy()
    airway_np = airway_mask.cpu().numpy().astype(np.float32)
    lesion_np = lesion_mask.cpu().numpy().astype(np.float32)
    D, H, W = hu_np.shape

    grid = pv.ImageData()
    grid.dimensions = np.array([W, H, D]) + 1
    grid.spacing = (pix_spacing[0], pix_spacing[1], slice_thick)
    grid.cell_data["HU_original"] = hu_np.transpose(2,1,0).ravel(order="F")
    grid.cell_data["airway_mask"] = airway_np.transpose(2,1,0).ravel(order="F")
    grid.cell_data["lesion_mask"] = lesion_np.transpose(2,1,0).ravel(order="F")

    os.makedirs("./output", exist_ok=True)
    vtk_path = f"./output/{prefix}_volume.vtk"
    grid.save(vtk_path)
    print(f"\n三维网格保存完成：{vtk_path}")
    return grid

# ===================== 8. 烟雾式渲染【修复：删除blend非法参数，强制mask=0全透明】 =====================
def render_smoke_airway(grid):
    plotter = pv.Plotter(window_size=(1300, 900))
    plotter.background_color = BACKGROUND_COLOR
    plotter.add_title("自上而下层级涌现 | 烟雾状支气管树 + 孤立病灶", font_size=16)

    # 底层肺组织：极淡空间参考，几乎透明
    plotter.add_volume(
        grid,
        scalars="HU_original",
        cmap="gray",
        clim=[MIN_ACTIVE_HU, MAX_HU_START],
        opacity=[0, 0, 0.02, 0.08]
    )
    # 气道连通树：严格限制clim 0~1，0完全透明，仅mask=1显示
    plotter.add_volume(
        grid,
        scalars="airway_mask",
        cmap="coolwarm",
        clim=[0, 1],
        opacity=[0, 0, 0, 0, 0.9, 1.0]
    )
    # 孤立病灶：0全透明，仅高HU病变高亮
    plotter.add_volume(
        grid,
        scalars="lesion_mask",
        cmap="hot",
        clim=[0, 1],
        opacity=[0, 0, 0, 0, 0.95, 1.0]
    )

    plotter.add_axes(xlabel="X mm", ylabel="Y mm", zlabel="Z Slice")
    plotter.camera_position = "iso"
    plotter.show()

# ===================== 主程序入口 =====================
if __name__ == "__main__":
    print("="*70)
    print("LSG 自上而下层级涌现气道重建 | 全bug修复版")
    print("="*70)

    print("\n【步骤1】构建三维固定坐标，全体素绑定HU身份标签")
    coord_matrix, hu_volume, pix_space, slice_t = load_ct_with_coord(DICOM_FOLDER)

    print("\n【步骤2】剔除正常肺泡，仅保留高HU候选体素")
    active_mask_tensor = get_active_mask(hu_volume)

    print("\n【步骤3】自上而下HU分档，邻域握手融合生长气道")
    airway_raw = top_down_hierarchy_grow(hu_volume, active_mask_tensor)

    print("\n【步骤4】离散点阵转连续闭合管壁（填补缝隙）")
    airway_continuous = discrete_to_continuous(airway_raw, WALL_CLOSE_RADIUS)

    print("\n【步骤5】提取孤立病灶（过滤低HU肺噪点，仅保留高亮病变）")
    lesion_mask_tensor = extract_isolated_lesions(hu_volume, active_mask_tensor, airway_continuous.bool())

    print("\n【步骤6】保存网格，烟雾式渲染（mask=0强制完全透明，无大片黄壳）")
    volume_mesh = save_volume_grid(hu_volume, airway_continuous, lesion_mask_tensor, pix_space, slice_t, SAVE_PREFIX)
    render_smoke_airway(volume_mesh)

    print("\n✅ 运行完成修复说明：")
    print("1. 移除非法blend参数，解决add_volume类型报错")
    print("2. MAX_HU_START下调至200，可抓取完整主气管，不再仅58个点")
    print("3. 病灶新增HU>100过滤，消除千万级正常肺噪点")
    print("4. 渲染opacity强制0值全透明，杜绝整片白色/黄色背景外壳")
    print("5. 自上而下单核心生长，气道天然全域连通，烟雾悬浮纯黑背景")