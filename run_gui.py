#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手启动脚本
自动使用项目内置Python解释器运行gui.py
"""

import os
import sys
import subprocess

def main():
    """主函数"""
    try:
        # 判断是否在PyInstaller打包环境中
        if getattr(sys, 'frozen', False):
            # 打包环境下，使用当前工作目录作为项目根目录
            # 因为exe文件会被放在项目根目录，当前工作目录就是项目根目录
            root_dir = os.getcwd()
        else:
            # 普通环境下，使用脚本所在目录作为项目根目录
            root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建文件路径
        python_exe = os.path.join(root_dir, "python", "python.exe")
        gui_file = os.path.join(root_dir, "gui.py")
        
        # 检查文件是否存在
        if not os.path.exists(python_exe):
            print(f"错误：找不到Python解释器：{python_exe}")
            input("按回车键退出...")
            sys.exit(1)
        
        if not os.path.exists(gui_file):
            print(f"错误：找不到GUI文件：{gui_file}")
            input("按回车键退出...")
            sys.exit(1)
        
        # 启动GUI应用
        subprocess.Popen([python_exe, gui_file], cwd=root_dir)
        print("AI助手已成功启动！")
        
    except Exception as e:
        print(f"启动出错：{str(e)}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()

