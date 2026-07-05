"""
LSG 通用IO工具
全行业兼容的传感器数据解析、三维模型导出接口
统一输入输出格式，保证跨场景数据互通
"""

import numpy as np
import struct


def parse_generic_sensor_data(file_path, data_type="float32", shape=None):
    """
    通用传感器原始数据解析
    支持二进制原始切片数据、文本点云数据
    :param file_path: 文件路径
    :param data_type: 数据类型 float32 / uint16 / point_cloud
    :param shape: 数据形状，二维截面用 (H,W)，点云可不填
    :return: 解析后numpy数组
    """
    if data_type == "point_cloud":
        # 通用点云txt格式：每行 x y z [value]
        data = np.loadtxt(file_path)
        return data
    
    else:
        # 二进制原始数据
        dtype_map = {
            "float32": np.float32,
            "float64": np.float64,
            "uint8": np.uint8,
            "uint16": np.uint16,
            "int32": np.int32
        }
        raw = np.fromfile(file_path, dtype=dtype_map.get(data_type, np.float32))
        if shape is not None:
            raw = raw.reshape(shape)
        return raw


def export_point_cloud(points, file_path, values=None):
    """
    导出三维点云模型（通用txt格式，全软件兼容）
    :param points: 点坐标 (N, 3)
    :param file_path: 输出文件路径
    :param values: 可选，每个点的数值 (N,)
    """
    if values is not None:
        data = np.column_stack((points, values))
        fmt = "%.6f %.6f %.6f %.4f"
    else:
        data = points
        fmt = "%.6f %.6f %.6f"
    
    np.savetxt(file_path, data, fmt=fmt)


def export_mesh_stl(vertices, faces, file_path, binary=True):
    """
    导出STL三角网格模型（通用工业标准格式）
    :param vertices: 顶点坐标 (N, 3)
    :param faces: 三角面索引 (M, 3)
    :param file_path: 输出文件路径
    :param binary: 是否二进制格式
    """
    if binary:
        # 二进制STL
        with open(file_path, 'wb') as f:
            # 80字节头
            f.write(b'LSG Layered Section Geometry Export' + b'\x00' * (80 - len(b'LSG Layered Section Geometry Export')))
            # 三角面数量
            f.write(struct.pack('<I', len(faces)))
            
            for face in faces:
                v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                # 法向量
                normal = np.cross(v1 - v0, v2 - v0)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                f.write(struct.pack('<3f', *normal))
                f.write(struct.pack('<3f', *v0))
                f.write(struct.pack('<3f', *v1))
                f.write(struct.pack('<3f', *v2))
                f.write(struct.pack('<H', 0))
    else:
        # ASCII STL
        with open(file_path, 'w') as f:
            f.write("solid lsg_mesh\n")
            for face in faces:
                v0, v1, v2 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                normal = np.cross(v1 - v0, v2 - v0)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                f.write(f"facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                f.write("  outer loop\n")
                f.write(f"    vertex {v0[0]:.6f} {v0[1]:.6f} {v0[2]:.6f}\n")
                f.write(f"    vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n")
                f.write(f"    vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n")
                f.write("  endloop\n")
                f.write("endfacet\n")
            f.write("endsolid lsg_mesh\n")
