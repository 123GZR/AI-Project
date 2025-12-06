import asyncio
from llama_index.core.workflow import Context
from .config import DEBUG_MODE, debug_print
from .agent import computer_expert_agent
from .task_analyzer import analyze_task_type
from knowledge_base import knowledge_base

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
                if hasattr(event, 'delta'):
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
                        from tools import ALL_TOOLS
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
                    from tools import ALL_TOOLS
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
