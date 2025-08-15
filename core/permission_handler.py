#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限处理模块
处理macOS特定权限和Windows UAC权限问题
"""

import os
import sys
import platform
import subprocess
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QStandardPaths


class PermissionHandler:
    """权限处理类"""
    
    @staticmethod
    def check_and_request_permissions(path):
        """
        检查并请求必要的权限
        
        Args:
            path (str): 要检查权限的路径
            
        Returns:
            bool: 是否有权限访问路径
        """
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                return PermissionHandler._check_macos_permissions(path)
            elif system == "Windows":  # Windows
                return PermissionHandler._check_windows_permissions(path)
            else:  # Linux或其他系统
                return PermissionHandler._check_linux_permissions(path)
        except Exception as e:
            print(f"权限检查出错: {e}")
            return False
    
    @staticmethod
    def _check_macos_permissions(path):
        """
        检查macOS权限
        
        Args:
            path (str): 要检查权限的路径
            
        Returns:
            bool: 是否有权限访问路径
        """
        try:
            # 检查是否是受保护的目录
            protected_paths = [
                "/System",
                "/Library",
                "/Applications",
                "/usr",
                "/private"
            ]
            
            # 检查用户主目录下的特殊目录
            user_home = os.path.expanduser("~")
            user_protected_paths = [
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Pictures"),
                os.path.join(user_home, "Music"),
                os.path.join(user_home, "Movies")
            ]
            
            # 检查路径是否在受保护的目录中
            for protected_path in protected_paths:
                if os.path.commonpath([path, protected_path]) == protected_path:
                    # 检查是否具有访问权限
                    if not PermissionHandler._can_access_path(path):
                        return False
            
            # 检查用户目录下的特殊路径
            for protected_path in user_protected_paths:
                if os.path.commonpath([path, protected_path]) == protected_path:
                    # 检查是否具有访问权限
                    if not PermissionHandler._can_access_path(path):
                        return False
                        
            return True
        except Exception as e:
            print(f"macOS权限检查出错: {e}")
            return False
    
    @staticmethod
    def _check_windows_permissions(path):
        """
        检查Windows权限
        
        Args:
            path (str): 要检查权限的路径
            
        Returns:
            bool: 是否有权限访问路径
        """
        try:
            # 检查是否具有访问权限
            return PermissionHandler._can_access_path(path)
        except Exception as e:
            print(f"Windows权限检查出错: {e}")
            return False
    
    @staticmethod
    def _check_linux_permissions(path):
        """
        检查Linux权限
        
        Args:
            path (str): 要检查权限的路径
            
        Returns:
            bool: 是否有权限访问路径
        """
        try:
            # 检查是否具有访问权限
            return PermissionHandler._can_access_path(path)
        except Exception as e:
            print(f"Linux权限检查出错: {e}")
            return False
    
    @staticmethod
    def _can_access_path(path):
        """
        检查是否可以访问指定路径
        
        Args:
            path (str): 要检查的路径
            
        Returns:
            bool: 是否可以访问路径
        """
        try:
            # 检查路径是否存在
            if not os.path.exists(path):
                return True  # 路径不存在但可能有权限创建
            
            # 检查是否可以读取目录内容
            if os.path.isdir(path):
                os.listdir(path)  # 尝试列出目录内容
            else:
                # 检查是否可以读取文件
                with open(path, 'rb') as f:
                    f.read(1)  # 尝试读取文件的第一个字节
                    
            return True
        except PermissionError:
            return False
        except Exception:
            # 其他异常可能不代表权限问题
            return True
    
    @staticmethod
    def request_macos_full_disk_access(parent_window=None):
        """
        请求macOS完全磁盘访问权限
        
        Args:
            parent_window: 父窗口，用于显示消息框
        """
        try:
            # 显示说明信息
            QMessageBox.information(
                parent_window,
                "需要完全磁盘访问权限",
                "为了扫描所有文件，需要授予完全磁盘访问权限。\n\n"
                "请在弹出的系统偏好设置中，找到本应用程序并勾选权限。\n"
                "如果系统偏好设置没有自动打开，请手动打开:\n"
                "系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限"
            )
            
            # 尝试打开系统偏好设置
            subprocess.run([
                "osascript", "-e", 
                'tell application "System Preferences" to activate'
            ])
            subprocess.run([
                "osascript", "-e", 
                'tell application "System Preferences" to set current pane to pane "com.apple.preference.security"'
            ])
        except Exception as e:
            print(f"请求macOS完全磁盘访问权限时出错: {e}")
            QMessageBox.warning(
                parent_window,
                "权限请求失败",
                f"无法自动打开系统偏好设置，请手动授予权限:\n\n{str(e)}"
            )
    
    @staticmethod
    def request_windows_admin_privileges(parent_window=None):
        """
        请求Windows管理员权限
        
        Args:
            parent_window: 父窗口，用于显示消息框
        """
        try:
            # 检查是否已经具有管理员权限
            if PermissionHandler._is_admin():
                return True
                
            # 显示说明信息
            reply = QMessageBox.question(
                parent_window,
                "需要管理员权限",
                "扫描某些系统目录需要管理员权限。\n\n是否以管理员身份重新启动应用程序？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 尝试以管理员权限重新启动
                PermissionHandler._restart_as_admin()
                
            return False
        except Exception as e:
            print(f"请求Windows管理员权限时出错: {e}")
            QMessageBox.warning(
                parent_window,
                "权限请求失败",
                f"无法请求管理员权限:\n\n{str(e)}"
            )
            return False
    
    @staticmethod
    def _is_admin():
        """
        检查当前进程是否具有管理员权限
        
        Returns:
            bool: 是否具有管理员权限
        """
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    @staticmethod
    def _restart_as_admin():
        """
        以管理员权限重新启动应用程序
        """
        try:
            if platform.system() == "Windows":
                import ctypes
                # 获取当前Python脚本路径
                script_path = sys.executable
                # 以管理员权限重新启动
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", script_path, " ".join(sys.argv), None, 1
                )
                # 退出当前进程
                sys.exit(0)
        except Exception as e:
            raise Exception(f"无法以管理员权限重启: {e}")
    
    @staticmethod
    def get_restricted_paths():
        """
        获取受限制的路径列表
        
        Returns:
            list: 受限制的路径列表
        """
        system = platform.system()
        restricted_paths = []
        
        if system == "Darwin":  # macOS
            user_home = os.path.expanduser("~")
            restricted_paths = [
                "/System",
                "/Library", 
                "/Applications",
                "/usr",
                "/private",
                os.path.join(user_home, "Desktop"),
                os.path.join(user_home, "Documents"),
                os.path.join(user_home, "Downloads"),
                os.path.join(user_home, "Pictures"),
                os.path.join(user_home, "Music"),
                os.path.join(user_home, "Movies")
            ]
        elif system == "Windows":  # Windows
            # Windows受限制的路径通常需要管理员权限
            restricted_paths = [
                os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32"),
                os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "SysWOW64"),
                "C:\\Program Files",
                "C:\\Program Files (x86)"
            ]
            
        return restricted_paths