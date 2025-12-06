#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多窗口独立处理模块
实现窗口的独立捕获、识别和处理
"""

import time
import threading
from typing import Dict, List, Optional, Any
import pygetwindow as gw
from .visual_tools import (
    capture_region_to_numpy,
    recognize_text_in_region,
    capture_screen_fast
)
from .windows_tools import (
    get_all_windows,
    get_window_info,
    window_exists
)


class WindowProcessor:
    """单个窗口的处理器"""
    
    def __init__(self, hwnd: int, title: str, x: int, y: int, width: int, height: int):
        self.hwnd = hwnd
        self.title = title
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_running = False
        self.thread = None
        self.last_content = None
        self.content_history = []
        self.lock = threading.Lock()
        self.fps = 30
        self.frame_interval = 1.0 / self.fps
    
    def start(self):
        """启动窗口处理器"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._process_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """停止窗口处理器"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def update_window_info(self, x: int, y: int, width: int, height: int):
        """更新窗口信息"""
        with self.lock:
            self.x = x
            self.y = y
            self.width = width
            self.height = height
    
    def _process_loop(self):
        """窗口处理主循环"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # 捕获窗口内容
                frame = self._capture_window()
                if frame is not None:
                    # 处理窗口内容
                    self._process_content(frame)
                
                # 控制帧率
                elapsed_time = time.time() - start_time
                sleep_time = self.frame_interval - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
            except Exception as e:
                print(f"窗口处理错误 (HWND: {self.hwnd}, Title: {self.title}): {e}")
                time.sleep(0.1)
    
    def _capture_window(self) -> Optional[Any]:
        """捕获窗口内容"""
        with self.lock:
            x, y, width, height = self.x, self.y, self.width, self.height
        
        # 检查窗口是否有效
        if width <= 0 or height <= 0:
            return None
        
        try:
            # 使用快速捕获方法捕获窗口区域
            frame = capture_region_to_numpy(x, y, width, height)
            return frame
        except Exception as e:
            print(f"窗口捕获错误 (HWND: {self.hwnd}): {e}")
            return None
    
    def _process_content(self, frame: Any):
        """处理窗口内容"""
        # 这里可以添加各种内容处理逻辑
        # 1. OCR文本识别
        # 2. 图像分类
        # 3. 界面元素检测
        # 4. 内容变化检测
        
        # 示例：使用OCR识别窗口文本
        ocr_result = recognize_text_in_region(
            self.x, self.y, self.width, self.height
        )
        
        # 存储内容历史
        with self.lock:
            if isinstance(ocr_result, dict) and ocr_result.get("status") == "success":
                self.last_content = ocr_result
                self.content_history.append({
                    "timestamp": time.time(),
                    "content": ocr_result,
                    "window_info": {
                        "x": self.x,
                        "y": self.y,
                        "width": self.width,
                        "height": self.height
                    }
                })
                # 限制历史记录长度
                if len(self.content_history) > 100:
                    self.content_history = self.content_history[-100:]
    
    def get_last_content(self) -> Optional[Dict[str, Any]]:
        """获取最近的窗口内容"""
        with self.lock:
            return self.last_content
    
    def get_content_history(self) -> List[Dict[str, Any]]:
        """获取窗口内容历史"""
        with self.lock:
            return self.content_history.copy()
    
    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口信息"""
        with self.lock:
            return {
                "hwnd": self.hwnd,
                "title": self.title,
                "x": self.x,
                "y": self.y,
                "width": self.width,
                "height": self.height,
                "is_running": self.is_running
            }


class MultiWindowProcessor:
    """多窗口处理器"""
    
    def __init__(self):
        self.window_processors: Dict[int, WindowProcessor] = {}
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()
        self.monitor_interval = 0.5  # 窗口监控间隔（秒）
    
    def start(self):
        """启动多窗口处理器"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        """停止多窗口处理器"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # 停止所有窗口处理器
        with self.lock:
            for processor in self.window_processors.values():
                processor.stop()
            self.window_processors.clear()
    
    def _monitor_loop(self):
        """窗口监控主循环"""
        while self.is_running:
            try:
                # 获取当前所有窗口
                windows_result = get_all_windows()
                if isinstance(windows_result, str):
                    time.sleep(self.monitor_interval)
                    continue
                
                current_windows = windows_result.get("windows", {})
                current_hwnds = set()
                
                # 处理当前存在的窗口
                for win_id, win_info in current_windows.items():
                    hwnd = win_info["hwnd"]
                    current_hwnds.add(hwnd)
                    
                    with self.lock:
                        if hwnd in self.window_processors:
                            # 更新现有窗口的信息
                            processor = self.window_processors[hwnd]
                            processor.update_window_info(
                                win_info["x"], win_info["y"],
                                win_info["width"], win_info["height"]
                            )
                        else:
                            # 创建新的窗口处理器
                            processor = WindowProcessor(
                                hwnd, win_info["title"],
                                win_info["x"], win_info["y"],
                                win_info["width"], win_info["height"]
                            )
                            self.window_processors[hwnd] = processor
                            processor.start()
                
                # 清理已关闭的窗口处理器
                with self.lock:
                    for hwnd in list(self.window_processors.keys()):
                        if hwnd not in current_hwnds:
                            processor = self.window_processors.pop(hwnd)
                            processor.stop()
                
                time.sleep(self.monitor_interval)
            except Exception as e:
                print(f"多窗口监控错误: {e}")
                time.sleep(self.monitor_interval)
    
    def get_window_processor(self, hwnd: int) -> Optional[WindowProcessor]:
        """获取指定窗口的处理器"""
        with self.lock:
            return self.window_processors.get(hwnd)
    
    def get_all_window_processors(self) -> Dict[int, WindowProcessor]:
        """获取所有窗口处理器"""
        with self.lock:
            return self.window_processors.copy()
    
    def get_window_content(self, hwnd: int) -> Optional[Dict[str, Any]]:
        """获取指定窗口的内容"""
        processor = self.get_window_processor(hwnd)
        if processor:
            return processor.get_last_content()
        return None
    
    def get_all_window_contents(self) -> Dict[int, Optional[Dict[str, Any]]]:
        """获取所有窗口的内容"""
        result = {}
        with self.lock:
            for hwnd, processor in self.window_processors.items():
                result[hwnd] = processor.get_last_content()
        return result
    
    def get_active_window_content(self) -> Optional[Dict[str, Any]]:
        """获取当前活动窗口的内容"""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                return self.get_window_content(active_window._hWnd)
        except Exception as e:
            print(f"获取活动窗口内容错误: {e}")
        return None


# 全局多窗口处理器实例
_global_multi_window_processor = None


def get_multi_window_processor() -> MultiWindowProcessor:
    """获取全局多窗口处理器实例（单例模式）"""
    global _global_multi_window_processor
    if _global_multi_window_processor is None:
        _global_multi_window_processor = MultiWindowProcessor()
    return _global_multi_window_processor


def start_multi_window_processing() -> str:
    """启动多窗口处理"""
    try:
        processor = get_multi_window_processor()
        processor.start()
        return "多窗口处理已启动"
    except Exception as e:
        return f"启动多窗口处理时出错: {str(e)}"


def stop_multi_window_processing() -> str:
    """停止多窗口处理"""
    try:
        processor = get_multi_window_processor()
        processor.stop()
        return "多窗口处理已停止"
    except Exception as e:
        return f"停止多窗口处理时出错: {str(e)}"


def get_window_content(hwnd: int) -> Dict[str, Any]:
    """获取指定窗口的内容"""
    try:
        processor = get_multi_window_processor()
        content = processor.get_window_content(hwnd)
        if content:
            return {
                "status": "success",
                "hwnd": hwnd,
                "content": content
            }
        else:
            return {
                "status": "success",
                "hwnd": hwnd,
                "content": None,
                "message": "未获取到窗口内容"
            }
    except Exception as e:
        return f"获取窗口内容时出错: {str(e)}"


def get_all_window_contents() -> Dict[str, Any]:
    """获取所有窗口的内容"""
    try:
        processor = get_multi_window_processor()
        contents = processor.get_all_window_contents()
        return {
            "status": "success",
            "window_contents": contents,
            "total_windows": len(contents)
        }
    except Exception as e:
        return f"获取所有窗口内容时出错: {str(e)}"


def get_active_window_content() -> Dict[str, Any]:
    """获取当前活动窗口的内容"""
    try:
        processor = get_multi_window_processor()
        content = processor.get_active_window_content()
        if content:
            return {
                "status": "success",
                "content": content
            }
        else:
            return {
                "status": "success",
                "content": None,
                "message": "未获取到活动窗口内容"
            }
    except Exception as e:
        return f"获取活动窗口内容时出错: {str(e)}"


def get_window_processing_status() -> Dict[str, Any]:
    """获取窗口处理状态"""
    try:
        processor = get_multi_window_processor()
        processors = processor.get_all_window_processors()
        status = {
            "status": "success",
            "is_running": processor.is_running,
            "total_processors": len(processors),
            "window_details": []
        }
        
        for hwnd, proc in processors.items():
            proc_info = proc.get_window_info()
            status["window_details"].append(proc_info)
        
        return status
    except Exception as e:
        return f"获取窗口处理状态时出错: {str(e)}"
