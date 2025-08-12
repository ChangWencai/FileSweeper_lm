# 图标使用说明

## 生成的图标文件

图标生成脚本 (`generate_icon.py`) 会生成适用于不同平台的图标文件，所有图标文件都位于 `icons` 目录中：

### Windows
- `icons/icon.ico` - Windows应用程序图标（包含多种尺寸）

### macOS
- `icons/icon_16x16.png`
- `icons/icon_32x32.png`
- `icons/icon_64x64.png`
- `icons/icon_128x128.png`
- `icons/icon_256x256.png`
- `icons/icon_512x512.png`

注意：macOS原生使用ICNS格式，但PyInstaller等打包工具通常可以直接使用PNG文件。如需生成ICNS文件，可以使用macOS自带的`sips`或第三方工具。

### Linux
- `icons/icon_linux_16x16.png`
- `icons/icon_linux_24x24.png`
- `icons/icon_linux_32x32.png`
- `icons/icon_linux_48x48.png`
- `icons/icon_linux_64x64.png`
- `icons/icon_linux_128x128.png`
- `icons/icon_linux_256x256.png`

## 打包时使用图标

### 使用PyInstaller打包

#### Windows
```bash
pyinstaller --onefile --windowed --icon=icons/icon.ico main.py
```

#### macOS
```bash
pyinstaller --onefile --windowed --icon=icons/icon_256x256.png main.py
```

#### Linux
```bash
pyinstaller --onefile --windowed --icon=icons/icon_linux_256x256.png main.py
```

## 创建macOS ICNS文件（可选）

在macOS系统上，可以使用以下命令将PNG文件转换为ICNS格式：

```bash
# 创建图标目录
mkdir -p icons/icon.iconset

# 复制PNG文件到图标目录（需要特定文件名）
cp icons/icon_16x16.png icons/icon.iconset/icon_16x16.png
cp icons/icon_32x32.png icons/icon.iconset/icon_16x16@2x.png
cp icons/icon_32x32.png icons/icon.iconset/icon_32x32.png
cp icons/icon_64x64.png icons/icon.iconset/icon_32x32@2x.png
cp icons/icon_128x128.png icons/icon.iconset/icon_128x128.png
cp icons/icon_256x256.png icons/icon.iconset/icon_128x128@2x.png
cp icons/icon_256x256.png icons/icon.iconset/icon_256x256.png
cp icons/icon_512x512.png icons/icon.iconset/icon_256x256@2x.png
cp icons/icon_512x512.png icons/icon.iconset/icon_512x512.png

# 创建ICNS文件
iconutil -c icns icons/icon.iconset

# 清理临时目录
rm -rf icons/icon.iconset
```

## Qt应用程序中使用图标

在Qt/PySide6应用程序中，可以在代码中设置窗口图标：

```python
# 在主窗口初始化时
self.setWindowIcon(QIcon('icons/icon_256x256.png'))
```

或者在打包时通过资源文件指定。

## 注意事项

1. 图标设计采用了文件夹和重复文件的视觉元素，体现FileSweeper的功能特性
2. 使用钢蓝色作为主色调，体现专业性和技术感
3. 所有图标都是PNG格式（除了Windows的ICO文件），支持透明度
4. 建议在不同平台使用对应尺寸的图标以获得最佳显示效果