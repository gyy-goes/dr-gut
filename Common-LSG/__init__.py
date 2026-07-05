# LSG 层级截面几何通用底层核心库
# 本模块全部代码永久归入人类公共知识领域，禁止申请独占专利

from .axiom_calc import (
    section_mapping,
    layer_gradient_integral,
    dimension_reciprocal_transform,
    dual_force_gradient
)
from .slice_rebuild import (
    non_orthogonal_slice_align,
    multi_section_fusion,
    universal_slice_reconstruct
)
from .constraint_algo import (
    general_noise_smooth,
    global_coordinate_calibrate,
    geometry_distortion_correct
)
from .io_utils import (
    parse_generic_sensor_data,
    export_point_cloud,
    export_mesh_stl
)

__all__ = [
    # 公理计算核心
    "section_mapping",
    "layer_gradient_integral",
    "dimension_reciprocal_transform",
    "dual_force_gradient",
    # 通用切片重建
    "non_orthogonal_slice_align",
    "multi_section_fusion",
    "universal_slice_reconstruct",
    # 基础约束算法
    "general_noise_smooth",
    "global_coordinate_calibrate",
    "geometry_distortion_correct",
    # 通用IO工具
    "parse_generic_sensor_data",
    "export_point_cloud",
    "export_mesh_stl"
]
