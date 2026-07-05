# Layered Section Geometry (LSG)
仓库全称：layered-section-geometry-lsg
配套理论体系：GYY-GOES 全域本源演化体系（DR-TOE 维度互易万物理论）
开源版本当前：v0.2-Core4Industry
已完成开发批次：批次0（基础骨架）、批次1（Common-LSG底层内核）、批次2（四大成熟核心行业落地模块）

## 一、项目核心定义
### 1.1 层级截面几何 LSG 简介
层级截面几何（Layered Section Geometry，简称LSG）是一套全新三维重建数学几何体系，为黎曼几何升级替代方案。
核心思路：抛弃传统正交切片重建限制，以**层级截面矩阵+层级积分+维度互易变换**为底层公理支撑，支持任意旋转角度、非规则、非正交截面数据连续顺滑三维建模，解决传统CT、点云、声呐成像阶梯伪影、高密度采集高成本、多源异构数据不兼容行业痛点。

### 1.2 四大底层本源公理（理论基石）
完整数学推导存放于 `docs/LSG_Theory_Base.md`
1. 截面映射公理：任意空间几何体可分解为无限多层独立截面矩阵
2. 层级积分公理：多层截面矩阵积分可还原完整连续三维空间梯度场
3. 约束边界公理：物理场景固有参数可作为截面值域约束优化重建精度
4. 维度互易变换公理：截面空间与实体空间双向可逆映射，实现跨维度数据转换

### 1.3 技术核心优势
1. 兼容稀疏采样数据：仅需传统方案30%采集数据即可完成高精度三维重建
2. 原生支持非正交切片：无需设备固定正交扫描角度，适配绝大多数成像传感器
3. 全局梯度顺滑机制：彻底消除传统重建阶梯状断层伪影
4. 统一标准化输入接口：医疗CT、超声、激光雷达、水下声呐全部复用同一底层内核
5. 底层框架永久公有领域，杜绝底层算法专利垄断

## 二、开源法律约束与协议说明
本仓库全部代码遵循 **MIT开源协议 + 人类公共领域补充约束条款**，完整约束文本查看根目录 `LICENSE` 文件，核心约束摘要：
1. Common-LSG 全部底层几何算法、矩阵运算、层级积分、非正交切片重建核心逻辑永久归入人类公共知识领域，任何企业、机构、个人**不得基于该基础内核申请独占专利**；
2. 使用者基于本仓库行业场景增量优化代码申请专利时，必须无偿、永久向全球所有第三方授予本LSG底层框架免费商用/学术使用许可；
3. 禁止单独剥离通用底层Common-LSG库进行闭源售卖、框架买断式独家授权；
4. 所有公开代码、文档、数学推导永久留存Git时间戳存证，形成完整现有技术证据链，用于规避后续专利纠纷。

配套法律逻辑文档：`docs/Patent_Prevention_Logic.md`

## 三、仓库批次化开发架构（分阶段开源存证）
整体分为4大开发批次，由底层至行业逻辑递进，每批次独立Git提交并打上永久版本标签，分段完成开源存证。
### 已完成批次
1. **批次0 BaseSkeleton（v0.0-BaseSkeleton）**
    仓库基础骨架搭建：协议文件、顶层README、gitignore、全局规范文档、空目录骨架，初始化完整工程结构。
2. **批次1 Common-LSG 底层内核（v0.1-CommonCore）**
    整套LSG通用几何底层库，所有行业模块统一依赖，锁定基础理论公有领域，为全项目核心。
    - axiom_calc：公理矩阵、层级积分、维度互易变换数学实现
    - slice_rebuild：通用非正交切片融合重建内核
    - constraint_algo：全局坐标校准、噪声平滑、几何畸变基础算子
    - io_utils：多源数据解析、三维模型通用导出工具
3. **批次2 四大成熟核心行业模块（v0.2-Core4Industry）【当前完成】**
    四大商业化落地成熟赛道，仅编写场景专属校正、降噪、硬件适配代码，无重复底层逻辑：
    - Medical-CT：医用CT DICOM三维靶器官重建、术前规划建模
    - Medical-Ultrasound：超声射频/影像三维重建，抑制斑点噪声与深度衰减
    - Geo-MountainNav：山区无人机LiDAR稀疏点云高精地形建图、离线自主导航
    - Ocean-SubNav：多波束声呐海底地形测绘、水下潜航离线导航地图构建

### 待开发预留批次
4. **批次3 八大全工业高价值场景（v0.3-Full12Industry）**
    Aerospace-Space、Industrial-3DInspect、Architecture-BIM、Robot-Vision、Energy-OilGeo、VirtualReality-VRAR、Traffic-SmartRoad、Bio-Microscope
5. **批次4 小众拓展领域（最终稳定版 v1.0-LSG_Full_OpenSource）**
    Meteorology-Atmosphere大气三维分层建模、Archaeology-RelicScan文物扫描重建

完整目录树、版本迭代记录：`docs/Repository_Structure.md`

## 四、四大核心行业模块功能简述
### 4.1 Medical-CT 医学CT模块
- 标准DICOM序列解析，自动转换人体HU值灰度矩阵
- 金属伪影、射束硬化专属修复算法
- 基于人体组织HU区间分层边界约束，精准分割骨骼、肺部、软组织
- 输出可用于手术模拟、3D打印的STL人体组织模型

### 4.2 Medical-Ultrasound 超声成像模块
- 超声DICOM与原始射频信号兼容解析
- 自适应Lee滤波消除超声固有斑点噪声
- 声速、声学阻抗物理约束强化组织界面分层
- 深度衰减补偿，解决远场灰度衰减失真问题

### 4.3 Geo-MountainNav 山区无人机地形导航
- LAS激光雷达点云、航拍视觉图像双数据源适配
- 植被、飞鸟离群点自动过滤，还原裸地真实地形
- 山体自然坡度梯度约束，杜绝重建断崖失真
- 稀疏点云快速构建山区离线导航高精地图

### 4.4 Ocean-SubNav 水下海底测绘导航
- 多波束测深xyz、las水文数据解析接口
- 水体气泡散射、声呐多途反射伪影抑制
- 海底沉积地貌坡度分层约束
- 生成水下潜航器专用海底地形导航模型

## 五、环境部署与依赖安装
### 5.1 环境基础要求
Python >= 3.8

### 5.2 一键安装全部依赖
```bash
pip install -r requirements.txt
六、项目目录快速总览
layered-section-geometry-lsg/
├─ README.md                    # 本总说明文档
├─ LICENSE                      # MIT协议+公有领域专利约束
├─ .gitignore                   # 缓存、原始数据、IDE配置过滤规则
├─ requirements.txt             # 全仓库Python依赖清单
├─ git_push_batch2.sh           # Linux/Mac批次2一键提交存证脚本
├─ git_push_batch2.bat          # Windows批次2一键提交存证脚本
├─ Common-LSG/                  # 批次1底层通用几何内核
├─ Medical-CT/                  # 批次2 医学CT模块
├─ Medical-Ultrasound/          # 批次2 超声成像模块
├─ Geo-MountainNav/             # 批次2 山区无人机导航模块
├─ Ocean-SubNav/                # 批次2 水下声呐测绘模块
└─ docs/                        # 全局理论、规范、版本文档库
   ├─ LSG_Theory_Base.md        # LSG完整数学公理与推导
   ├─ Repository_Structure.md   # 完整仓库目录树+版本存证记录
   ├─ Patent_Prevention_Logic.md# 开源专利规避完整逻辑说明
   ├─ Preprint_Link.md          # GYY-GOES理论预印本DOI存证链接
   └─ Dev_Standard.md           # 全局统一代码、矩阵、接口开发规范
七、运行示例（通用调用逻辑）
所有行业模块调用逻辑统一，仅替换场景专属解析、约束、降噪类，底层重建完全复用 Common-LSG。
以 Medical-CT 极简调用示例：
# 导入场景适配工具
from Medical-CT.hardware_adapt.dicom_ct_parser import DicomCTParser
from Medical-CT.scene_constraint.ct_tissue_constraint import CTTissueConstraint
# 导入通用底层重建内核
from Common-LSG.slice_rebuild import SectionRebuilder

# 1. 解析DICOM影像为标准截面矩阵
parser = DicomCTParser()
ct_data = parser.load_dicom_series("./sample_ct_folder")
# 2. 施加人体组织边界约束
constraint = CTTissueConstraint()
constrained_stack = [constraint.apply_hu_boundary_constraint(s, tissue_type="bone") for s in ct_data.section_stack]
# 3. 调用通用LSG非正交重建
rebuilder = SectionRebuilder()
volume_model = rebuilder.non_orthogonal_rebuild(constrained_stack, ct_data.spacing)
每个行业模块内 demo_case/ 文件夹包含可直接运行完整流水线 Demo 代码。 
八、版本迭代存证记录 
1. v0.0-BaseSkeleton：批次 0 仓库基础框架初始化提交 
2. v0.1-CommonCore：批次 1 Common-LSG 底层内核完整开源，锁定基础几何公有领域 
3. v0.2-Core4Industry：批次 2 四大成熟商业行业模块全量提交，覆盖医疗影像、空对地测绘、水下声呐三大核心赛道，阻断主流落地场景底层专利独占路径  
九、理论溯源与预印本 完整全域本源演化体系（GYY-GOES / DR-TOE）预印本信息存放于 docs/Preprint_Link.md所有代码推导严格对齐预印本数学公式，实现理论与工程代码双向可验证。
十、开源规范与贡献说明 
1. 所有代码严格遵循 docs/Dev_Standard.md 统一开发规范，保证跨模块接口兼容； 
2. 新增行业场景仅允许编写场景专属优化代码，禁止重复实现 Common-LSG 底层几何逻辑； 
3. 所有提交必须附带对应批次版本标签，留存完整 Git 时间戳用于开源存证； 
4. 底层 Common-LSG 库永久公有领域，任何人可免费商用、学术使用、二次修改分发，仅需遵守 LICENSE 附加专利约束。
