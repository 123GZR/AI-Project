import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class ChatArea:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
    
    def create(self):
        """创建聊天区域"""
        # 创建右侧聊天区域
        self.chat_frame = ttk.Frame(self.parent.content_frame)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 创建聊天历史区域
        self.create_chat_history()
        
        # 创建输入区域
        self.create_input_area()
    
    def create_chat_history(self):
        """创建聊天历史区域"""
        chat_history_frame = ttk.LabelFrame(self.chat_frame, text="聊天历史")
        chat_history_frame.pack(fill=tk.BOTH, expand=True)
        
        # 聊天历史文本框
        self.chat_history = scrolledtext.ScrolledText(chat_history_frame, wrap=tk.WORD, font=('微软雅黑', 10))
        self.chat_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_history.config(state=tk.DISABLED)
        
        # 设置聊天历史样式
        self.chat_history.tag_configure("user", foreground="blue", font=('微软雅黑', 10, 'bold'))
        self.chat_history.tag_configure("ai", foreground="green", font=('微软雅黑', 10, 'bold'))
        self.chat_history.tag_configure("system", foreground="gray", font=('微软雅黑', 10, 'italic'))
        self.chat_history.tag_configure("tool", foreground="purple", font=('微软雅黑', 10))
    
    def create_input_area(self):
        """创建输入区域"""
        input_frame = ttk.LabelFrame(self.chat_frame, text="输入问题")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=5, font=('微软雅黑', 10))
        self.input_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空聊天", command=self.clear_chat)
        clear_button.pack(side=tk.LEFT)
        
        # 发送按钮
        send_button = ttk.Button(button_frame, text="发送", command=self.parent.send_message, style="Accent.TButton")
        send_button.pack(side=tk.RIGHT)
        
        # 设置发送按钮样式
        self.parent.style.configure("Accent.TButton", foreground="white", background="#0078d7")
    
    def add_message(self, sender, content, is_system=False, is_tool=False):
        """添加消息到聊天历史"""
        self.chat_history.config(state=tk.NORMAL)
        
        # 确定消息类型和标签
        if is_system:
            tag = "system"
            prefix = f"[{sender}] "
        elif is_tool:
            tag = "tool"
            prefix = f"[{sender}] "
        else:
            tag = "user" if sender == "我" else "ai"
            prefix = f"{sender}: "
        
        # 添加消息
        self.chat_history.insert(tk.END, prefix, tag)
        self.chat_history.insert(tk.END, content + "\n\n")
        
        # 自动滚动到底部
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
    
    def update_ai_response(self, chunk, is_ai_responding, current_ai_response):
        """更新AI助手的回复"""
        self.chat_history.config(state=tk.NORMAL)
        
        # 过滤掉chunk中所有的"AI助手:"前缀
        filtered_chunk = chunk.replace("AI助手:", "")
        
        # 检查是否需要添加AI前缀
        if not is_ai_responding:
            # 如果不是正在回复状态，添加完整的AI回复
            self.chat_history.insert(tk.END, "AI助手: ", "ai")
        elif not current_ai_response:
            # 如果是第一次收到回复，添加前缀
            self.chat_history.insert(tk.END, "AI助手: ", "ai")
        
        # 添加过滤后的回复内容
        if filtered_chunk:
            self.chat_history.insert(tk.END, filtered_chunk)
            self.chat_history.see(tk.END)
        
        self.chat_history.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """清空聊天记录"""
        if messagebox.askyesno("确认", "确定要清空聊天记录吗？"):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)
            self.parent.add_message("系统", "聊天记录已清空", is_system=True)
