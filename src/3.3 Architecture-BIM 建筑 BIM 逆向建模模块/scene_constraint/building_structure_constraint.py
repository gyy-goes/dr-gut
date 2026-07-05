"""
建筑结构约束模块（场景专属）
底层依赖：Common-LSG constraint_algo 基类
功能：基于建筑正交特性约束墙体、楼板层级，提升BIM建模精度
"""
from Common_LSG.constraint_algo import BaseSectionConstraint

class BuildingStructureConstraint(BaseSectionConstraint):
    def orthogonal_structure_constrain(self, section_matrix):
        """建筑正交结构约束，校正非正交采集导致的墙体形变"""
        constrained_matrix = self.orthogonal_projection_constrain(section_matrix)
        return constrained_matrix

    def component_layer_extract(self, section_stack, component_type="wall"):
        """建筑构件层级提取，分离墙体、楼板、门窗等结构"""
        layer_mask = self.structure_layer_segment(section_stack, component_type=component_type)
        return layer_mask