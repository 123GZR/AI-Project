# 电脑操作专家AI助手

这是一个基于大语言模型的电脑操作专家AI助手，可以帮助用户解决各种电脑操作相关的问题。

## 功能特性

- 提供详细的电脑操作步骤指导
- 解决常见电脑故障问题
- 提供软件安装与配置建议
- 支持交互式对话
- 包含实用的文件和目录操作工具

## 环境要求

- Python 3.11+
- 依赖包：见 requirements.txt

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 确保 .env 文件中包含正确的 API 密钥配置

## 配置说明

项目使用 .env 文件存储 API 密钥信息，请确保文件中包含以下内容：

```
QIANWEN_API_KEY=您的API密钥
QIANWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 使用方法

1. 运行主程序：
   ```bash
   python computer_expert_agent.py
   ```

2. 在交互式界面中，输入您的电脑操作问题，例如：
   - "如何在Windows上查看系统信息？"
   - "如何安装Python？"
   - "电脑运行缓慢怎么办？"

3. 输入 'exit'、'quit'、'退出' 或 '结束' 来终止对话

## 示例问题

- 如何创建文件夹？
- 如何查看文件大小？
- 如何在Windows上截图？
- 如何优化电脑性能？
- 如何安装常用软件？

## 注意事项

- 请确保您的API密钥有效且有足够的使用额度
- 本助手仅提供电脑操作相关的指导，不涉及其他领域
- 对于复杂或高风险的操作，请谨慎执行并备份重要数据

## 依赖说明

- llama-index: 用于构建大语言模型应用
- openai: 用于与大语言模型交互
- python-dotenv: 用于加载环境变量
- nest-asyncio: 用于处理嵌套事件循环问题