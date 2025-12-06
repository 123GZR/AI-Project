import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
import os
import json
from datetime import datetime
from computer_expert_agent import run_computer_expert_agent_stream, DEBUG_MODE
from knowledge_base import knowledge_base
from .title_bar import TitleBar
from .tool_navigation import ToolNavigation
from .chat_area import ChatArea
from .status_bar import StatusBar
from .utility import show_toast

class ComputerExpertGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("电脑操作专家AI助手")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 设置主题
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 初始化变量
        self.ai_status = "空闲"
        self.debug_mode = DEBUG_MODE
        self.conversation_ctx = None
        self.is_ai_responding = False  # 添加标记，记录是否正在显示AI回复
        self.current_ai_response = ""  # 记录当前AI回复的内容
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部标题栏
        self.title_bar = TitleBar(self)
        self.title_bar.create()
        
        # 创建中间内容区域
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建左侧工具导航
        self.tool_navigation = ToolNavigation(self)
        self.tool_navigation.create()
        
        # 创建右侧聊天区域
        self.chat_area = ChatArea(self)
        self.chat_area.create()
        
        # 创建状态显示
        self.status_bar = StatusBar(self)
        self.status_bar.create()
        
        # 绑定事件
        self.bind_events()
        
        # 显示欢迎信息
        self.add_message("系统", "欢迎使用电脑操作专家AI助手！请输入您的电脑操作问题。", is_system=True)
    
    def bind_events(self):
        """绑定事件"""
        # 输入框回车发送，Shift+回车换行
        self.chat_area.input_text.bind("<Return>", self.on_enter)
        self.chat_area.input_text.bind("<Shift-Return>", self.on_shift_enter)
    
    def on_enter(self, event):
        """处理回车键发送消息"""
        self.send_message()
        return "break"
    
    def on_shift_enter(self, event):
        """处理Shift+回车键换行"""
        self.chat_area.input_text.insert(tk.INSERT, "\n")
        return "break"
    
    def toggle_debug(self):
        """切换调试模式"""
        self.debug_mode = self.title_bar.debug_var.get()
        global DEBUG_MODE
        DEBUG_MODE = self.debug_mode
        self.add_message("系统", f"调试模式已{'开启' if self.debug_mode else '关闭'}", is_system=True)
    
    def add_message(self, sender, content, is_system=False, is_tool=False):
        """添加消息到聊天历史"""
        self.chat_area.add_message(sender, content, is_system, is_tool)
    
    def send_message(self):
        """发送消息"""
        message = self.chat_area.input_text.get("1.0", tk.END).strip()
        if not message:
            return
        
        # 添加用户消息
        self.add_message("我", message)
        
        # 清空输入框
        self.chat_area.input_text.delete("1.0", tk.END)
        
        # 更新AI状态
        self.update_status("思考中")
        self.is_ai_responding = True  # 设置AI正在回复标记
        self.current_ai_response = ""  # 重置当前AI回复内容
        
        # 在新线程中运行AI助手，避免阻塞GUI
        threading.Thread(target=self.run_ai_assistant, args=(message,), daemon=True).start()
    
    def run_ai_assistant(self, message):
        """运行AI助手"""
        try:
            # 由于run_computer_expert_agent_stream是异步函数，需要在异步事件循环中运行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 定义一个回调函数来处理流式输出
            def stream_callback(chunk):
                # 在主线程中更新GUI
                self.root.after(0, self.update_ai_response, chunk)
            
            # 运行AI助手
            response = loop.run_until_complete(
                run_computer_expert_agent_stream(message, ctx=self.conversation_ctx, callback=stream_callback)
            )
            
            # 更新AI状态
            self.root.after(0, self.update_status, "空闲")
            self.root.after(0, self.end_ai_response)
        except Exception as e:
            error_msg = f"AI助手出错: {str(e)}"
            self.root.after(0, self.add_message, "系统", error_msg, True)
            self.root.after(0, self.update_status, "空闲")
            self.root.after(0, self.end_ai_response)
            import traceback
            traceback.print_exc()
    
    def update_ai_response(self, chunk):
        """更新AI助手的回复"""
        self.chat_area.update_ai_response(chunk, self.is_ai_responding, self.current_ai_response)
        
        if not self.is_ai_responding:
            self.is_ai_responding = True
        if chunk:
            self.current_ai_response += chunk.replace("AI助手:", "")
    
    def end_ai_response(self):
        """结束AI回复"""
        self.is_ai_responding = False
        self.current_ai_response = ""
    
    def update_status(self, status):
        """更新AI状态"""
        self.ai_status = status
        self.status_bar.update_status(status)
    
    def clear_chat(self):
        """清空聊天记录"""
        self.chat_area.clear_chat()
    
    def show_toast(self, message, duration=2000):
        """显示提示信息"""
        show_toast(self.root, message, duration)
