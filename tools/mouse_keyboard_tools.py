import pyautogui
import time
from typing import Optional, Tuple, List

# 设置pyautogui的安全功能
pyautogui.FAILSAFE = True  # 启用故障安全，将鼠标移动到屏幕左上角可以中断操作
pyautogui.PAUSE = 0.1  # 每个操作之间的暂停时间（秒）

def get_mouse_position() -> str:
    """获取当前鼠标位置"""
    try:
        x, y = pyautogui.position()
        return f"当前鼠标位置: X={x}, Y={y}"
    except Exception as e:
        return f"获取鼠标位置时出错: {str(e)}"

def move_mouse(x: int, y: int, duration: float = 0.2) -> str:
    """移动鼠标到指定位置
    
    参数:
        x: 目标X坐标
        y: 目标Y坐标
        duration: 移动持续时间（秒）
    """
    try:
        screen_width, screen_height = pyautogui.size()
        # 检查坐标是否在屏幕范围内
        if x < 0 or x > screen_width or y < 0 or y > screen_height:
            return f"坐标 ({x}, {y}) 超出屏幕范围 (0,0) 到 ({screen_width},{screen_height})"
        
        pyautogui.moveTo(x, y, duration=duration)
        return f"鼠标已移动到位置: X={x}, Y={y}"
    except Exception as e:
        return f"移动鼠标时出错: {str(e)}"

def move_mouse_relative(dx: int, dy: int, duration: float = 0.2) -> str:
    """相对当前位置移动鼠标
    
    参数:
        dx: X方向相对移动距离
        dy: Y方向相对移动距离
        duration: 移动持续时间（秒）
    """
    try:
        pyautogui.moveRel(dx, dy, duration=duration)
        new_x, new_y = pyautogui.position()
        return f"鼠标已相对移动 (dx={dx}, dy={dy})，新位置: X={new_x}, Y={new_y}"
    except Exception as e:
        return f"相对移动鼠标时出错: {str(e)}"

def click_mouse(x: Optional[int] = None, y: Optional[int] = None, button: str = 'left', clicks: int = 1) -> str:
    """点击鼠标
    
    参数:
        x: 点击位置X坐标（可选，不提供则在当前位置点击）
        y: 点击位置Y坐标（可选，不提供则在当前位置点击）
        button: 按钮类型 ('left', 'right', 'middle')
        clicks: 点击次数
    """
    try:
        if x is not None and y is not None:
            # 检查坐标是否有效
            screen_width, screen_height = pyautogui.size()
            if x < 0 or x > screen_width or y < 0 or y > screen_height:
                return f"坐标 ({x}, {y}) 超出屏幕范围"
            
            pyautogui.click(x, y, clicks=clicks, button=button)
            return f"已在位置 ({x}, {y}) {button}键点击 {clicks} 次"
        else:
            # 在当前位置点击
            current_x, current_y = pyautogui.position()
            pyautogui.click(clicks=clicks, button=button)
            return f"已在当前位置 ({current_x}, {current_y}) {button}键点击 {clicks} 次"
    except Exception as e:
        return f"点击鼠标时出错: {str(e)}"

def right_click_mouse(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """右键点击鼠标
    
    参数:
        x: 点击位置X坐标（可选）
        y: 点击位置Y坐标（可选）
    """
    return click_mouse(x, y, button='right')

def double_click_mouse(x: Optional[int] = None, y: Optional[int] = None) -> str:
    """双击鼠标左键
    
    参数:
        x: 点击位置X坐标（可选）
        y: 点击位置Y坐标（可选）
    """
    return click_mouse(x, y, clicks=2)

def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5, button: str = 'left') -> str:
    """拖动鼠标
    
    参数:
        start_x: 起始位置X坐标
        start_y: 起始位置Y坐标
        end_x: 结束位置X坐标
        end_y: 结束位置Y坐标
        duration: 拖动持续时间（秒）
        button: 按下的按钮 ('left', 'right', 'middle')
    """
    try:
        # 检查坐标是否有效
        screen_width, screen_height = pyautogui.size()
        if (start_x < 0 or start_x > screen_width or start_y < 0 or start_y > screen_height or
            end_x < 0 or end_x > screen_width or end_y < 0 or end_y > screen_height):
            return "起始或结束坐标超出屏幕范围"
        
        # 先移动到起始位置
        pyautogui.moveTo(start_x, start_y)
        # 然后拖动
        pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        return f"鼠标已从 ({start_x}, {start_y}) 拖动到 ({end_x}, {end_y})"
    except Exception as e:
        return f"拖动鼠标时出错: {str(e)}"

def press_key(key: str) -> str:
    """按下并释放单个按键
    
    参数:
        key: 按键名称，支持的特殊按键包括：
             'enter', 'esc', 'shift', 'ctrl', 'alt', 'tab', 'space',
             'up', 'down', 'left', 'right', 'backspace', 'delete',
             'f1'-'f12', 'pageup', 'pagedown', 'home', 'end'
    """
    try:
        pyautogui.press(key)
        return f"已按下并释放按键: {key}"
    except Exception as e:
        return f"按键操作时出错: {str(e)}"

def type_text(text: str, interval: float = 0.05) -> str:
    """输入文本
    
    参数:
        text: 要输入的文本
        interval: 每个字符之间的间隔时间（秒）
    """
    try:
        pyautogui.typewrite(text, interval=interval)
        return f"已输入文本: {text}"
    except Exception as e:
        return f"输入文本时出错: {str(e)}"

def hotkey(*keys: str) -> str:
    """按下组合键
    
    参数:
        *keys: 要按下的按键列表，例如 hotkey('ctrl', 'c') 表示复制操作
    """
    try:
        pyautogui.hotkey(*keys)
        return f"已执行组合键: {', '.join(keys)}"
    except Exception as e:
        return f"执行组合键时出错: {str(e)}"

def scroll_mouse(amount: int) -> str:
    """滚动鼠标滚轮
    
    参数:
        amount: 滚动的量，正数向上滚动，负数向下滚动
    """
    try:
        pyautogui.scroll(amount)
        direction = "向上" if amount > 0 else "向下"
        return f"鼠标滚轮已{direction}滚动: {abs(amount)} 单位"
    except Exception as e:
        return f"滚动鼠标时出错: {str(e)}"


def safe_click_sequence(clicks: List[Tuple[int, int, str]]) -> str:
    """执行安全的点击序列
    
    参数:
        clicks: 点击序列列表，每个元素为 (x, y, button) 元组
    """
    try:
        results = []
        for i, (x, y, button) in enumerate(clicks):
            # 每次点击前短暂暂停
            time.sleep(0.2)
            result = click_mouse(x, y, button=button)
            results.append(f"步骤 {i+1}: {result}")
        return "\n".join(results)
    except Exception as e:
        return f"执行点击序列时出错: {str(e)}"

def safe_type_and_click(text: str, click_x: int, click_y: int, button: str = 'left') -> str:
    """安全地输入文本并点击
    
    参数:
        text: 要输入的文本
        click_x: 点击位置X坐标
        click_y: 点击位置Y坐标
        button: 点击按钮
    """
    try:
        # 先点击
        click_result = click_mouse(click_x, click_y, button=button)
        # 短暂暂停以确保焦点正确
        time.sleep(0.3)
        # 然后输入文本
        type_result = type_text(text)
        return f"{click_result}\n{type_result}"
    except Exception as e:
        return f"执行输入和点击操作时出错: {str(e)}"