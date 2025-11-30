@echo off
cls
echo 电脑操作专家AI助手
 echo ===================
echo 请选择启动模式：
echo 1. GUI界面（推荐）
echo 2. 命令行界面
echo ===================
set /p choice=请输入选项（1或2）：

if "%choice%"=="1" (
    echo 启动GUI界面...
    python gui.py
) else if "%choice%"=="2" (
    echo 启动命令行界面...
    python computer_expert_agent.py
) else (
    echo 无效选项，默认启动GUI界面...
    python gui.py
)

pause