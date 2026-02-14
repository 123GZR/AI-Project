# PyInstaller项目打包计划

## 1. 项目分析

### 1.1 项目结构

* 主入口文件：`gui.py`（GUI应用）

* 核心逻辑：`computer_expert_agent.py`

* 工具模块：`tools/`目录（包含窗口管理等功能）

* 配置文件：`.env`

* 依赖文件：`requirements.txt`

### 1.2 关键依赖

* **LLM相关**：`llama-index`, `openai`

* **计算机视觉**：`opencv-python-headless`, `numpy`

* **GUI相关**：`tkinter`（内置）

* **其他**：`pyautogui`, `pygetwindow`, `pywin32`, `psutil`

## 2. 打包前准备

### 2.1 安装PyInstaller

```bash
.venv\Scripts\python.exe -m pip install pyinstaller
```

### 2.2 生成初始spec文件

```bash
.venv\Scripts\pyi-makespec --onefile --windowed gui.py
```

## 3. spec文件配置

### 3.1 基础配置

* 采用`Analysis`类配置入口文件和依赖

* 采用`PYZ`类打包Python字节码

* 采用`EXE`类生成可执行文件

* 采用`COLLECT`类收集所有依赖文件（--onedir模式）

### 3.2 大型框架处理

* **llama-index**：添加`hiddenimports`，确保所有子模块被正确打包

* **openai**：确保API配置正确处理

* **OpenCV**：添加二进制依赖，处理DLL文件

* **numpy**：确保科学计算库正确打包

### 3.3 GUI资源处理

* 确保tkinter资源正确加载

* 处理界面元素和交互功能

## 4. 打包执行

### 4.1 执行打包命令

```bash
.venv\Scripts\python.exe -m PyInstaller gui.spec
```

### 4.2 输出目录

* 打包结果将生成在`dist/`目录下

## 5. 测试与优化

### 5.1 功能测试

* 运行打包后的可执行文件

* 测试窗口管理功能

* 测试AI助手功能

### 5.2 依赖缺失处理

* 检查并添加缺失的依赖

* 处理路径错误

* 优化二进制文件打包

### 5.3 性能优化

* 减少打包体积

* 优化启动速度

* 处理内存占用

## 6. 最终交付

### 6.1 打包结果

* 生成目录形式的可执行文件

* 包含所有必要的依赖和资源文件

### 6.2 spec文件优化建议

* 提供最终优化的spec文件

* 说明关键配置项和优化点

## 7. 预期问题与解决方案

| 问题        | 解决方案                         |
| --------- | ---------------------------- |
| 大型框架依赖缺失  | 配置`hiddenimports`和`binaries` |
| GUI资源加载失败 | 配置`datas`参数                  |
| 路径错误      | 使用相对路径或动态路径处理                |
| 性能问题      | 优化导入和资源加载                    |
| 环境变量缺失    | 打包时包含`.env`文件                |

