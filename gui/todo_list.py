import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from datetime import datetime

class TodoList:
    def __init__(self, parent, frame):
        self.parent = parent
        self.frame = frame
        self.root = parent.root
        self.todo_items = []
        self.todo_id_counter = 1
        self.todo_file = "todos.json"
    
    def create(self):
        """创建待办事项界面"""
        # 待办事项列表
        self.todo_listbox = tk.Listbox(
            self.frame, 
            width=30, 
            height=20, 
            font=('微软雅黑', 10),
            selectmode=tk.SINGLE,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            bg="#f0f0f0"
        )
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.todo_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_listbox.config(yscrollcommand=scrollbar.set)
        
        # 待办事项输入框
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.todo_input = ttk.Entry(input_frame, width=25, font=('微软雅黑', 10))
        self.todo_input.pack(side=tk.LEFT, padx=(0, 5))
        self.todo_input.bind("<Return>", self.add_todo)
        
        # 添加按钮
        add_button = ttk.Button(input_frame, text="添加", command=self.add_todo, width=6)
        add_button.pack(side=tk.LEFT)
        
        # 操作按钮框架
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 标记完成按钮
        complete_button = ttk.Button(action_frame, text="完成", command=self.toggle_todo_status, width=6)
        complete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 编辑按钮
        edit_button = ttk.Button(action_frame, text="编辑", command=self.edit_todo, width=6)
        edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 删除按钮
        delete_button = ttk.Button(action_frame, text="删除", command=self.delete_todo, width=6)
        delete_button.pack(side=tk.LEFT)
        
        # 绑定事件
        self.todo_listbox.bind("<Double-1>", self.toggle_todo_status)
        self.todo_listbox.bind("<Button-3>", self.show_todo_menu)
        
        # 创建右键菜单
        self.todo_menu = tk.Menu(self.root, tearoff=0)
        self.todo_menu.add_command(label="标记完成", command=self.toggle_todo_status)
        self.todo_menu.add_command(label="编辑", command=self.edit_todo)
        self.todo_menu.add_command(label="删除", command=self.delete_todo)
        
        # 加载待办事项
        self.load_todos()
    
    def add_todo(self, event=None):
        """添加待办事项"""
        todo_text = self.todo_input.get().strip()
        if todo_text:
            todo = {
                "id": self.todo_id_counter,
                "text": todo_text,
                "status": "未开始",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.todo_items.append(todo)
            self.todo_id_counter += 1
            self.update_todo_list()
            self.save_todos()
            self.todo_input.delete(0, tk.END)
            # 添加成功提示
            self.parent.show_toast("待办事项已添加")
    
    def toggle_todo_status(self, event=None):
        """切换待办事项状态"""
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            todo = self.todo_items[index]
            if todo["status"] == "已完成":
                todo["status"] = "未开始"
            elif todo["status"] == "未开始":
                todo["status"] = "已完成"
            else:
                todo["status"] = "已完成"
            todo["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.update_todo_list()
            self.save_todos()
            # 添加状态变更提示
            self.parent.show_toast(f"待办事项已标记为{todo['status']}")
    
    def edit_todo(self, event=None):
        """编辑待办事项"""
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            todo = self.todo_items[index]
            
            # 创建编辑对话框
            edit_window = tk.Toplevel(self.root)
            edit_window.title("编辑待办事项")
            edit_window.geometry("300x150")
            edit_window.resizable(False, False)
            
            # 输入框
            edit_label = ttk.Label(edit_window, text="待办事项:")
            edit_label.pack(pady=10)
            
            edit_input = ttk.Entry(edit_window, width=30, font=('微软雅黑', 10))
            edit_input.pack(pady=5, padx=10)
            edit_input.insert(0, todo["text"])
            edit_input.focus()
            
            # 状态选择
            status_frame = ttk.Frame(edit_window)
            status_frame.pack(pady=5)
            
            status_label = ttk.Label(status_frame, text="状态:")
            status_label.pack(side=tk.LEFT, padx=(10, 5))
            
            status_var = tk.StringVar(value=todo["status"])
            status_combobox = ttk.Combobox(
                status_frame, 
                textvariable=status_var,
                values=["未开始", "进行中", "已完成"],
                state="readonly",
                width=10
            )
            status_combobox.pack(side=tk.LEFT)
            
            # 按钮
            button_frame = ttk.Frame(edit_window)
            button_frame.pack(pady=10)
            
            def save_edit():
                new_text = edit_input.get().strip()
                if new_text:
                    todo["text"] = new_text
                    todo["status"] = status_var.get()
                    todo["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.update_todo_list()
                    self.save_todos()
                    edit_window.destroy()
                    # 添加编辑成功提示
                    self.parent.show_toast("待办事项已更新")
                else:
                    messagebox.showwarning("警告", "待办事项内容不能为空")
            
            save_button = ttk.Button(button_frame, text="保存", command=save_edit)
            save_button.pack(side=tk.LEFT, padx=5)
            
            cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
            cancel_button.pack(side=tk.LEFT, padx=5)
            
            # 回车键保存
            edit_window.bind("<Return>", lambda e: save_edit())
    
    def delete_todo(self, event=None):
        """删除待办事项"""
        selection = self.todo_listbox.curselection()
        if selection:
            if messagebox.askyesno("确认", "确定要删除这个待办事项吗？"):
                index = selection[0]
                self.todo_items.pop(index)
                self.update_todo_list()
                self.save_todos()
                # 添加删除成功提示
                self.parent.show_toast("待办事项已删除")
    
    def show_todo_menu(self, event):
        """显示右键菜单"""
        try:
            # 获取选中项
            index = self.todo_listbox.nearest(event.y)
            self.todo_listbox.selection_clear(0, tk.END)
            self.todo_listbox.selection_set(index)
            # 显示菜单
            self.todo_menu.post(event.x_root, event.y_root)
        except Exception as e:
            pass
    
    def update_todo_list(self):
        """更新待办事项列表"""
        self.todo_listbox.delete(0, tk.END)
        for todo in self.todo_items:
            if todo["status"] == "已完成":
                display_text = f"[✓] {todo['text']}"
                self.todo_listbox.insert(tk.END, display_text)
                self.todo_listbox.itemconfig(tk.END, fg="#888888", selectbackground="#e0e0e0")
            elif todo["status"] == "进行中":
                display_text = f"[⏳] {todo['text']}"
                self.todo_listbox.insert(tk.END, display_text)
                self.todo_listbox.itemconfig(tk.END, fg="#0078d7", selectbackground="#e6f2ff")
            else:
                display_text = f"[ ] {todo['text']}"
                self.todo_listbox.insert(tk.END, display_text)
                self.todo_listbox.itemconfig(tk.END, fg="#000000", selectbackground="#e0e0e0")
    
    def load_todos(self):
        """从文件加载待办事项"""
        try:
            if os.path.exists(self.todo_file):
                with open(self.todo_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.todo_items = data.get("items", [])
                    self.todo_id_counter = data.get("next_id", 1)
                    self.update_todo_list()
        except Exception as e:
            print(f"加载待办事项失败: {e}")
            self.todo_items = []
            self.todo_id_counter = 1
    
    def save_todos(self):
        """保存待办事项到文件"""
        try:
            data = {
                "items": self.todo_items,
                "next_id": self.todo_id_counter
            }
            with open(self.todo_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存待办事项失败: {e}")
