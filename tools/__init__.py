#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具集合文件
将所有工具函数集中在此文件中，方便主程序统一导入
"""

# 从各个工具模块导入所有函数
from tools.windows_tools import (
    get_system_info,
    open_windows_tool,
    get_running_processes,
    check_disk_space,
    find_file,
    show_windows_version,
    get_all_windows,
    find_window_by_title,
    get_window_info,
    get_active_window,
    monitor_window_changes,
    get_window_z_order,
    bring_window_to_front,
    window_exists,
    get_window_process_info,
    close_window_by_hwnd,
    close_window_by_title
)

from tools.installed_applications_tool import get_installed_applications, open_application

from tools.file_operations import (
    create_folder,
    delete_file,
    delete_item,
    copy_file,
    move_file,
    read_text_file as read_file,
    create_text_file as write_file,
    list_directory,
    read_tutorial,
    get_desktop_path
)

from tools.mouse_keyboard_tools import (
    get_mouse_position,
    move_mouse,
    move_mouse_relative,
    click_mouse,
    right_click_mouse,
    double_click_mouse,
    drag_mouse,
    press_key,
    type_text,
    hotkey,
    scroll_mouse,
    safe_click_sequence,
    safe_type_and_click
)

from tools.visual_tools import (
    get_screen_size,
    take_screenshot,
    locate_on_screen,
    locate_all_on_screen,
    wait_for_image,
    click_on_image,
    wait_and_click_image,
    capture_screen_region,
    find_text_on_screen,
    get_screen_color_at,
    wait_for_color_change,
    # 高帧率屏幕捕获功能
    get_monitors_info,
    capture_screen_fast,
    capture_screen_region_fast,
    capture_screen_to_numpy,
    capture_region_to_numpy,
    benchmark_screen_capture,
    # OCR文本识别功能
    recognize_text_in_image,
    recognize_text_in_screen,
    recognize_text_in_region,
    real_time_text_detection
)

# 从多窗口处理模块导入函数
from tools.multi_window_processor import (
    start_multi_window_processing,
    stop_multi_window_processing,
    get_window_content,
    get_all_window_contents,
    get_active_window_content,
    get_window_processing_status
)

# 定义所有工具的集合
ALL_TOOLS = [
    # 文件操作工具（包括实用工具）
    get_desktop_path,
    # Windows系统工具
    get_system_info,
    open_windows_tool,
    get_running_processes,
    check_disk_space,
    find_file,
    show_windows_version,
    get_installed_applications,
    open_application,
    # 窗口管理工具
    get_all_windows,
    find_window_by_title,
    get_window_info,
    get_active_window,
    monitor_window_changes,
    get_window_z_order,
    bring_window_to_front,
    window_exists,
    get_window_process_info,
    close_window_by_hwnd,
    close_window_by_title,
    
    # 文件操作工具
    create_folder,
    delete_file,
    delete_item,
    copy_file,
    move_file,
    read_file,
    write_file,
    list_directory,
    
    # 教程工具
    read_tutorial,
    
    # 鼠标键盘控制工具
    get_mouse_position,
    move_mouse,
    move_mouse_relative,
    click_mouse,
    right_click_mouse,
    double_click_mouse,
    drag_mouse,
    press_key,
    type_text,
    hotkey,
    scroll_mouse,
    safe_click_sequence,
    safe_type_and_click,
    
    # 视觉工具
    get_screen_size,
    take_screenshot,
    locate_on_screen,
    locate_all_on_screen,
    wait_for_image,
    click_on_image,
    wait_and_click_image,
    capture_screen_region,
    find_text_on_screen,
    get_screen_color_at,
    wait_for_color_change,
    # 高帧率屏幕捕获功能
    get_monitors_info,
    capture_screen_fast,
    capture_screen_region_fast,
    benchmark_screen_capture,
    # OCR文本识别功能
    recognize_text_in_image,
    recognize_text_in_screen,
    recognize_text_in_region,
    real_time_text_detection,
    # 多窗口处理功能
    start_multi_window_processing,
    stop_multi_window_processing,
    get_window_content,
    get_all_window_contents,
    get_active_window_content,
    get_window_processing_status
]

# 按功能分类的工具集合
WINDOWS_TOOLS = [
    get_system_info,
    open_windows_tool,
    get_running_processes,
    check_disk_space,
    find_file,
    show_windows_version,
    get_installed_applications,
    open_application,
    # 窗口管理工具
    get_all_windows,
    find_window_by_title,
    get_window_info,
    get_active_window,
    monitor_window_changes,
    get_window_z_order,
    bring_window_to_front,
    window_exists,
    get_window_process_info,
    close_window_by_hwnd,
    close_window_by_title,
    # 多窗口处理功能
    start_multi_window_processing,
    stop_multi_window_processing,
    get_window_content,
    get_all_window_contents,
    get_active_window_content,
    get_window_processing_status
]

FILE_OPERATION_TOOLS = [
    get_desktop_path,
    create_folder,
    delete_file,
    delete_item,
    copy_file,
    move_file,
    read_file,
    write_file,
    list_directory,
    read_tutorial
]

MOUSE_KEYBOARD_TOOLS = [
    get_mouse_position,
    move_mouse,
    move_mouse_relative,
    click_mouse,
    right_click_mouse,
    double_click_mouse,
    drag_mouse,
    press_key,
    type_text,
    hotkey,
    scroll_mouse,
    safe_click_sequence,
    safe_type_and_click
]

VISUAL_TOOLS = [
    get_screen_size,
    take_screenshot,
    locate_on_screen,
    locate_all_on_screen,
    wait_for_image,
    click_on_image,
    wait_and_click_image,
    capture_screen_region,
    find_text_on_screen,
    get_screen_color_at,
    wait_for_color_change,
    # 高帧率屏幕捕获功能
    get_monitors_info,
    capture_screen_fast,
    capture_screen_region_fast,
    benchmark_screen_capture,
    # OCR文本识别功能
    recognize_text_in_image,
    recognize_text_in_screen,
    recognize_text_in_region,
    real_time_text_detection
]

# 导出所有工具以便外部使用
__all__ = [
    # 工具集合
    'ALL_TOOLS',
    'WINDOWS_TOOLS',
    'FILE_OPERATION_TOOLS',
    'MOUSE_KEYBOARD_TOOLS',
    'VISUAL_TOOLS',
    # 单个工具
    'get_system_info',
    'open_windows_tool',
    'get_running_processes',
    'check_disk_space',
    'find_file',
    'show_windows_version',
    'get_installed_applications',
    'open_application',
    # 窗口管理工具
    'get_all_windows',
    'find_window_by_title',
    'get_window_info',
    'get_active_window',
    'monitor_window_changes',
    'get_window_z_order',
    'bring_window_to_front',
    'window_exists',
    'get_window_process_info',
    'close_window_by_hwnd',
    'close_window_by_title',
    'create_folder',
    'delete_file',
    'delete_item',
    'copy_file',
    'move_file',
    'read_file',
    'write_file',
    'list_directory',
    'read_tutorial',
    'get_desktop_path',
    'get_mouse_position',
    'move_mouse',
    'move_mouse_relative',
    'click_mouse',
    'right_click_mouse',
    'double_click_mouse',
    'drag_mouse',
    'press_key',
    'type_text',
    'hotkey',
    'scroll_mouse',
    'safe_click_sequence',
    'safe_type_and_click',
    'get_screen_size',
    'take_screenshot',
    'locate_on_screen',
    'locate_all_on_screen',
    'wait_for_image',
    'click_on_image',
    'wait_and_click_image',
    'capture_screen_region',
    'find_text_on_screen',
    'get_screen_color_at',
    'wait_for_color_change',
    # 高帧率屏幕捕获功能
    'get_monitors_info',
    'capture_screen_fast',
    'capture_screen_region_fast',
    'benchmark_screen_capture',
    # OCR文本识别功能
    'recognize_text_in_image',
    'recognize_text_in_screen',
    'recognize_text_in_region',
    'real_time_text_detection',
    # 多窗口处理功能
    'start_multi_window_processing',
    'stop_multi_window_processing',
    'get_window_content',
    'get_all_window_contents',
    'get_active_window_content',
    'get_window_processing_status'
]
