# FileSweeper 打包和发布指南

## 目录
1. [概述](#概述)
2. [准备工作](#准备工作)
3. [Windows 打包](#windows-打包)
4. [macOS 打包](#macos-打包)
5. [Linux 打包](#linux-打包)
6. [跨平台打包](#跨平台打包)
7. [通用打包方法](#通用打包方法)
8. [优化和配置](#优化和配置)
9. [签名和公证](#签名和公证)
10. [发布流程](#发布流程)
11. [故障排除](#故障排除)

## 概述

本指南详细介绍了如何将 FileSweeper 打包成可在各平台上分发的可执行文件。FileSweeper 基于 Python 和 PySide6 构建，因此可以使用多种工具进行打包。

支持的打包方式：
- **PyInstaller**：跨平台打包工具，支持 Windows、macOS 和 Linux
- **cx_Freeze**：另一个跨平台打包工具
- **Nuitka**：Python 编译器，可将 Python 代码编译为 C++ 程序

## 准备工作

### 安装打包工具

1. **安装 PyInstaller**（推荐）：
   ```bash
   pip install pyinstaller
   ```

2. **安装 cx_Freeze**（可选）：
   ```bash
   pip install cx_Freeze
   ```

3. **安装 Nuitka**（可选）：
   ```bash
   pip install nuitka
   ```

### 解决常见依赖问题

在某些Python环境中，可能会遇到依赖冲突问题：

1. **卸载过时的pathlib包**（如果遇到相关错误）：
   ```bash
   pip uninstall pathlib -y
   ```
   这是因为pathlib现在是Python标准库的一部分，旧的回溯包与PyInstaller不兼容。

### 验证环境

在开始打包前，请确保：

1. 已正确安装所有依赖项：
   ```bash
   pip install -r requirements.txt
   ```

2. 程序可以正常运行：
   ```bash
   python main.py
   ```

3. 已测试所有功能，确保没有错误

## Windows 打包

### 使用 PyInstaller

1. **基本打包命令**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon.ico main.py
   ```

2. **详细参数说明**：
   - `--onefile`：打包成单个可执行文件
   - `--windowed`：不显示控制台窗口（GUI 应用程序）
   - `--icon=icons/icon.ico`：指定应用程序图标

3. **添加额外资源**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" main.py
   ```

4. **完整打包命令**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

### 优化 Windows 打包

1. **减小文件大小**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --hidden-import=send2trash --hidden-import=psutil --exclude-module=tkinter --exclude-module=matplotlib main.py
   ```

2. **添加版本信息**：
   创建 `version_info.txt` 文件：
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
       mask=0x3f,
       flags=0x0,
       OS=0x40004,
       fileType=0x1,
       subtype=0x0,
       date=(0, 0)
       ),
     kids=[
       StringFileInfo([
         StringTable(
           u'040904B0',
           [StringStruct(u'CompanyName', u'FileSweeper'),
            StringStruct(u'FileDescription', u'FileSweeper - Duplicate File Finder'),
            StringStruct(u'FileVersion', u'1.0.0'),
            StringStruct(u'ProductName', u'FileSweeper')])
         ]),
       VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
     ]
   )
   ```

   使用版本信息打包：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --version-file=version_info.txt main.py
   ```

### Windows 打包后处理

1. **输出位置**：
   - 可执行文件位于 `dist/` 目录中
   - 临时文件位于 `build/` 目录中

2. **清理**：
   - 打包完成后可以删除 `build/` 和 `*.spec` 文件

## macOS 打包

### 使用 PyInstaller

1. **基本打包命令**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon_256x256.png main.py
   ```

2. **详细参数说明**：
   - `--onefile`：打包成单个可执行文件
   - `--windowed`：不显示终端窗口（GUI 应用程序）
   - `--icon=icons/icon_256x256.png`：指定应用程序图标

3. **添加额外资源**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" main.py
   ```

4. **完整打包命令**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

> **注意**：PyInstaller 6.0+版本显示警告，建议在macOS上使用onedir模式而不是onefile模式，因为onefile与.app包不兼容且可能与macOS安全机制冲突。如果你遇到问题，可以尝试使用onedir模式：
   ```bash
   pyinstaller --name FileSweeper --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

### 优化 macOS 打包

1. **减小文件大小**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil --exclude-module=tkinter main.py
   ```

2. **创建 .app 包**：
   ```bash
   pyinstaller --name FileSweeper --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

### macOS 打包后处理

1. **输出位置**：
   - `.app` 应用程序包位于 `dist/` 目录中
   - 单个可执行文件也在 `dist/` 目录中

2. **权限设置**：
   ```bash
   chmod +x dist/FileSweeper.app/Contents/MacOS/FileSweeper
   ```

## Linux 打包

### 使用 PyInstaller

1. **基本打包命令**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon_linux_256x256.png main.py
   ```

2. **详细参数说明**：
   - `--onefile`：打包成单个可执行文件
   - `--windowed`：不显示终端窗口（GUI 应用程序）
   - `--icon=icons/icon_linux_256x256.png`：指定应用程序图标

3. **添加额外资源**：
   ```bash
   pyinstaller --onefile --windowed --icon=icons/icon_linux_256x256.png --add-data "icons:icons" main.py
   ```

4. **完整打包命令**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_linux_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

### 优化 Linux 打包

1. **减小文件大小**：
   ```bash
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_linux_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil --exclude-module=tkinter main.py
   ```

### Linux 打包后处理

1. **输出位置**：
   - 可执行文件位于 `dist/` 目录中

2. **权限设置**：
   ```bash
   chmod +x dist/FileSweeper
   ```

## 跨平台打包

当您在一台机器上需要为其他平台创建打包时，有几种方法可以实现：

### 使用GitHub Actions进行跨平台打包（推荐）

创建 `.github/workflows/build.yml` 文件：

```
name: Build FileSweeper

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    strategy:
      matrix:
        architecture: [x64, x86]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        architecture: ${{ matrix.architecture }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build with PyInstaller
      run: |
        pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --hidden-import=send2trash --hidden-import=psutil main.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: FileSweeper-Windows-${{ matrix.architecture }}
        path: dist/FileSweeper.exe

  build-macos:
    runs-on: macos-latest
    strategy:
      matrix:
        architecture: [x64, arm64]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    - name: Build with PyInstaller
      run: |
        pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
    - name: Create Universal Binary (Optional)
      if: matrix.architecture == 'arm64'
      run: |
        # 创建通用二进制文件的额外步骤
        echo "Creating universal binary steps here"
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: FileSweeper-macOS-${{ matrix.architecture }}
        path: dist/FileSweeper

  build-linux:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        architecture: [x64, arm64]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install python3-pip
        python3 -m pip install --upgrade pip
        pip3 install -r requirements.txt
        pip3 install pyinstaller
    - name: Build with PyInstaller
      run: |
        pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_linux_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: FileSweeper-Linux-${{ matrix.architecture }}
        path: dist/FileSweeper
```

### 为不同CPU架构打包

#### 为Intel Mac (x86_64)打包（从Apple Silicon Mac）

如果您使用的是Apple Silicon Mac（ARM64），但需要为Intel Mac创建打包，有几种方法：

1. **使用Rosetta在Intel模式下运行PyInstaller**：
   ```bash
   # 安装Intel版本的Python
   # 通过Rosetta运行Intel Python
   arch -x86_64 python -m pip install pyinstaller
   arch -x86_64 pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

2. **创建通用二进制文件**：
   ```bash
   # 分别为两种架构构建
   # ARM64版本
   pyinstaller --name FileSweeper-arm64 --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   
   # x86_64版本（在Rosetta下）
   arch -x86_64 pyinstaller --name FileSweeper-x86_64 --onefile --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   
   # 合并为通用二进制文件
   # 使用lipo工具合并两个可执行文件
   lipo -create -output FileSweeper dist/FileSweeper-arm64 dist/FileSweeper-x86_64
   ```

3. **使用GitHub Actions自动构建**：
   GitHub Actions工作流已配置为自动构建两种macOS架构：
   - ARM64（Apple Silicon）
   - x64（Intel Mac）
   
   这确保了您的应用程序可以在所有现代Mac上运行。

#### 为Windows不同架构打包

1. **为Windows x64打包**：
   ```bash
   # 在Windows x64机器上
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

2. **为Windows x86 (32位)打包**：
   ```bash
   # 需要在32位Windows系统或使用32位Python环境
   pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon.ico --add-data "icons;icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

#### 创建通用macOS应用程序

为了创建一个能在所有Mac上运行的通用应用程序，您可以创建一个通用二进制文件：

1. **分别构建两个架构**：
   ```bash
   # 构建ARM64版本
   pyinstaller --name FileSweeper-arm64 --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   
   # 在Rosetta下构建x86_64版本
   arch -x86_64 pyinstaller --name FileSweeper-x86_64 --windowed --icon=icons/icon_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py
   ```

2. **合并为通用二进制文件**：
   ```bash
   # 使用lipo工具合并两个可执行文件
   lipo -create -output FileSweeper dist/FileSweeper-arm64 dist/FileSweeper-x86_64
   ```

3. **创建通用.app包**：
   合并.app包中的可执行文件以创建通用应用程序包。

### 使用虚拟机进行跨平台打包

1. **Windows虚拟机**：
   - 安装Windows虚拟机（使用Parallels Desktop、VMware或VirtualBox）
   - 在Windows VM中安装Python和依赖项
   - 使用PyInstaller进行Windows打包

2. **Intel macOS虚拟机**：
   - 在Apple Silicon Mac上可以使用Virtualization框架运行Intel macOS虚拟机
   - 安装Intel版本的Python
   - 进行标准的macOS打包流程

### 使用云服务进行跨平台打包

除了本地虚拟机和GitHub Actions，还可以使用云服务进行跨平台打包：

1. **使用MacStadium**：
   - 提供真实的Apple硬件托管服务
   - 可以租用Intel和Apple Silicon Mac进行构建

2. **使用MacInCloud**：
   - 按小时付费的Mac云服务
   - 支持远程桌面访问进行打包

3. **使用AWS EC2**：
   - Windows实例：用于Windows打包
   - Linux实例：用于Linux打包

4. **使用Azure Virtual Machines**：
   - 提供Windows、Linux等多种操作系统
   - 支持不同CPU架构

### 自动化构建和发布

为了简化跨平台打包流程，建议设置自动化构建系统：

1. **使用GitHub Actions**：
   - 创建多个工作流，每个平台一个
   - 自动在每次发布时构建所有平台版本
   - 自动上传到发布页面

2. **使用GitLab CI/CD**：
   - 类似GitHub Actions的功能
   - 可以使用GitLab的runner进行构建

3. **使用Jenkins**：
   - 自托管的自动化服务器
   - 可以配置多个节点进行不同平台的构建

### 使用Docker进行Linux打包

创建 `Dockerfile`：

```
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pyinstaller

COPY . .

RUN pyinstaller --name FileSweeper --onefile --windowed --icon=icons/icon_linux_256x256.png --add-data "icons:icons" --hidden-import=send2trash --hidden-import=psutil main.py

FROM alpine:latest
WORKDIR /app
COPY --from=0 /app/dist/FileSweeper .
CMD ["./FileSweeper"]
```

构建Docker镜像：
```bash
docker build -t filesweeper-builder .
docker run --rm -v $(pwd):/dist filesweeper-builder cp FileSweeper /dist/
```

### 使用交叉编译工具

虽然Python本身不支持交叉编译，但可以使用一些工具来实现：

1. **使用Nuitka进行交叉编译**：
   ```bash
   # 在Mac上为Windows编译
   python -m nuitka --onefile --windows-icon-from-ico=icons/icon.ico --enable-plugin=pyside6 --output-filename=FileSweeper.exe main.py
   ```

2. **使用cx_Freeze进行跨平台打包**：
   创建 `setup.py`：
   ```python
   from cx_Freeze import setup, Executable
   
   # 依赖项
   build_exe_options = {
       "packages": ["send2trash", "psutil"],
       "include_files": ["icons/"],
       "excludes": ["tkinter"]
   }
   
   # 可执行文件设置
   base = None
   if sys.platform == "win32":
       base = "Win32GUI"  # 不显示控制台窗口
   
   setup(
       name="FileSweeper",
       version="1.0",
       description="FileSweeper - Duplicate File Finder",
       options={"build_exe": build_exe_options},
       executables=[Executable("main.py", base=base, icon="icons/icon.ico")]
   )
   ```

   然后运行：
   ```bash
   python setup.py build
   ```

## 通用打包方法

### 使用 spec 文件自定义打包

PyInstaller 使用 spec 文件来控制打包过程。可以生成并修改 spec 文件来定制打包选项：

1. **生成 spec 文件**：
   ```bash
   pyinstaller --name FileSweeper --windowed --icon=icons/icon_256x256.png main.py
   ```

2. **编辑 spec 文件**（FileSweeper.spec）：
   ```python
   # -*- mode: python ; coding: utf-8 -*-
   
   block_cipher = None
   
   a = Analysis(
       ['main.py'],
       pathex=[],
       binaries=[],
       datas=[('icons', 'icons')],
       hiddenimports=['send2trash', 'psutil'],
       hookspath=[],
       hooksconfig={},
       runtime_hooks=[],
       excludes=['tkinter'],
       win_no_prefer_redirects=False,
       win_private_assemblies=False,
       cipher=block_cipher,
       noarchive=False,
   )
   
   pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
   
   exe = EXE(
       pyz,
       a.scripts,
       a.binaries,
       a.zipfiles,
       a.datas,
       [],
       name='FileSweeper',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       upx_exclude=[],
       runtime_tmpdir=None,
       console=False,
       disable_windowed_traceback=False,
       argv_emulation=False,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
       icon='icons/icon_256x256.png'
   )
   ```

3. **使用 spec 文件打包**：
   ```bash
   pyinstaller FileSweeper.spec
   ```

## 优化和配置

### 减小打包文件大小

1. **排除不必要的模块**：
   ```bash
   pyinstaller --exclude-module tkinter --exclude-module matplotlib --exclude-module numpy main.py
   ```

2. **使用 UPX 压缩**：
   - 安装 UPX：
     - Windows: 从 https://upx.github.io/ 下载
     - macOS: `brew install upx`
     - Linux: `sudo apt install upx`
   - 启用 UPX：
     ```bash
     pyinstaller --upx-dir /path/to/upx main.py
     ```

3. **使用虚拟环境**：
   - 创建干净的虚拟环境，只安装必要的依赖
   - 这样可以避免打包不必要的包

### 性能优化

1. **预编译 Python 字节码**：
   ```bash
   python -m compileall .
   ```

2. **使用 Nuitka 编译**：
   ```bash
   python -m nuitka --standalone --onefile --enable-plugin=pyside6 main.py
   ```

### 资源文件处理

确保所有资源文件都被正确打包：

1. **图标文件**：
   - Windows: `.ico` 格式
   - macOS: `.png` 或 `.icns` 格式
   - Linux: `.png` 格式

2. **数据文件**：
   - 使用 `--add-data` 参数添加
   - 在代码中使用 `sys._MEIPASS` 访问打包的数据文件

## 签名和公证

### Windows 代码签名

1. **获取代码签名证书**
2. **使用 signtool 签名**：
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/FileSweeper.exe
   ```

### macOS 代码签名和公证

对于 macOS 10.15+，需要进行代码签名和公证：

1. **代码签名**：
   ```bash
   codesign --force --deep --sign "Developer ID Application: YOUR_NAME" dist/FileSweeper.app
   ```

2. **创建归档文件**：
   ```bash
   ditto -c -k --keepParent dist/FileSweeper.app dist/FileSweeper.zip
   ```

3. **公证应用**：
   ```bash
   xcrun altool --notarize-app --primary-bundle-id com.filesweeper.app --username APPLE_ID --password APP_SPECIFIC_PASSWORD --file dist/FileSweeper.zip
   ```

4. **检查公证状态**：
   ```bash
   xcrun altool --notarization-info NOTARIZATION_ID -u APPLE_ID -p APP_SPECIFIC_PASSWORD
   ```

5. **归档公证**：
   ```bash
   xcrun stapler staple dist/FileSweeper.app
   ```

## 发布流程

### 准备发布版本

1. **更新版本号**：
   - 更新 `main.py` 中的应用程序版本
   - 更新用户手册中的版本信息

2. **测试打包版本**：
   - 在目标平台上测试打包的应用程序
   - 确保所有功能正常工作

3. **创建发布说明**：
   - 列出新功能、修复和改进
   - 包含安装和升级说明

### 创建发布包

1. **Windows**：
   - 打包 `.exe` 文件
   - 创建安装程序（可选，使用 Inno Setup 或 NSIS）

2. **macOS**：
   - 打包 `.app` 文件
   - 创建 `.dmg` 磁盘映像文件：
     ```bash
     hdiutil create -volname "FileSweeper" -srcfolder "dist/FileSweeper.app" -ov -format UDZO "dist/FileSweeper.dmg"
     ```

3. **Linux**：
   - 打包可执行文件
   - 创建 `.tar.gz` 压缩包：
     ```bash
     tar -czvf FileSweeper-linux.tar.gz -C dist FileSweeper
     ```

### 发布渠道

1. **GitHub Releases**：
   - 在 GitHub 项目页面创建新版本
   - 上传所有平台的打包文件
   - 添加详细的发布说明

2. **应用商店**：
   - Microsoft Store（Windows）
   - Mac App Store（macOS）
   - Flathub（Linux）

3. **官方网站**：
   - 在项目网站提供下载链接
   - 提供详细的安装说明

## 故障排除

### 常见打包问题

1. **缺少模块错误**：
   - 使用 `--hidden-import` 参数添加缺失的模块
   - 检查是否有条件导入的模块

2. **资源文件找不到**：
   - 确保使用 `--add-data` 添加资源文件
   - 在代码中使用以下方式访问资源文件：
     ```python
     import sys
     import os
     
     def resource_path(relative_path):
         """获取资源文件路径"""
         try:
             # PyInstaller 创建的临时文件夹
             base_path = sys._MEIPASS
         except Exception:
             base_path = os.path.abspath(".")
     
         return os.path.join(base_path, relative_path)
     ```

3. **图标不显示**：
   - 确保图标文件格式正确
   - 检查图标文件路径是否正确

4. **打包文件过大**：
   - 排除不必要的模块
   - 使用 UPX 压缩
   - 检查是否包含了测试文件或开发文件

5. **pathlib 包冲突**：
   - 错误信息：`The 'pathlib' package is an obsolete backport of a standard library package and is incompatible with PyInstaller`
   - 解决方法：卸载过时的 pathlib 包
     ```bash
     pip uninstall pathlib -y
     ```
   - 这是因为 pathlib 现在是 Python 标准库的一部分，旧的回溯包与 PyInstaller 不兼容

6. **macOS 上的 onefile 模式警告**：
   - 警告信息：`Onefile mode in combination with macOS .app bundles (windowed mode) don't make sense`
   - 解决方法：考虑使用 onedir 模式替代 onefile 模式
   - 或者忽略警告，因为应用程序仍然可以正常工作

### 平台特定问题

1. **Windows**：
   - 防病毒软件可能误报：提交误报报告
   - 用户账户控制(UAC)：确保正确处理权限

2. **macOS**：
   - Gatekeeper 阻止应用运行：需要用户手动允许
   - 权限问题：确保正确处理隐私权限

3. **Linux**：
   - 依赖库问题：确保目标系统有必要的库
   - 桌面集成：提供 `.desktop` 文件

### 调试打包应用

1. **启用控制台输出**：
   ```bash
   pyinstaller --console main.py
   ```

2. **添加调试信息**：
   ```bash
   pyinstaller --debug=all main.py
   ```

3. **检查打包日志**：
   - 查看 PyInstaller 生成的日志文件
   - 检查是否有警告或错误信息

通过遵循本指南，您应该能够成功地将 FileSweeper 打包为可在各平台上分发的可执行文件。如有任何问题，请参考 PyInstaller 官方文档或在项目 GitHub 页面提交 Issue。