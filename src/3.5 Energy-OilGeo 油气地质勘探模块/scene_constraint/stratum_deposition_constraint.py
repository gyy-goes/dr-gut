"""
地层沉积约束模块（场景专属）
底层依赖：Common-LSG constraint_algo 基类
功能：基于沉积岩地层特性约束层位边界，校正大尺度地层畸变
"""
from Common_LSG.constraint_algo import BaseSectionConstraint

class StratumDepositionConstraint(BaseSectionConstraint):
    def stratum_layer_constrain(self, section_stack):
        """地层沉积层序约束，保证层位连续顺滑"""
        constrained_stack = self.layer_sequence_constrain(section_stack, smooth_strength=0.8)
        return constrained_stack

    def reservoir_boundary_extract(self, section_matrix, porosity_threshold):
        """油气储层边界提取，基于孔隙度阈值分层"""
        reservoir_mask = self.threshold_layer_segment(section_matrix, porosity_threshold)
        return reservoir_mask