import tkinter as tk
from tkinter import ttk

class TitleBar:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
    
    def create(self):
        """创建顶部标题栏"""
        title_frame = ttk.Frame(self.parent.main_frame)
        title_frame.pack(fill=tk.X)
        
        # 标题
        title_label = ttk.Label(title_frame, text="电脑操作专家AI助手", font=('微软雅黑', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # 调试模式开关
        debug_frame = ttk.Frame(title_frame)
        debug_frame.pack(side=tk.RIGHT)
        
        self.debug_var = tk.BooleanVar(value=self.parent.debug_mode)
        debug_check = ttk.Checkbutton(debug_frame, text="调试模式", variable=self.debug_var, command=self.parent.toggle_debug)
        debug_check.pack(side=tk.RIGHT, padx=(0, 10))
