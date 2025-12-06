import tkinter as tk
from tkinter import ttk

class StatusBar:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
    
    def create(self):
        """创建状态显示栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        # AI状态
        self.status_var = tk.StringVar(value=f"AI状态: {self.parent.ai_status}")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # API状态
        self.api_status_var = tk.StringVar(value="API状态: 已连接")
        api_label = ttk.Label(status_frame, textvariable=self.api_status_var, anchor=tk.E)
        api_label.pack(side=tk.RIGHT)
    
    def update_status(self, status):
        """更新AI状态"""
        self.status_var.set(f"AI状态: {status}")
