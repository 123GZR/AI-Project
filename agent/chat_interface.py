import asyncio
from .config import DEBUG_MODE, debug_print
from .workflow import run_computer_expert_agent_stream

# 交互式对话函数（使用流式输出）
async def interactive_chat():
    # 声明全局变量
    global DEBUG_MODE
    
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
        # 启动时显示调试模式状态
        if DEBUG_MODE:
            print("[提示] 调试模式已开启")
        
        while True:
            # 检查是否需要重置上下文
            if conversation_count % MAX_CONVERSATIONS == 0 or ctx is None:
                print(f"\n创建新的对话上下文")
                from llama_index.core.workflow import Context
                from agent import computer_expert_agent
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
                    # 修改全局调试模式
                    DEBUG_MODE = True
                    print("[提示] 调试模式已开启")
                    continue
                elif user_input.lower() == "/debug off":
                    # 修改全局调试模式
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
                    # 调用智能体处理用户请求并流式输出，设置180秒超时
                    assistant_response = await asyncio.wait_for(
                        run_computer_expert_agent_stream(processed_input, ctx=ctx), 
                        timeout=180.0
                    )
                except asyncio.TimeoutError:
                    print("\n\n[错误] 对话处理超时！请尝试简化问题。")
                    # 强制重置上下文
                    from llama_index.core.workflow import Context
                    from agent import computer_expert_agent
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
