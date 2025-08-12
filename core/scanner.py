#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件扫描器
"""

import os
import threading
from PySide6.QtCore import QObject, Signal, QThread


class ScannerThread(QThread):
    """扫描线程类"""
    # 定义信号
    scan_started = Signal()
    scan_progress = Signal(int, str)  # 进度百分比和消息
    scan_finished = Signal(list)      # 扫描完成，传递文件列表
    scan_error = Signal(str)          # 扫描出错，传递错误消息

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self._stop_flag = False

    def run(self):
        """线程执行函数"""
        try:
            self.scan_started.emit()
            
            files = []
            total_files = self._count_files()
            processed_files = 0
            
            # 遍历目录
            for dirpath, dirnames, filenames in os.walk(self.root_path):
                if self._stop_flag:
                    break
                    
                for filename in filenames:
                    if self._stop_flag:
                        break
                        
                    filepath = os.path.join(dirpath, filename)
                    try:
                        # 检查文件是否存在且可访问
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            files.append(filepath)
                            
                        processed_files += 1
                        if total_files > 0:
                            progress = int((processed_files / total_files) * 100)
                            self.scan_progress.emit(progress, f"正在扫描: {filepath}")
                    except Exception as e:
                        # 忽略单个文件错误，继续扫描
                        continue
                        
            if not self._stop_flag:
                self.scan_finished.emit(files)
        except Exception as e:
            self.scan_error.emit(str(e))

    def stop(self):
        """停止扫描"""
        self._stop_flag = True

    def _count_files(self):
        """计算文件总数（估算）"""
        try:
            count = 0
            for dirpath, dirnames, filenames in os.walk(self.root_path):
                if self._stop_flag:
                    break
                count += len(filenames)
            return count
        except:
            return 0


class FileScanner(QObject):
    """文件扫描器类"""
    # 定义信号
    scan_started = Signal()
    scan_progress = Signal(int, str)  # 进度百分比和消息
    scan_finished = Signal(list)      # 扫描完成，传递文件列表
    scan_error = Signal(str)          # 扫描出错，传递错误消息

    def __init__(self):
        super().__init__()
        self.scan_thread = None

    def start_scan(self, root_path):
        """开始扫描"""
        # 如果已有扫描线程在运行，则先停止
        if self.scan_thread and self.scan_thread.isRunning():
            self.stop_scan()
            
        # 创建新的扫描线程
        self.scan_thread = ScannerThread(root_path)
        
        # 连接信号
        self.scan_thread.scan_started.connect(self.scan_started)
        self.scan_thread.scan_progress.connect(self.scan_progress)
        self.scan_thread.scan_finished.connect(self.scan_finished)
        self.scan_thread.scan_error.connect(self.scan_error)
        
        # 启动线程
        self.scan_thread.start()

    def stop_scan(self):
        """停止扫描"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()