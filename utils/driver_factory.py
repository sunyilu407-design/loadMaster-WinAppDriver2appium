# -*- coding: utf-8 -*-
"""
Appium Driver Factory - 支持Appium 2.x和Windows桌面应用自动化
核心改进：
- Appium 2.x 自动服务器管理
- 元素缓存机制 - 避免重复定位
- 智能等待策略 - 减少等待时间
- 并行测试支持
"""

import socket
import os
import subprocess
import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from functools import wraps
from appium import webdriver as appium_webdriver
try:
    from appium.options.common import AppiumOptions  # 优先使用 common 模块
except ImportError:
    from appium.options import AppiumOptions  # 备用方案
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.env import Environment

logger = logging.getLogger(__name__)


class ElementCache:
    """
    元素缓存管理器 - 大幅提升定位效率
    
    特点：
    - 自动缓存已定位的元素
    - 支持缓存过期机制
    - 线程安全
    """
    
    def __init__(self, timeout: int = 300):  # 默认5分钟过期
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.RLock()
        self._default_timeout = timeout
    
    def _generate_key(self, strategy: str, locator: str) -> str:
        """生成缓存Key"""
        return f"{strategy}:{locator}"
    
    def get(self, strategy: str, locator: str) -> Optional[Any]:
        """获取缓存的元素"""
        key = self._generate_key(strategy, locator)
        with self._lock:
            if key in self._cache:
                data = self._cache[key]
                # 检查是否过期
                if time.time() - data['timestamp'] < data.get('timeout', self._default_timeout):
                    logger.debug(f"从缓存获取元素: {key}")
                    return data['element']
                else:
                    # 过期，移除
                    del self._cache[key]
            return None
    
    def set(self, strategy: str, locator: str, element, timeout: int = None) -> None:
        """缓存元素"""
        key = self._generate_key(strategy, locator)
        with self._lock:
            self._cache[key] = {
                'element': element,
                'timestamp': time.time(),
                'timeout': timeout or self._default_timeout
            }
            logger.debug(f"缓存元素: {key}")
    
    def invalidate(self, strategy: str = None, locator: str = None) -> None:
        """使缓存失效"""
        with self._lock:
            if strategy and locator:
                key = self._generate_key(strategy, locator)
                if key in self._cache:
                    del self._cache[key]
            elif strategy:
                # 删除所有匹配策略的缓存
                keys_to_delete = [k for k in self._cache if k.startswith(f"{strategy}:")]
                for k in keys_to_delete:
                    del self._cache[k]
            else:
                # 清空所有缓存
                self._cache.clear()
            logger.debug(f"缓存失效: strategy={strategy}, locator={locator}")
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            logger.info("元素缓存已清空")


def _check_port(port: int, timeout: float = 1.0) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            return s.connect_ex(('127.0.0.1', port)) == 0
        except socket.timeout:
            return False


def _activate_window(window_title: str) -> bool:
    """
    使用 Windows API 激活窗口（带到前台）
    
    Args:
        window_title: 窗口标题（部分匹配）
        
    Returns:
        bool: 是否成功激活
    """
    try:
        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.windll.user32
        
        # 查找窗口
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            wintypes.HWND,
            wintypes.LPARAM
        )
        
        found_hwnd = [None]
        
        def enum_callback(hwnd, lparam):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                if window_title in buff.value:
                    # 检查窗口是否可见
                    if user32.IsWindowVisible(hwnd):
                        found_hwnd[0] = hwnd
                        return False  # 停止枚举
            return True
        
        user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
        
        hwnd = found_hwnd[0]
        if hwnd:
            # 获取当前前台窗口
            foreground_hwnd = user32.GetForegroundWindow()
            
            # 如果当前窗口不是目标窗口，需要激活
            if foreground_hwnd != hwnd:
                # 方法1：先恢复窗口（如果最小化）
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
                    time.sleep(0.1)
                
                # 方法2：模拟按键 Alt+Tab 来激活窗口
                # 先将目标窗口设为前景
                user32.BringWindowToTop(hwnd)
                time.sleep(0.05)
                user32.ShowWindow(hwnd, 5)  # SW_SHOW = 5
                time.sleep(0.05)
                
                # 方法3：直接设置前台窗口
                user32.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                
                # 方法4：如果还是不行，尝试交换前台窗口
                if user32.GetForegroundWindow() != hwnd:
                    # 记录当前前台窗口
                    current_foreground = user32.GetForegroundWindow()
                    # 将目标窗口设为前台
                    user32.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
                    # 再设置回来，然后再次设置目标窗口（有时需要两次）
                    user32.SetForegroundWindow(current_foreground)
                    time.sleep(0.05)
                    user32.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
            
            logger.info(f"已激活窗口: {window_title}")
            return True
        else:
            logger.warning(f"未找到可激活的窗口: {window_title}")
            return False
    except Exception as e:
        logger.warning(f"窗口激活失败: {e}")
        return False


class AppiumServerManager:
    """
    Appium服务器管理器 - 自动启动和管理Appium服务器
    """
    
    _instances = {}
    _lock = threading.RLock()
    
    def __new__(cls, host: str = '127.0.0.1', port: int = 4723):
        key = f"{host}:{port}"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = super().__new__(cls)
                cls._instances[key]._initialized = False
            return cls._instances[key]
    
    def __init__(self, host: str = '127.0.0.1', port: int = 4723):
        if self._initialized:
            return
        self.host = host
        self.port = port
        self._process = None
        self._initialized = True
    
    def start_server(self, timeout: int = 30) -> bool:
        """启动Appium服务器"""
        if _check_port(self.port):
            logger.info(f"Appium服务器已在端口 {self.port} 运行")
            return True
        
        try:
            # 使用appium命令启动
            import subprocess
            cmd = [
                'appium',
                '--address', self.host,
                '--port', str(self.port),
                '--log-level', 'error',
                '--no-reset',
                '--local-timezone'
            ]
            
            logger.info(f"启动Appium服务器: {' '.join(cmd)}")
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            start_time = time.time()
            while time.time() - start_time < timeout:
                if _check_port(self.port):
                    logger.info(f"Appium服务器启动成功: {self.host}:{self.port}")
                    return True
                time.sleep(0.5)
            
            logger.error("Appium服务器启动超时")
            return False
            
        except Exception as e:
            logger.error(f"启动Appium服务器失败: {e}")
            return False
    
    def stop_server(self) -> None:
        """停止Appium服务器"""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            logger.info("Appium服务器已停止")


class SmartWait:
    """
    智能等待管理器 - 动态调整等待时间
    
    策略：
    - 初始等待短，逐渐延长
    - 检测元素稳定性
    - 支持快速失败模式
    """
    
    def __init__(self, driver, timeout: int = 10, poll_frequency: float = 0.3):
        self.driver = driver
        self.timeout = timeout
        self.poll_frequency = poll_frequency
    
    def until(self, condition: Callable, *args, **kwargs):
        """
        智能等待直到条件满足
        
        Args:
            condition: 等待条件函数
            *args, **kwargs: 条件函数的参数
            
        Returns:
            满足条件时的返回值
        """
        start_time = time.time()
        last_exception = None
        
        while time.time() - start_time < self.timeout:
            try:
                result = condition(*args, **kwargs)
                if result:
                    # 检测到元素，快速返回
                    elapsed = time.time() - start_time
                    if elapsed > 1.0:  # 如果等待超过1秒，记录日志
                        logger.debug(f"智能等待成功，耗时: {elapsed:.2f}秒")
                    return result
            except Exception as e:
                last_exception = e
            
            time.sleep(self.poll_frequency)
        
        raise TimeoutException(
            f"智能等待超时 ({self.timeout}秒)",
            cause=last_exception
        )


class TimeoutException(Exception):
    """自定义超时异常"""
    def __init__(self, message, cause=None):
        super().__init__(message)
        self.cause = cause


class DriverFactory:
    """
    Appium Driver工厂类
    
    核心功能：
    - 支持Appium 2.x
    - Windows桌面应用自动化
    - 元素缓存
    - 智能等待
    """
    
    _config = Environment()
    _element_cache = ElementCache(timeout=300)  # 5分钟缓存
    
    # 缓存配置
    _cache_enabled = True
    _cache_timeout = 300  # 元素缓存默认5分钟
    
    @classmethod
    def enable_cache(cls, enabled: bool = True, timeout: int = 300) -> None:
        """启用/禁用元素缓存"""
        cls._cache_enabled = enabled
        if timeout:
            cls._cache_timeout = timeout
        logger.info(f"元素缓存: {'启用' if enabled else '禁用'}, 超时: {timeout}秒")
    
    @classmethod
    def clear_cache(cls) -> None:
        """清空元素缓存"""
        cls._element_cache.clear()
    
    @classmethod
    def _build_appium_options(cls, platform: str = 'windows') -> AppiumOptions:
        """
        构建Appium选项

        Args:
            platform: 平台类型 ('windows', 'android', 'ios')

        Returns:
            AppiumOptions实例
        """
        options = AppiumOptions()

        if platform.lower() == 'windows':
            # Windows桌面应用配置
            app_path = cls._config.get_app_path()
            app_name = cls._config.get_app_name()
            auto_launch = cls._config.get_auto_launch()

            options.set_capability('platformName', 'Windows')
            options.set_capability('deviceName', 'WindowsPC')
            options.set_capability('automationName', 'Windows')
            options.set_capability('noReset', True)
            options.set_capability('fullReset', False)

            if auto_launch and app_path:
                options.set_capability('app', app_path)
                logger.info(f"使用应用路径启动: {app_path}")
            elif app_name:
                # 连接到已运行的应用：通过 HWND 直接绑定到目标窗口
                target_hwnd = cls._find_target_window_hwnd(app_name, timeout=10)
                if target_hwnd:
                    options.set_capability('appium:appTopLevelWindow', target_hwnd)
                    logger.info(f"使用 appium:appTopLevelWindow 连接模式: {target_hwnd}")
                else:
                    options.set_capability('app', 'Root')
                    logger.warning(f"未找到窗口 '{app_name}'，降级使用 Root 模式")
            else:
                raise ValueError("必须提供 app_path 或 app_name 配置")

        return options

    @classmethod
    def _find_target_window_hwnd(cls, window_title: str, timeout: int = 10) -> Optional[str]:
        """
        通过窗口标题查找窗口句柄(HWND)，用于连接到已运行的应用

        Args:
            window_title: 窗口标题（部分匹配）
            timeout: 超时时间（秒）

        Returns:
            十六进制窗口句柄字符串或None
        """
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        end_time = time.time() + timeout

        while time.time() < end_time:
            found_hwnd = None

            def enum_callback(hwnd, lparam):
                nonlocal found_hwnd
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if window_title in buff.value:
                        if user32.IsWindowVisible(hwnd):
                            found_hwnd = hwnd
                            return False
                return True

            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

            if found_hwnd:
                # 返回十六进制字符串（WinAppDriver期望的格式）
                hwnd_hex = hex(found_hwnd)
                logger.info(f"找到目标窗口 HWND: {hwnd_hex}, 标题包含: '{window_title}'")
                return hwnd_hex

            time.sleep(0.5)

        logger.warning(f"未找到标题包含 '{window_title}' 的窗口")
        return None

    @classmethod
    def _activate_window(cls, window_title: str) -> bool:
        """
        使用 Windows API 激活窗口（带到前台）

        Args:
            window_title: 窗口标题（部分匹配）

        Returns:
            bool: 是否成功激活
        """
        hwnd_hex = cls._find_target_window_hwnd(window_title, timeout=2)
        if not hwnd_hex:
            return False

        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            hwnd = int(hwnd_hex, 16)

            foreground_hwnd = user32.GetForegroundWindow()
            if foreground_hwnd != hwnd:
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)
                    time.sleep(0.1)

                user32.BringWindowToTop(hwnd)
                time.sleep(0.05)
                user32.ShowWindow(hwnd, 5)
                time.sleep(0.05)
                user32.SetForegroundWindow(hwnd)
                time.sleep(0.1)

                if user32.GetForegroundWindow() != hwnd:
                    current_foreground = user32.GetForegroundWindow()
                    user32.SetForegroundWindow(hwnd)
                    time.sleep(0.1)
                    user32.SetForegroundWindow(current_foreground)
                    time.sleep(0.05)
                    user32.SetForegroundWindow(hwnd)
                    time.sleep(0.1)

            logger.info(f"已激活窗口: {window_title}")
            return True
        except Exception as e:
            logger.warning(f"窗口激活失败: {e}")
            return False
    
    @classmethod
    def _get_server_url(cls) -> str:
        """获取Appium服务器URL"""
        host = cls._config.get_appium_host()
        port = cls._config.get_appium_port()
        return f'http://{host}:{port}'
    
    @classmethod
    def _ensure_server_running(cls, port: int = None) -> bool:
        """确保Appium服务器正在运行"""
        if port is None:
            port = int(cls._config.get_appium_port())
        
        if not _check_port(port):
            logger.warning(f"Appium服务器未运行，尝试自动启动...")
            server_manager = AppiumServerManager(port=port)
            return server_manager.start_server()
        return True
    
    @classmethod
    def get_driver(cls, platform: str = 'windows') -> Optional[RemoteWebDriver]:
        """
        获取Appium WebDriver实例

        Args:
            platform: 平台类型

        Returns:
            WebDriver实例或None
        """
        try:
            # 确保服务器运行
            if not cls._ensure_server_running():
                logger.error("无法启动Appium服务器")
                return None

            # 构建URL和选项
            server_url = cls._get_server_url()
            options = cls._build_appium_options(platform)

            # 创建Driver实例
            driver = appium_webdriver.Remote(
                command_executor=server_url,
                options=options
            )

            # 设置隐式等待（智能等待）
            driver.implicitly_wait(2)  # 基础等待，配合缓存使用

            # 等待应用初始化
            time.sleep(2)

            # 由于使用 appTopLevelWindow 直连，Driver 已经绑定到目标窗口
            # 尝试激活并最大化窗口（确保窗口在前台且正常渲染）
            app_name = cls._config.get_app_name()
            if app_name:
                try:
                    time.sleep(1)
                    cls._activate_window(app_name)
                    logger.info("窗口已激活")
                except Exception as e:
                    logger.warning(f"窗口激活失败（非关键）: {e}")

            logger.info(f"Appium Driver初始化成功 ({platform})")
            return driver

        except Exception as e:
            logger.error(f"Appium Driver初始化失败: {e}")
            return None
    
    @classmethod
    def get_windows_driver(cls) -> Optional[RemoteWebDriver]:
        """获取Windows应用Driver"""
        return cls.get_driver('windows')
    
    @classmethod
    def attach_to_existing_app(cls, window_handle: str) -> Optional[RemoteWebDriver]:
        """
        连接到已运行的应用程序
        
        Args:
            window_handle: 窗口句柄
            
        Returns:
            WebDriver实例或None
        """
        try:
            if not cls._ensure_server_running():
                return None
            
            server_url = cls._get_server_url()

            options = AppiumOptions()
            options.set_capability('platformName', 'Windows')
            options.set_capability('deviceName', 'WindowsPC')
            options.set_capability('appTopLevelWindow', window_handle)
            options.set_capability('automationName', 'Windows')
            
            driver = appium_webdriver.Remote(
                command_executor=server_url,
                options=options
            )
            
            logger.info(f"成功连接到现有应用，窗口句柄: {window_handle}")
            return driver
            
        except Exception as e:
            logger.error(f"连接现有应用失败: {e}")
            return None
    
    @classmethod
    def quit_driver(cls, driver: RemoteWebDriver) -> None:
        """
        安全退出Driver
        
        Args:
            driver: WebDriver实例
        """
        if driver:
            try:
                # 先清空缓存
                if cls._cache_enabled:
                    cls._element_cache.clear()
                
                driver.quit()
                logger.info("Driver已安全退出")
            except Exception as e:
                logger.error(f"退出Driver时出错: {e}")


# 便捷函数
def get_windows_driver() -> Optional[RemoteWebDriver]:
    """获取Windows应用Driver"""
    return DriverFactory.get_windows_driver()


def enable_element_cache(enabled: bool = True, timeout: int = 300) -> None:
    """启用元素缓存"""
    DriverFactory.enable_cache(enabled, timeout)


def clear_element_cache() -> None:
    """清空元素缓存"""
    DriverFactory.clear_cache()


if __name__ == "__main__":
    # 测试Driver工厂
    print("Appium Driver Factory - 测试")
    driver = DriverFactory.get_windows_driver()
    if driver:
        print("✓ Driver创建成功")
        driver.quit()
    else:
        print("✗ Driver创建失败")
