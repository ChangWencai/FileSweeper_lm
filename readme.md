# FileSweeper

FileSweeper is a cross-platform desktop application built with Python and PySide6 that helps you identify and manage duplicate files on your computer. It can scan directories, find duplicate files based on content (not just names), and allows you to selectively delete duplicates while keeping one copy.

## Features

- Cross-platform support (Windows, macOS, Linux)
- Fast duplicate file detection using file hashing
- Intuitive graphical user interface
- Selective file deletion with recycle bin support
- Group-based file organization for easy management
- Configurable settings for default behaviors
- Double-click to open files with system default applications

## Screenshots

![Main Interface](screenshots/main_interface.png)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Select a directory to scan for duplicate files
2. Click "Scan" to start the scanning process
3. Review the detected duplicate files organized in groups
4. Select files you want to delete (by default, the first file in each group is not selected)
5. Click "Delete Selected" to move selected files to the recycle bin

## Configuration

You can customize FileSweeper's behavior through the Settings dialog:

- **Auto-select duplicates**: Choose whether to automatically select all but the first file in each duplicate group
- **Trash delete method**: Choose whether to move files to the recycle bin or permanently delete them

Settings are saved automatically and will persist between application sessions.

## Icons

Application icons for Windows, macOS, and Linux are located in the `icons` directory:

- Windows: `icons/icon.ico`
- macOS: `icons/icon_*.png` (multiple sizes)
- Linux: `icons/icon_linux_*.png` (multiple sizes)

See [ICONS.md](ICONS.md) for detailed information on how to use these icons when packaging the application.

## Technical Details

### Architecture

FileSweeper follows a modular architecture with clear separation of concerns:

- **UI Layer**: PySide6-based graphical interface
- **Core Logic**: File scanning and duplicate detection algorithms
- **Data Models**: Qt models for efficient data handling and display

### File Scanning Process

1. Directory traversal using `os.walk`
2. File grouping by size (quick pre-filtering)
3. Content-based duplicate detection using MD5 hashing
4. Results displayed in a structured table view

### Security

- Files are moved to the recycle bin by default (using `send2trash` library)
- Confirmation dialog before any deletion operation
- No automatic deletion without user consent

## Building Executables

### Windows

Using PyInstaller:
```bash
pyinstaller --onefile --windowed --icon=icons/icon.ico main.py
```

### macOS

Using PyInstaller:
```bash
pyinstaller --onefile --windowed --icon=icons/icon_256x256.png main.py
```

Note: For macOS 10.15+, code signing and notarization may be required for distribution.

### Linux

Using PyInstaller:
```bash
pyinstaller --onefile --windowed --icon=icons/icon_linux_256x256.png main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PySide6](https://www.qt.io/qt-for-python)
- Uses [send2trash](https://github.com/arsenetar/send2trash) for safe file deletion
# 文件清理工具(FileSweeper)需求文档

## 1. 项目概述

### 1.1 项目目标
开发一个跨平台的图形化应用程序，帮助用户识别、查看和管理计算机上的重复文件，提供直观的界面让用户决定保留或删除这些文件，从而优化存储空间。

### 1.2 适用平台
- macOS
- Windows
- Linux

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 文件扫描
- 允许用户选择要扫描的文件夹或驱动器
- 支持递归扫描子文件夹
- 提供扫描进度显示
- 允许用户设置扫描过滤条件（如文件类型、大小范围、修改日期等）

#### 2.1.2 重复文件识别
- 使用文件哈希算法（如MD5、SHA-1）识别内容完全相同的文件
- 支持按文件名、大小进行初步筛选以提高效率
- 显示重复文件列表及其详细信息（路径、大小、修改日期等）

#### 2.1.3 文件管理
- 允许用户查看重复文件的内容预览（适用于图片、文本等常见格式）
- 提供文件选择机制，让用户标记要删除的文件
- 支持自动选择策略（如保留最新的文件、保留特定文件夹中的文件等）
- 提供批量删除功能
- 支持将文件移动到回收站或永久删除选项

### 2.2 辅助功能

#### 2.2.1 扫描结果管理
- 支持保存扫描结果以便后续使用
- 允许导出扫描结果（如CSV格式）

#### 2.2.2 用户偏好设置
- 界面语言选择
- 默认扫描设置
- 文件比较方式设置

## 3. 非功能需求

### 3.1 性能要求
- 能够高效处理大量文件（10万+）
- 扫描过程中内存占用合理
- 支持多线程扫描以提高效率

### 3.2 用户体验
- 简洁直观的用户界面
- 响应迅速，操作流畅
- 提供操作确认机制，防止误删文件
- 支持拖放操作

### 3.3 安全性
- 不收集用户个人数据
- 删除操作需要用户确认
- 提供文件恢复选项（如使用系统回收站）

## 4. 用户界面设计

### 4.1 主界面
- 顶部：菜单栏和工具栏
- 左侧：文件夹树状结构或扫描位置列表
- 中央：重复文件列表
- 右侧：选中文件组的详细信息和预览
- 底部：状态栏（显示扫描进度、统计信息等）

### 4.2 扫描设置对话框
- 扫描位置选择
- 过滤条件设置
- 扫描方式选项

### 4.3 结果视图
- 分组显示重复文件
- 提供列表/网格/详细信息等多种查看模式
- 支持排序和筛选功能

### 4.4 文件操作界面
- 文件选择复选框
- 右键菜单提供快捷操作
- 批量操作按钮

## 5. 技术要求

### 5.1 开发技术
- 使用跨平台框架（Python+PySide6）
- 支持本地文件系统操作

### 5.2 系统要求
- macOS 10.13或更高版本
- Windows 10或更高版本
- 最小内存要求：4GB

## 6. 项目交付

### 6.1 交付物
- 可执行应用程序（macOS和Windows版本）
- 用户手册
- 源代码

### 6.2 未来扩展可能性
- 支持更多平台
- 增加相似图片识别功能
- 添加云存储扫描支持
- 提供命令行界面版本

## 7. 项目风险

- 大文件扫描性能挑战
- 跨平台界面一致性
- 文件系统权限问题
- 误删风险管理

## 8. 验收标准

- 应用能在指定的操作系统上正常安装和运行
- 成功识别并显示重复文件
- 文件删除功能正常工作且安全
- 用户界面响应迅速，操作直观
- 无明显崩溃或数据丢失风险

## 9. 技术实现建议

### 9.1 性能与文件扫描优化

#### 9.1.1 内存管理
- 避免一次性加载所有文件信息到内存
- 使用生成器（yield）或分批加载来节省内存
- UI显示时采用懒加载（分页/滚动加载）

#### 9.1.2 多线程/多进程处理
- GUI主线程负责界面响应
- 文件扫描、哈希计算放到QThread或concurrent.futures.ThreadPoolExecutor
- 避免在UI线程直接执行os.walk()和哈希计算，防止界面卡死

#### 9.1.3 哈希计算优化
- 分两步处理：先比较文件大小→相同大小才计算哈希（MD5/SHA256）
- 大文件先计算前几MB哈希（快速比较），再做全文件哈希（确认）

### 9.2 跨平台兼容性

#### 9.2.1 路径处理
- 使用os.path或pathlib处理路径（避免硬编码/或\）

#### 9.2.2 编码问题
- macOS默认UTF-8，Windows有时是cp1252或gbk，需统一为UTF-8

#### 9.2.3 文件删除
- 不直接使用os.remove，推荐使用send2trash库，文件进入回收站（防止误删）

#### 9.2.4 权限问题
- macOS 10.15+访问"桌面/文档/下载"等需要用户授权
- Windows有时需要管理员权限（UAC提升）
- 应用程序会自动检测权限问题并提示用户授予权限

#### 9.3 PySide6开发注意事项

#### 9.3.1 信号槽
- PySide6的信号自动类型推断较好，但要注意循环引用问题
- 槽函数引用控件时，考虑使用弱引用或适时断开连接

#### 9.3.2 UI更新
- 只能在主线程更新UI
- 后台线程完成任务后使用Signal通知主线程刷新

#### 9.3.3 Qt Designer集成
- 可以用Qt Designer设计界面，再用pyside6-uic转换为Python类
- 不要直接修改生成的.py文件，应在自定义类中继承

#### 9.3.4 资源文件
- 图片、图标等放到.qrc文件中，用pyside6-rcc编译成Python模块

### 9.4 打包与发布

#### 9.4.1 Windows打包
- 使用PyInstaller打包成.exe，添加--noconsole参数去掉终端窗口

#### 9.4.2 macOS打包
- 使用py2app或PyInstaller打包.app
- 记得进行签名和公证（macOS 10.15+需要）

#### 9.4.3 打包优化
- PySide6程序打包后体积较大（50-100MB），可使用--onefile或UPX压缩
- 确保.qss（样式表）、图标等资源被正确打包

### 9.5 UI设计实现

#### 9.5.1 文件列表
- 使用QTableView或QTreeView，配合QStandardItemModel
- 支持多选、排序（按大小、路径、重复列表）

#### 9.5.2 批量选择功能
- 按重复列表自动选中（保留一个，选中其他）

#### 9.5.3 进度与状态提示
- 扫描和删除过程添加QProgressBar
- 状态栏(QStatusBar)显示扫描进度和剩余时间

#### 9.5.4 主题
- 使用QSS美化界面，或使用第三方主题（如Qt Material）

### 9.6 权限与安全
- 删除文件前必须二次确认（弹窗）
- 提供"预览"功能（图片、文本文件可以小预览）
- 写日志文件，记录删除操作（方便追踪）

### 9.7 总结建议
- 架构：主线程负责UI，后台线程处理扫描和哈希计算
- 交互：提供及时反馈（进度条、可取消操作）
- 跨平台：特别注意路径、编码、权限问题
- 打包：提前测试打包产物在目标系统的兼容性