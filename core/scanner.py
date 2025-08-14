#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件扫描器
"""

import os
import threading
from PySide6.QtCore import QObject, Signal, QDir


class FileScanner(QObject):
    """文件扫描器类"""
    scan_started = Signal()
    # 扫描进度信号 (当前路径)
    scan_progress = Signal(str)
    
    # 扫描完成信号 (文件列表)
    scan_finished = Signal(list)
    
    # 扫描取消信号
    scan_cancelled = Signal()
    
    # 扫描错误信号
    scan_error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.cancelled = False
        self.min_file_size = 0      # 最小文件大小(KB)
        self.max_file_size = 0      # 最大文件大小(KB)
        self.file_type_filter = "all"  # 文件类型过滤器
        self.custom_extensions = ""    # 自定义扩展名
        self.scan_thread = None        # 扫描线程引用
        
    def set_filters(self, min_size, max_size, file_type, custom_ext):
        """设置文件过滤器"""
        self.min_file_size = min_size
        self.max_file_size = max_size
        self.file_type_filter = file_type
        self.custom_extensions = custom_ext
        
    def start_scan(self, path):
        """开始扫描"""
        self.cancelled = False
        # 在新线程中执行扫描
        self.scan_thread = threading.Thread(target=self._scan_directory, args=(path,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def stop_scan(self):
        """停止扫描"""
        self.cancelled = True
        
    def _scan_directory(self, path):
        """扫描目录"""
        try:
            file_list = []
            
            # 检查路径是否存在
            if not os.path.exists(path):
                self.scan_error.emit(f"路径不存在: {path}")
                return
                
            # 检查路径是否为目录
            if not os.path.isdir(path):
                self.scan_error.emit(f"路径不是目录: {path}")
                return
                
            # 遍历目录
            for root, dirs, files in os.walk(path):
                # 检查是否需要取消扫描
                if self.cancelled:
                    self.scan_cancelled.emit()
                    return
                    
                # 发出进度信号
                self.scan_progress.emit(root)
                
                # 遍历文件
                for file in files:
                    # 检查是否需要取消扫描
                    if self.cancelled:
                        self.scan_cancelled.emit()
                        return
                        
                    file_path = os.path.join(root, file)
                    
                    # 检查是否为有效文件
                    if not os.path.isfile(file_path):
                        continue
                        
                    # 根据设置过滤文件
                    if self._should_include_file(file_path):
                        file_list.append(file_path)
            
            # 扫描完成
            self.scan_finished.emit(file_list)
            
        except Exception as e:
            self.scan_error.emit(str(e))
            
    def _should_include_file(self, file_path):
        """检查文件是否应该包含在扫描结果中"""
        try:
            # 获取文件大小（字节）
            file_size = os.path.getsize(file_path)
            file_size_kb = file_size / 1024  # 转换为KB
            
            # 检查最小文件大小
            if self.min_file_size > 0 and file_size_kb < self.min_file_size:
                return False
                
            # 检查最大文件大小
            if self.max_file_size > 0 and file_size_kb > self.max_file_size:
                return False
                
            # 检查文件类型过滤器
            if self.file_type_filter != "all":
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if self.file_type_filter == "image":
                    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico"}
                    if file_ext not in image_extensions:
                        return False
                        
                elif self.file_type_filter == "document":
                    document_extensions = {".txt", ".doc", ".docx", ".pdf", ".md", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx",".csv",".xlsm",".xlsb",".xltx",".xltm",".yaml",".json",".xml",".yml"}
                    if file_ext not in document_extensions:
                        return False
                        
                elif self.file_type_filter == "audio":
                    audio_extensions = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"}
                    if file_ext not in audio_extensions:
                        return False
                        
                elif self.file_type_filter == "video":
                    video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"}
                    if file_ext not in video_extensions:
                        return False
                        
                elif self.file_type_filter == "custom":
                    # 处理自定义扩展名
                    if self.custom_extensions:
                        custom_exts = {ext.strip().lower() for ext in self.custom_extensions.split(",") if ext.strip()}
                        # 确保扩展名以点开头
                        custom_exts = {ext if ext.startswith(".") else "." + ext for ext in custom_exts}
                        if file_ext not in custom_exts:
                            return False
                    else:
                        # 如果没有自定义扩展名，则不包含任何文件
                        return False
                        
            return True
        except:
            # 如果出现错误（如无法获取文件信息），默认包含文件
            return True