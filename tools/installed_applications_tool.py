import subprocess
import winreg
from datetime import datetime
from typing import List, Dict

def get_installed_applications(max_count: int = 500, sort_by: str = 'install_date') -> str:
    """
    获取Windows系统中已安装的应用程序列表，包括通过Windows Installer和其他方式安装的程序。
    
    参数:
        max_count: 返回的最大应用程序数量
        sort_by: 排序依据，可选值：name, version, install_date
    
    返回:
        格式化的已安装应用程序列表字符串
    """
    try:
        applications = []
        
        # 从注册表获取已安装程序
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for registry_path in registry_paths:
            try:
                # 打开注册表键
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                    # 枚举子键
                    index = 0
                    while True:
                        try:
                            # 获取子键名称
                            subkey_name = winreg.EnumKey(key, index)
                            index += 1
                            
                            # 打开子键
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    # 获取程序名称
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    if not name:
                                        continue
                                    
                                    # 获取其他信息
                                    version = "未知"
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except FileNotFoundError:
                                        pass
                                    
                                    install_date = "未知"
                                    try:
                                        install_date_str = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                        if install_date_str and len(install_date_str) == 8:
                                            date_obj = datetime.strptime(install_date_str, '%Y%m%d')
                                            install_date = date_obj.strftime('%Y-%m-%d')
                                    except (FileNotFoundError, ValueError):
                                        pass
                                    
                                    vendor = "未知"
                                    try:
                                        vendor = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except FileNotFoundError:
                                        pass
                                    
                                    # 添加到应用列表
                                    applications.append({
                                        'name': name,
                                        'version': version or "未知",
                                        'install_date': install_date,
                                        'vendor': vendor or "未知"
                                    })
                                except Exception:
                                    # 跳过无法读取的子键
                                    continue
                        except OSError:
                            # 枚举结束
                            break
            except Exception:
                # 跳过无法打开的注册表路径
                continue
        
        # 从wmic获取补充信息（确保覆盖Windows Installer安装的程序）
        try:
            result = subprocess.check_output(['wmic', 'product', 'get', 'Name,Version,InstallDate,Vendor'], 
                                           universal_newlines=True, stderr=subprocess.STDOUT)
            
            lines = result.strip().split('\n')
            if len(lines) >= 2:
                header = lines[0].strip()
                install_date_idx = header.find('InstallDate')
                name_idx = header.find('Name')
                vendor_idx = header.find('Vendor')
                version_idx = header.find('Version')
                  
                for line in lines[1:]:
                    line = line.rstrip()
                    if not line:
                        continue
                    
                    install_date = line[install_date_idx:name_idx].strip()
                    name = line[name_idx:vendor_idx].strip()
                    vendor = line[vendor_idx:version_idx].strip()
                    version = line[version_idx:].strip()
                    
                    formatted_date = "未知"
                    if install_date and len(install_date) == 8:
                        try:
                            formatted_date = f"{install_date[:4]}-{install_date[4:6]}-{install_date[6:8]}"
                        except:
                            pass
                    
                    # 检查是否已存在相同名称的应用
                    existing_app = None
                    for app in applications:
                        if app['name'] == name:
                            existing_app = app
                            break
                    
                    if existing_app:
                        # 更新现有应用的信息（如果wmic提供的信息更完整）
                        if version and existing_app['version'] == "未知":
                            existing_app['version'] = version
                        if formatted_date != "未知" and existing_app['install_date'] == "未知":
                            existing_app['install_date'] = formatted_date
                        if vendor and existing_app['vendor'] == "未知":
                            existing_app['vendor'] = vendor
                    else:
                        # 添加新应用
                        applications.append({
                            'name': name,
                            'version': version or "未知",
                            'install_date': formatted_date,
                            'vendor': vendor or "未知"
                        })
        except Exception:
            # 跳过wmic获取失败的情况
            pass
        
        # 去重（基于名称）
        unique_applications = []
        seen_names = set()
        for app in applications:
            if app['name'] not in seen_names:
                seen_names.add(app['name'])
                unique_applications.append(app)
        
        applications = unique_applications
        
        # 排序
        if sort_by in ['name', 'version', 'install_date']:
            applications.sort(key=lambda x: (x[sort_by] == "未知", x[sort_by]), reverse=True)
        
        # 限制数量
        applications = applications[:max_count]
        
        # 生成输出
        output = f"已安装的应用程序 ({len(applications)}):\n"
        for app in applications:
            output += f"- 名称: {app['name']}\n"
            output += f"  版本: {app['version']}\n"
            output += f"  安装日期: {app['install_date']}\n"
            output += f"  开发商: {app['vendor']}\n"
        
        return output
    except Exception as e:
        return f"获取已安装应用程序时出错: {str(e)}"

if __name__ == "__main__":
    # 测试函数
    print(get_installed_applications(max_count=20))