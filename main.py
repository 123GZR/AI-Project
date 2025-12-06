import sys
import asyncio
from agent.config import DEBUG_MODE
from agent.workflow import run_computer_expert_agent_stream
from agent.chat_interface import interactive_chat

# 主函数
async def main():
    # 处理命令行参数
    if len(sys.argv) > 1:
        if '--debug' in sys.argv:
            # 修改全局调试模式
            global DEBUG_MODE
            DEBUG_MODE = True
            print("[提示] 调试模式已开启")
        elif '--help' in sys.argv:
            print("使用方法：")
            print("  python main.py              # 正常模式启动")
            print("  python main.py --debug      # 开启调试模式启动")
            print("  python main.py --help       # 显示帮助信息")
            print("  python main.py '问题'       # 直接回答指定问题")
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
