import subprocess
import winreg
import os
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
        
        # 先获取App Paths中的应用路径信息
        app_paths_dict = {}
        try:
            app_paths_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, app_paths_key) as key:
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, index)
                        index += 1
                        
                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                app_path = winreg.QueryValue(subkey, None)
                                if app_path and os.path.exists(app_path):
                                    # 使用应用名称作为键，用于后续匹配
                                    app_name = os.path.splitext(subkey_name)[0]
                                    app_paths_dict[app_name.lower()] = app_path
                        except Exception:
                            continue
                    except OSError:
                        break
        except Exception:
            pass
        
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
                                        elif install_date_str:
                                            install_date = install_date_str
                                    except (FileNotFoundError, ValueError):
                                        pass
                                    
                                    vendor = "未知"
                                    try:
                                        vendor = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except FileNotFoundError:
                                        pass
                                    
                                    # 获取应用路径
                                    app_path = "未知"
                                    try:
                                        # 尝试从Uninstall键获取路径
                                        if "InstallLocation" in [winreg.EnumValue(subkey, i)[0] for i in range(winreg.QueryInfoKey(subkey)[1])]:
                                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                            if install_location and os.path.exists(install_location):
                                                # 尝试从安装目录查找可执行文件
                                                for file in os.listdir(install_location):
                                                    if file.endswith(".exe") and name.lower() in file.lower():
                                                        app_path = os.path.join(install_location, file)
                                                        break
                                        
                                        # 如果没找到，尝试从DisplayIcon获取
                                        if app_path == "未知" and "DisplayIcon" in [winreg.EnumValue(subkey, i)[0] for i in range(winreg.QueryInfoKey(subkey)[1])]:
                                            display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                            if display_icon:
                                                # DisplayIcon可能是可执行文件路径或"路径,索引"格式
                                                if "," in display_icon:
                                                    display_icon = display_icon.split(",")[0]
                                                if os.path.exists(display_icon):
                                                    app_path = display_icon
                                        
                                        # 如果没找到，尝试从App Paths字典匹配
                                        if app_path == "未知":
                                            for app_name_key in app_paths_dict:
                                                if app_name_key in name.lower():
                                                    app_path = app_paths_dict[app_name_key]
                                                    break
                                    except Exception:
                                        pass
                                    
                                    # 添加到应用列表
                                    applications.append({
                                        'name': name,
                                        'version': version or "未知",
                                        'install_date': install_date,
                                        'vendor': vendor or "未知",
                                        'path': app_path
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
                    
                    # 获取应用路径
                    app_path = "未知"
                    for app_name_key in app_paths_dict:
                        if app_name_key in name.lower():
                            app_path = app_paths_dict[app_name_key]
                            break
                    
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
                        if app_path != "未知" and existing_app['path'] == "未知":
                            existing_app['path'] = app_path
                    else:
                        # 添加新应用
                        applications.append({
                            'name': name,
                            'version': version or "未知",
                            'install_date': formatted_date,
                            'vendor': vendor or "未知",
                            'path': app_path
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
            output += f"  路径: {app['path']}\n"
        
        return output
    except Exception as e:
        return f"获取已安装应用程序时出错: {str(e)}"

def open_application(app_name: str) -> str:
    """
    根据应用名称打开应用程序
    
    参数:
        app_name: 应用程序的名称
    
    返回:
        操作结果的字符串
    """
    try:
        # 注册表路径
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
        ]
        
        # 先尝试从App Paths查找（更直接）
        app_path = None
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_paths[2]) as key:
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, index)
                    index += 1
                    
                    # 检查子键名称是否包含应用名称
                    if app_name.lower() in subkey_name.lower():
                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                app_path = winreg.QueryValue(subkey, None)
                                if app_path and os.path.exists(app_path):
                                    break
                        except Exception:
                            continue
                except OSError:
                    break
        
        # 如果从App Paths没有找到，尝试从Uninstall路径查找
        if not app_path:
            for registry_path in registry_paths[:2]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                        index = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, index)
                                index += 1
                                
                                try:
                                    with winreg.OpenKey(key, subkey_name) as subkey:
                                        # 读取应用名称
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0] if "DisplayName" in [winreg.EnumValue(subkey, i)[0] for i in range(winreg.QueryInfoKey(subkey)[1])] else ""
                                        
                                        # 检查应用名称是否匹配
                                        if display_name and app_name.lower() in display_name.lower():
                                            # 尝试读取可执行文件路径
                                            if "InstallLocation" in [winreg.EnumValue(subkey, i)[0] for i in range(winreg.QueryInfoKey(subkey)[1])]:
                                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                                if install_location and os.path.exists(install_location):
                                                    # 尝试查找可执行文件
                                                    for file in os.listdir(install_location):
                                                        if file.endswith(".exe") and app_name.lower() in file.lower():
                                                            app_path = os.path.join(install_location, file)
                                                            break
                                            
                                            if not app_path and "DisplayIcon" in [winreg.EnumValue(subkey, i)[0] for i in range(winreg.QueryInfoKey(subkey)[1])]:
                                                display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                                if display_icon:
                                                    # DisplayIcon可能是可执行文件路径或"路径,索引"格式
                                                    if "," in display_icon:
                                                        display_icon = display_icon.split(",")[0]
                                                    if os.path.exists(display_icon):
                                                        app_path = display_icon
                                                        break
                                            
                                            if app_path:
                                                break
                                except Exception:
                                    continue
                            except OSError:
                                break
                    
                    if app_path:
                        break
                except Exception:
                    continue
        
        # 如果找到了应用路径，尝试打开它
        if app_path:
            try:
                subprocess.Popen([app_path], shell=True)
                return f"成功打开应用程序: {app_name}"
            except Exception as e:
                return f"打开应用程序失败: {str(e)}"
        else:
            # 尝试使用start命令打开（适用于系统应用）
            try:
                subprocess.Popen(["start", app_name], shell=True)
                return f"尝试使用系统命令打开应用程序: {app_name}"
            except Exception as e:
                return f"未找到应用程序: {app_name}, 或无法打开它: {str(e)}"
    except Exception as e:
        return f"执行打开应用程序操作时出错: {str(e)}"

if __name__ == "__main__":
    # 测试函数
    print(get_installed_applications(max_count=20))
    # 测试打开应用
    # print(open_application("记事本"))