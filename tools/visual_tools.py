import pyautogui
import time
import os
from typing import Optional, Tuple

def get_screen_size() -> str:
    """获取屏幕尺寸信息"""
    try:
        width, height = pyautogui.size()
        return f"屏幕尺寸: {width} x {height} 像素"
    except Exception as e:
        return f"获取屏幕尺寸时出错: {str(e)}"

def take_screenshot(save_path: Optional[str] = None, region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """截取屏幕截图
    
    参数:
        save_path: 保存路径（可选），如果不提供则仅返回截图信息
        region: 截图区域，格式为 (x, y, width, height)（可选）
    """
    try:
        screenshot = pyautogui.screenshot(region=region)
        if save_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            screenshot.save(save_path)
            return f"屏幕截图已保存至: {save_path}"
        else:
            return "已成功截取屏幕截图"
    except Exception as e:
        return f"截取屏幕截图时出错: {str(e)}"

def locate_on_screen(image_path: str, confidence: float = 0.7, grayscale: bool = False) -> str:
    """在屏幕上查找图像
    
    参数:
        image_path: 要查找的图像文件路径
        confidence: 匹配的置信度（0-1）
        grayscale: 是否转换为灰度图像进行匹配（可以提高速度但可能降低准确性）
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        # 需要安装opencv-python以支持confidence参数
        try:
            position = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=grayscale)
        except TypeError:
            # 如果没有opencv，不使用confidence参数
            position = pyautogui.locateOnScreen(image_path, grayscale=grayscale)
        
        if position:
            x, y, width, height = position
            center_x = x + width // 2
            center_y = y + height // 2
            return f"找到图像 '{image_path}'，位置: X={x}, Y={y}, 宽度={width}, 高度={height}，中心点: ({center_x}, {center_y})"
        else:
            return f"未在屏幕上找到图像 '{image_path}'"
    except Exception as e:
        return f"查找图像时出错: {str(e)}"

def locate_all_on_screen(image_path: str, confidence: float = 0.7, grayscale: bool = False) -> str:
    """在屏幕上查找所有匹配的图像
    
    参数:
        image_path: 要查找的图像文件路径
        confidence: 匹配的置信度（0-1）
        grayscale: 是否转换为灰度图像进行匹配
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        # 需要安装opencv-python以支持confidence参数
        try:
            positions = list(pyautogui.locateAllOnScreen(image_path, confidence=confidence, grayscale=grayscale))
        except TypeError:
            # 如果没有opencv，不使用confidence参数
            positions = list(pyautogui.locateAllOnScreen(image_path, grayscale=grayscale))
        
        if positions:
            results = []
            for i, position in enumerate(positions):
                x, y, width, height = position
                center_x = x + width // 2
                center_y = y + height // 2
                results.append(f"匹配 {i+1}: X={x}, Y={y}, 宽度={width}, 高度={height}, 中心点: ({center_x}, {center_y})")
            return f"找到 {len(positions)} 个匹配 '{image_path}' 的图像:\n" + "\n".join(results)
        else:
            return f"未在屏幕上找到图像 '{image_path}'"
    except Exception as e:
        return f"查找所有图像时出错: {str(e)}"

def wait_for_image(image_path: str, timeout: int = 10, confidence: float = 0.7) -> str:
    """等待屏幕上出现指定图像
    
    参数:
        image_path: 要等待的图像文件路径
        timeout: 超时时间（秒）
        confidence: 匹配的置信度（0-1）
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                position = pyautogui.locateOnScreen(image_path, confidence=confidence)
            except TypeError:
                position = pyautogui.locateOnScreen(image_path)
            
            if position:
                x, y, width, height = position
                center_x = x + width // 2
                center_y = y + height // 2
                elapsed_time = time.time() - start_time
                return f"在 {elapsed_time:.2f} 秒后找到图像 '{image_path}'，位置: ({center_x}, {center_y})"
            time.sleep(0.5)
        return f"在 {timeout} 秒内未找到图像 '{image_path}'"
    except Exception as e:
        return f"等待图像时出错: {str(e)}"

def click_on_image(image_path: str, confidence: float = 0.7, button: str = 'left', clicks: int = 1) -> str:
    """在屏幕上找到图像并点击
    
    参数:
        image_path: 要查找的图像文件路径
        confidence: 匹配的置信度（0-1）
        button: 点击按钮 ('left', 'right', 'middle')
        clicks: 点击次数
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        # 首先找到图像
        try:
            position = pyautogui.locateOnScreen(image_path, confidence=confidence)
        except TypeError:
            position = pyautogui.locateOnScreen(image_path)
        
        if position:
            # 获取图像中心点
            center_x, center_y = pyautogui.center(position)
            # 点击该位置
            pyautogui.click(center_x, center_y, clicks=clicks, button=button)
            return f"已在找到的图像 '{image_path}' 中心点 ({center_x}, {center_y}) 进行 {button}键点击 {clicks} 次"
        else:
            return f"未在屏幕上找到图像 '{image_path}'，无法进行点击操作"
    except Exception as e:
        return f"点击图像时出错: {str(e)}"

def wait_and_click_image(image_path: str, timeout: int = 10, confidence: float = 0.7, button: str = 'left') -> str:
    """等待图像出现并点击
    
    参数:
        image_path: 要等待和点击的图像文件路径
        timeout: 超时时间（秒）
        confidence: 匹配的置信度（0-1）
        button: 点击按钮 ('left', 'right', 'middle')
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                position = pyautogui.locateOnScreen(image_path, confidence=confidence)
            except TypeError:
                position = pyautogui.locateOnScreen(image_path)
            
            if position:
                # 获取图像中心点并点击
                center_x, center_y = pyautogui.center(position)
                pyautogui.click(center_x, center_y, button=button)
                elapsed_time = time.time() - start_time
                return f"在 {elapsed_time:.2f} 秒后找到并点击了图像 '{image_path}'，位置: ({center_x}, {center_y})"
            time.sleep(0.5)
        return f"在 {timeout} 秒内未找到图像 '{image_path}'，无法进行点击操作"
    except Exception as e:
        return f"等待并点击图像时出错: {str(e)}"

def capture_screen_region(x: int, y: int, width: int, height: int, save_path: Optional[str] = None) -> str:
    """捕获屏幕特定区域
    
    参数:
        x: 区域左上角X坐标
        y: 区域左上角Y坐标
        width: 区域宽度
        height: 区域高度
        save_path: 保存路径（可选）
    """
    try:
        # 检查坐标是否有效
        screen_width, screen_height = pyautogui.size()
        if (x < 0 or y < 0 or width <= 0 or height <= 0 or
            x + width > screen_width or y + height > screen_height):
            return f"区域 ({x}, {y}, {width}, {height}) 超出屏幕范围 (0,0) 到 ({screen_width},{screen_height})"
        
        # 捕获指定区域
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        if save_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            screenshot.save(save_path)
            return f"区域截图已保存至: {save_path}"
        else:
            return f"已成功捕获区域 ({x}, {y}, {width}, {height}) 的截图"
    except Exception as e:
        return f"捕获屏幕区域时出错: {str(e)}"

def find_text_on_screen(text: str) -> str:
    """在屏幕上查找文本（此功能需要额外的OCR支持）
    注意：此函数是一个占位符，完整功能需要安装如pytesseract等OCR库
    
    参数:
        text: 要查找的文本
    """
    try:
        # 这里只是一个占位符实现
        # 实际使用时，需要安装pytesseract和PIL等库
        # 并实现OCR功能来识别屏幕上的文本
        return f"查找文本 '{text}' 的功能需要额外的OCR支持。请安装pytesseract和相关依赖。"
    except Exception as e:
        return f"查找文本时出错: {str(e)}"

def get_screen_color_at(x: int, y: int) -> str:
    """获取屏幕指定位置的颜色
    
    参数:
        x: X坐标
        y: Y坐标
    """
    try:
        # 检查坐标是否有效
        screen_width, screen_height = pyautogui.size()
        if x < 0 or x >= screen_width or y < 0 or y >= screen_height:
            return f"坐标 ({x}, {y}) 超出屏幕范围"
        
        # 获取颜色
        pixel_color = pyautogui.pixel(x, y)
        return f"坐标 ({x}, {y}) 的颜色为: RGB({pixel_color[0]}, {pixel_color[1]}, {pixel_color[2]})"
    except Exception as e:
        return f"获取屏幕颜色时出错: {str(e)}"

def wait_for_color_change(x: int, y: int, initial_color: Optional[Tuple[int, int, int]] = None, timeout: int = 10) -> str:
    """等待指定位置的颜色变化
    
    参数:
        x: X坐标
        y: Y坐标
        initial_color: 初始颜色（可选，不提供则使用当前颜色）
        timeout: 超时时间（秒）
    """
    try:
        # 检查坐标是否有效
        screen_width, screen_height = pyautogui.size()
        if x < 0 or x >= screen_width or y < 0 or y >= screen_height:
            return f"坐标 ({x}, {y}) 超出屏幕范围"
        
        # 获取初始颜色
        if initial_color is None:
            initial_color = pyautogui.pixel(x, y)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_color = pyautogui.pixel(x, y)
            if current_color != initial_color:
                elapsed_time = time.time() - start_time
                return f"在 {elapsed_time:.2f} 秒后检测到颜色变化: 从 RGB({initial_color[0]}, {initial_color[1]}, {initial_color[2]}) 变为 RGB({current_color[0]}, {current_color[1]}, {current_color[2]})"
            time.sleep(0.2)
        current_color = pyautogui.pixel(x, y)
        return f"在 {timeout} 秒内颜色未发生变化，当前颜色: RGB({current_color[0]}, {current_color[1]}, {current_color[2]})"
    except Exception as e:
        return f"等待颜色变化时出错: {str(e)}"