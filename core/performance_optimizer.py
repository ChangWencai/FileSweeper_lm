#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
性能优化模块
提供更完善的性能优化功能
"""

import os
import sys
import hashlib
import mmap
import json
import time
import tempfile
import platform
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import psutil


class PerformanceOptimizer:
    """性能优化器类"""
    
    def __init__(self):
        # 哈希缓存
        self.hash_cache = {}
        self.cache_file = os.path.join(tempfile.gettempdir(), 'filesweeper_hash_cache.json')
        
        # 系统信息
        self.cpu_count = psutil.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.system = platform.system()
        
        # 性能配置
        self.config = {
            'max_workers': self._calculate_optimal_workers(),
            'chunk_size': 65536,  # 64KB chunks
            'memory_limit': int(self.total_memory * 0.1),  # 使用不超过10%的内存
            'use_mmap_threshold': 1024 * 1024 * 1024,  # 1GB
            'cache_enabled': True,
            'adaptive_processing': True
        }
        
        # 加载缓存
        self.load_cache()
        
    def _calculate_optimal_workers(self):
        """计算最优工作线程数"""
        # 基于CPU核心数和系统类型计算
        if self.system == "Darwin":  # macOS
            # macOS上通常使用较少的进程以避免系统负担
            return min(self.cpu_count, 4)
        elif self.system == "Windows":
            # Windows上可以使用更多进程
            return min(self.cpu_count + 2, 8)
        else:
            # Linux上根据内存调整
            if self.total_memory > 8 * 1024 * 1024 * 1024:  # 8GB以上内存
                return min(self.cpu_count + 2, 12)
            else:
                return min(self.cpu_count, 6)
    
    def load_cache(self):
        """加载哈希缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.hash_cache = json.load(f)
        except Exception as e:
            print(f"加载哈希缓存时出错: {e}")
            self.hash_cache = {}
    
    def save_cache(self):
        """保存哈希缓存"""
        if not self.config['cache_enabled']:
            return
            
        try:
            # 限制缓存大小
            if len(self.hash_cache) > 5000:
                # 只保留最近使用的2000项
                sorted_items = sorted(self.hash_cache.items(), 
                                    key=lambda x: x[1].get('timestamp', 0), 
                                    reverse=True)
                self.hash_cache = dict(sorted_items[:2000])
                
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.hash_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存哈希缓存时出错: {e}")
    
    def get_file_hash(self, filepath, fast_scan_mode=False, fast_scan_size=4):
        """
        获取文件哈希值，使用多种优化技术
        
        Args:
            filepath (str): 文件路径
            fast_scan_mode (bool): 是否启用快速扫描模式
            fast_scan_size (int): 快速扫描大小(MB)
            
        Returns:
            str: 文件哈希值，出错时返回None
        """
        try:
            # 获取文件信息
            file_size = os.path.getsize(filepath)
            file_mtime = os.path.getmtime(filepath)
            
            # 检查缓存
            if self.config['cache_enabled']:
                cache_key = f"{file_size}_{file_mtime}_{fast_scan_mode}_{fast_scan_size}"
                if cache_key in self.hash_cache:
                    cached_data = self.hash_cache[cache_key]
                    # 验证缓存有效性
                    if (cached_data.get('filepath') == filepath and 
                        time.time() - cached_data.get('timestamp', 0) < 86400):  # 24小时内有效
                        return cached_data['hash']
            
            # 根据文件大小和系统资源选择最优处理方式
            file_hash = self._calculate_hash_adaptive(filepath, file_size, fast_scan_mode, fast_scan_size)
            
            # 保存到缓存
            if self.config['cache_enabled'] and file_hash:
                self.hash_cache[f"{file_size}_{file_mtime}_{fast_scan_mode}_{fast_scan_size}"] = {
                    'filepath': filepath,
                    'hash': file_hash,
                    'timestamp': time.time()
                }
            
            return file_hash
        except Exception as e:
            print(f"计算文件哈希时出错 {filepath}: {e}")
            return None
    
    def _calculate_hash_adaptive(self, filepath, file_size, fast_scan_mode=False, fast_scan_size=4):
        """
        自适应哈希计算
        
        Args:
            filepath (str): 文件路径
            file_size (int): 文件大小
            fast_scan_mode (bool): 是否启用快速扫描模式
            fast_scan_size (int): 快速扫描大小(MB)
            
        Returns:
            str: 文件哈希值
        """
        # 确定读取大小
        read_size = file_size
        if fast_scan_mode and file_size > fast_scan_size * 1024 * 1024:
            read_size = fast_scan_size * 1024 * 1024
            
        # 根据文件大小和系统选择处理方式
        if file_size > self.config['use_mmap_threshold']:
            # 大文件使用内存映射
            return self._calculate_hash_mmap(filepath, read_size)
        elif file_size > 100 * 1024 * 1024:  # 100MB
            # 中等文件使用优化的读取方式
            return self._calculate_hash_chunked(filepath, read_size)
        else:
            # 小文件使用标准方式
            return self._calculate_hash_standard(filepath, read_size)
    
    def _calculate_hash_mmap(self, filepath, read_size):
        """使用内存映射计算哈希"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    hash_md5.update(mm[:read_size])
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"内存映射哈希计算出错 {filepath}: {e}")
            # 回退到标准方式
            return self._calculate_hash_chunked(filepath, read_size)
    
    def _calculate_hash_chunked(self, filepath, read_size):
        """分块读取计算哈希"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                remaining = read_size
                while remaining > 0:
                    # 根据剩余大小调整块大小
                    chunk_size = min(self.config['chunk_size'], remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    hash_md5.update(data)
                    remaining -= len(data)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"分块哈希计算出错 {filepath}: {e}")
            return None
    
    def _calculate_hash_standard(self, filepath, read_size):
        """标准方式计算哈希"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                data = f.read(read_size)
                hash_md5.update(data)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"标准哈希计算出错 {filepath}: {e}")
            return None
    
    def find_duplicates_parallel(self, files, fast_scan_mode=False, fast_scan_size=4, 
                               use_multiprocessing=True, progress_callback=None):
        """
        并行查找重复文件
        
        Args:
            files (list): 文件路径列表
            fast_scan_mode (bool): 是否启用快速扫描模式
            fast_scan_size (int): 快速扫描大小(MB)
            use_multiprocessing (bool): 是否使用多进程
            progress_callback (callable): 进度回调函数
            
        Returns:
            dict: 重复文件字典 {hash: [file_path, ...]}
        """
        try:
            # 按文件大小预分组
            size_groups = defaultdict(list)
            for filepath in files:
                try:
                    size = os.path.getsize(filepath)
                    size_groups[size].append(filepath)
                except:
                    continue
            
            # 只处理有重复大小的组
            duplicate_candidates = [group for group in size_groups.values() if len(group) > 1]
            
            if not duplicate_candidates:
                return {}
            
            # 根据文件数量选择处理方式
            total_files = sum(len(group) for group in duplicate_candidates)
            
            if total_files > 100 and use_multiprocessing:
                # 大量文件使用并行处理
                return self._find_duplicates_multiprocess(
                    duplicate_candidates, fast_scan_mode, fast_scan_size, progress_callback)
            else:
                # 少量文件使用线程池
                return self._find_duplicates_threaded(
                    duplicate_candidates, fast_scan_mode, fast_scan_size, progress_callback)
        except Exception as e:
            print(f"并行查找重复文件时出错: {e}")
            return {}
    
    def _find_duplicates_multiprocess(self, candidate_groups, fast_scan_mode, fast_scan_size, progress_callback):
        """使用多进程查找重复文件"""
        try:
            duplicates = defaultdict(list)
            processed_count = 0
            total_groups = len(candidate_groups)
            
            # 创建进程池
            max_workers = min(self.config['max_workers'], len(candidate_groups))
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                futures = []
                for group in candidate_groups:
                    future = executor.submit(
                        self._process_group_task,
                        group, fast_scan_mode, fast_scan_size
                    )
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        group_result = future.result()
                        for file_hash, files in group_result.items():
                            if len(files) > 1:
                                duplicates[file_hash] = files
                                
                        processed_count += 1
                        if progress_callback:
                            progress = int(processed_count / total_groups * 100)
                            progress_callback(progress, f"正在处理文件组: {processed_count}/{total_groups}")
                    except Exception as e:
                        print(f"处理文件组结果时出错: {e}")
            
            return dict(duplicates)
        except Exception as e:
            print(f"多进程查找重复文件时出错: {e}")
            return {}
    
    def _find_duplicates_threaded(self, candidate_groups, fast_scan_mode, fast_scan_size, progress_callback):
        """使用线程池查找重复文件"""
        try:
            duplicates = defaultdict(list)
            processed_count = 0
            total_groups = len(candidate_groups)
            
            # 创建线程池
            max_workers = min(max(4, self.cpu_count), len(candidate_groups))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                futures = []
                for group in candidate_groups:
                    future = executor.submit(
                        self._process_group_task,
                        group, fast_scan_mode, fast_scan_size
                    )
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        group_result = future.result()
                        for file_hash, files in group_result.items():
                            if len(files) > 1:
                                duplicates[file_hash] = files
                                
                        processed_count += 1
                        if progress_callback:
                            progress = int(processed_count / total_groups * 100)
                            progress_callback(progress, f"正在处理文件组: {processed_count}/{total_groups}")
                    except Exception as e:
                        print(f"处理文件组结果时出错: {e}")
            
            return dict(duplicates)
        except Exception as e:
            print(f"线程池查找重复文件时出错: {e}")
            return {}
    
    def _process_group_task(self, file_group, fast_scan_mode, fast_scan_size):
        """
        处理单个文件组的任务（用于并行处理）
        
        Args:
            file_group (list): 文件路径列表
            fast_scan_mode (bool): 是否启用快速扫描模式
            fast_scan_size (int): 快速扫描大小(MB)
            
        Returns:
            dict: {hash: [file_path, ...]}
        """
        try:
            hash_groups = defaultdict(list)
            for filepath in file_group:
                file_hash = self.get_file_hash(filepath, fast_scan_mode, fast_scan_size)
                if file_hash:
                    hash_groups[file_hash].append(filepath)
            return dict(hash_groups)
        except Exception as e:
            print(f"处理文件组时出错: {e}")
            return {}
    
    def get_system_resources(self):
        """
        获取系统资源信息
        
        Returns:
            dict: 系统资源信息
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': (disk.total - disk.free) / disk.total * 100
            }
        except Exception as e:
            print(f"获取系统资源信息时出错: {e}")
            return {}
    
    def update_config(self, **kwargs):
        """
        更新配置
        
        Args:
            **kwargs: 配置参数
        """
        self.config.update(kwargs)
        
        # 重新计算相关参数
        if 'max_workers' not in kwargs:
            self.config['max_workers'] = self._calculate_optimal_workers()