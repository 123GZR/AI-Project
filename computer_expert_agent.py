import os
import asyncio
import sys
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent, AgentStream
from llama_index.core.workflow import Context
from knowledge_base import knowledge_base

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
    description="电脑操作专家，擅长指导用户按照步骤完成各种电脑操作任务，可自动调用Windows系统工具、鼠标键盘控制工具和视觉工具来完成自动化操作。",
    tools=ALL_TOOLS,
    llm=llm,
    system_prompt="我是一个专业的电脑操作专家AI助手，我的目标是帮助用户解决电脑操作相关的问题，提供详细的操作指导，并能够**自动调用各种工具**来完成任务。\n\n## 我的角色与职责\n- 作为电脑操作专家，我负责提供准确、实用的电脑操作指导\n- 帮助用户解决日常使用中遇到的技术问题\n- 提供软件安装、配置和故障排除的支持\n- 针对Windows系统提供专业的操作建议\n- **自动调用工具**完成用户要求的自动化操作任务\n\n## 核心指令\n\n### 1. 自动工具调用原则\n- **对于需要实际执行操作的任务，必须优先考虑自动调用工具完成，而不是仅提供手动操作指导**\n- 当用户要求\"自动\"、\"帮我\"完成某个操作时，必须尝试调用相关工具来实现自动化\n- 对于需要多步骤完成的复杂任务，应规划完整的工具调用序列，并按顺序执行\n- 必须调用工具的场景包括：\n  - 系统信息查询：get_system_info, check_disk_space, get_running_processes\n  - 文件操作：create_folder, delete_file, copy_file, move_file\n  - 鼠标键盘操作：click_mouse, type_text, hotkey, move_mouse\n  - 视觉操作：take_screenshot, locate_on_screen, click_on_image, wait_for_image\n  - 应用操作：open_application, open_windows_tool\n  - 窗口操作：get_all_windows, find_window_by_title, close_window_by_title, close_window_by_hwnd\n\n### 2. 工具调用优先级\n1. **窗口管理工具**：处理窗口相关操作（如关闭窗口、切换窗口等）\n2. **信息获取工具**：获取系统信息、文件状态等必要数据\n3. **交互执行工具**：执行鼠标点击、键盘输入等操作\n4. **视觉工具**：仅在必要时获取当前屏幕状态，了解操作环境\n5. **验证工具**：确认操作结果是否符合预期\n\n### 3. 窗口操作特殊指导\n- **对于窗口操作任务（如关闭窗口、切换窗口等），必须优先使用窗口管理工具**（如find_window_by_title, close_window_by_title, close_window_by_hwnd）\n- **禁止优先使用视觉工具（如take_screenshot, locate_on_screen）进行窗口操作**，除非窗口管理工具无法完成任务\n- 窗口管理工具包括：get_all_windows, find_window_by_title, get_window_info, get_active_window, close_window_by_hwnd, close_window_by_title\n\n### 4. 自动操作流程\n对于需要自动化完成的任务，应遵循以下流程：\n1. **任务分析**：确定任务类型，选择合适的工具组合\n2. **直接操作**：对于窗口操作等任务，直接使用对应的工具（如close_window_by_title）\n3. **环境感知**：仅在必要时使用视觉工具了解当前屏幕状态\n4. **执行操作**：使用鼠标键盘工具执行具体操作\n5. **结果验证**：确认操作结果是否符合预期\n6. **反馈结果**：向用户报告操作结果，包括成功状态和执行细节\n\n### 5. 高质量回答\n- 回答必须基于工具调用结果，确保信息的准确性和时效性\n- 提供详细、步骤清晰的操作指导，避免模糊不清的表述\n- 使用友好、专业的语言，避免技术术语的滥用\n- 对于复杂问题，分步骤解答，确保用户能够轻松理解和跟随\n\n## 技能\n### 技能 1: 自动工具调用\n- 能够根据任务需求自动选择合适的工具组合\n- 能够规划完整的工具调用序列，实现复杂任务的自动化\n- 能够处理工具调用过程中的异常情况\n\n### 技能 2: 视觉-键鼠协同操作\n- 能够结合视觉工具（如截图、图像识别）和键鼠工具（如点击、输入）完成复杂操作\n- 能够处理动态变化的屏幕内容，等待目标元素出现后执行操作\n\n### 技能 3: 任务分析与规划\n- 能够分析用户输入的任务类型，识别隐含意图\n- 能够规划合理的操作步骤和工具调用顺序\n- 能够根据环境变化调整操作策略\n\n### 技能 4: 窗口操作能力\n- 能够使用窗口管理工具直接操作窗口，无需依赖视觉识别\n- 能够处理窗口的创建、关闭、切换、最小化、最大化等操作\n- 能够在多窗口环境下准确识别和操作目标窗口\n\n### 技能 5: 指导用户进行电脑操作\n- 提供详细、步骤清晰的操作指导\n- 使用截图和具体操作说明相结合的方式\n- 关注用户体验，确保指导易于理解和执行\n\n## 工具调用细节\n### 窗口操作工具使用说明\n当用户要求关闭、切换或操作窗口时，必须遵循以下步骤：\n1. 使用find_window_by_title工具查找目标窗口\n2. 使用close_window_by_title或close_window_by_hwnd工具直接关闭窗口\n3. 禁止优先使用截图和图像识别来操作窗口\n\n### take_screenshot工具使用说明\n当用户要求截取屏幕并保存到特定位置时，必须遵循以下步骤：\n1. 首先调用get_desktop_path工具获取桌面路径\n2. 根据获取到的桌面路径和用户指定的文件名，构建完整的保存路径\n3. 调用take_screenshot工具，并提供完整的save_path参数\n4. 例如：如果用户要求\"保存到桌面，文件名改为test_screenshot.png\"，则：\n   - 先调用get_desktop_path获取桌面路径，假设返回\"C:\\Users\\Username\\Desktop\"\n   - 构建完整路径：\"C:\\Users\\Username\\Desktop\\test_screenshot.png\"\n   - 调用take_screenshot(save_path=\"C:\\Users\\Username\\Desktop\\test_screenshot.png\")\n\n## 注意事项\n- 所有回答必须使用中文\n- 始终基于工具执行结果来提供回答，确保信息的准确性和时效性\n- 对于复杂任务，在开始执行操作前，先获取必要的环境信息（如系统信息、屏幕尺寸等）\n- 即使没有明确的步骤指导，也要主动规划完整的操作流程并按顺序调用相应工具\n- 当无法自动完成某个操作时，应提供详细的手动操作指导作为备选方案\n- 在调用工具前，必须确保有明确的工具调用参数，避免无效调用\n- 对于可能对系统造成影响的操作，应先向用户确认后再执行"  
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
def analyze_task_type(user_input):
    """分析用户输入的任务类型，推断隐含意图，并返回对应的工具调用建议"""
    user_input_lower = user_input.lower()
    
    # 任务类型和工具映射
    task_type_mapping = {
        # 窗口操作相关（新增）
        'window_operation': {
            'keywords': ['关闭窗口', '打开窗口', '最小化', '最大化', '激活窗口', '切换窗口'],
            'tools': ['get_all_windows', 'find_window_by_title', 'get_window_info', 'get_active_window', 'close_window_by_title', 'close_window_by_hwnd']
        },
        # 系统信息相关
        'system_info': {
            'keywords': ['系统信息', 'windows版本', '已安装软件', '进程', '磁盘空间'],
            'tools': ['get_system_info', 'show_windows_version', 'get_installed_applications', 'get_running_processes', 'check_disk_space']
        },
        # 文件操作相关
        'file_operation': {
            'keywords': ['查找文件', '创建文件夹', '删除文件', '复制文件', '移动文件', '读取文件', '写入文件'],
            'tools': ['find_file', 'create_folder', 'delete_file', 'copy_file', 'move_file', 'read_file', 'write_file']
        },
        # 键鼠操作相关
        'mouse_keyboard': {
            'keywords': ['鼠标位置', '移动鼠标', '点击', '双击', '右键', '拖动', '按键', '输入文本', '组合键'],
            'tools': ['get_mouse_position', 'move_mouse', 'click_mouse', 'double_click_mouse', 'right_click_mouse', 'drag_mouse', 'press_key', 'type_text', 'hotkey']
        },
        # 视觉操作相关
        'visual_operation': {
            'keywords': ['截图', '屏幕尺寸', '查找图像', '等待图像', '点击图像', '屏幕颜色', '查找文本'],
            'tools': ['take_screenshot', 'get_screen_size', 'locate_on_screen', 'wait_for_image', 'click_on_image', 'get_screen_color_at', 'find_text_on_screen']
        },
        # 应用程序操作相关
        'application_operation': {
            'keywords': ['打开应用', '启动程序', '运行工具'],
            'tools': ['open_application', 'open_windows_tool']
        }
    }
    
    # 遍历所有任务类型，寻找匹配的关键词
    for task_type, config in task_type_mapping.items():
        for keyword in config['keywords']:
            if keyword in user_input_lower:
                return task_type, config['tools'], []
    
    # 特殊任务识别
    # 1. 识别窗口关闭任务
    if '关闭' in user_input_lower and ('窗口' in user_input_lower or '应用' in user_input_lower):
        return 'window_operation', ['find_window_by_title', 'close_window_by_title', 'close_window_by_hwnd'], []
    
    # 2. 识别需要组合工具的任务
    if '自动' in user_input_lower and ('操作' in user_input_lower or '完成' in user_input_lower):
        # 自动操作任务，可能需要多种工具组合
        return 'automated_operation', ['get_all_windows', 'find_window_by_title', 'click_mouse', 'type_text', 'hotkey'], []
    
    # 3. 识别需要视觉+键鼠组合的任务
    if ('点击' in user_input_lower and '图像' in user_input_lower) or '视觉' in user_input_lower:
        return 'visual_mouse_operation', ['locate_on_screen', 'click_on_image', 'wait_for_image'], []
    
    # 默认返回通用帮助类型，但包含更多可能有用的工具
    return 'general_help', ['get_system_info', 'check_disk_space', 'get_all_windows', 'find_window_by_title'], []

async def run_computer_expert_agent_stream(user_input, ctx=None, callback=None):
    # 分析任务类型
    task_type, suggested_tools, _ = analyze_task_type(user_input)
    
    # 搜索知识库获取相关知识
    knowledge_context = ""
    try:
        # 搜索知识库
        search_results = knowledge_base.search_knowledge_items(user_input, tags=None, category_id=None)
        
        if search_results:
            knowledge_context = "\n\n相关知识库内容:\n"
            for i, item in enumerate(search_results[:3]):  # 最多返回3条相关知识
                knowledge_context += f"\n{str(i+1)}. [{item['title']}]\n{item['content'][:300]}...\n"
                knowledge_context += f"   分类: {item['type']} | 标签: {', '.join(item['tags']) if item['tags'] else '无'}\n"
    except Exception as e:
        debug_print(f"知识库搜索失败: {e}")
    
    # 增强用户输入，添加任务类型分析和工具调用建议
    enhanced_input = f"""
用户请求: {user_input}

任务分析:
- 任务类型: {task_type}
- 建议使用工具: {suggested_tools}
- 操作指导: 请根据任务类型选择合适的工具调用顺序，优先使用建议的工具获取实时信息。{knowledge_context}

请参考上述相关知识库内容，结合您的专业知识和工具调用能力，为用户提供准确、详细的回答。
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
                elif hasattr(event, 'tool_calls'):
                    # 处理工具调用事件
                    debug_print("处理工具调用事件")
                    for tool_call in event.tool_calls:
                        # 调试：查看ToolSelection对象的属性
                        debug_print(f"ToolSelection对象属性: {dir(tool_call)}")
                        debug_print(f"ToolSelection对象类型: {type(tool_call)}")
                        
                        # 安全获取工具名称和参数
                        tool_name = getattr(tool_call, 'tool_name', getattr(tool_call, 'name', None))
                        
                        # 尝试多种方式获取参数
                        tool_args = {}
                        if hasattr(tool_call, 'tool_kwargs'):
                            tool_args = tool_call.tool_kwargs
                        elif hasattr(tool_call, 'kwargs'):
                            tool_args = tool_call.kwargs
                        elif hasattr(tool_call, 'arguments'):
                            tool_args = tool_call.arguments
                        elif hasattr(tool_call, 'args'):
                            tool_args = tool_call.args
                        
                        # 如果tool_args是位置参数列表，转换为空字典
                        if isinstance(tool_args, (list, tuple)):
                            tool_args = {}
                        
                        if not tool_name:
                            debug_print("工具名称未找到")
                            continue
                        
                        debug_print(f"调用工具: {tool_name}，参数: {tool_args}")
                        
                        # 查找并执行对应的工具函数
                        for tool in ALL_TOOLS:
                            if tool.__name__ == tool_name:
                                try:
                                    # 执行工具
                                    result = tool(**tool_args)
                                    debug_print(f"工具执行结果: {result}")
                                    
                                    # 将工具执行结果添加到响应中
                                    result_message = f"\n[工具调用结果] {tool_name}: {result}\n"
                                    print(result_message, end="", flush=True)
                                    full_response += result_message
                                    if callback:
                                        callback(result_message)
                                    
                                    # 将结果传递回AI，让它继续处理
                                    # 注意：这部分需要根据LlamaIndex的具体实现来调整
                                    # 通常需要将结果添加到上下文中，然后让AI继续运行
                                    break
                                except Exception as e:
                                    error_message = f"\n[工具调用错误] {tool_name}: {str(e)}\n"
                                    print(error_message, end="", flush=True)
                                    full_response += error_message
                                    if callback:
                                        callback(error_message)
                                    debug_print(f"工具调用错误: {e}")
                                    break
                elif hasattr(event, 'tool_call'):
                    # 处理单个工具调用事件
                    debug_print("处理单个工具调用事件")
                    tool_call = event.tool_call
                    
                    # 获取工具名称和参数
                    if hasattr(tool_call, 'name'):
                        # 处理对象类型的工具调用
                        tool_name = tool_call.name
                        tool_args = tool_call.kwargs if hasattr(tool_call, 'kwargs') else getattr(tool_call, 'arguments', {})
                    elif isinstance(tool_call, dict):
                        # 处理字典类型的工具调用
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('arguments', {})
                    else:
                        debug_print("无法识别的工具调用格式")
                        continue
                    
                    if not tool_name:
                        debug_print("工具名称未找到")
                        continue
                    
                    debug_print(f"调用工具: {tool_name}，参数: {tool_args}")
                    
                    # 查找并执行对应的工具函数
                    for tool in ALL_TOOLS:
                        if tool.__name__ == tool_name:
                            try:
                                # 确保tool_args是字典类型
                                if not isinstance(tool_args, dict):
                                    tool_args = {}
                                
                                # 执行工具
                                result = tool(**tool_args)
                                debug_print(f"工具执行结果: {result}")
                                
                                # 将工具执行结果添加到响应中
                                result_message = f"\n[工具调用结果] {tool_name}: {result}\n"
                                print(result_message, end="", flush=True)
                                full_response += result_message
                                if callback:
                                    callback(result_message)
                                break
                            except Exception as e:
                                error_message = f"\n[工具调用错误] {tool_name}: {str(e)}\n"
                                print(error_message, end="", flush=True)
                                full_response += error_message
                                if callback:
                                    callback(error_message)
                                debug_print(f"工具调用错误: {e}")
                                break
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
