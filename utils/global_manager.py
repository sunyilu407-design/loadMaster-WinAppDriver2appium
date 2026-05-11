"""
全局管理器 - 提供全局单例的资源管理
"""

import logging
import time
from .driver_factory import DriverFactory


class GlobalManager:
    """
    全局管理器单例类
    负责统一管理driver和config_manager资源
    为所有Handler提供自动化的资源获取
    """

    _instance = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logging.info("🌍 全局管理器实例已创建")
        return cls._instance

    def __init__(self):
        """初始化全局管理器"""
        self.config_manager = None
        self.driver = None
        self.driver_lock = False
        self.config_lock = False
        self.log = logging.getLogger("global_manager")

    def initialize(self, config_path=None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径（可选）
        """
        if self.config_manager is None and not self.config_lock:
            from .config_manager import ConfigManager

            self.config_lock = True
            try:
                if config_path:
                    self.config_manager = ConfigManager(config_path)
                else:
                    self.config_manager = ConfigManager()

                self.log.info("🔧 配置管理器初始化完成")
                self.config_lock = False

            except Exception as e:
                self.config_lock = False
                self.log.error(f"🔴 配置管理器初始化失败: {e}")
                raise

    def get_config_manager(self):
        """
        获取配置管理器实例（确保已初始化）

        Returns:
            ConfigManager实例
        """
        if self.config_manager is None:
            self.initialize()

        if not self.config_manager:
            raise Exception("配置管理器未初始化")

        return self.config_manager

    def get_driver(self):
        """
        获取全局驱动实例（确保已初始化）

        Returns:
            WinAppDriver实例
        """
        if self.driver is None and not self.driver_lock:
            self.driver_lock = True
            try:
                self.log.info("🚗 正在初始化全局驱动...")
                self.driver = DriverFactory.get_windows_driver()
                self.log.info("✅ 全局驱动初始化完成")
            except Exception as e:
                self.log.error(f"🔴 全局驱动初始化失败: {e}")
                raise
            finally:
                self.driver_lock = False

        if not self.driver:
            raise Exception("全局驱动未初始化")

        return self.driver

    def get_page(self, page_class, *args, **kwargs):
        """
        创建页面对象实例（使用全局资源）

        Args:
            page_class: 页面对象类
            *args: 页面对象构造参数
            **kwargs: 页面对象构造关键字参数

        Returns:
            页面对象实例
        """
        try:
            # 使用全局driver和config_manager
            driver = self.get_driver()
            config_manager = self.get_config_manager()

            # 创建页面对象实例
            page_instance = page_class(driver, config_manager, *args, **kwargs)

            self.log.info(f"✅ 创建页面对象: {page_class.__name__}")
            return page_instance

        except Exception as e:
            self.log.error(f"🔴 创建页面对象失败 {page_class.__name__}: {e}")
            raise

    def get_handler(self, handler_class, page_class, *args, **kwargs):
        """
        创建Handler实例（使用全局资源）

        Args:
            handler_class: Handler类
            page_class: 页面对象类
            *args: Handler构造参数
            **kwargs: Handler构造关键字参数

        Returns:
            Handler实例
        """
        try:
            # 使用全局driver和config_manager
            config_manager = self.get_config_manager()
            driver = self.get_driver()

            # 创建页面对象
            page_instance = self.get_page(page_class, *args, **kwargs)

            # 创建Handler实例
            handler_instance = handler_class(page_instance, config_manager, *args, **kwargs)

            self.log.info(f"✅ 创建Handler实例: {handler_class.__name__}")
            return handler_instance

        except Exception as e:
            self.log.error(f"🔴 创建Handler实例失败 {handler_class.__name__}: {e}")
            raise

    def get_status(self):
        """
        获取全局管理器状态

        Returns:
            dict: 状态信息
        """
        return {
            'config_manager_initialized': self.config_manager is not None,
            'config_manager_locked': self.config_lock,
            'driver_initialized': self.driver is not None,
            'driver_locked': self.driver_lock,
            'config_path': getattr(self.config_manager, 'config_path', 'default') if self.config_manager else None,
            'driver_type': type(self.driver).__name__ if self.driver else None
        }

    def reset(self):
        """
        重置全局管理器状态（用于测试清理）
        """
        self.config_manager = None
        self.driver = None
        self.config_lock = False
        self.driver_lock = False
        self.log.info("🔄 全局管理器已重置")


# 全局单例实例
global_manager = GlobalManager()