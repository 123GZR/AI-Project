# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 单一文件模式配置
single_file = True

# 分析主启动脚本
analysis = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含所有必要的Python文件
        ('gui.py', '.'),
        ('computer_expert_agent.py', '.'),
        # 包含tools目录及其所有内容
        ('tools', 'tools'),
        # 包含项目内置Python解释器（可选，根据需要决定是否包含）
        # ('python', 'python'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件（Python压缩归档）
pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

# 创建EXE文件
executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    [],
    name='AI助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 设置为False可隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 使用项目中的图标文件
    # 单一文件模式特有配置
    onefile=single_file,
)
