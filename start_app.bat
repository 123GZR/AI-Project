@echo off
REM AI Assistant Startup Script

echo Starting AI Assistant...
cd /d "%~dp0"

REM 使用项目内置Python解释器启动应用
echo Using built-in Python interpreter...
python\python.exe gui.py

pause