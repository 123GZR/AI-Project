import os
import asyncio
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent, AgentStream
from llama_index.core.workflow import Context

from tools.windows_tools import (
    get_system_info,
    open_windows_tool,
    get_running_processes,
    check_disk_space,
    find_file,
    show_windows_version
)
from tools.file_operations import (
    create_directory,
    delete_file,
    copy_file,
    move_file,
    read_file,
    write_file,
    list_directory
)
from tools.mouse_keyboard_tools import (
    get_mouse_position,
    move_mouse,
    move_mouse_relative,
    click_mouse,
    right_click_mouse,
    double_click_mouse,
    drag_mouse,
    press_key,
    type_text,
    hotkey,
    scroll_mouse,
    safe_click_sequence,
    safe_type_and_click
)
from tools.visual_tools import (
    get_screen_size,
    take_screenshot,
    locate_on_screen,
    locate_all_on_screen,
    wait_for_image,
    click_on_image,
    wait_and_click_image,
    capture_screen_region,
    find_text_on_screen,
    get_screen_color_at,
    wait_for_color_change
)

# 加载环境变量
load_dotenv()

# 定义大模型
DASHSCOPE_API_KEY = os.environ.get("QIANWEN_API_KEY")  # 注意这里使用QIANWEN_API_KEY而不是DASHSCOPE_API_KEY
QWEN_API_BASE = os.environ.get("QIANWEN_API_BASE")  # 注意这里使用QIANWEN_API_BASE

# 确保API密钥和基础URL存在
if not DASHSCOPE_API_KEY or not QWEN_API_BASE:
    raise EnvironmentError("请确保.env文件中包含QIANWEN_API_KEY和QIANWEN_API_BASE环境变量")

llm = OpenAI(
    model="qwen-max", 
    api_key=DASHSCOPE_API_KEY, 
    api_base=QWEN_API_BASE,
)

# 定义一些有用的工具函数
def check_file_existence(file_path: str) -> str:
    """检查文件是否存在"""
    if os.path.isfile(file_path):
        return f"文件 '{file_path}' 存在。"
    else:
        return f"文件 '{file_path}' 不存在。"

def list_directory_contents(dir_path: str) -> str:
    """列出目录内容"""
    if os.path.isdir(dir_path):
        try:
            contents = os.listdir(dir_path)
            return f"目录 '{dir_path}' 的内容：\n" + "\n".join(contents)
        except Exception as e:
            return f"无法列出目录内容：{str(e)}"
    else:
        return f"路径 '{dir_path}' 不是一个有效的目录。"

def get_file_size(file_path: str) -> str:
    """获取文件大小（以字节为单位）"""
    if os.path.isfile(file_path):
        try:
            size = os.path.getsize(file_path)
            return f"文件 '{file_path}' 的大小为 {size} 字节。"
        except Exception as e:
            return f"无法获取文件大小：{str(e)}"
    else:
        return f"文件 '{file_path}' 不存在。"

def read_tutorial() -> str:
    """读取教程文档内容，提供给AI作为参考资料"""
    tutorial_path = os.path.join(os.path.dirname(__file__), 'tutorial.md')
    if os.path.isfile(tutorial_path):
        try:
            with open(tutorial_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"教程文档内容：\n{content}"
        except Exception as e:
            return f"读取教程文档时出错：{str(e)}"
    else:
        return "教程文档不存在。"

# 创建电脑操作专家智能体
computer_expert_agent = FunctionAgent(
    name="computer_expert_agent",
    description="电脑操作专家，擅长指导用户按照步骤完成各种电脑操作任务，可调用Windows工具和教程。",
    tools=[
        # 基础工具
        check_file_existence, 
        list_directory_contents, 
        get_file_size,
        
        # Windows系统工具
        get_system_info,
        open_windows_tool,
        get_running_processes,
        check_disk_space,
        find_file,
        show_windows_version,
        
        # 文件操作工具
        create_directory,
        delete_file,
        copy_file,
        move_file,
        read_file,
        write_file,
        list_directory,
        
        # 教程工具
        read_tutorial,
        
        # 鼠标键盘控制工具
        get_mouse_position,
        move_mouse,
        move_mouse_relative,
        click_mouse,
        right_click_mouse,
        double_click_mouse,
        drag_mouse,
        press_key,
        type_text,
        hotkey,
        scroll_mouse,
        safe_click_sequence,
        safe_type_and_click,
        
        # 视觉工具
        get_screen_size,
        take_screenshot,
        locate_on_screen,
        locate_all_on_screen,
        wait_for_image,
        click_on_image,
        wait_and_click_image,
        capture_screen_region,
        find_text_on_screen,
        get_screen_color_at,
        wait_for_color_change
    ],
    llm=llm,
    system_prompt="""你是一位电脑操作专家，擅长指导用户按照步骤完成各种电脑操作任务。

## 技能
### 技能 1: 指导用户进行电脑操作
- 根据用户的需求，提供详细的步骤来完成特定的电脑操作。
- 确定用户需要执行的具体任务。
- 提供清晰、逐步的操作指南，确保用户能够顺利完成任务。
- 解释每个步骤的目的和可能的结果，帮助用户理解整个过程。

### 技能 2: 故障排除
- 当用户在操作过程中遇到问题时，提供故障排除建议。
- 识别用户遇到的具体问题。
- 提供具体的解决方案或建议，帮助用户解决问题。

### 技能 3: 软件安装与配置
- 指导用户安装和配置各种软件。
- 根据用户的需求，推荐合适的软件。
- 提供详细的安装步骤和配置指南。
- 解释软件的功能和使用方法，确保用户能够充分利用软件。

## 限制
- 只提供一种方法。
- 只提供Windows系统的操作步骤。
- 只回答与电脑操作相关的问题，不涉及其他领域。
- 在提供操作步骤时，假设用户具有基本的电脑操作知识。
- 提供的步骤应尽可能详细且易于理解，避免使用过于专业的术语。

## 重要提示
- 当需要回答与Windows系统操作、故障排除或文件操作相关的问题时，请调用read_tutorial工具获取教程内容作为参考。
- 根据问题的具体需求，合理使用提供的工具函数。
- 回答应当基于教程内容和工具执行结果，保持专业性和准确性。
- 执行鼠标和键盘操作时，请确保操作的安全性，避免可能的误操作。
- 控制鼠标移动时，请注意坐标范围，避免超出屏幕边界。
"""
)

# 异步运行工作流（普通输出）
async def run_computer_expert_agent(prompt):
    try:
        # 创建上下文以保持对话状态
        ctx = Context(computer_expert_agent)
        response = await computer_expert_agent.run(prompt, ctx=ctx)
        print("\nAI助手回复：")
        print(response)
        return response
    except Exception as e:
        print(f"工作流执行错误：{e}")
        return None

# 异步运行工作流（流式输出）
async def run_computer_expert_agent_stream(prompt, ctx=None):
    try:
        # 如果没有提供上下文，创建一个新的上下文
        if ctx is None:
            ctx = Context(computer_expert_agent)
        
        print("\nAI助手回复：")
        # 获取流式处理器
        handler = computer_expert_agent.run(prompt, ctx=ctx)
        
        # 收集完整响应以便返回
        full_response = ""
        
        # 异步迭代流式事件
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                # 实时打印每个token
                print(event.delta, end="", flush=True)
                full_response += event.delta
        
        print()  # 添加一个换行符
        return full_response
    except Exception as e:
        print(f"工作流执行错误：{e}")
        return None

# 交互式对话函数（使用流式输出）
async def interactive_chat():
    print("欢迎使用电脑操作专家AI助手！")
    print("请输入您的电脑操作问题，输入 'exit' 或 'quit' 退出对话。")
    
    # 创建上下文以保持整个对话状态
    ctx = Context(computer_expert_agent)
    
    while True:
        user_input = input("\n您的问题：")
        
        if user_input.lower() in ['exit', 'quit', '退出', '结束']:
            print("感谢使用，再见！")
            break
        
        try:
            # 使用流式输出函数
            await run_computer_expert_agent_stream(user_input, ctx=ctx)
        except Exception as e:
            print(f"发生错误：{e}")

# 主函数
async def main():
    # 可以选择运行交互式对话或直接回答一个问题
    # 示例：直接回答一个问题（使用流式输出）
    # await run_computer_expert_agent_stream("如何在Windows上查看系统信息？")
    
    # 运行交互式对话（默认使用流式输出）
    await interactive_chat()

if __name__ == "__main__":
    try:
        # 尝试导入nest_asyncio来处理可能的嵌套事件循环问题
        try:
            import nest_asyncio
            nest_asyncio.apply()
            print("已应用nest_asyncio以支持嵌套事件循环")
        except ImportError:
            print("未安装nest_asyncio，可能在某些环境中会遇到嵌套事件循环问题")
        
        # 运行主函数
        asyncio.run(main())
    except Exception as e:
        print(f"程序启动错误：{e}")
        print("请确保已安装所有必要的依赖：pip install llama-index python-dotenv nest-asyncio")