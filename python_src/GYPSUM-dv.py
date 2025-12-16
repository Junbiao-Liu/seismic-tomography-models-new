import numpy as np
from netCDF4 import Dataset

# 输入文件路径
input_filename = '../orig_nc/GYPSUM_percent.nc'
# 输出文件路径
output_filename = '../processing_nc/GYPSUM-dv.nc'

# ---------------------------- 读取原始文件并转换 ----------------------------
with Dataset(input_filename, mode='r') as src:
    # 创建新文件
    with Dataset(output_filename, mode='w') as dst:
        
        # 复制维度
        for dimname, dim in src.dimensions.items():
            dst.createDimension(dimname, len(dim) if not dim.isunlimited() else None)
        
        # 复制所有变量，除了要重命名的 'dvs' 和 'dvp' 变量
        for varname, variable in src.variables.items():
            if varname in ['dvs', 'dvp']:
                continue  # 跳过需要重命名的变量
            
            # 检查是否有 _FillValue 属性
            fill_value = getattr(variable, '_FillValue', None)
            
            # 创建新变量并复制数据和属性
            if fill_value is not None:
                out_var = dst.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
            else:
                out_var = dst.createVariable(varname, variable.datatype, variable.dimensions)
            
            out_var[:] = variable[:]
            
            # 复制除 _FillValue 之外的所有属性
            for attr_name in variable.ncattrs():
                if attr_name != '_FillValue':
                    setattr(out_var, attr_name, getattr(variable, attr_name))
        
        # 特别处理 'dvs' 变量，重命名为 'dVs(%)'
        if 'dvs' in src.variables:
            dvs_var = src.variables['dvs']
            # 检查是否有 _FillValue 属性
            fill_value = getattr(dvs_var, '_FillValue', None)
            
            # 创建新变量
            if fill_value is not None:
                dvs_pct_var = dst.createVariable('dVs(%)', dvs_var.datatype, dvs_var.dimensions, fill_value=fill_value)
            else:
                dvs_pct_var = dst.createVariable('dVs(%)', dvs_var.datatype, dvs_var.dimensions)
            
            dvs_pct_var[:] = dvs_var[:]
            
            # 复制除 _FillValue 之外的所有属性
            for attr_name in dvs_var.ncattrs():
                if attr_name != '_FillValue':
                    setattr(dvs_pct_var, attr_name, getattr(dvs_var, attr_name))
        
        # 特别处理 'dvp' 变量，重命名为 'dVp(%)'
        if 'dvp' in src.variables:
            dvp_var = src.variables['dvp']
            # 检查是否有 _FillValue 属性
            fill_value = getattr(dvp_var, '_FillValue', None)
            
            # 创建新变量
            if fill_value is not None:
                dvp_pct_var = dst.createVariable('dVp(%)', dvp_var.datatype, dvp_var.dimensions, fill_value=fill_value)
            else:
                dvp_pct_var = dst.createVariable('dVp(%)', dvp_var.datatype, dvp_var.dimensions)
            
            dvp_pct_var[:] = dvp_var[:]
            
            # 复制除 _FillValue 之外的所有属性
            for attr_name in dvp_var.ncattrs():
                if attr_name != '_FillValue':
                    setattr(dvp_pct_var, attr_name, getattr(dvp_var, attr_name))

print(f"✅ 成功生成新文件 '{output_filename}'，变量 'dvs' 和 'dvp' 已重命名为 'dVs(%)' 和 'dVp(%)'")
