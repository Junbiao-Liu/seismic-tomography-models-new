import numpy as np
from netCDF4 import Dataset

# 输入文件路径
input_filename = '../orig_nc/UUP07.nc'
# 输出文件路径
output_filename = '../processing_nc/UUP07-dvp.nc'

# ---------------------------- 读取原始文件并转换 ----------------------------
with Dataset(input_filename, mode='r') as src:
    # 创建新文件
    with Dataset(output_filename, mode='w') as dst:
        
        # 复制维度
        for dimname, dim in src.dimensions.items():
            dst.createDimension(dimname, len(dim) if not dim.isunlimited() else None)
        
        # 复制所有变量，除了要重命名的 'dvp' 变量
        for varname, variable in src.variables.items():
            if varname == 'dvp':
                continue  # 跳过原始变量
            
            # 创建新变量并复制数据和属性
            out_var = dst.createVariable(varname, variable.datatype, variable.dimensions)
            out_var[:] = variable[:]
            
            # 复制所有属性
            for attr_name in variable.ncattrs():
                setattr(out_var, attr_name, getattr(variable, attr_name))
        
        # 特别处理 'dvp' 变量，重命名为 'dVp(%)'
        dvp_var = src.variables['dvp']
        dvppct_var = dst.createVariable('dVp(%)', dvp_var.datatype, dvp_var.dimensions)
        dvppct_var[:] = dvp_var[:]
        
        # 设置 'dVp(%)' 变量的标准元数据
        dvppct_var.units = '%'
        dvppct_var.long_name = 'dVp(%)'
        dvppct_var.coordinates = "depth latitude longitude"
        dvppct_var.standard_name = 'compressional_velocity_perturbation_relative_to_depth_mean_percentage'
        dvppct_var.description = 'Perturbation of compressional wave speed from depth-average reference model, expressed as percentage.'
        
        # 复制 'dvp' 变量的其他属性（如果有的话）
        for attr_name in dvp_var.ncattrs():
            if attr_name not in ['units', 'long_name', 'coordinates', 'standard_name', 'description']:
                setattr(dvppct_var, attr_name, getattr(dvp_var, attr_name))
        
        # 特别处理经度变量，将其从 [180,540] 转换为 [-180,180]
        if 'longitude' in dst.variables:
            lon_var = dst.variables['longitude']
            lon_data = lon_var[:]
            # 转换经度范围：从 [180,540] 到 [-180,180]
            lon_converted = ((lon_data - 180) % 360) - 180
            # 重新排序经度和对应的数据维度
            sort_idx = np.argsort(lon_converted)
            lon_var[:] = lon_converted[sort_idx]
            
            # 添加标准的经度元数据
            lon_var.units = 'degrees_east'
            lon_var.long_name = 'longitude'
            lon_var.standard_name = 'longitude'
            lon_var.axis = 'X'
            
            # 如果存在 'dVp(%)' 变量，也需要对其经度维度重新排序
            if 'dVp(%)' in dst.variables:
                dvppct_data = dst.variables['dVp(%)'][:]
                # 假设经度是最后一个维度
                dvppct_sorted = dvppct_data[..., sort_idx]
                dst.variables['dVp(%)'][:] = dvppct_sorted
        
        # 处理纬度变量，添加标准元数据
        if 'latitude' in dst.variables:
            lat_var = dst.variables['latitude']
            # 添加标准的纬度元数据
            lat_var.units = 'degrees_north'
            lat_var.long_name = 'latitude'
            lat_var.standard_name = 'latitude'
            lat_var.axis = 'Y'
        
        # 处理深度变量，添加标准元数据
        if 'depth' in dst.variables:
            depth_var = dst.variables['depth']
            # 添加标准的深度元数据
            depth_var.units = 'km'
            depth_var.long_name = 'depth'
            depth_var.standard_name = 'depth'
            depth_var.axis = 'Z'
            depth_var.positive = 'down'

print(f"✅ 成功生成新文件 '{output_filename}'，变量 'dvp' 已重命名为 'dVp(%)'，经度已转换为 [-180, 180]，并添加了完整元数据")
