import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

# 全局调试开关，默认关闭调试信息
DEBUG_MODE = False

def debug_print(message):
    """根据调试模式决定是否打印调试信息"""
    if DEBUG_MODE:
        print(f"[调试] {message}")

# 加载环境变量
load_dotenv()

# 定义大模型配置
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
