#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面
"""

import os
import sys
import send2trash
from PySide6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QMenuBar,
                               QWidget, QVBoxLayout, QSplitter, QFileDialog,
                               QMessageBox, QProgressBar, QLabel, QTreeView,
                               QPushButton, QTableView, QHeaderView, QHBoxLayout,
                               QDialog, QTextEdit, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QDir, QModelIndex
from PySide6.QtGui import QAction, QIcon, QPixmap, QImage
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from ui.file_tree_view import FileTreeView
from ui.duplicate_table_view import DuplicateTableView
from ui.settings_dialog import SettingsDialog
from core.scanner import FileScanner
from core.duplicate_finder import DuplicateFinder


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件清理工具(FileSweeper)")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # 初始化核心组件
        self.scanner = FileScanner()
        self.duplicate_finder = DuplicateFinder()
        
        # 初始化设置
        self.settings = SettingsDialog(self)

        # 初始化UI
        self.init_ui()
        
        # 应用保存的设置（必须在UI初始化之后调用）
        self.apply_settings()
        
        self.init_connections()

    def init_ui(self):
        """初始化UI界面"""
        # 创建菜单栏
        self.create_menus()

        # 创建工具栏
        self.create_toolbar()

        # 创建状态栏
        self.create_status_bar()

        # 创建中央部件
        self.create_central_widget()

    def create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 选择扫描目录
        self.select_folder_action = QAction("选择扫描目录...", self)
        self.select_folder_action.setShortcut("Ctrl+O")
        file_menu.addAction(self.select_folder_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 扫描菜单
        scan_menu = menubar.addMenu("扫描(&S)")

        # 开始扫描
        self.start_scan_action = QAction("开始扫描", self)
        self.start_scan_action.setShortcut("F5")
        scan_menu.addAction(self.start_scan_action)

        # 停止扫描
        self.stop_scan_action = QAction("停止扫描", self)
        self.stop_scan_action.setEnabled(False)
        scan_menu.addAction(self.stop_scan_action)

        # 选择菜单
        select_menu = menubar.addMenu("选择(&E)")
        
        # 全选
        self.select_all_action = QAction("全选", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.setEnabled(False)
        select_menu.addAction(self.select_all_action)
        
        # 全不选
        self.select_none_action = QAction("全不选", self)
        self.select_none_action.setShortcut("Ctrl+Shift+A")
        self.select_none_action.setEnabled(False)
        select_menu.addAction(self.select_none_action)
        
        # 反选
        self.select_invert_action = QAction("反选", self)
        self.select_invert_action.setShortcut("Ctrl+I")
        self.select_invert_action.setEnabled(False)
        select_menu.addAction(self.select_invert_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        # 设置
        settings_action = QAction("设置...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于
        about_action = QAction("关于...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("工具栏")
        toolbar.setMovable(False)

        # 选择文件夹按钮
        self.select_folder_btn = QPushButton("选择扫描目录")
        self.select_folder_btn.clicked.connect(self.select_folder)
        toolbar.addWidget(self.select_folder_btn)

        toolbar.addSeparator()

        # 开始扫描按钮
        self.start_scan_btn = QPushButton("开始扫描")
        self.start_scan_btn.clicked.connect(self.start_scan)
        toolbar.addWidget(self.start_scan_btn)

        # 停止扫描按钮
        self.stop_scan_btn = QPushButton("停止扫描")
        self.stop_scan_btn.setEnabled(False)
        self.stop_scan_btn.clicked.connect(self.stop_scan)
        toolbar.addWidget(self.stop_scan_btn)

        toolbar.addSeparator()

        # 全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setEnabled(False)
        toolbar.addWidget(self.select_all_btn)

        # 全不选按钮
        self.select_none_btn = QPushButton("全不选")
        self.select_none_btn.clicked.connect(self.select_none)
        self.select_none_btn.setEnabled(False)
        toolbar.addWidget(self.select_none_btn)

        # 反选按钮
        self.select_invert_btn = QPushButton("反选")
        self.select_invert_btn.clicked.connect(self.invert_selection)
        self.select_invert_btn.setEnabled(False)
        toolbar.addWidget(self.select_invert_btn)

        toolbar.addSeparator()
        
        # 自动选择按钮
        self.auto_select_btn = QPushButton("自动选择")
        self.auto_select_btn.clicked.connect(self.auto_select_files)
        self.auto_select_btn.setEnabled(False)
        self.auto_select_btn.setToolTip("根据设置的高级自动选择策略来选择文件")
        toolbar.addWidget(self.auto_select_btn)

        toolbar.addSeparator()

        # 删除选中文件按钮
        self.delete_selected_btn = QPushButton("删除选中文件")
        self.delete_selected_btn.clicked.connect(self.delete_selected_files)
        self.delete_selected_btn.setEnabled(False)
        toolbar.addWidget(self.delete_selected_btn)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # 选中文件计数标签
        self.selected_count_label = QLabel("选中: 0 个文件")
        self.status_bar.addPermanentWidget(self.selected_count_label)

    def create_central_widget(self):
        """创建中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建主分割器（水平分割）
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧：文件夹树状结构
        self.file_tree_view = FileTreeView()
        main_splitter.addWidget(self.file_tree_view)

        # 中间：重复文件列表
        self.duplicate_table_view = DuplicateTableView()
        main_splitter.addWidget(self.duplicate_table_view)

        # 右侧：预览面板
        self.create_preview_panel()
        main_splitter.addWidget(self.preview_panel)

        # 设置分割器比例
        main_splitter.setSizes([200, 600, 200])

        layout.addWidget(main_splitter)
        
    def create_preview_panel(self):
        """创建预览面板"""
        self.preview_panel = QWidget()
        self.preview_panel.setWindowTitle("文件预览")
        preview_layout = QVBoxLayout(self.preview_panel)
        
        # 预览标题
        self.preview_title = QLabel("文件预览")
        self.preview_title.setAlignment(Qt.AlignCenter)
        self.preview_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        preview_layout.addWidget(self.preview_title)
        
        # 预览内容区域（图片）
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(150, 200)
        self.image_preview.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.image_preview.setScaledContents(False)
        preview_layout.addWidget(self.image_preview)
        
        # 文本预览区域
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setMaximumHeight(150)
        self.text_preview.hide()
        preview_layout.addWidget(self.text_preview)
        
        # 文件信息区域
        self.file_info = QLabel()
        self.file_info.setWordWrap(True)
        self.file_info.setStyleSheet("padding: 5px;")
        preview_layout.addWidget(self.file_info)
        
        # 添加弹簧以使布局更美观
        preview_layout.addStretch()
        
    def preview_file(self, file_path):
        """预览文件内容"""
        if not file_path or not os.path.exists(file_path):
            self.preview_title.setText("文件预览")
            self.image_preview.show()
            self.image_preview.setText("文件不存在")
            self.text_preview.hide()
            self.file_info.setText("")
            return
            
        # 更新预览标题
        self.preview_title.setText(f"文件预览: {os.path.basename(file_path)}")
        
        # 获取文件信息
        try:
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            from PySide6.QtCore import QDateTime
            mtime_str = QDateTime.fromSecsSinceEpoch(int(file_mtime)).toString("yyyy-MM-dd hh:mm:ss")
            
            info_text = f"路径: {file_path}\n大小: {self.format_file_size(file_size)}\n修改时间: {mtime_str}"
            self.file_info.setText(info_text)
        except Exception as e:
            self.file_info.setText(f"无法获取文件信息: {str(e)}")
            
        # 隐藏所有预览控件
        self.image_preview.hide()
        self.text_preview.hide()
            
        # 根据文件类型进行预览
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 图片文件预览
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp']:
            self.preview_image(file_path)
        # 文本文件预览
        elif file_ext in ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.yaml', '.yml']:
            self.preview_text(file_path)
        # 其他文件类型
        else:
            self.image_preview.show()
            self.image_preview.setText(f"文件类型: {file_ext}\n\n此文件类型不支持预览。\n\n双击文件可在默认应用程序中打开。")
            
    def preview_image(self, file_path):
        """预览图片文件"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.image_preview.show()
                self.image_preview.setText("无法加载图片")
                return
                
            # 缩放图片以适应预览区域
            pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.image_preview.setPixmap(pixmap)
            self.image_preview.show()
        except Exception as e:
            self.image_preview.show()
            self.image_preview.setText(f"加载图片时出错: {str(e)}")
            
    def preview_text(self, file_path):
        """预览文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # 只读取前1000个字符
                
            if len(content) == 1000:
                content += "\n\n... (内容过长，仅显示前1000个字符)"
                
            self.text_preview.setPlainText(content)
            self.text_preview.show()
        except Exception as e:
            self.text_preview.show()
            self.text_preview.setPlainText(f"读取文本文件时出错: {str(e)}")

    def init_connections(self):
        """初始化信号连接"""
        self.select_folder_action.triggered.connect(self.select_folder)
        self.start_scan_action.triggered.connect(self.start_scan)
        self.stop_scan_action.triggered.connect(self.stop_scan)
        self.select_all_action.triggered.connect(self.select_all)
        self.select_none_action.triggered.connect(self.select_none)
        self.select_invert_action.triggered.connect(self.invert_selection)

        # 连接扫描器信号
        self.scanner.scan_started.connect(self.on_scan_started)
        self.scanner.scan_progress.connect(self.on_scan_progress)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.scan_error.connect(self.on_scan_error)

        # 连接重复文件查找器信号
        self.duplicate_finder.find_started.connect(self.on_find_started)
        self.duplicate_finder.find_progress.connect(self.on_find_progress)
        self.duplicate_finder.find_finished.connect(self.on_find_finished)
        self.duplicate_finder.find_error.connect(self.on_find_error)

        # 连接表格视图信号
        self.duplicate_table_view.checked_files_changed.connect(self.on_checked_files_changed)
        self.duplicate_table_view.file_selected.connect(self.on_file_selected)

    def select_folder(self):
        """选择扫描目录"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择扫描目录", QDir.homePath())

        if folder:
            self.file_tree_view.set_root_path(folder)
            self.status_label.setText(f"已选择目录: {folder}")

    def start_scan(self):
        """开始扫描"""
        root_path = self.file_tree_view.get_root_path()
        if not root_path:
            QMessageBox.warning(self, "警告", "请先选择要扫描的目录！")
            return

        if not os.path.exists(root_path):
            QMessageBox.critical(self, "错误", "选择的目录不存在！")
            return

        # 禁用开始扫描相关控件，启用停止扫描控件
        self.select_folder_action.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.start_scan_action.setEnabled(False)
        self.start_scan_btn.setEnabled(False)
        self.stop_scan_action.setEnabled(True)
        self.stop_scan_btn.setEnabled(True)
        self.delete_selected_btn.setEnabled(False)
        self.select_all_action.setEnabled(False)
        self.select_none_action.setEnabled(False)
        self.select_invert_action.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.select_none_btn.setEnabled(False)
        self.select_invert_btn.setEnabled(False)
        self.auto_select_btn.setEnabled(False)  # 禁用自动选择按钮

        # 开始扫描
        self.scanner.start_scan(root_path)

    def stop_scan(self):
        """停止扫描"""
        self.scanner.stop_scan()

    def select_all(self):
        """全选所有文件"""
        self.duplicate_table_view.select_all()

    def select_none(self):
        """全不选所有文件"""
        self.duplicate_table_view.deselect_all()

    def invert_selection(self):
        """反选所有文件"""
        self.duplicate_table_view.invert_selection()

    def auto_select_files(self):
        """根据高级自动选择策略自动选择文件"""
        # 获取当前的策略设置
        strategy = self.settings.get_auto_select_strategy()
        folder = self.settings.get_auto_select_folder()
        
        # 应用策略到当前数据
        self.duplicate_table_view.model.set_auto_select_strategy(strategy, folder)
        self.duplicate_table_view.model.apply_auto_select_strategy()
        
        # 更新选中文件计数
        self.on_checked_files_changed()
        
        # 更新状态栏信息
        strategy_names = {
            "first": "保留每组第一个文件",
            "newest": "保留每组最新文件",
            "folder": f"保留{folder}中的文件" if folder else "保留指定文件夹中的文件"
        }
        strategy_name = strategy_names.get(strategy, "默认策略")
        self.status_label.setText(f"已根据策略'{strategy_name}'自动选择文件")

    def on_scan_started(self):
        """扫描开始时的处理"""
        self.status_label.setText("正在扫描...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

    def on_scan_progress(self, message):
        """扫描进度更新"""
        self.status_label.setText(message)
        # 如果消息包含进度信息，尝试解析并更新进度条
        if "扫描完成" in message:
            self.progress_bar.setValue(100)
        elif "正在扫描" in message:
            # 对于正在扫描的消息，保持进度条活动状态
            current_value = self.progress_bar.value()
            if current_value < 90:  # 不要达到100%，直到真正完成
                self.progress_bar.setValue(min(current_value + 1, 90))

    def on_scan_finished(self, files):
        """扫描完成时的处理"""
        self.status_label.setText(f"扫描完成，共发现 {len(files)} 个文件")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

        # 启用开始扫描相关控件，禁用停止扫描控件
        self.select_folder_action.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.start_scan_action.setEnabled(True)
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_action.setEnabled(False)
        self.stop_scan_btn.setEnabled(False)

        # 应用设置
        self.apply_settings()

        # 查找重复文件
        self.find_duplicates(files)

    def on_scan_error(self, error_message):
        """扫描出错时的处理"""
        QMessageBox.critical(self, "扫描错误", error_message)
        self.status_label.setText("扫描出错")
        self.progress_bar.setVisible(False)

        # 启用开始扫描相关控件，禁用停止扫描控件
        self.select_folder_action.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.start_scan_action.setEnabled(True)
        self.start_scan_btn.setEnabled(True)
        self.stop_scan_action.setEnabled(False)
        self.stop_scan_btn.setEnabled(False)
        self.auto_select_btn.setEnabled(False)  # 禁用自动选择按钮

    def find_duplicates(self, files):
        """查找重复文件"""
        # 使用DuplicateFinder来查找重复文件
        self.duplicate_finder.start_find(files)

    def on_find_started(self):
        """查找重复文件开始时的处理"""
        self.status_label.setText("正在查找重复文件...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式

    def on_find_progress(self, progress, message):
        """查找重复文件进度更新"""
        if progress >= 0:  # 如果进度不是不确定模式
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    def on_find_finished(self, duplicates):
        """查找重复文件完成时的处理"""
        self.progress_bar.setVisible(False)
        
        # 更新表格视图
        self.duplicate_table_view.update_data(duplicates)
        
        # 启用选择和删除相关控件
        self.delete_selected_btn.setEnabled(True)
        self.select_all_action.setEnabled(True)
        self.select_none_action.setEnabled(True)
        self.select_invert_action.setEnabled(True)
        self.select_all_btn.setEnabled(True)
        self.select_none_btn.setEnabled(True)
        self.select_invert_btn.setEnabled(True)
        self.auto_select_btn.setEnabled(True)  # 启用自动选择按钮
        
        # 更新状态和选中文件计数
        total_groups = len(duplicates)
        total_files = sum(len(files) for files in duplicates.values())
        checked_files = len(self.duplicate_table_view.model.get_checked_files())
        
        self.status_label.setText(f"扫描完成: 发现 {total_groups} 组重复文件，共 {total_files} 个文件")
        self.selected_count_label.setText(f"选中: {checked_files} 个文件")

    def on_find_error(self, error_message):
        """查找重复文件出错时的处理"""
        QMessageBox.critical(self, "查找错误", error_message)
        self.status_label.setText("查找重复文件出错")
        self.progress_bar.setVisible(False)
        self.auto_select_btn.setEnabled(False)  # 禁用自动选择按钮

    def on_checked_files_changed(self):
        """选中文件改变时的处理"""
        checked_files = self.duplicate_table_view.get_checked_files()
        self.selected_count_label.setText(f"选中: {len(checked_files)} 个文件")

    def on_file_selected(self, file_path):
        """文件被选中时的处理"""
        self.preview_file(file_path)

    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def delete_selected_files(self):
        """删除选中的文件"""
        checked_files = self.duplicate_table_view.get_checked_files()
        
        if not checked_files:
            QMessageBox.information(self, "提示", "没有选中的文件需要删除！")
            return

        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除选中的 {len(checked_files)} 个文件吗？\n\n"
            "文件将被移至回收站。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                deleted_count = 0
                for file_path in checked_files:
                    try:
                        send2trash.send2trash(file_path)
                        deleted_count += 1
                    except Exception as e:
                        QMessageBox.warning(
                            self, 
                            "删除失败", 
                            f"无法删除文件: {file_path}\n错误: {str(e)}"
                        )

                QMessageBox.information(
                    self, 
                    "删除完成", 
                    f"成功删除 {deleted_count} 个文件（已移至回收站）"
                )
                
                # 重新扫描以更新结果
                self.status_label.setText("正在重新扫描...")
                root_path = self.file_tree_view.get_root_path()
                if root_path:
                    self.scanner.start_scan(root_path)
                else:
                    # 如果没有有效的根路径，确保按钮状态正确
                    self.auto_select_btn.setEnabled(False)
                    
            except Exception as e:
                QMessageBox.critical(self, "删除错误", f"删除过程中发生错误: {str(e)}")
                # 出错时确保按钮状态正确
                self.auto_select_btn.setEnabled(bool(self.duplicate_table_view.model.duplicates))
            
    def show_settings(self):
        """显示设置对话框"""
        # 显示设置对话框
        if self.settings.exec() == QDialog.Accepted:
            # 应用设置
            self.apply_settings()
            
    def apply_settings(self):
        """应用设置"""
        # 获取设置值并应用到相关组件
        auto_select = self.settings.get_auto_select_duplicates()
        self.duplicate_table_view.model.set_auto_select_duplicates(auto_select)
        
        # 应用高级自动选择策略
        strategy = self.settings.get_auto_select_strategy()
        folder = self.settings.get_auto_select_folder()
        self.duplicate_table_view.model.set_auto_select_strategy(strategy, folder)
        
        # 应用扫描过滤设置
        min_size = self.settings.get_min_file_size()
        max_size = self.settings.get_max_file_size()
        file_type = self.settings.get_file_type_filter()
        custom_ext = self.settings.get_custom_extensions()
        self.scanner.set_filters(min_size, max_size, file_type, custom_ext)
        
        # 应用大文件优化设置到重复文件查找器
        fast_scan_mode = self.settings.get_fast_scan_mode()
        fast_scan_size = self.settings.get_fast_scan_size()
        use_multiprocessing = self.settings.get_use_multiprocessing()
        use_mmap = self.settings.get_use_mmap()
        cache_hashes = self.settings.get_cache_hashes()
        
        self.duplicate_finder.set_optimization_settings(
            fast_scan_mode, fast_scan_size, use_multiprocessing, use_mmap, cache_hashes)
        
        # 如果已经有扫描结果，重新应用设置
        if self.duplicate_table_view.model.duplicates:
            self.duplicate_table_view.model.update_data(self.duplicate_table_view.model.duplicates)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于文件清理工具",
                          "文件清理工具(FileSweeper) v1.0.0\n\n"
                          "一个帮助您识别和管理重复文件的工具。\n"
                          "支持Windows、macOS和Linux平台。")