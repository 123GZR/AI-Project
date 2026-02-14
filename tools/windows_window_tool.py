#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows窗口管理工具
提供获取窗口信息和操作窗口的功能
"""

import pygetwindow as gw
import win32gui
import win32con
from typing import List, Dict, Any, Optional

# 重要窗口列表，避免误操作
IMPORTANT_WINDOWS = [
    "explorer",  # 文件资源管理器
    "Task Manager",  # 任务管理器
    "cmd.exe",  # 命令提示符
    "powershell.exe",  # PowerShell
    "python.exe",  # Python解释器
    "系统设置",  # Windows设置
    "控制面板",  # 控制面板
    "Microsoft Edge",  # Edge浏览器
    "Chrome",  # Chrome浏览器
    "Firefox",  # Firefox浏览器
    "Discord",  # Discord
    "Steam",  # Steam
    "VS Code",  # VS Code
    "PyCharm",  # PyCharm
    "IntelliJ IDEA",  # IntelliJ IDEA
    "Notepad++",  # Notepad++
    "记事本",  # 记事本
    "写字板",  # 写字板
    "Excel",  # Excel
    "Word",  # Word
    "PowerPoint",  # PowerPoint
    "Outlook",  # Outlook
    "Teams",  # Teams
    "Zoom"  # Zoom
]

# 忽略窗口列表，这些窗口将不被返回给用户
IGNORE_WINDOWS = [
    "开始",  # 开始菜单
]

# 忽略的进程列表
IGNORE_PROCESSES = [
    "ShellExperienceHost.exe",  # 壳体验宿主
    "StartMenuExperienceHost.exe",  # 开始菜单体验宿主
]


def get_all_windows() -> List[Dict[str, Any]]:
    """
    获取系统中所有用户可见的应用程序窗口信息
    
    Returns:
        List[Dict[str, Any]]: 包含所有可见应用程序窗口信息的列表，每个窗口信息包含：
            - window_id: 窗口ID
            - title: 窗口标题
            - position: 窗口位置 (x, y)
            - size: 窗口大小 (width, height)
            - is_minimized: 是否最小化
            - is_maximized: 是否最大化
            - is_active: 是否为活动窗口
            - process_name: 进程名称（如果可获取）
    """
    windows = []
    try:
        # 获取所有窗口
        all_windows = gw.getAllWindows()
        
        # 获取所有活动进程的PID集合
        active_pids = set()
        try:
            import psutil
            active_pids = {p.pid for p in psutil.process_iter(['pid', 'status']) if p.info['status'] in ['running', 'sleeping']}
        except Exception:
            pass
        
        for window in all_windows:
            try:
                # 严格过滤条件：只返回真正的应用程序窗口
                
                # 1. 跳过不可见的窗口
                if not window.visible:
                    continue
                
                # 2. 跳过标题为空的窗口（系统窗口、托盘等）
                if not window.title or window.title.strip() == "":
                    continue
                
                # 3. 跳过尺寸过小的窗口（通常是系统组件）
                if window.width <= 10 or window.height <= 10:
                    continue
                
                # 4. 跳过特定的系统窗口
                sys_window_titles = [
                    "Program Manager",  # 桌面
                    "Microsoft Text Input Application",  # 输入法
                    "Windows Input Experience"
                ]
                if window.title in sys_window_titles:
                    continue
                
                # 5. 跳过用户配置的忽略窗口
                if any(ignore_title in window.title for ignore_title in IGNORE_WINDOWS):
                    continue
                
                # 6. 跳过屏幕外窗口
                if window.left < -1000 or window.top < -1000:
                    continue
                
                # 7. 检查窗口是否为真正的顶级窗口（避免子窗口）
                try:
                    parent = win32gui.GetParent(window._hWnd)
                    if parent != 0:
                        continue
                except Exception:
                    pass
                
                # 8. 检查窗口对应的进程是否活跃
                try:
                    import win32process
                    _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
                    if pid not in active_pids:
                        continue
                except Exception:
                    pass
                
                # 9. 检查窗口是否真的存在（避免残留句柄）
                try:
                    # 使用win32gui验证窗口是否真的存在且可访问
                    if not win32gui.IsWindow(window._hWnd):
                        continue
                    
                    # 检查窗口是否可见（双重验证）
                    if not win32gui.IsWindowVisible(window._hWnd):
                        continue
                    
                    # 检查窗口是否启用
                    if not win32gui.IsWindowEnabled(window._hWnd):
                        continue
                except Exception:
                    pass
                
                # 10. 检查进程是否在忽略列表中
                process_name = ""
                try:
                    import psutil
                    import win32process
                    _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
                    process = psutil.Process(pid)
                    process_name = process.name()
                    
                    # 跳过忽略的进程
                    if process_name in IGNORE_PROCESSES:
                        continue
                except Exception:
                    pass
                
                # 获取窗口状态
                window_info = {
                    "window_id": window._hWnd,
                    "title": window.title,
                    "position": (window.left, window.top),
                    "size": (window.width, window.height),
                    "is_minimized": window.isMinimized,
                    "is_maximized": window.isMaximized,
                    "is_active": window.isActive,
                    "process_name": process_name
                }
                
                windows.append(window_info)
            except Exception as e:
                # 跳过无法访问的窗口
                continue
        
        return windows
    except Exception as e:
        return [{"error": f"获取窗口信息失败: {str(e)}"}]


def get_active_window() -> Dict[str, Any]:
    """
    获取当前活动窗口的信息
    
    Returns:
        Dict[str, Any]: 包含活动窗口信息的字典
    """
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return {
                "window_id": active_window._hWnd,
                "title": active_window.title,
                "position": (active_window.left, active_window.top),
                "size": (active_window.width, active_window.height),
                "is_minimized": active_window.isMinimized,
                "is_maximized": active_window.isMaximized,
                "is_active": True
            }
        return {"error": "没有找到活动窗口"}
    except Exception as e:
        return {"error": f"获取活动窗口失败: {str(e)}"}


def find_window_by_title(title: str) -> Optional[gw.Win32Window]:
    """
    根据标题查找窗口
    
    Args:
        title (str): 窗口标题（支持部分匹配）
    
    Returns:
        Optional[gw.Win32Window]: 找到的窗口对象，否则返回None
    """
    try:
        return gw.getWindowsWithTitle(title)[0]
    except Exception:
        return None


def find_window_by_id(window_id: int) -> Optional[gw.Win32Window]:
    """
    根据窗口ID查找窗口
    
    Args:
        window_id (int): 窗口ID
    
    Returns:
        Optional[gw.Win32Window]: 找到的窗口对象，否则返回None
    """
    try:
        return gw.Window(window_id)
    except Exception:
        return None


def is_important_window(title: str) -> bool:
    """
    检查窗口是否为重要窗口
    
    Args:
        title (str): 窗口标题
    
    Returns:
        bool: 如果是重要窗口返回True，否则返回False
    """
    for important_window in IMPORTANT_WINDOWS:
        if important_window.lower() in title.lower():
            return True
    return False


def move_window(window_id: Optional[int] = None, title: Optional[str] = None, x: int = 0, y: int = 0) -> Dict[str, Any]:
    """
    移动窗口到指定位置
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
        x (int): 目标X坐标
        y (int): 目标Y坐标
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 移动窗口
        window.moveTo(x, y)
        return {
            "success": True,
            "message": f"窗口已移动到 ({x}, {y})",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"移动窗口失败: {str(e)}"}


def resize_window(window_id: Optional[int] = None, title: Optional[str] = None, width: int = 800, height: int = 600) -> Dict[str, Any]:
    """
    调整窗口大小
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
        width (int): 目标宽度
        height (int): 目标高度
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 调整窗口大小
        window.resizeTo(width, height)
        return {
            "success": True,
            "message": f"窗口已调整大小为 ({width}, {height})",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"调整窗口大小失败: {str(e)}"}


def minimize_window(window_id: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    最小化窗口
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 最小化窗口
        window.minimize()
        return {
            "success": True,
            "message": "窗口已最小化",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"最小化窗口失败: {str(e)}"}


def maximize_window(window_id: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    最大化窗口
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 最大化窗口
        window.maximize()
        return {
            "success": True,
            "message": "窗口已最大化",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"最大化窗口失败: {str(e)}"}


def restore_window(window_id: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    恢复窗口（从最小化或最大化状态）
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 恢复窗口
        window.restore()
        return {
            "success": True,
            "message": "窗口已恢复",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"恢复窗口失败: {str(e)}"}


def activate_window(window_id: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    激活窗口（将窗口置于前台）
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 激活窗口
        window.activate()
        return {
            "success": True,
            "message": "窗口已激活",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"激活窗口失败: {str(e)}"}


def close_window(window_id: Optional[int] = None, title: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
    """
    关闭窗口
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
        force (bool): 是否强制关闭，如果为False则会检查是否为重要窗口
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 检查是否为重要窗口
        if is_important_window(window.title) and not force:
            return {
                "error": f"'{window.title}' 是重要窗口，如需关闭请使用force=True参数",
                "is_important": True
            }
        
        # 关闭窗口
        window.close()
        return {
            "success": True,
            "message": f"窗口 '{window.title}' 已关闭",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"关闭窗口失败: {str(e)}"}


def get_window_by_process(process_name: str) -> List[Dict[str, Any]]:
    """
    根据进程名称获取窗口列表
    
    Args:
        process_name (str): 进程名称，如 "chrome.exe"
    
    Returns:
        List[Dict[str, Any]]: 匹配的窗口列表
    """
    try:
        all_windows = get_all_windows()
        return [window for window in all_windows if window.get("process_name", "").lower() == process_name.lower()]
    except Exception as e:
        return [{"error": f"根据进程获取窗口失败: {str(e)}"}]


def get_window_by_title_pattern(pattern: str) -> List[Dict[str, Any]]:
    """
    根据标题模式匹配窗口
    
    Args:
        pattern (str): 标题模式，支持部分匹配
    
    Returns:
        List[Dict[str, Any]]: 匹配的窗口列表
    """
    try:
        all_windows = get_all_windows()
        return [window for window in all_windows if pattern.lower() in window.get("title", "").lower()]
    except Exception as e:
        return [{"error": f"根据标题模式获取窗口失败: {str(e)}"}]


def set_window_always_on_top(window_id: Optional[int] = None, title: Optional[str] = None, on_top: bool = True) -> Dict[str, Any]:
    """
    设置窗口是否总是置顶
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
        on_top (bool): 是否置顶，默认为True
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 设置窗口置顶
        hwnd = window._hWnd
        if on_top:
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
        else:
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
        
        return {
            "success": True,
            "message": f"窗口已{'设置为' if on_top else '取消'}总是置顶",
            "window_title": window.title
        }
    except Exception as e:
        return {"error": f"设置窗口置顶失败: {str(e)}"}


def get_window_state(window_id: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    获取窗口状态
    
    Args:
        window_id (Optional[int]): 窗口ID，如果不提供则使用title查找
        title (Optional[str]): 窗口标题，如果不提供则使用window_id
    
    Returns:
        Dict[str, Any]: 窗口状态信息
    """
    try:
        # 查找窗口
        window = None
        if window_id:
            window = find_window_by_id(window_id)
        elif title:
            window = find_window_by_title(title)
        
        if not window:
            return {"error": "未找到指定窗口"}
        
        # 获取窗口状态
        return {
            "window_id": window._hWnd,
            "title": window.title,
            "position": (window.left, window.top),
            "size": (window.width, window.height),
            "is_minimized": window.isMinimized,
            "is_maximized": window.isMaximized,
            "is_active": window.isActive,
            "is_visible": window.visible
        }
    except Exception as e:
        return {"error": f"获取窗口状态失败: {str(e)}"}
