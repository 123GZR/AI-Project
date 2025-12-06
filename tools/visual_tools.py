import pyautogui
import time
import os
from typing import Optional, Tuple, Dict, List
import mss
import mss.tools
import numpy as np
import cv2

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


def get_monitors_info() -> Dict[str, any]:
    """获取所有显示器信息
    
    返回:
        包含所有显示器信息的字典
    """
    try:
        with mss.mss() as sct:
            monitors = sct.monitors
            result = {}
            for i, monitor in enumerate(monitors):
                result[f"monitor_{i}"] = {
                    "left": monitor["left"],
                    "top": monitor["top"],
                    "width": monitor["width"],
                    "height": monitor["height"],
                    "name": f"显示器 {i}"
                }
            return result
    except Exception as e:
        return f"获取显示器信息时出错: {str(e)}"


def capture_screen_fast(save_path: Optional[str] = None, monitor_id: int = 1) -> str:
    """使用mss快速捕获屏幕截图
    
    参数:
        save_path: 保存路径（可选），如果不提供则仅返回截图信息
        monitor_id: 显示器ID，0表示所有显示器，1表示主显示器
    """
    try:
        with mss.mss() as sct:
            # 获取指定显示器
            monitor = sct.monitors[monitor_id]
            # 捕获屏幕
            screenshot = sct.grab(monitor)
            
            if save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                # 保存截图
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=save_path)
                return f"快速屏幕截图已保存至: {save_path}"
            else:
                return f"已成功快速截取屏幕截图，尺寸: {screenshot.width} x {screenshot.height}"
    except Exception as e:
        return f"快速捕获屏幕截图时出错: {str(e)}"


def capture_screen_region_fast(x: int, y: int, width: int, height: int, save_path: Optional[str] = None) -> str:
    """使用mss快速捕获屏幕特定区域
    
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
        
        with mss.mss() as sct:
            # 定义捕获区域
            monitor = {
                "left": x,
                "top": y,
                "width": width,
                "height": height
            }
            # 捕获区域
            screenshot = sct.grab(monitor)
            
            if save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                # 保存截图
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=save_path)
                return f"快速区域截图已保存至: {save_path}"
            else:
                return f"已成功快速捕获区域 ({x}, {y}, {width}, {height}) 的截图"
    except Exception as e:
        return f"快速捕获屏幕区域时出错: {str(e)}"


def capture_screen_to_numpy(monitor_id: int = 1) -> np.ndarray:
    """捕获屏幕并返回numpy数组（用于实时处理）
    
    参数:
        monitor_id: 显示器ID，0表示所有显示器，1表示主显示器
    
    返回:
        屏幕截图的numpy数组（BGR格式）
    """
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[monitor_id]
            screenshot = sct.grab(monitor)
            # 转换为numpy数组
            img = np.array(screenshot)
            # 转换为BGR格式（OpenCV使用）
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            return img_bgr
    except Exception as e:
        raise Exception(f"捕获屏幕到numpy数组时出错: {str(e)}")


def capture_region_to_numpy(x: int, y: int, width: int, height: int) -> np.ndarray:
    """捕获屏幕区域并返回numpy数组（用于实时处理）
    
    参数:
        x: 区域左上角X坐标
        y: 区域左上角Y坐标
        width: 区域宽度
        height: 区域高度
    
    返回:
        区域截图的numpy数组（BGR格式）
    """
    try:
        with mss.mss() as sct:
            monitor = {
                "left": x,
                "top": y,
                "width": width,
                "height": height
            }
            screenshot = sct.grab(monitor)
            # 转换为numpy数组
            img = np.array(screenshot)
            # 转换为BGR格式（OpenCV使用）
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            return img_bgr
    except Exception as e:
        raise Exception(f"捕获区域到numpy数组时出错: {str(e)}")


def benchmark_screen_capture(num_iterations: int = 100) -> str:
    """基准测试屏幕捕获性能
    
    参数:
        num_iterations: 测试迭代次数
    """
    try:
        # 测试pyautogui捕获性能
        start_time = time.time()
        for _ in range(num_iterations):
            pyautogui.screenshot()
        pyautogui_time = time.time() - start_time
        
        # 测试mss捕获性能
        start_time = time.time()
        with mss.mss() as sct:
            for _ in range(num_iterations):
                sct.grab(sct.monitors[1])
        mss_time = time.time() - start_time
        
        return (f"屏幕捕获性能基准测试 ({num_iterations} 次迭代):\n" +
                f"pyautogui: {pyautogui_time:.2f} 秒, {num_iterations/pyautogui_time:.1f} FPS\n" +
                f"mss: {mss_time:.2f} 秒, {num_iterations/mss_time:.1f} FPS" +
                f"\nmss比pyautogui快 {pyautogui_time/mss_time:.2f} 倍")
    except Exception as e:
        return f"基准测试屏幕捕获性能时出错: {str(e)}"


# OCR文本识别功能
_easyocr_reader = None

def _get_easyocr_reader(langs: List[str] = ['ch_sim', 'en']) -> any:
    """获取EasyOCR读取器实例（单例模式）
    
    参数:
        langs: 支持的语言列表
    """
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            _easyocr_reader = easyocr.Reader(langs)
        except Exception as e:
            raise Exception(f"初始化EasyOCR读取器失败: {str(e)}")
    return _easyocr_reader


def recognize_text_in_image(image_path: str, langs: List[str] = ['ch_sim', 'en']) -> Dict[str, any]:
    """识别图像中的文本
    
    参数:
        image_path: 图像文件路径
        langs: 支持的语言列表
    
    返回:
        包含识别结果的字典
    """
    try:
        if not os.path.exists(image_path):
            return f"图像文件 '{image_path}' 不存在"
        
        reader = _get_easyocr_reader(langs)
        results = reader.readtext(image_path)
        
        # 处理识别结果
        text_results = []
        for result in results:
            bbox, text, confidence = result
            text_results.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": {
                    "x1": int(bbox[0][0]),
                    "y1": int(bbox[0][1]),
                    "x2": int(bbox[2][0]),
                    "y2": int(bbox[2][1])
                }
            })
        
        return {
            "status": "success",
            "results": text_results,
            "total_texts": len(text_results)
        }
    except Exception as e:
        return f"识别图像文本时出错: {str(e)}"


def recognize_text_in_screen(monitor_id: int = 1, langs: List[str] = ['ch_sim', 'en']) -> Dict[str, any]:
    """识别屏幕上的文本
    
    参数:
        monitor_id: 显示器ID，0表示所有显示器，1表示主显示器
        langs: 支持的语言列表
    
    返回:
        包含识别结果的字典
    """
    try:
        # 快速捕获屏幕
        img_bgr = capture_screen_to_numpy(monitor_id)
        # 转换为RGB格式（EasyOCR使用）
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        reader = _get_easyocr_reader(langs)
        results = reader.readtext(img_rgb)
        
        # 处理识别结果
        text_results = []
        for result in results:
            bbox, text, confidence = result
            text_results.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": {
                    "x1": int(bbox[0][0]),
                    "y1": int(bbox[0][1]),
                    "x2": int(bbox[2][0]),
                    "y2": int(bbox[2][1])
                }
            })
        
        return {
            "status": "success",
            "results": text_results,
            "total_texts": len(text_results),
            "screen_info": {
                "monitor_id": monitor_id,
                "width": img_bgr.shape[1],
                "height": img_bgr.shape[0]
            }
        }
    except Exception as e:
        return f"识别屏幕文本时出错: {str(e)}"


def recognize_text_in_region(x: int, y: int, width: int, height: int, langs: List[str] = ['ch_sim', 'en']) -> Dict[str, any]:
    """识别屏幕特定区域内的文本
    
    参数:
        x: 区域左上角X坐标
        y: 区域左上角Y坐标
        width: 区域宽度
        height: 区域高度
        langs: 支持的语言列表
    
    返回:
        包含识别结果的字典
    """
    try:
        # 快速捕获区域
        img_bgr = capture_region_to_numpy(x, y, width, height)
        # 转换为RGB格式（EasyOCR使用）
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        reader = _get_easyocr_reader(langs)
        results = reader.readtext(img_rgb)
        
        # 处理识别结果，调整坐标为全局坐标
        text_results = []
        for result in results:
            bbox, text, confidence = result
            text_results.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": {
                    "x1": int(bbox[0][0] + x),
                    "y1": int(bbox[0][1] + y),
                    "x2": int(bbox[2][0] + x),
                    "y2": int(bbox[2][1] + y)
                }
            })
        
        return {
            "status": "success",
            "results": text_results,
            "total_texts": len(text_results),
            "region_info": {
                "x": x,
                "y": y,
                "width": width,
                "height": height
            }
        }
    except Exception as e:
        return f"识别区域文本时出错: {str(e)}"


def find_text_on_screen(text: str, confidence_threshold: float = 0.7, monitor_id: int = 1, langs: List[str] = ['ch_sim', 'en']) -> Dict[str, any]:
    """在屏幕上查找指定文本
    
    参数:
        text: 要查找的文本
        confidence_threshold: 置信度阈值
        monitor_id: 显示器ID
        langs: 支持的语言列表
    
    返回:
        包含查找结果的字典
    """
    try:
        # 识别屏幕文本
        ocr_result = recognize_text_in_screen(monitor_id, langs)
        if isinstance(ocr_result, str):
            return ocr_result
        
        # 查找匹配的文本
        matches = []
        for result in ocr_result["results"]:
            if text in result["text"] and result["confidence"] >= confidence_threshold:
                matches.append(result)
        
        return {
            "status": "success",
            "matches": matches,
            "total_matches": len(matches),
            "search_text": text,
            "confidence_threshold": confidence_threshold
        }
    except Exception as e:
        return f"在屏幕上查找文本时出错: {str(e)}"


def real_time_text_detection(duration: float = 5.0, confidence_threshold: float = 0.7, monitor_id: int = 1, langs: List[str] = ['ch_sim', 'en']) -> Dict[str, any]:
    """实时文本检测
    
    参数:
        duration: 检测持续时间（秒）
        confidence_threshold: 置信度阈值
        monitor_id: 显示器ID
        langs: 支持的语言列表
    
    返回:
        包含检测结果的字典
    """
    try:
        start_time = time.time()
        detected_texts = set()
        all_results = []
        
        while time.time() - start_time < duration:
            # 识别当前屏幕文本
            ocr_result = recognize_text_in_screen(monitor_id, langs)
            if isinstance(ocr_result, str):
                continue
            
            # 收集检测到的文本
            for result in ocr_result["results"]:
                if result["confidence"] >= confidence_threshold:
                    text = result["text"]
                    if text not in detected_texts:
                        detected_texts.add(text)
                        all_results.append(result)
            
            # 短暂休眠，控制检测频率
            time.sleep(0.5)
        
        return {
            "status": "success",
            "duration": duration,
            "detected_texts_count": len(detected_texts),
            "results": all_results
        }
    except Exception as e:
        return f"实时文本检测时出错: {str(e)}"