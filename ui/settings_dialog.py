#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置对话框
"""

import os
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
                               QPushButton, QGroupBox, QButtonGroup, QRadioButton,
                               QLabel, QSpinBox, QFormLayout, QComboBox)
from PySide6.QtCore import Qt, QDir


class SettingsDialog(QDialog):
    """设置对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(400, 300)
        
        # 配置文件路径
        self.config_file = os.path.join(QDir.homePath(), '.filesweeper_config.json')
        
        # 设置项
        self.auto_select_duplicates = True  # 默认选中重复文件
        self.trash_delete_method = True     # 默认使用回收站删除
        
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
        
        # 添加到主布局
        layout.addWidget(duplicate_group)
        layout.addWidget(delete_group)
        
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
        
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auto_select_duplicates = config.get('auto_select_duplicates', True)
                    self.trash_delete_method = config.get('trash_delete_method', True)
            else:
                # 如果配置文件不存在，使用默认值
                self.auto_select_duplicates = True
                self.trash_delete_method = True
        except Exception as e:
            print(f"加载设置时出错: {e}")
            # 出错时使用默认值
            self.auto_select_duplicates = True
            self.trash_delete_method = True
            
        # 更新UI
        self.auto_select_checkbox.setChecked(self.auto_select_duplicates)
        self.trash_delete_checkbox.setChecked(self.trash_delete_method)
        
    def save_settings(self):
        """保存设置"""
        self.auto_select_duplicates = self.auto_select_checkbox.isChecked()
        self.trash_delete_method = self.trash_delete_checkbox.isChecked()
        
        # 保存到配置文件
        try:
            config = {
                'auto_select_duplicates': self.auto_select_duplicates,
                'trash_delete_method': self.trash_delete_method
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
        
    def accept(self):
        """确定按钮点击事件"""
        self.save_settings()
        super().accept()