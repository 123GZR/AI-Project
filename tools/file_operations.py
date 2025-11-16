import os
import shutil
import time
from datetime import datetime
from typing import List, Optional

def create_folder(folder_path: str) -> str:
    """创建新文件夹
    
    参数:
        folder_path: 要创建的文件夹路径
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"文件夹 '{folder_path}' 已成功创建"
    except Exception as e:
        return f"创建文件夹时出错: {str(e)}"

def delete_file(file_path: str) -> str:
    """删除文件
    
    参数:
        file_path: 要删除的文件路径
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"文件 '{file_path}' 已成功删除"
        else:
            return f"路径 '{file_path}' 不是一个有效的文件"
    except Exception as e:
        return f"删除文件时出错: {str(e)}"

def delete_folder(folder_path: str, recursive: bool = False) -> str:
    """删除文件夹
    
    参数:
        folder_path: 要删除的文件夹路径
        recursive: 是否递归删除（如果为True，则删除文件夹及其所有内容；如果为False，只删除空文件夹）
    """
    try:
        if os.path.isdir(folder_path):
            if recursive:
                shutil.rmtree(folder_path)
                return f"文件夹 '{folder_path}' 及其所有内容已成功删除"
            else:
                os.rmdir(folder_path)
                return f"空文件夹 '{folder_path}' 已成功删除"
        else:
            return f"路径 '{folder_path}' 不是一个有效的文件夹"
    except OSError as e:
        if "Directory not empty" in str(e) and not recursive:
            return f"文件夹 '{folder_path}' 不为空，请使用 recursive=True 参数递归删除所有内容"
        return f"删除文件夹时出错: {str(e)}"

def copy_file(source_path: str, destination_path: str) -> str:
    """复制文件
    
    参数:
        source_path: 源文件路径
        destination_path: 目标文件路径
    """
    try:
        if os.path.isfile(source_path):
            # 确保目标文件夹存在
            destination_dir = os.path.dirname(destination_path)
            if destination_dir and not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)
            
            shutil.copy2(source_path, destination_path)
            return f"文件已从 '{source_path}' 成功复制到 '{destination_path}'"
        else:
            return f"源路径 '{source_path}' 不是一个有效的文件"
    except Exception as e:
        return f"复制文件时出错: {str(e)}"

def move_file(source_path: str, destination_path: str) -> str:
    """移动文件
    
    参数:
        source_path: 源文件路径
        destination_path: 目标文件路径
    """
    try:
        if os.path.exists(source_path):
            # 确保目标文件夹存在
            destination_dir = os.path.dirname(destination_path)
            if destination_dir and not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)
            
            shutil.move(source_path, destination_path)
            return f"文件已从 '{source_path}' 成功移动到 '{destination_path}'"
        else:
            return f"源路径 '{source_path}' 不存在"
    except Exception as e:
        return f"移动文件时出错: {str(e)}"

def get_file_info(file_path: str) -> str:
    """获取文件详细信息
    
    参数:
        file_path: 文件路径
    """
    try:
        if os.path.isfile(file_path):
            # 获取文件基本信息
            stats = os.stat(file_path)
            file_size = stats.st_size
            created_time = datetime.fromtimestamp(stats.st_ctime)
            modified_time = datetime.fromtimestamp(stats.st_mtime)
            accessed_time = datetime.fromtimestamp(stats.st_atime)
            
            # 格式化文件大小
            def format_size(size_bytes):
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size_bytes < 1024 or unit == 'TB':
                        return f"{size_bytes:.2f} {unit}"
                    size_bytes /= 1024
            
            return (
                f"文件信息 '{file_path}':\n"
                f"大小: {format_size(file_size)}\n"
                f"创建时间: {created_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"修改时间: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"访问时间: {accessed_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"是否只读: {'是' if not os.access(file_path, os.W_OK) else '否'}"
            )
        else:
            return f"路径 '{file_path}' 不是一个有效的文件"
    except Exception as e:
        return f"获取文件信息时出错: {str(e)}"

def list_directory(directory_path: str, show_hidden: bool = False) -> str:
    """列出目录内容
    
    参数:
        directory_path: 目录路径
        show_hidden: 是否显示隐藏文件和文件夹
    """
    try:
        if os.path.isdir(directory_path):
            # 获取目录内容
            items = []
            for item in os.listdir(directory_path):
                # 跳过隐藏文件（除非指定显示）
                if not show_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item)
                is_dir = os.path.isdir(item_path)
                item_type = "[目录]" if is_dir else "[文件]"
                
                # 如果是文件，获取大小
                if not is_dir:
                    size = os.path.getsize(item_path)
                    def format_size(size_bytes):
                        for unit in ['B', 'KB', 'MB', 'GB']:
                            if size_bytes < 1024 or unit == 'GB':
                                return f"{size_bytes:.2f} {unit}"
                            size_bytes /= 1024
                    items.append(f"{item_type} {item} - {format_size(size)}")
                else:
                    items.append(f"{item_type} {item}")
            
            if items:
                return f"目录 '{directory_path}' 的内容 ({len(items)} 项):\n" + "\n".join(items)
            else:
                return f"目录 '{directory_path}' 为空"
        else:
            return f"路径 '{directory_path}' 不是一个有效的目录"
    except Exception as e:
        return f"列出目录内容时出错: {str(e)}"

def create_text_file(file_path: str, content: str = "") -> str:
    """创建文本文件
    
    参数:
        file_path: 要创建的文件路径
        content: 文件内容（可选）
    """
    try:
        # 确保文件夹存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"文本文件 '{file_path}' 已成功创建"
    except Exception as e:
        return f"创建文本文件时出错: {str(e)}"

def read_text_file(file_path: str, max_lines: Optional[int] = None) -> str:
    """读取文本文件内容
    
    参数:
        file_path: 文件路径
        max_lines: 最多读取的行数（可选）
    """
    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                if max_lines:
                    lines = [next(f) for _ in range(max_lines)]
                    content = ''.join(lines)
                    # 检查是否还有更多内容
                    if f.readline():
                        content += "\n[...内容过多，已截断...]"
                else:
                    content = f.read()
            
            # 如果文件太大，限制返回内容大小
            if len(content) > 10000:
                content = content[:10000] + "\n[...内容过多，已截断...]"
            
            return f"文件 '{file_path}' 的内容:\n{content}"
        else:
            return f"路径 '{file_path}' 不是一个有效的文件"
    except UnicodeDecodeError:
        return f"无法读取文件 '{file_path}'，可能是二进制文件"
    except Exception as e:
        return f"读取文件时出错: {str(e)}"

def get_desktop_path() -> str:
    """获取当前用户的桌面路径，自动适应不同操作系统"""
    try:
        # 使用os.path.expanduser获取当前用户主目录（自动处理不同用户名）
        user_home = os.path.expanduser("~")
        
        # 在Windows系统上，桌面路径通常是用户主目录下的Desktop文件夹
        if os.name == 'nt':  # Windows系统
            desktop_path = os.path.join(user_home, "Desktop")
        else:  # 非Windows系统（虽然程序主要针对Windows）
            desktop_path = os.path.join(user_home, "Desktop")
        
        # 验证路径是否存在且为目录
        if os.path.exists(desktop_path) and os.path.isdir(desktop_path):
            return f"当前用户的桌面路径是: {desktop_path}"
        else:
            # 尝试查找常见的桌面路径变体
            common_desktop_paths = [
                os.path.join(user_home, "桌面"),  # 中文Windows
                os.path.join(user_home, "Desktop"),  # 英文Windows
                os.path.join(os.path.join(os.environ.get('USERPROFILE', user_home), "Desktop"))  # 使用环境变量
            ]
            
            for path in common_desktop_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    return f"当前用户的桌面路径是: {path}"
            
            return f"无法找到桌面目录。尝试过的路径: {desktop_path}"
    except Exception as e:
        return f"获取桌面路径时出错: {str(e)}"

def read_tutorial() -> str:
    """读取教程文档内容，提供给AI作为参考资料"""
    try:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tutorial_path = os.path.join(script_dir, 'tutorial.md')
        
        if os.path.isfile(tutorial_path):
            try:
                with open(tutorial_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"教程文档内容：\n{content}"
            except Exception as e:
                return f"读取教程文档时出错：{str(e)}"
        else:
            return f"教程文档不存在于路径：{tutorial_path}"
    except Exception as e:
        return f"查找教程文档时出错：{str(e)}"
