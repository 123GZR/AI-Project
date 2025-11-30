import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
import os
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
        """创建左侧工具导航"""
        nav_frame = ttk.LabelFrame(self.content_frame, text="工具分类", width=200)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N)
        nav_frame.pack_propagate(False)
        
        # 工具分类
        tool_categories = {
            "Windows系统工具": ["get_system_info", "open_windows_tool", "get_running_processes", "check_disk_space", "find_file", "show_windows_version", "get_installed_applications"],
            "文件操作工具": ["create_folder", "delete_file", "copy_file", "move_file", "read_file", "write_file", "list_directory", "read_tutorial"],
            "鼠标键盘控制工具": ["get_mouse_position", "move_mouse", "click_mouse", "type_text", "hotkey"],
            "视觉工具": ["take_screenshot", "click_on_image", "find_text_on_screen"]
        }
        
        # 创建工具分类树
        self.tool_tree = ttk.Treeview(nav_frame, show="tree", selectmode="browse")
        self.tool_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加工具分类到树
        for category, tools in tool_categories.items():
            parent = self.tool_tree.insert("", tk.END, text=category, open=False)
            for tool in tools:
                self.tool_tree.insert(parent, tk.END, text=tool)
        
        # 工具搜索框
        search_frame = ttk.Frame(nav_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        search_label = ttk.Label(search_frame, text="搜索工具:")
        search_label.pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
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
        
        # 工具树点击事件
        self.tool_tree.bind("<<TreeviewSelect>>", self.on_tool_select)
        
        # 搜索框事件
        self.search_var.trace("w", self.on_tool_search)
    
    def on_enter(self, event):
        """处理回车键发送消息"""
        self.send_message()
        return "break"
    
    def on_shift_enter(self, event):
        """处理Shift+回车键换行"""
        self.input_text.insert(tk.INSERT, "\n")
        return "break"
    
    def on_tool_select(self, event):
        """处理工具选择事件"""
        selection = self.tool_tree.selection()
        if selection:
            item = self.tool_tree.item(selection[0])
            tool_name = item["text"]
            # 这里可以添加工具详细说明的显示
            print(f"选中工具: {tool_name}")
    
    def on_tool_search(self, *args):
        """处理工具搜索"""
        search_text = self.search_var.get().lower()
        # 这里可以添加搜索逻辑
        print(f"搜索工具: {search_text}")
    
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
        except Exception as e:
            error_msg = f"AI助手出错: {str(e)}"
            self.root.after(0, self.add_message, "系统", error_msg, True)
            self.root.after(0, self.update_status, "空闲")
            import traceback
            traceback.print_exc()
    
    def update_ai_response(self, chunk):
        """更新AI助手的回复"""
        self.chat_history.config(state=tk.NORMAL)
        
        # 检查是否需要添加AI前缀
        last_line = self.chat_history.get("end-2l", "end-1l").strip()
        if not last_line or not last_line.startswith("AI助手:"):
            self.chat_history.insert(tk.END, "AI助手: ", "ai")
        
        # 添加回复内容
        self.chat_history.insert(tk.END, chunk)
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)
    
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
