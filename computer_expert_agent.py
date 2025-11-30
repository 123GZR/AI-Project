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

# 从tools包导入所有工具
from tools import ALL_TOOLS

# 创建电脑操作专家智能体
computer_expert_agent = FunctionAgent(
    name="computer_expert_agent",
    description="电脑操作专家，擅长指导用户按照步骤完成各种电脑操作任务，可调用Windows工具和教程。",
    tools=ALL_TOOLS,
    llm=llm,
    system_prompt="""我是一个专业的电脑操作专家AI助手，我的目标是帮助用户解决电脑操作相关的问题，提供详细的操作指导，并在必要时使用工具获取实时信息。

## 我的角色与职责
- 作为电脑操作专家，我负责提供准确、实用的电脑操作指导
- 帮助用户解决日常使用中遇到的技术问题
- 提供软件安装、配置和故障排除的支持
- 针对Windows系统提供专业的操作建议

## 核心指令

### 1. 工具优先原则
- 对于需要实时信息的问题，**必须**优先调用工具获取最新数据，而不是依赖记忆中的知识
- 必须调用工具的场景包括：系统信息查询、已安装软件列表、磁盘空间检查、进程管理、文件查找、文件夹创建、截图、点击操作、工具打开、教程阅读
- 在调用工具前，必须确保有明确的工具调用参数，避免无效调用
- 对于需要实时信息的问题，禁止在没有工具调用结果的情况下进行推测性回答

### 2. 高质量回答
- 回答必须基于工具调用结果，确保信息的准确性和时效性
- 提供详细、步骤清晰的操作指导，避免模糊不清的表述
- 使用友好、专业的语言，避免技术术语的滥用
- 对于复杂问题，分步骤解答，确保用户能够轻松理解和跟随

### 3. 多步骤任务处理
- 对于需要多个步骤完成的任务，必须规划清晰的步骤顺序
- 每完成一个步骤后，向用户提供明确的反馈
- 对于操作类任务，先检查条件，再执行操作，最后验证结果

## 技能
### 技能 1: 指导用户进行电脑操作
- 提供详细、步骤清晰的操作指导
- 使用截图和具体操作说明相结合的方式
- 关注用户体验，确保指导易于理解和执行

### 技能 2: 故障排除
- 系统性地分析问题症状
- 提供逐步的故障排除步骤
- 使用工具获取系统信息，帮助诊断问题

### 技能 3: 软件安装与配置
- 提供软件安装的详细步骤
- 指导用户进行必要的配置调整
- 解决常见的安装和配置问题

## 注意事项
- 所有回答必须使用中文
- 始终基于工具执行结果来提供回答，确保信息的准确性和时效性。
- 对于复杂任务，在开始执行操作前，先获取必要的环境信息（如系统信息、屏幕尺寸等）。
- 即使没有明确的步骤指导，也要主动规划完整的操作流程并按顺序调用相应工具。""")

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
def analyze_task_type(user_input):
    """分析用户输入的任务类型，推断隐含意图，并返回对应的工具调用建议"""
    # 默认返回通用帮助类型和read_tutorial工具
    return 'general_help', ['read_tutorial'], []

async def run_computer_expert_agent_stream(user_input, ctx=None, callback=None):
    # 分析任务类型
    task_type, suggested_tools, _ = analyze_task_type(user_input)
    
    # 增强用户输入，添加任务类型分析和工具调用建议
    enhanced_input = f"""
用户请求: {user_input}

任务分析:
- 任务类型: {task_type}
- 建议使用工具: {suggested_tools}
- 操作指导: 请根据任务类型选择合适的工具调用顺序，优先使用建议的工具获取实时信息。
"""
    
    # 调试输出
    debug_print(f"\n任务类型分析: {task_type}")
    debug_print(f"建议工具: {suggested_tools}")
    debug_print(f"增强后的用户输入:\n{enhanced_input}")
    
    # 使用增强后的用户输入调用AI
    return await stream_chat_with_agent(enhanced_input, computer_expert_agent, ctx=ctx, callback=callback)

async def stream_chat_with_agent(prompt, agent, ctx=None, callback=None):
    try:
        # 如果没有提供上下文，创建一个新的上下文
        if ctx is None:
            ctx = Context(agent)
            debug_print("创建了新的上下文")
        else:
            debug_print("使用现有上下文")
        
        debug_print("调用agent.run")
        handler = agent.run(prompt, ctx=ctx)
        debug_print("获取到handler，开始stream_events")
        
        # 收集完整响应以便返回
        full_response = ""
        event_count = 0
        
        try:
            # 异步迭代流式事件
            async for event in handler.stream_events():
                event_count += 1
                debug_print(f"收到事件 #{event_count}: {type(event).__name__}")
                debug_print(f"事件内容: {event}")
                
                # 处理不同类型的事件
                if isinstance(event, AgentStream):
                    # 实时打印每个token
                    print(event.delta, end="", flush=True)
                    full_response += event.delta
                    # 调用回调函数（如果提供）
                    if callback:
                        callback(event.delta)
                    # 每10个事件强制刷新一次
                    if event_count % 10 == 0:
                        debug_print(f"已处理 {event_count} 个事件")
                elif hasattr(event, 'message'):
                    # 处理包含message属性的事件
                    message_content = event.message
                    print(message_content, end="", flush=True)
                    full_response += message_content
                    # 调用回调函数（如果提供）
                    if callback:
                        callback(message_content)
                elif hasattr(event, 'content'):
                    # 处理包含content属性的事件
                    print(event.content, end="", flush=True)
                    full_response += event.content
                    # 调用回调函数（如果提供）
                    if callback:
                        callback(event.content)
        except asyncio.TimeoutError:
            debug_print("流式处理超时")
        except StopAsyncIteration:
            debug_print("流式处理正常结束")
        except Exception as stream_e:
            debug_print(f"流式处理异常: {stream_e}")
            import traceback
            traceback.print_exc()
        
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

    # 工具关键词映射表，用于预处理用户输入
    tool_keywords = {
        '系统信息': 'get_system_info',
        'Windows版本': 'show_windows_version',
        '已安装软件': 'get_installed_applications',
        '磁盘空间': 'check_disk_space',
        '进程': 'get_running_processes',
        '查找文件': 'find_file',
        '文件操作': 'list_directory',
        '创建文件夹': 'create_folder',
        '打开工具': 'open_windows_tool',
        '截图': 'screenshot',
        '点击': 'click_on_image',
        '教程': 'read_tutorial'
    }

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

                # 预处理：检查用户输入是否包含需要使用工具的关键词
                # 添加工具调用提示，提高AI调用工具的主动性
                processed_input = user_input
                tool_hint_added = False
                for keyword, tool_name in tool_keywords.items():
                    if keyword in user_input and not tool_hint_added:
                        processed_input += f"\n[系统提示：此问题可能需要使用{tool_name}工具获取实时信息，请优先调用工具。]"
                        tool_hint_added = True
                        break

                # 添加用户消息到消息列表
                messages.append({"role": "user", "content": processed_input})
                conversation_count += 1

                # 使用超时控制来防止卡住
                print("\nAI助手回复：")
                try:
                    # 调用智能体处理用户请求并流式输出，设置60秒超时
                    assistant_response = await asyncio.wait_for(
                        run_computer_expert_agent_stream(processed_input, ctx=ctx), 
                        timeout=180.0
                    )
                except asyncio.TimeoutError:
                    print("\n\n[错误] 对话处理超时！请尝试简化问题。")
                    # 强制重置上下文
                    ctx = Context(computer_expert_agent)
                    print("上下文已重置，可以继续提问。")
                    continue

                # 添加助手回复到消息列表
                messages.append({"role": "assistant", "content": assistant_response})

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
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        if '--debug' in sys.argv:
            DEBUG_MODE = True
            print("[提示] 调试模式已开启")
        elif '--help' in sys.argv:
            print("使用方法：")
            print("  python computer_expert_agent.py              # 正常模式启动")
            print("  python computer_expert_agent.py --debug      # 开启调试模式启动")
            print("  python computer_expert_agent.py --help       # 显示帮助信息")
            print("  python computer_expert_agent.py '问题'       # 直接回答指定问题")
            return
    
    # 如果有非选项参数，直接回答问题
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        question = ' '.join(sys.argv[1:])
        print("=== 电脑操作专家AI助手 ===")
        print(f"您的问题：{question}")
        await run_computer_expert_agent_stream(question)
    else:
        # 否则进入交互式对话
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
