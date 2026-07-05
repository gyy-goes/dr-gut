"""
生物显微三维重建Demo
"""
from Bio_Microscope.hardware_adapt.confocal_microscope_parser import ConfocalMicroscopeParser
from Bio_Microscope.noise_optimize.microscope_noise_optimize import MicroscopeNoiseOptimize
from Bio_Microscope.scene_constraint.cell_layer_constraint import CellLayerConstraint
from Common_LSG.slice_rebuild import SectionRebuilder

def micro_rebuild_pipeline(tiff_folder, output_path):
    parser = ConfocalMicroscopeParser()
    micro_data = parser.load_tiff_stack(tiff_folder)
    
    optimizer = MicroscopeNoiseOptimize()
    optimized_stack = optimizer.photobleaching_correct(micro_data.section_stack)
    optimized_stack = [optimizer.shot_noise_suppress(s) for s in optimized_stack]
    
    constraint = CellLayerConstraint()
    constrained_stack = [constraint.cell_boundary_enhance(s, min_cell_size=0.5) for s in optimized_stack]
    
    rebuilder = SectionRebuilder()
    micro_model = rebuilder.non_orthogonal_rebuild(constrained_stack, micro_data.spacing)
    
    print("生物显微三维重建完成")
    return micro_model

if __name__ == "__main__":
    micro_rebuild_pipeline("./micro_tiff", "./output/cell_model.stl")