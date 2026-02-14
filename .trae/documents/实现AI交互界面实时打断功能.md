# 实现AI交互界面实时打断功能

## 实现目标
当AI正在生成并输出回答内容时，将界面上原有的"发送"按钮动态更改为"打断"按钮；用户点击"打断"按钮后，系统应立即终止当前AI的回答生成过程，并将按钮恢复为"发送"状态，同时保留已生成的部分回答内容。

## 实现步骤

### 1. 修改GUI类初始化
- 将发送按钮设为实例变量，以便在其他方法中访问和修改
- 添加`is_generating`标志来跟踪AI是否正在生成回答
- 添加`should_interrupt`标志来指示是否需要打断AI生成

### 2. 修改发送按钮创建代码
- 将发送按钮从局部变量改为实例变量`self.send_button`
- 设置按钮的初始文本为"发送"

### 3. 修改`send_message`方法
- 在发送消息前检查是否正在生成，如果是则不执行操作
- 将按钮文本改为"打断"
- 按钮点击事件改为调用`interrupt_generation`方法
- 设置`is_generating`为True，`should_interrupt`为False

### 4. 实现`interrupt_generation`方法
- 设置`should_interrupt`为True
- 将按钮文本恢复为"发送"
- 按钮点击事件恢复为调用`send_message`方法
- 设置`is_generating`为False

### 5. 修改`run_computer_expert_agent_stream`函数
- 添加`should_interrupt`参数，用于接收打断信号
- 在流式事件循环中检查该标志，如果为True则退出循环

### 6. 修改`stream_chat_with_agent`函数
- 添加`should_interrupt`参数
- 在异步事件迭代中定期检查该标志
- 如果标志为True，跳出事件循环并返回已生成的内容

### 7. 修改GUI中的`run_ai_assistant`方法
- 将`should_interrupt`标志传递给`run_computer_expert_agent_stream`函数
- 在生成结束后，恢复按钮状态和标志

### 8. 确保线程安全
- 使用线程安全的方式访问和修改标志
- 在GUI更新中使用`root.after`确保在主线程中执行

## 预期效果
- 当用户点击"发送"按钮后，按钮文本变为"打断"
- 当AI正在生成回答时，用户可以点击"打断"按钮立即停止生成
- 打断后，按钮恢复为"发送"状态，已生成的内容保留在聊天历史中
- 系统状态更新为"空闲"

## 代码修改点
1. `gui.py` - ComputerExpertGUI类的初始化和按钮创建
2. `gui.py` - send_message方法
3. `gui.py` - 新增interrupt_generation方法
4. `gui.py` - run_ai_assistant方法
5. `computer_expert_agent.py` - run_computer_expert_agent_stream函数
6. `computer_expert_agent.py` - stream_chat_with_agent函数