# 实现AI系统操作前确认机制

## 1. 设计思路
- 使用装饰器模式为需要确认的工具函数添加操作前确认逻辑
- 装饰器将在函数执行前向用户显示操作详情，并等待用户确认
- 只有用户输入"yes"时才执行实际操作，否则取消操作

## 2. 实现步骤

### 2.1 创建装饰器函数
- 在tools目录下创建一个新文件`confirmation_decorator.py`
- 实现`require_confirmation`装饰器，该装饰器：
  - 接收函数参数并生成清晰的操作描述
  - 向用户显示操作详情，等待用户输入
  - 只有用户输入"yes"时才执行原函数，否则返回取消信息

### 2.2 识别需要确认的工具函数
需要确认的操作包括：
- **文件操作**：delete_file, delete_item, move_file, create_text_file, write_file
- **窗口操作**：close_window, move_window, resize_window, minimize_window, maximize_window, restore_window, activate_window, set_window_always_on_top
- **应用程序操作**：open_application, open_application_by_path
- **鼠标键盘操作**：move_mouse, click_mouse, right_click_mouse, double_click_mouse, drag_mouse, press_key, type_text, hotkey, scroll_mouse, safe_click_sequence, safe_type_and_click
- **Windows系统操作**：open_windows_tool

### 2.3 应用装饰器
- 修改各个工具模块文件，导入并应用装饰器
- 为需要确认的工具函数添加`@require_confirmation`装饰器

### 2.4 测试和验证
- 确保装饰器能够正确处理不同类型的函数参数
- 验证确认流程正常工作
- 确保取消操作时能够正确返回取消信息

## 3. 实现细节

### 3.1 装饰器实现
```python
def require_confirmation(func):
    """操作前确认装饰器"""
    async def wrapper(*args, **kwargs):
        # 生成操作描述
        operation_desc = f"即将执行：{func.__name__}"
        if args or kwargs:
            operation_desc += f"\n参数：{args} {kwargs}"
        
        # 显示操作详情并等待用户确认
        print(f"\n[操作确认] {operation_desc}")
        print("是否继续执行？(输入yes确认，其他内容取消)")
        
        confirmation = input("您的选择：").strip().lower()
        if confirmation != "yes":
            return f"操作已取消：{func.__name__}"
        
        # 执行原函数
        return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    
    return wrapper
```

### 3.2 应用示例
```python
@require_confirmation
def delete_file(file_path: str) -> str:
    # 原函数实现
    pass
```

## 4. 预期效果
- 当AI尝试执行删除文件、移动窗口等操作时，会先显示操作详情
- 用户需要明确输入"yes"才能继续执行
- 任何其他输入都会导致操作取消
- 确认流程清晰、直观，提高了系统操作的安全性