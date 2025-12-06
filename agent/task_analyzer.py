def analyze_task_type(user_input):
    """分析用户输入的任务类型，推断隐含意图，并返回对应的工具调用建议"""
    user_input_lower = user_input.lower()
    
    # 任务类型和工具映射
    task_type_mapping = {
        # 窗口操作相关（新增）
        'window_operation': {
            'keywords': ['关闭窗口', '打开窗口', '最小化', '最大化', '激活窗口', '切换窗口'],
            'tools': ['get_all_windows', 'find_window_by_title', 'get_window_info', 'get_active_window', 'close_window_by_title', 'close_window_by_hwnd']
        },
        # 系统信息相关
        'system_info': {
            'keywords': ['系统信息', 'windows版本', '已安装软件', '进程', '磁盘空间'],
            'tools': ['get_system_info', 'show_windows_version', 'get_installed_applications', 'get_running_processes', 'check_disk_space']
        },
        # 文件操作相关
        'file_operation': {
            'keywords': ['查找文件', '创建文件夹', '删除文件', '复制文件', '移动文件', '读取文件', '写入文件'],
            'tools': ['find_file', 'create_folder', 'delete_file', 'copy_file', 'move_file', 'read_file', 'write_file']
        },
        # 键鼠操作相关
        'mouse_keyboard': {
            'keywords': ['鼠标位置', '移动鼠标', '点击', '双击', '右键', '拖动', '按键', '输入文本', '组合键'],
            'tools': ['get_mouse_position', 'move_mouse', 'click_mouse', 'double_click_mouse', 'right_click_mouse', 'drag_mouse', 'press_key', 'type_text', 'hotkey']
        },
        # 视觉操作相关
        'visual_operation': {
            'keywords': ['截图', '屏幕尺寸', '查找图像', '等待图像', '点击图像', '屏幕颜色', '查找文本'],
            'tools': ['take_screenshot', 'get_screen_size', 'locate_on_screen', 'wait_for_image', 'click_on_image', 'get_screen_color_at', 'find_text_on_screen']
        },
        # 应用程序操作相关
        'application_operation': {
            'keywords': ['打开应用', '启动程序', '运行工具'],
            'tools': ['open_application', 'open_windows_tool']
        }
    }
    
    # 遍历所有任务类型，寻找匹配的关键词
    for task_type, config in task_type_mapping.items():
        for keyword in config['keywords']:
            if keyword in user_input_lower:
                return task_type, config['tools'], []
    
    # 特殊任务识别
    # 1. 识别窗口关闭任务
    if '关闭' in user_input_lower and ('窗口' in user_input_lower or '应用' in user_input_lower):
        return 'window_operation', ['find_window_by_title', 'close_window_by_title', 'close_window_by_hwnd'], []
    
    # 2. 识别需要组合工具的任务
    if '自动' in user_input_lower and ('操作' in user_input_lower or '完成' in user_input_lower):
        # 自动操作任务，可能需要多种工具组合
        return 'automated_operation', ['get_all_windows', 'find_window_by_title', 'click_mouse', 'type_text', 'hotkey'], []
    
    # 3. 识别需要视觉+键鼠组合的任务
    if ('点击' in user_input_lower and '图像' in user_input_lower) or '视觉' in user_input_lower:
        return 'visual_mouse_operation', ['locate_on_screen', 'click_on_image', 'wait_for_image'], []
    
    # 默认返回通用帮助类型，但包含更多可能有用的工具
    return 'general_help', ['get_system_info', 'check_disk_space', 'get_all_windows', 'find_window_by_title'], []
