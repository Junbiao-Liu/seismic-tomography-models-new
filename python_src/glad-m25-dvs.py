import numpy as np
from netCDF4 import Dataset

# 输入文件路径
input_filename = '../orig_nc/glad-m25-vs-0.0-n4.nc'
# 输出文件路径
output_filename = '../processing_nc/glad-m25-dvs.nc'

# ---------------------------- 1. 读取原始文件中的变量和维度 ----------------------------
# ---------------------------- 2. 计算 vs 和 dlnVs(%) ----------------------------
# ---------------------------- 3. 创建新文件并只写入必要变量 ----------------------------
with Dataset(input_filename, mode='r') as src:
    depth = src.variables['depth'][:]
    latitude = src.variables['latitude'][:]
    longitude = src.variables['longitude'][:]

    vsv = src.variables['vsv'][:]
    vsh = src.variables['vsh'][:]

    # ---------------------------- 2. 计算 vs 和 dlnVs(%) ----------------------------
    # 原始 shape: (depth, lon, lat)，先进行转置为 (depth, lat, lon)
    vsv = np.transpose(vsv, (0, 2, 1))
    vsh = np.transpose(vsh, (0, 2, 1))

    # 计算各向平均的 Vs
    vs = np.sqrt((2 * vsv**2 + vsh**2) / 3)

    # 每层深度对经纬度求均值：shape (depth,)
    vs_mean = np.mean(vs, axis=(1, 2), keepdims=True)  # shape: (depth, 1, 1)

    # 计算相对扰动百分比 dlnVs (%)
    dlnVs_pct = (vs - vs_mean) / vs_mean * 100  # 单位是 %

    # ---------------------------- 3. 创建新文件并只写入必要变量 ----------------------------
    with Dataset(output_filename, mode='w') as dst:
        
        # 创建维度
        dst.createDimension('depth', len(depth))
        dst.createDimension('latitude', len(latitude))
        dst.createDimension('longitude', len(longitude))
        
        # 复制坐标变量及其属性
        # depth
        var_depth = dst.createVariable('depth', np.float32, ('depth',))
        var_depth[:] = depth
        if 'depth' in src.variables:
            for attr in src.variables['depth'].ncattrs():
                setattr(var_depth, attr, getattr(src.variables['depth'], attr))
        
        # latitude
        var_latitude = dst.createVariable('latitude', np.float32, ('latitude',))
        var_latitude[:] = latitude
        if 'latitude' in src.variables:
            for attr in src.variables['latitude'].ncattrs():
                setattr(var_latitude, attr, getattr(src.variables['latitude'], attr))
        
        # longitude
        var_longitude = dst.createVariable('longitude', np.float32, ('longitude',))
        var_longitude[:] = longitude
        if 'longitude' in src.variables:
            for attr in src.variables['longitude'].ncattrs():
                setattr(var_longitude, attr, getattr(src.variables['longitude'], attr))
        
        # 写入计算后的 Vs
        var_vs = dst.createVariable('vs', np.float32, ('depth', 'latitude', 'longitude'))
        var_vs[:] = np.transpose(vs, (0, 2, 1))  # 还原成原始维度结构 (depth, lon, lat)
        var_vs.units = 'km/s'
        var_vs.long_name = 'Shear wave velocity'
        var_vs.coordinates = "depth latitude longitude"
        
        # 写入 dlnVs(%)
        var_dlnVs_pct = dst.createVariable('dVs(%)', np.float32, ('depth', 'latitude', 'longitude'))
        var_dlnVs_pct[:] = np.transpose(dlnVs_pct, (0, 2, 1))  # 还原成原始维度结构 (depth, lon, lat)
        var_dlnVs_pct.units = '%, dV relative to depth-averaged velocity'
        var_dlnVs_pct.long_name = 'dVs(%)'
        var_dlnVs_pct.coordinates = "depth latitude longitude"
        var_dlnVs_pct.standard_name = 'shear_velocity_perturbation_relative_to_depth_mean_percentage'
        var_dlnVs_pct.description = 'Perturbation of shear wave speed from depth-average reference model, expressed as percentage.'

print("✅ 已成功创建精简文件 'glad-m25-dvs.nc'，只包含 vs 和 dVs(%)")
