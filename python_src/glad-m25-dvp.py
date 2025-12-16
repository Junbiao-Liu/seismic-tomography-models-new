import numpy as np
from netCDF4 import Dataset

# 输入文件路径
input_filename = '../orig_nc/glad-m25-vp-0.0-n4.nc'
# 输出文件路径
output_filename = '../processing_nc/glad-m25-dvp.nc'

# ---------------------------- 1. 读取原始文件中的变量和维度 ----------------------------
# ---------------------------- 2. 计算 vp 和 dlnVp(%) ----------------------------
# ---------------------------- 3. 创建新文件并只写入必要变量 ----------------------------
with Dataset(input_filename, mode='r') as src:
    # 读取数据
    depth = src.variables['depth'][:]
    latitude = src.variables['latitude'][:]
    longitude = src.variables['longitude'][:]

    vpv = src.variables['vpv'][:]
    vph = src.variables['vph'][:]

    # 计算 vp 和 dlnVp(%)
    # 原始 shape: (depth, lon, lat)，先进行转置为 (depth, lat, lon)
    vpv = np.transpose(vpv, (0, 2, 1))
    vph = np.transpose(vph, (0, 2, 1))

    # 计算各向平均的 Vp
    vp = np.sqrt((3 * vpv**2 + 2 * vph**2) / 5)

    # 每层深度对经纬度求均值：shape (depth,)
    vp_mean = np.mean(vp, axis=(1, 2), keepdims=True)  # shape: (depth, 1, 1)

    # 计算相对扰动百分比 dlnVp (%)
    dlnVp_pct = (vp - vp_mean) / vp_mean * 100  # 单位是 %

    # 创建新文件并只写入必要变量
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
        
        # 写入计算后的 Vp
        var_vp = dst.createVariable('vp', np.float32, ('depth', 'latitude', 'longitude'))
        var_vp[:] = np.transpose(vp, (0, 2, 1))  # 还原成原始维度结构 (depth, lon, lat)
        var_vp.units = 'km/s'
        var_vp.long_name = 'Compressional wave velocity'
        var_vp.coordinates = "depth latitude longitude"
        
        # 写入 dlnVp(%)
        var_dlnVp_pct = dst.createVariable('dVp(%)', np.float32, ('depth', 'latitude', 'longitude'))
        var_dlnVp_pct[:] = np.transpose(dlnVp_pct, (0, 2, 1))  # 还原成原始维度结构 (depth, lon, lat)
        var_dlnVp_pct.units = '%, dV relative to depth-averaged velocity'
        var_dlnVp_pct.long_name = 'dVp(%)'
        var_dlnVp_pct.coordinates = "depth latitude longitude"
        var_dlnVp_pct.standard_name = 'compressional_velocity_perturbation_relative_to_depth_mean_percentage'
        var_dlnVp_pct.description = 'Perturbation of compressional wave speed from depth-average reference model, expressed as percentage.'

print("✅ 已成功创建精简文件 'glad-m25-dvp.nc'，只包含 vp 和 dVp(%)")
