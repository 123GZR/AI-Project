import os
import subprocess
import platform
from typing import List, Optional

def get_system_info() -> str:
    """获取Windows系统的基本信息"""
    try:
        # 获取操作系统信息
        os_info = platform.system() + " " + platform.version()
        # 获取计算机名称
        computer_name = os.environ.get('COMPUTERNAME', '未知')
        # 获取用户名
        username = os.environ.get('USERNAME', '未知')
        # 获取处理器信息
        try:
            cpu_info = subprocess.check_output(['wmic', 'cpu', 'get', 'name'], universal_newlines=True).strip().split('\n')[1]
        except:
            cpu_info = '无法获取'
        # 获取内存信息
        try:
            mem_info = subprocess.check_output(['wmic', 'OS', 'get', 'TotalVisibleMemorySize'], universal_newlines=True).strip().split('\n')[1]
            mem_gb = round(int(mem_info) / 1024 / 1024, 2)
            mem_info = f"{mem_gb} GB"
        except:
            mem_info = '无法获取'
        
        return f"系统信息：\n操作系统: {os_info}\n计算机名称: {computer_name}\n用户名: {username}\n处理器: {cpu_info}\n内存: {mem_info}"
    except Exception as e:
        return f"获取系统信息时出错: {str(e)}"

def open_windows_tool(tool_name: str) -> str:
    """打开Windows系统工具
    
    参数:
        tool_name: 工具名称，支持以下值:
            - 'taskmanager': 任务管理器
            - 'controlpanel': 控制面板
            - 'fileexplorer': 文件资源管理器
            - 'cmd': 命令提示符
            - 'powershell': PowerShell
            - 'systeminfo': 系统信息
            - 'diskmgmt': 磁盘管理
            - 'device': 设备管理器
    """
    tool_map = {
        'taskmanager': 'taskmgr',
        'controlpanel': 'control',
        'fileexplorer': 'explorer',
        'cmd': 'cmd',
        'powershell': 'powershell',
        'systeminfo': 'msinfo32',
        'diskmgmt': 'diskmgmt.msc',
        'device': 'devmgmt.msc'
    }
    
    if tool_name.lower() not in tool_map:
        supported_tools = ', '.join(tool_map.keys())
        return f"不支持的工具名称。支持的工具: {supported_tools}"
    
    try:
        subprocess.Popen(tool_map[tool_name.lower()])
        return f"已成功打开 {tool_name} 工具"
    except Exception as e:
        return f"打开 {tool_name} 工具时出错: {str(e)}"

def get_running_processes(max_count: int = 20) -> str:
    """获取当前运行的进程列表
    
    参数:
        max_count: 返回的最大进程数量，默认20个
    """
    try:
        # 使用wmic获取进程列表
        result = subprocess.check_output(['wmic', 'process', 'get', 'Name,ProcessId,WorkingSetSize'], universal_newlines=True)
        lines = result.strip().split('\n')[1:]  # 跳过标题行
        
        processes = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                name = ' '.join(parts[:-2])
                pid = parts[-2]
                memory_mb = round(int(parts[-1]) / 1024 / 1024, 2)
                processes.append(f"进程名: {name}, PID: {pid}, 内存: {memory_mb} MB")
        
        # 按内存使用量排序并限制数量
        processes = processes[:max_count]
        
        return f"当前运行的进程 ({len(processes)}):\n" + "\n".join(processes)
    except Exception as e:
        return f"获取进程列表时出错: {str(e)}"

def check_disk_space() -> str:
    """检查磁盘空间使用情况"""
    try:
        result = subprocess.check_output(['wmic', 'logicaldisk', 'get', 'DeviceID,Size,FreeSpace'], universal_newlines=True)
        lines = result.strip().split('\n')[1:]  # 跳过标题行
        
        disk_info = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                drive = parts[0]
                free_space = int(parts[1])
                total_size = int(parts[2])
                
                # 转换为GB
                free_gb = round(free_space / 1024 / 1024 / 1024, 2)
                total_gb = round(total_size / 1024 / 1024 / 1024, 2)
                used_gb = total_gb - free_gb
                usage_percent = round((used_gb / total_gb) * 100, 1)
                
                disk_info.append(f"驱动器 {drive}: 总计 {total_gb} GB, 已用 {used_gb} GB, 可用 {free_gb} GB ({usage_percent}%)")
        
        return f"磁盘空间使用情况:\n" + "\n".join(disk_info)
    except Exception as e:
        return f"检查磁盘空间时出错: {str(e)}"

def find_file(file_name: str, search_path: str = "C:") -> str:
    """在指定路径下搜索文件
    
    参数:
        file_name: 要搜索的文件名（支持通配符，如*.txt）
        search_path: 搜索的起始路径，默认为C盘
    """
    if not os.path.isdir(search_path):
        return f"搜索路径 '{search_path}' 不存在或不是有效的目录"
    
    try:
        # 使用where命令搜索文件（Windows专用）
        command = f'where /r "{search_path}" "{file_name}"'
        result = subprocess.check_output(command, shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
        
        files = result.strip().split('\n')
        if files and files[0]:  # 确保有结果
            return f"找到 {len(files)} 个匹配的文件:\n" + "\n".join(files)
        else:
            return f"在 '{search_path}' 下未找到匹配 '{file_name}' 的文件"
    except subprocess.CalledProcessError as e:
        # where命令在没有找到文件时会返回错误码
        if e.returncode == 1:
            return f"在 '{search_path}' 下未找到匹配 '{file_name}' 的文件"
        return f"搜索文件时出错: {str(e)}"
    except Exception as e:
        return f"搜索文件时出错: {str(e)}"

def show_windows_version() -> str:
    """显示详细的Windows版本信息"""
    try:
        result = subprocess.check_output(['winver', '/?'], shell=True, universal_newlines=True, stderr=subprocess.STDOUT)
        # 由于winver会打开图形界面，我们使用systeminfo命令获取版本信息
        system_info = subprocess.check_output(['systeminfo'], universal_newlines=True)
        
        # 提取版本相关信息
        version_info = []
        for line in system_info.split('\n'):
            if any(keyword in line for keyword in ['OS Name', 'OS Version', 'System Type', 'Hotfix(s)']):
                version_info.append(line.strip())
        
        return f"Windows版本信息:\n" + "\n".join(version_info)
    except Exception as e:
        return f"获取Windows版本信息时出错: {str(e)}"