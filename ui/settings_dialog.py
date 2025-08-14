#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置对话框
"""

import os
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
                               QPushButton, QGroupBox, QButtonGroup, QRadioButton,
                               QLabel, QSpinBox, QFormLayout, QComboBox, QLineEdit, QSizePolicy)
from PySide6.QtCore import Qt, QDir


class SettingsDialog(QDialog):
    """设置对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(400, 400)
        
        # 配置文件路径
        self.config_file = os.path.join(QDir.homePath(), '.filesweeper_config.json')
        
        # 设置项
        self.auto_select_duplicates = True  # 默认选中重复文件
        self.trash_delete_method = True     # 默认使用回收站删除
        self.min_file_size = 0              # 最小文件大小（KB）
        self.max_file_size = 0              # 最大文件大小（KB，0表示无限制）
        self.file_type_filter = "all"       # 文件类型过滤器
        self.custom_extensions = ""         # 自定义扩展名
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 重复文件设置组
        duplicate_group = QGroupBox("重复文件处理")
        duplicate_layout = QVBoxLayout(duplicate_group)
        
        self.auto_select_checkbox = QCheckBox("默认选中重复文件(除每组第一个文件外)")
        self.auto_select_checkbox.setToolTip("开启后，在扫描完成后自动选中除每组第一个文件外的所有重复文件")
        duplicate_layout.addWidget(self.auto_select_checkbox)
        
        # 删除设置组
        delete_group = QGroupBox("文件删除")
        delete_layout = QVBoxLayout(delete_group)
        
        self.trash_delete_checkbox = QCheckBox("使用回收站删除文件")
        self.trash_delete_checkbox.setToolTip("开启后删除文件时会放入回收站，而不是永久删除")
        delete_layout.addWidget(self.trash_delete_checkbox)
        
        # 扫描过滤设置组
        filter_group = QGroupBox("扫描过滤设置")
        filter_layout = QFormLayout(filter_group)
        
        # 最小文件大小
        self.min_size_spinbox = QSpinBox()
        self.min_size_spinbox.setRange(0, 1000000)  # 0 KB 到 1 TB
        self.min_size_spinbox.setValue(0)
        self.min_size_spinbox.setSuffix(" KB")
        filter_layout.addRow(QLabel("最小文件大小:"), self.min_size_spinbox)
        
        # 最大文件大小
        self.max_size_spinbox = QSpinBox()
        self.max_size_spinbox.setRange(0, 1000000)  # 0 KB 到 1 TB
        self.max_size_spinbox.setValue(0)
        self.max_size_spinbox.setSuffix(" KB")
        self.max_size_spinbox.setToolTip("设置为0表示无限制")
        filter_layout.addRow(QLabel("最大文件大小:"), self.max_size_spinbox)
        
        # 文件类型过滤
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItem("所有文件", "all")
        self.file_type_combo.addItem("图片", "image")
        self.file_type_combo.addItem("文档", "document")
        self.file_type_combo.addItem("音频", "audio")
        self.file_type_combo.addItem("视频", "video")
        self.file_type_combo.addItem("自定义", "custom")
        filter_layout.addRow(QLabel("文件类型:"), self.file_type_combo)
        
        # 自定义扩展名
        self.custom_extensions_edit = QLineEdit()
        self.custom_extensions_edit.setPlaceholderText("例如: txt,log,md (用逗号分隔)")
        self.custom_extensions_edit.setToolTip("输入自定义文件扩展名，用逗号分隔")
        filter_layout.addRow(QLabel("自定义扩展名:"), self.custom_extensions_edit)
        
        # 添加到主布局
        layout.addWidget(duplicate_group)
        layout.addWidget(delete_group)
        layout.addWidget(filter_group)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.file_type_combo.currentIndexChanged.connect(self.on_file_type_changed)
        
    def on_file_type_changed(self, index):
        """文件类型选择改变时的处理"""
        file_type = self.file_type_combo.currentData()
        # 只有选择"自定义"时才启用自定义扩展名输入框
        self.custom_extensions_edit.setEnabled(file_type == "custom")
        
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auto_select_duplicates = config.get('auto_select_duplicates', True)
                    self.trash_delete_method = config.get('trash_delete_method', True)
                    self.min_file_size = config.get('min_file_size', 0)
                    self.max_file_size = config.get('max_file_size', 0)
                    self.file_type_filter = config.get('file_type_filter', 'all')
                    self.custom_extensions = config.get('custom_extensions', '')
            else:
                # 如果配置文件不存在，使用默认值
                self.auto_select_duplicates = True
                self.trash_delete_method = True
                self.min_file_size = 0
                self.max_file_size = 0
                self.file_type_filter = "all"
                self.custom_extensions = ""
        except Exception as e:
            print(f"加载设置时出错: {e}")
            # 出错时使用默认值
            self.auto_select_duplicates = True
            self.trash_delete_method = True
            self.min_file_size = 0
            self.max_file_size = 0
            self.file_type_filter = "all"
            self.custom_extensions = ""
            
        # 更新UI
        self.auto_select_checkbox.setChecked(self.auto_select_duplicates)
        self.trash_delete_checkbox.setChecked(self.trash_delete_method)
        self.min_size_spinbox.setValue(self.min_file_size)
        self.max_size_spinbox.setValue(self.max_file_size)
        
        # 设置文件类型过滤器
        index = self.file_type_combo.findData(self.file_type_filter)
        if index >= 0:
            self.file_type_combo.setCurrentIndex(index)
        else:
            self.file_type_combo.setCurrentIndex(0)  # 默认选择"所有文件"
            
        self.custom_extensions_edit.setText(self.custom_extensions)
        self.custom_extensions_edit.setEnabled(self.file_type_filter == "custom")
        
    def save_settings(self):
        """保存设置"""
        self.auto_select_duplicates = self.auto_select_checkbox.isChecked()
        self.trash_delete_method = self.trash_delete_checkbox.isChecked()
        self.min_file_size = self.min_size_spinbox.value()
        self.max_file_size = self.max_size_spinbox.value()
        self.file_type_filter = self.file_type_combo.currentData()
        self.custom_extensions = self.custom_extensions_edit.text().strip()
        
        # 保存到配置文件
        try:
            config = {
                'auto_select_duplicates': self.auto_select_duplicates,
                'trash_delete_method': self.trash_delete_method,
                'min_file_size': self.min_file_size,
                'max_file_size': self.max_file_size,
                'file_type_filter': self.file_type_filter,
                'custom_extensions': self.custom_extensions
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")
        
    def get_auto_select_duplicates(self):
        """获取是否默认选中重复文件"""
        return self.auto_select_duplicates
        
    def get_trash_delete_method(self):
        """获取是否使用回收站删除"""
        return self.trash_delete_method
        
    def get_min_file_size(self):
        """获取最小文件大小(KB)"""
        return self.min_file_size
        
    def get_max_file_size(self):
        """获取最大文件大小(KB)"""
        return self.max_file_size
        
    def get_file_type_filter(self):
        """获取文件类型过滤器"""
        return self.file_type_filter
        
    def get_custom_extensions(self):
        """获取自定义扩展名"""
        return self.custom_extensions
        
    def accept(self):
        """确定按钮点击事件"""
        self.save_settings()
        super().accept()