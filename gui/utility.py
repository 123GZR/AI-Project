import tkinter as tk
from tkinter import ttk

def show_toast(root, message, duration=2000):
    """显示提示信息"""
    toast = tk.Toplevel(root)
    toast.title("")
    toast.geometry("200x50")
    toast.resizable(False, False)
    toast.overrideredirect(True)  # 去掉窗口边框
    
    # 设置背景色和文字
    toast.configure(bg="#333333")
    label = ttk.Label(toast, text=message, foreground="white", background="#333333")
    label.pack(expand=True, fill=tk.BOTH)
    
    # 计算位置（右下角）
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    
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
        root.after(50)
