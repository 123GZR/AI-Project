import os
import subprocess
import platform
import time
from typing import List, Optional, Dict, Any
import pygetwindow as gw
import win32gui
import win32process
import win32con

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


# 窗口管理功能

def get_all_windows() -> Dict[str, Any]:
    """获取所有窗口信息
    
    返回:
        包含所有窗口信息的字典
    """
    try:
        windows = gw.getAllWindows()
        result = {}
        
        for i, window in enumerate(windows):
            if window.visible:
                try:
                    result[f"window_{i}"] = {
                        "title": window.title,
                        "hwnd": window._hWnd,
                        "x": window.left,
                        "y": window.top,
                        "width": window.width,
                        "height": window.height,
                        "visible": window.visible,
                        "active": window.isActive,
                        "z_order": i
                    }
                except Exception as e:
                    continue
        
        return {
            "status": "success",
            "windows": result,
            "total_windows": len(result)
        }
    except Exception as e:
        return f"获取所有窗口信息时出错: {str(e)}"


def find_window_by_title(title: str, exact_match: bool = False) -> Dict[str, Any]:
    """根据标题查找窗口
    
    参数:
        title: 窗口标题
        exact_match: 是否精确匹配
    
    返回:
        包含查找结果的字典
    """
    try:
        if exact_match:
            window = gw.getWindowsWithTitle(title)
            window = [w for w in window if w.title == title]
        else:
            window = gw.getWindowsWithTitle(title)
        
        matches = []
        for i, w in enumerate(window):
            matches.append({
                "title": w.title,
                "hwnd": w._hWnd,
                "x": w.left,
                "y": w.top,
                "width": w.width,
                "height": w.height,
                "visible": w.visible,
                "active": w.isActive
            })
        
        return {
            "status": "success",
            "matches": matches,
            "total_matches": len(matches),
            "search_title": title,
            "exact_match": exact_match
        }
    except Exception as e:
        return f"根据标题查找窗口时出错: {str(e)}"


def get_window_info(hwnd: int) -> Dict[str, Any]:
    """获取窗口详细信息
    
    参数:
        hwnd: 窗口句柄
    
    返回:
        包含窗口详细信息的字典
    """
    try:
        window = gw.getWindowsWithHWND(hwnd)
        if not window:
            return f"未找到句柄为 {hwnd} 的窗口"
        
        window = window[0]
        
        # 获取进程ID
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # 获取窗口类名
        class_name = win32gui.GetClassName(hwnd)
        
        # 获取窗口样式
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        
        return {
            "status": "success",
            "window_info": {
                "title": window.title,
                "hwnd": hwnd,
                "pid": pid,
                "tid": tid,
                "class_name": class_name,
                "style": style,
                "x": window.left,
                "y": window.top,
                "width": window.width,
                "height": window.height,
                "visible": window.visible,
                "active": window.isActive
            }
        }
    except Exception as e:
        return f"获取窗口详细信息时出错: {str(e)}"


def get_active_window() -> Dict[str, Any]:
    """获取当前活动窗口
    
    返回:
        包含当前活动窗口信息的字典
    """
    try:
        window = gw.getActiveWindow()
        if not window:
            return "当前没有活动窗口"
        
        return {
            "status": "success",
            "active_window": {
                "title": window.title,
                "hwnd": window._hWnd,
                "x": window.left,
                "y": window.top,
                "width": window.width,
                "height": window.height,
                "visible": window.visible
            }
        }
    except Exception as e:
        return f"获取当前活动窗口时出错: {str(e)}"


def monitor_window_changes(duration: float = 5.0, check_interval: float = 0.5) -> Dict[str, Any]:
    """监控窗口状态变化
    
    参数:
        duration: 监控持续时间（秒）
        check_interval: 检查间隔（秒）
    
    返回:
        包含监控结果的字典
    """
    try:
        start_time = time.time()
        initial_windows = get_all_windows()
        if isinstance(initial_windows, str):
            return initial_windows
        
        changes = []
        window_history = {}
        
        # 初始化窗口历史
        for win_id, win_info in initial_windows["windows"].items():
            window_history[win_info["hwnd"]] = win_info
        
        while time.time() - start_time < duration:
            current_windows = get_all_windows()
            if isinstance(current_windows, str):
                continue
            
            current_window_hwnds = set()
            
            # 检查现有窗口的变化
            for win_id, win_info in current_windows["windows"].items():
                hwnd = win_info["hwnd"]
                current_window_hwnds.add(hwnd)
                
                if hwnd in window_history:
                    # 检查窗口状态变化
                    old_info = window_history[hwnd]
                    
                    # 检查位置变化
                    if (win_info["x"] != old_info["x"] or win_info["y"] != old_info["y"]):
                        changes.append({
                            "type": "move",
                            "hwnd": hwnd,
                            "title": win_info["title"],
                            "old_position": {"x": old_info["x"], "y": old_info["y"]},
                            "new_position": {"x": win_info["x"], "y": win_info["y"]},
                            "timestamp": time.time()
                        })
                    
                    # 检查大小变化
                    if (win_info["width"] != old_info["width"] or win_info["height"] != old_info["height"]):
                        changes.append({
                            "type": "resize",
                            "hwnd": hwnd,
                            "title": win_info["title"],
                            "old_size": {"width": old_info["width"], "height": old_info["height"]},
                            "new_size": {"width": win_info["width"], "height": win_info["height"]},
                            "timestamp": time.time()
                        })
                    
                    # 检查激活状态变化
                    if (win_info["active"] != old_info["active"]):
                        changes.append({
                            "type": "activate" if win_info["active"] else "deactivate",
                            "hwnd": hwnd,
                            "title": win_info["title"],
                            "timestamp": time.time()
                        })
                
                # 更新窗口历史
                window_history[hwnd] = win_info
            
            # 检查新创建的窗口
            for hwnd in current_window_hwnds:
                if hwnd not in window_history:
                    changes.append({
                        "type": "create",
                        "hwnd": hwnd,
                        "title": current_windows["windows"][f"window_{list(current_windows['windows'].keys()).index(win_id)}"]["title"],
                        "timestamp": time.time()
                    })
            
            # 检查关闭的窗口
            for hwnd in list(window_history.keys()):
                if hwnd not in current_window_hwnds:
                    changes.append({
                        "type": "close",
                        "hwnd": hwnd,
                        "title": window_history[hwnd]["title"],
                        "timestamp": time.time()
                    })
                    del window_history[hwnd]
            
            time.sleep(check_interval)
        
        return {
            "status": "success",
            "changes": changes,
            "total_changes": len(changes),
            "monitor_duration": duration,
            "check_interval": check_interval
        }
    except Exception as e:
        return f"监控窗口状态变化时出错: {str(e)}"


def get_window_z_order() -> Dict[str, Any]:
    """获取窗口Z-order（堆叠顺序）
    
    返回:
        包含窗口Z-order信息的字典
    """
    try:
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "z_order": len(windows)
                    })
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        return {
            "status": "success",
            "windows_z_order": windows,
            "total_windows": len(windows)
        }
    except Exception as e:
        return f"获取窗口Z-order时出错: {str(e)}"


def bring_window_to_front(hwnd: int) -> str:
    """将窗口置顶
    
    参数:
        hwnd: 窗口句柄
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return f"已将句柄为 {hwnd} 的窗口置顶"
    except Exception as e:
        return f"将窗口置顶时出错: {str(e)}"


def window_exists(hwnd: int) -> Dict[str, Any]:
    """检查窗口是否存在
    
    参数:
        hwnd: 窗口句柄
    
    返回:
        包含检查结果的字典
    """
    try:
        exists = win32gui.IsWindow(hwnd)
        return {
            "status": "success",
            "exists": exists,
            "hwnd": hwnd
        }
    except Exception as e:
        return f"检查窗口是否存在时出错: {str(e)}"


def get_window_process_info(hwnd: int) -> Dict[str, Any]:
    """获取窗口所属进程信息
    
    参数:
        hwnd: 窗口句柄
    
    返回:
        包含进程信息的字典
    """
    try:
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # 获取进程名
        try:
            import psutil
            process = psutil.Process(pid)
            process_name = process.name()
            process_path = process.exe()
            process_cmdline = " ".join(process.cmdline())
        except Exception as e:
            process_name = "未知"
            process_path = "未知"
            process_cmdline = "未知"
        
        return {
            "status": "success",
            "process_info": {
                "hwnd": hwnd,
                "pid": pid,
                "tid": tid,
                "process_name": process_name,
                "process_path": process_path,
                "process_cmdline": process_cmdline
            }
        }
    except Exception as e:
        return f"获取窗口所属进程信息时出错: {str(e)}"


def close_window_by_hwnd(hwnd: int) -> str:
    """通过窗口句柄关闭窗口
    
    参数:
        hwnd: 窗口句柄
    """
    try:
        # 检查窗口是否存在
        if not win32gui.IsWindow(hwnd):
            return f"窗口句柄 {hwnd} 无效或窗口已关闭"
        
        # 发送关闭消息
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return f"已向窗口句柄 {hwnd} 发送关闭消息"
    except Exception as e:
        return f"关闭窗口时出错: {str(e)}"


def close_window_by_title(title: str, exact_match: bool = False) -> str:
    """通过标题关闭窗口
    
    参数:
        title: 窗口标题
        exact_match: 是否精确匹配
    """
    try:
        # 查找匹配的窗口
        from .__init__ import find_window_by_title
        result = find_window_by_title(title, exact_match)
        
        if isinstance(result, str):
            return result
        
        matches = result.get("matches", [])
        if not matches:
            return f"未找到标题包含 '{title}' 的窗口"
        
        # 关闭所有匹配的窗口
        closed_count = 0
        for match in matches:
            hwnd = match["hwnd"]
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            closed_count += 1
        
        return f"已成功关闭 {closed_count} 个标题{'精确' if exact_match else '包含'} '{title}' 的窗口"
    except Exception as e:
        return f"通过标题关闭窗口时出错: {str(e)}"


