import os
import asyncio
import sys
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent, AgentStream
from llama_index.core.workflow import Context

# 全局调试开关，默认关闭调试信息
DEBUG_MODE = False

def debug_print(message):
    """根据调试模式决定是否打印调试信息"""
    if DEBUG_MODE:
        print(f"[调试] {message}")

from tools.windows_tools import (
    get_system_info,
    open_windows_tool,
    get_running_processes,
    check_disk_space,
    find_file,
    show_windows_version
)
from tools.file_operations import (
    create_folder,
    delete_file,
    copy_file,
    move_file,
    read_text_file as read_file,
    create_text_file as write_file,
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

# 导入工具函数
from tools.file_operations import read_tutorial, get_desktop_path

# 创建电脑操作专家智能体
computer_expert_agent = FunctionAgent(
    name="computer_expert_agent",
    description="电脑操作专家，擅长指导用户按照步骤完成各种电脑操作任务，可调用Windows工具和教程。",
    tools=[
        # 文件操作工具（包括实用工具）
        get_desktop_path,
        # Windows系统工具
        get_system_info,
        open_windows_tool,
        get_running_processes,
        check_disk_space,
        find_file,
        show_windows_version,
        
        # 文件操作工具
        create_folder,
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
        debug_print(f"开始处理问题: {prompt}")
        # 如果没有提供上下文，创建一个新的上下文
        if ctx is None:
            ctx = Context(computer_expert_agent)
            debug_print("创建了新的上下文")
        else:
            debug_print("使用现有上下文")
        
        print("\nAI助手回复：")
        # 获取流式处理器
        debug_print("调用computer_expert_agent.run")
        handler = computer_expert_agent.run(prompt, ctx=ctx)
        debug_print("获取到handler，开始stream_events")
        
        # 收集完整响应以便返回
        full_response = ""
        event_count = 0
        
        try:
            # 异步迭代流式事件
            async for event in handler.stream_events():
                event_count += 1
                debug_print(f"收到事件 #{event_count}: {type(event).__name__}")
                if isinstance(event, AgentStream):
                    # 实时打印每个token
                    print(event.delta, end="", flush=True)
                    full_response += event.delta
                    # 每10个事件强制刷新一次
                    if event_count % 10 == 0:
                        debug_print(f"已处理 {event_count} 个事件")
        except asyncio.TimeoutError:
            debug_print("流式处理超时")
        except StopAsyncIteration:
            debug_print("流式处理正常结束")
        except Exception as stream_e:
            debug_print(f"流式处理异常: {stream_e}")
        
        print()  # 添加一个换行符
        debug_print(f"完整响应长度: {len(full_response)} 字符")
        return full_response
    except Exception as e:
        debug_print(f"工作流执行错误：{e}")
        import traceback
        traceback.print_exc()
        return None

# 交互式对话函数（使用流式输出）
async def interactive_chat():
    print("欢迎使用电脑操作专家AI助手！请输入您的电脑操作问题")
    messages = []
    ctx = None
    conversation_count = 0
    MAX_CONVERSATIONS = 3  # 每3轮对话后重置上下文，避免内存泄漏

    try:
        # 声明全局变量
        global DEBUG_MODE
        
        # 启动时显示调试模式状态
        if DEBUG_MODE:
            print("[提示] 调试模式已开启")
        
        while True:
            # 检查是否需要重置上下文
            if conversation_count % MAX_CONVERSATIONS == 0 or ctx is None:
                print(f"\n创建新的对话上下文")
                ctx = Context(computer_expert_agent)
                # 只保留最近的消息
                if len(messages) > 2:
                    messages = messages[-2:]
            
            # 获取用户输入
            try:
                user_input = await asyncio.to_thread(input, "\n您的问题：")
                
                # 检查是否是特殊命令
                if user_input.lower() in ["exit", "quit", "退出", "结束"]:
                    print("感谢使用，再见！")
                    break
                
                # 处理调试模式切换命令
                if user_input.lower() == "/debug on":
                    DEBUG_MODE = True
                    print("[提示] 调试模式已开启")
                    continue
                elif user_input.lower() == "/debug off":
                    DEBUG_MODE = False
                    print("[提示] 调试模式已关闭")
                    continue
                elif user_input.lower() == "/debug":
                    status = "开启" if DEBUG_MODE else "关闭"
                    print(f"[提示] 当前调试模式：{status}")
                    continue

                # 添加用户消息到消息列表
                messages.append({"role": "user", "content": user_input})
                conversation_count += 1

                # 使用超时控制来防止卡住
                print("\nAI助手回复：")
                try:
                    # 调用智能体处理用户请求并流式输出，设置60秒超时
                    await asyncio.wait_for(
                        run_computer_expert_agent_stream(user_input, ctx=ctx), 
                        timeout=60.0
                    )
                except asyncio.TimeoutError:
                    print("\n\n[错误] 对话处理超时！请尝试简化问题。")
                    # 强制重置上下文
                    ctx = Context(computer_expert_agent)
                    print("上下文已重置，可以继续提问。")
                    continue

                # 添加助手回复到消息列表
                messages.append({"role": "assistant", "content": "[助手回复内容]"})

            except Exception as e:
                print(f"\n[错误] 处理输入时发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
                print("\n继续对话...")

    except KeyboardInterrupt:
        print("\n\n程序已中断，再见！")
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n清理资源...")
        # 确保资源被释放
        if ctx:
            del ctx

# 主函数
async def main():
    # 检查命令行参数是否包含调试模式
    global DEBUG_MODE
    if len(sys.argv) > 1:
        if '--debug' in sys.argv:
            DEBUG_MODE = True
            print("[提示] 调试模式已开启")
        elif '--help' in sys.argv:
            print("使用方法：")
            print("  python computer_expert_agent.py              # 正常模式启动")
            print("  python computer_expert_agent.py --debug      # 开启调试模式启动")
            print("  python computer_expert_agent.py --help       # 显示帮助信息")
            return
    
    print("=== 电脑操作专家AI助手 ===")
    print("功能：提供电脑操作指导、故障排除和软件安装配置等服务")
    print("注意：本助手仅支持Windows系统操作")
    print("输入 'exit'、'quit' 或 '退出' 结束对话")
    print("输入 '/debug on' 开启调试模式，输入 '/debug off' 关闭调试模式")
    print("=" * 50)
    
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