"""
卫星/航空遥感数据适配接口
底层依赖：Common-LSG io_utils 通用IO工具
功能：解析多光谱、高分辨率遥感影像，转换为LSG标准截面格式
"""
import numpy as np
from Common_LSG.io_utils import SectionDataStandard

class SatelliteAerialParser(SectionDataStandard):
    def load_remote_sensing_tiff(self, tiff_path):
        """加载GeoTIFF格式遥感影像"""
        try:
            from osgeo import gdal
        except ImportError:
            raise ImportError("需安装gdal依赖：pip install gdal")
        
        dataset = gdal.Open(tiff_path)
        band_array = dataset.GetRasterBand(1).ReadAsArray()
        geotransform = dataset.GetGeoTransform()
        resolution = [abs(geotransform[1]), abs(geotransform[5])]
        
        standard_data = self.format_section_stack(
            np.expand_dims(band_array, axis=0),
            spacing=resolution + [1.0],
            origin=[geotransform[0], geotransform[3], 0]
        )
        return standard_data