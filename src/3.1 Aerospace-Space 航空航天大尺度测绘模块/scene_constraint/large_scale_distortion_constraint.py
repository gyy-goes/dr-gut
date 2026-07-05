"""
大尺度空间畸变约束模块（场景专属）
底层依赖：Common-LSG constraint_algo 基类
功能：校正大气折射、地球曲率导致的大尺度遥感影像畸变
"""
import numpy as np
from Common_LSG.constraint_algo import BaseSectionConstraint

class LargeScaleDistortionConstraint(BaseSectionConstraint):
    def atmospheric_refraction_correct(self, section_stack, altitude_range):
        """大气折射畸变校正，适配高空遥感数据层级积分"""
        corrected_stack = self.radial_distortion_correct(
            section_stack, 
            refraction_coeff=0.13,
            altitude_range=altitude_range
        )
        return corrected_stack

    def earth_curvature_constrain(self, section_matrix, ground_resolution):
        """地球曲率约束，修正大跨度地形的弧面偏差"""
        constrained_matrix = self.curvature_surface_fit(
            section_matrix,
            resolution=ground_resolution,
            earth_radius=6371000
        )
        return constrained_matrix