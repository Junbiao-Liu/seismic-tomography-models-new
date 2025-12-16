import numpy as np
from netCDF4 import Dataset

# 输入文件路径
input_filename = '../orig_nc/SEMUCB-WM1_dvs.nc'
# 输出文件路径
output_filename = '../processing_nc/SEMUCB-WM1-dvs.nc'

# ---------------------------- 读取原始文件并转换 ----------------------------
with Dataset(input_filename, mode='r') as src:
    # 创建新文件
    with Dataset(output_filename, mode='w') as dst:
        
        # 复制维度
        for dimname, dim in src.dimensions.items():
            dst.createDimension(dimname, len(dim) if not dim.isunlimited() else None)
        
        # 复制所有变量，除了要重命名的 'dvs' 变量
        for varname, variable in src.variables.items():
            if varname == 'v':
                continue  # 跳过原始变量
            
            # 创建新变量并复制数据和属性
            out_var = dst.createVariable(varname, variable.datatype, variable.dimensions)
            out_var[:] = variable[:]
            
            # 复制所有属性
            for attr_name in variable.ncattrs():
                setattr(out_var, attr_name, getattr(variable, attr_name))
        
        # 特别处理 'dvs' 变量，重命名为 'dVs(%)'
        dvs_var = src.variables['v']
        dvs_pct_var = dst.createVariable('dVs(%)', dvs_var.datatype, dvs_var.dimensions)
        dvs_pct_var[:] = dvs_var[:]
        
        # 设置 'dVs(%)' 变量的标准元数据
        dvs_pct_var.units = '%, relative to the Voigt-averge of the given 1D reference model'
        dvs_pct_var.long_name = 'dVs(%)'
        dvs_pct_var.coordinates = "depth latitude longitude"
        dvs_pct_var.standard_name = 'shear_velocity_perturbation_relative_to_depth_mean_percentage'
        dvs_pct_var.description = 'Perturbation of shear wave speed from depth-average reference model, expressed as percentage.'
        
        # 复制 'dvs' 变量的其他属性（如果有的话）
        for attr_name in dvs_var.ncattrs():
            if attr_name not in ['units', 'long_name', 'coordinates', 'standard_name', 'description']:
                setattr(dvs_pct_var, attr_name, getattr(dvs_var, attr_name))
        
        # 处理坐标变量，添加标准元数据
        # 经度变量
        if 'longitude' in dst.variables:
            lon_var = dst.variables['longitude']
            # 添加标准的经度元数据
            lon_var.units = 'degrees_east'
            lon_var.long_name = 'longitude'
            lon_var.standard_name = 'longitude'
            lon_var.axis = 'X'
        
        # 纬度变量
        if 'latitude' in dst.variables:
            lat_var = dst.variables['latitude']
            # 添加标准的纬度元数据
            lat_var.units = 'degrees_north'
            lat_var.long_name = 'latitude'
            lat_var.standard_name = 'latitude'
            lat_var.axis = 'Y'
        
        # 深度变量
        if 'depth' in dst.variables:
            depth_var = dst.variables['depth']
            # 添加标准的深度元数据
            depth_var.units = 'km'
            depth_var.long_name = 'depth'
            depth_var.standard_name = 'depth'
            depth_var.axis = 'Z'
            depth_var.positive = 'down'

print(f"✅ 成功生成新文件 '{output_filename}'，变量 'v' 已重命名为 'dVs(%)'，并添加了完整元数据")
