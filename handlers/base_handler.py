"""
Handler基础类 - 提供统一的页面对象初始化逻辑
"""

import logging
from utils.driver_factory import DriverFactory
from utils.global_manager import GlobalManager


class BaseHandler:
    """
    Handler基础类 - 提供统一的初始化模式和页面对象管理
    """

    def __init__(self, page_instance=None, config_manager=None):
        """
        基础Handler初始化

        Args:
            page_instance: 页面对象实例（可为None）
            config_manager: 配置管理器
        """
        # 如果没有提供config_manager，使用GlobalManager获取
        if config_manager is None:
            global_manager = GlobalManager()
            config_manager = global_manager.get_config_manager()

        self.config_manager = config_manager
        self.log = logging.getLogger(__name__)

        # 初始化页面对象
        self.page_instance = self._initialize_page(page_instance, config_manager)

    def _initialize_page(self, page_instance, config_manager):
        """
        统一的页面对象初始化逻辑

        Args:
            page_instance: 传入的页面对象（可能为None或类）
            config_manager: 配置管理器

        Returns:
            初始化后的页面对象实例
        """
        if page_instance is None:
            # 情况1: page_instance为None，需要创建新实例
            return self._create_page_instance(config_manager)
        elif hasattr(page_instance, 'driver'):
            # 情况2: page_instance已经是实例，有driver属性
            return page_instance
        elif isinstance(page_instance, type):
            # 情况3: page_instance是类，需要创建实例
            # 使用DriverFactory直接获取driver，避免循环依赖
            driver = DriverFactory.get_windows_driver()
            return page_instance(driver, config_manager)
        else:
            # 情况4: 其他情况，尝试直接使用
            self.log.warning(f"未知的page_instance类型: {type(page_instance)}")
            return page_instance

    def _create_page_instance(self, config_manager):
        """
        创建页面对象实例（由子类实现）

        Args:
            config_manager: 配置管理器

        Returns:
            页面对象实例
        """
        # 子类需要重写此方法
        raise NotImplementedError("子类必须实现_create_page_instance方法")

    def _ensure_page_initialized(self):
        """
        确保页面对象已初始化（惰性初始化）
        """
        if isinstance(self.page_instance, type):
            driver = DriverFactory.get_windows_driver()
            self.page_instance = self.page_instance(driver, self.config_manager)
            self.log.info(f"惰性初始化页面对象: {type(self.page_instance).__name__}")

    def is_page_available(self):
        """
        检查页面对象是否可用

        Returns:
            bool: 页面对象是否有有效的driver
        """
        if not self.page_instance:
            return False
        return hasattr(self.page_instance, 'driver') and self.page_instance.driver is not None

    def _get_global_manager(self):
        """
        获取全局管理器实例

        Returns:
            GlobalManager: 全局管理器实例
        """
        return GlobalManager()

    def _get_page(self):
        """
        获取页面对象实例

        Returns:
            页面对象实例
        """
        return self.page_instance

    # ==================== 通用弹窗处理方法 ====================
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """
        轮询等待操作窗口出现（公共方法，子类可调用）

        Args:
            timeout: 超时时间
            poll_interval: 轮询间隔

        Returns:
            bool: 是否成功等到窗口
        """
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            # 调用 page_instance 的 switch_to_operation_window 方法
            if hasattr(self.page_instance, 'switch_to_operation_window'):
                if self.page_instance.switch_to_operation_window():
                    return True
            time.sleep(poll_interval)
        self.log.error("等待操作窗口超时")
        return False

    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        """
        通用操作提示弹窗处理方法（公共方法，子类可调用）
        处理 "操作提示" 窗口的确认/取消/退出按钮

        Args:
            action: 'confirm' (确认/是) / 'cancel' (取消/否) / 'quit' (退出)
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        # 等待操作窗口
        if not self.wait_for_operation_window(timeout):
            return False

        # 根据 action 调用对应的方法
        if action == 'confirm':
            if hasattr(self.page_instance, 'click_operation_window_confirm_button'):
                return self.page_instance.click_operation_window_confirm_button()
        elif action == 'cancel':
            if hasattr(self.page_instance, 'click_operation_window_cancel_button'):
                return self.page_instance.click_operation_window_cancel_button()
        elif action == 'quit':
            if hasattr(self.page_instance, 'click_operation_window_quit_button'):
                return self.page_instance.click_operation_window_quit_button()

        self.log.error(f"未知操作或页面对象不支持该操作: {action}")
        return False

    def handle_prompt_window(self, timeout=5.0):
        """
        通用消息提示弹窗处理方法（公共方法，子类可调用）
        处理 "操作提示" 窗口的确定按钮  消息提示窗口 只有一个确认按钮的

        Args:
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if hasattr(self.page_instance, 'switch_to_prompt_window'):
                if self.page_instance.switch_to_prompt_window():
                    break
            time.sleep(0.5)
        else:
            self.log.error("等待消息提示窗口超时")
            return False

        if hasattr(self.page_instance, 'click_prompt_window_confirm_button'):
            return self.page_instance.click_prompt_window_confirm_button()

        self.log.error("页面对象不支持 click_prompt_window_confirm_button 方法")
        return False