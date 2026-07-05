"""
VR设备RGB-D数据适配接口
底层依赖：Common-LSG io_utils 通用IO工具
功能：解析VR头显、深度相机数据，适配轻量化实时重建
"""
import numpy as np
from Common_LSG.io_utils import SectionDataStandard

class RGBDVRParser(SectionDataStandard):
    def load_vr_depth_frame(self, depth_array, intrinsic):
        """加载VR设备深度帧数据"""
        standard_data = self.format_section_stack(
            np.expand_dims(depth_array, axis=0),
            spacing=[intrinsic[0,0], intrinsic[1,1], 1.0],
            origin=[0, 0, 0]
        )
        return standard_data