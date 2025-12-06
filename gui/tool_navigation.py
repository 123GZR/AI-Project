import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from datetime import datetime
from knowledge_base import knowledge_base
from .todo_list import TodoList
from .knowledge_base_ui import KnowledgeBaseUI

class ToolNavigation:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
    
    def create(self):
        """创建左侧导航栏，包含知识库和待办事项选项卡"""
        # 创建主框架
        nav_frame = ttk.LabelFrame(self.parent.content_frame, text="导航中心", width=280)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N)
        nav_frame.pack_propagate(False)
        
        # 创建选项卡控件
        self.notebook = ttk.Notebook(nav_frame)
        # 隐藏标签页栏，防止用户手动切换
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 隐藏标签栏的样式设置
        style = ttk.Style()
        style.configure('TNotebook.Tab', width=0, height=0)
        style.configure('TNotebook', padding=0)
        
        # 1. 知识库选项卡
        self.knowledge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.knowledge_frame, text="知识库")
        self.knowledge_base_ui = KnowledgeBaseUI(self.parent, self.knowledge_frame)
        self.knowledge_base_ui.create()
        
        # 2. 待办事项选项卡
        self.todo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.todo_frame, text="待办事项")
        self.todo_list = TodoList(self.parent, self.todo_frame)
        self.todo_list.create()
        
        # 默认显示待办事项选项卡
        self.notebook.select(self.todo_frame)
