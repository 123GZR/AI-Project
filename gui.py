import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
import os
import json
from datetime import datetime
from computer_expert_agent import run_computer_expert_agent_stream, DEBUG_MODE

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
        self.create_title_bar()
        
        # 创建中间内容区域
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建左侧工具导航
        self.create_tool_navigation()
        
        # 创建右侧聊天区域
        self.chat_frame = ttk.Frame(self.content_frame)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 创建聊天历史区域
        self.create_chat_history()
        
        # 创建输入区域
        self.create_input_area()
        
        # 创建状态显示
        self.create_status_bar()
        
        # 绑定事件
        self.bind_events()
        
        # 显示欢迎信息
        self.add_message("系统", "欢迎使用电脑操作专家AI助手！请输入您的电脑操作问题。", is_system=True)
    
    def create_title_bar(self):
        """创建顶部标题栏"""
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X)
        
        # 标题
        title_label = ttk.Label(title_frame, text="电脑操作专家AI助手", font=('微软雅黑', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # 调试模式开关
        debug_frame = ttk.Frame(title_frame)
        debug_frame.pack(side=tk.RIGHT)
        
        self.debug_var = tk.BooleanVar(value=self.debug_mode)
        debug_check = ttk.Checkbutton(debug_frame, text="调试模式", variable=self.debug_var, command=self.toggle_debug)
        debug_check.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_tool_navigation(self):
        """创建左侧待办事项列表"""
        # 初始化待办事项数据
        self.todo_items = []
        self.todo_id_counter = 1
        self.todo_file = "todos.json"
        
        # 创建待办事项框架
        nav_frame = ttk.LabelFrame(self.content_frame, text="待办事项", width=250)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N)
        nav_frame.pack_propagate(False)
        
        # 待办事项列表
        self.todo_listbox = tk.Listbox(
            nav_frame, 
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
        scrollbar = ttk.Scrollbar(nav_frame, orient=tk.VERTICAL, command=self.todo_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_listbox.config(yscrollcommand=scrollbar.set)
        
        # 待办事项输入框
        input_frame = ttk.Frame(nav_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.todo_input = ttk.Entry(input_frame, width=25, font=('微软雅黑', 10))
        self.todo_input.pack(side=tk.LEFT, padx=(0, 5))
        self.todo_input.bind("<Return>", self.add_todo)
        
        # 添加按钮
        add_button = ttk.Button(input_frame, text="添加", command=self.add_todo, width=6)
        add_button.pack(side=tk.LEFT)
        
        # 操作按钮框架
        action_frame = ttk.Frame(nav_frame)
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
            self.show_toast("待办事项已添加")
    
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
            self.show_toast(f"待办事项已标记为{todo['status']}")
    
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
                    self.show_toast("待办事项已更新")
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
                self.show_toast("待办事项已删除")
    
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
    
    def show_toast(self, message, duration=2000):
        """显示提示信息"""
        toast = tk.Toplevel(self.root)
        toast.title("")
        toast.geometry("200x50")
        toast.resizable(False, False)
        toast.overrideredirect(True)  # 去掉窗口边框
        
        # 设置背景色和文字
        toast.configure(bg="#333333")
        label = ttk.Label(toast, text=message, foreground="white", background="#333333")
        label.pack(expand=True, fill=tk.BOTH)
        
        # 计算位置（右下角）
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        toast_width = 200
        toast_height = 50
        
        x = root_x + root_width - toast_width - 10
        y = root_y + root_height - toast_height - 10
        
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
        
        # 设置透明度
        toast.attributes("-alpha", 0.8)
        
        # 自动关闭
        def close_toast():
            toast.destroy()
        
        toast.after(duration, close_toast)
        
        # 显示动画
        for i in range(10):
            alpha = 0.8 * (i / 10)
            toast.attributes("-alpha", alpha)
            toast.update()
            self.root.after(50)
    
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
        send_button = ttk.Button(button_frame, text="发送", command=self.send_message, style="Accent.TButton")
        send_button.pack(side=tk.RIGHT)
        
        # 设置发送按钮样式
        self.style.configure("Accent.TButton", foreground="white", background="#0078d7")
    
    def create_status_bar(self):
        """创建状态显示栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        # AI状态
        self.status_var = tk.StringVar(value=f"AI状态: {self.ai_status}")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # API状态
        self.api_status_var = tk.StringVar(value="API状态: 已连接")
        api_label = ttk.Label(status_frame, textvariable=self.api_status_var, anchor=tk.E)
        api_label.pack(side=tk.RIGHT)
    
    def bind_events(self):
        """绑定事件"""
        # 输入框回车发送，Shift+回车换行
        self.input_text.bind("<Return>", self.on_enter)
        self.input_text.bind("<Shift-Return>", self.on_shift_enter)
    
    def on_enter(self, event):
        """处理回车键发送消息"""
        self.send_message()
        return "break"
    
    def on_shift_enter(self, event):
        """处理Shift+回车键换行"""
        self.input_text.insert(tk.INSERT, "\n")
        return "break"
    
    def toggle_debug(self):
        """切换调试模式"""
        self.debug_mode = self.debug_var.get()
        global DEBUG_MODE
        DEBUG_MODE = self.debug_mode
        self.add_message("系统", f"调试模式已{'开启' if self.debug_mode else '关闭'}", is_system=True)
    
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
    
    def send_message(self):
        """发送消息"""
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return
        
        # 添加用户消息
        self.add_message("我", message)
        
        # 清空输入框
        self.input_text.delete("1.0", tk.END)
        
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
        self.chat_history.config(state=tk.NORMAL)
        
        # 过滤掉chunk中所有的"AI助手:"前缀
        filtered_chunk = chunk.replace("AI助手:", "")
        
        # 检查是否需要添加AI前缀
        if not self.is_ai_responding:
            # 如果不是正在回复状态，添加完整的AI回复
            self.is_ai_responding = True
            self.chat_history.insert(tk.END, "AI助手: ", "ai")
        elif not self.current_ai_response:
            # 如果是第一次收到回复，添加前缀
            self.chat_history.insert(tk.END, "AI助手: ", "ai")
        
        # 添加过滤后的回复内容
        if filtered_chunk:
            self.chat_history.insert(tk.END, filtered_chunk)
            self.current_ai_response += filtered_chunk
            self.chat_history.see(tk.END)
        
        self.chat_history.config(state=tk.DISABLED)
    
    def end_ai_response(self):
        """结束AI回复"""
        self.is_ai_responding = False
        self.current_ai_response = ""
    
    def update_status(self, status):
        """更新AI状态"""
        self.ai_status = status
        self.status_var.set(f"AI状态: {self.ai_status}")
    
    def clear_chat(self):
        """清空聊天记录"""
        if messagebox.askyesno("确认", "确定要清空聊天记录吗？"):
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)
            self.add_message("系统", "聊天记录已清空", is_system=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComputerExpertGUI(root)
    root.mainloop()
