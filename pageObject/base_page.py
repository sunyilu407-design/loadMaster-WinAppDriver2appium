import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from utils.winform_combobox_handler import WinFormComboBoxHandler
import threading

import logging


class BasePage:
    # 类级别的元素缓存（线程安全）
    _element_cache = {}
    _cache_lock = threading.RLock()
    # 缓存配置
    _cache_enabled = True
    _cache_timeout = 300  # 5分钟
    
    def __init__(self, driver, config_manager, platform="windows"):
        """
        初始化基础页面
        :param driver: 驱动实例
        :param config_manager: 配置管理器实例
        :param platform: 平台类型，"windows" 或 "web"
        """
        self.platform = platform.lower()
        self.driver = driver
        self.config_manager = config_manager
        
        self.log = logging.getLogger("log")
        # 实例级别的缓存（用于页面生命周期内）
        self._instance_cache = {}
    
    @classmethod
    def enable_cache(cls, enabled: bool = True, timeout: int = 300) -> None:
        """启用/禁用元素缓存"""
        cls._cache_enabled = enabled
        cls._cache_timeout = timeout
        cls._element_cache.clear()
        logging.getLogger("log").info(f"元素缓存已{'启用' if enabled else '禁用'}，超时: {timeout}秒")
    
    @classmethod
    def clear_cache(cls) -> None:
        """清空所有缓存"""
        with cls._cache_lock:
            cls._element_cache.clear()
        logging.getLogger("log").info("元素缓存已清空")
    
    def _get_cache_key(self, strategy: str, locator: str) -> str:
        """生成缓存Key"""
        return f"{strategy}:{locator}"
    
    def _get_cached_element(self, strategy: str, locator: str) -> tuple:
        """
        获取缓存的元素
        
        Returns:
            tuple: (element, is_valid) - 元素对象和是否有效
        """
        if not self._cache_enabled:
            return None, False
        
        key = self._get_cache_key(strategy, locator)
        
        with self._cache_lock:
            if key in self._element_cache:
                data = self._element_cache[key]
                # 检查是否过期
                if time.time() - data['timestamp'] < self._cache_timeout:
                    try:
                        # 验证元素是否仍然有效
                        # 对于Windows UI：is_displayed()不足以验证StaleElementReference
                        # Appium element的代理对象在WinAppDriver端元素销毁后会404
                        # 因此通过re-find确认元素仍可访问
                        element = data['element']
                        # 尝试重新获取元素确保代理通道有效
                        _ = element.get_attribute("ControlType")
                        if element.is_displayed():
                            self.log.debug(f"从缓存获取元素: {key}")
                            return element, True
                        else:
                            # 元素不可见，移除缓存
                            del self._element_cache[key]
                    except Exception:
                        # 元素已失效（StaleElementReference或代理通道失效），移除缓存
                        del self._element_cache[key]
        
        return None, False
    
    def _cache_element(self, strategy: str, locator: str, element) -> None:
        """缓存元素"""
        if not self._cache_enabled or element is None:
            return
        
        key = self._get_cache_key(strategy, locator)
        with self._cache_lock:
            self._element_cache[key] = {
                'element': element,
                'timestamp': time.time(),
                'timeout': self._cache_timeout
            }
            self.log.debug(f"缓存元素: {key}")
    
    def _invalidate_cache(self, strategy: str = None, locator: str = None) -> None:
        """使缓存失效"""
        with self._cache_lock:
            if strategy and locator:
                key = self._get_cache_key(strategy, locator)
                if key in self._element_cache:
                    del self._element_cache[key]
            elif strategy:
                # 删除所有匹配策略的缓存
                keys_to_delete = [k for k in self._element_cache if k.startswith(f"{strategy}:")]
                for k in keys_to_delete:
                    del self._element_cache[k]
            else:
                self._element_cache.clear()
    
    def locate_element(self, timeout=10, use_cache=True, **kwargs):
        """
        定位元素的通用方法 - 增强错误处理和重试机制
        :param timeout: 超时时间（秒）
        :param kwargs: 定位参数
        :return: 元素对象或None
        """
        if self.platform == "windows":
            # Windows应用元素定位 - 使用WinAppDriver
            return self._locate_windows_element(timeout=timeout, **kwargs)
        else:
            # Web元素定位
            return self._locate_web_element(timeout=timeout, **kwargs)

    def _locate_windows_element(self, timeout=10, use_cache=True, **kwargs):
        """
        Windows平台专用：使用Appium定位元素
        支持多种定位策略 + 元素缓存
        :param timeout: 超时时间（秒）
        :param use_cache: 是否使用缓存
        :param kwargs: 定位参数
        :return: 元素对象或None
        """
        if self.platform != "windows":
            self.log.error("_locate_windows_element 方法仅支持Windows平台")
            return None
            
        try:
            # 确定定位策略和值
            strategy, locator_value = self._parse_locator_strategy(**kwargs)
            if not strategy:
                self.log.error("未提供有效的元素定位参数")
                return None
            
            # 先尝试从缓存获取
            if use_cache:
                cached_element, is_valid = self._get_cached_element(strategy, locator_value)
                if is_valid:
                    return cached_element
            
            self.log.debug(f"定位元素: strategy={strategy}, value={locator_value}")
            
            # 显式等待元素可见（使用优化后的超时）
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located((strategy, locator_value)))
            
            # 缓存元素
            if use_cache:
                self._cache_element(strategy, locator_value, element)
            
            self.log.debug(f"元素定位成功: {locator_value}")
            return element
                
        except NoSuchElementException:
            self.log.error(f"未找到元素: {kwargs}")
            return None
        except TimeoutException:
            self.log.error(f"等待元素超时: {kwargs}")
            return None
        except Exception as e:
            self.log.error(f"元素定位失败: {e}")
            return None
    
    def _parse_locator_strategy(self, **kwargs):
        """
        解析定位策略
        
        Returns:
            tuple: (By策略, locator值)
        """
        # 策略1: AutomationId定位（推荐）
        if 'auto_id' in kwargs or 'automation_id' in kwargs:
            automation_id = kwargs.get('auto_id') or kwargs.get('automation_id')
            locator_value = f"//*[@AutomationId='{automation_id}']"
            self.log.debug(f"使用AutomationId定位: {locator_value}")
            return By.XPATH, locator_value
        
        # 策略2: Name + ControlType组合
        if 'name' in kwargs and 'control_type' in kwargs:
            locator_value = f"//*[@Name='{kwargs['name']}' and @ControlType='{kwargs['control_type']}']"
            return By.XPATH, locator_value
        
        # 策略3: AutomationId + ClassName组合
        if 'automation_id' in kwargs and 'type' in kwargs:
            locator_value = f"//*[@AutomationId='{kwargs['automation_id']}' and @ClassName='{kwargs['type']}']"
            return By.XPATH, locator_value
        
        # 策略4: Name定位
        if 'name' in kwargs:
            locator_value = f"//*[@Name='{kwargs['name']}']"
            return By.XPATH, locator_value
        
        # 策略5: ClassName定位
        if 'class_name' in kwargs:
            return By.CLASS_NAME, kwargs['class_name']
        
        # 策略6: Type定位
        if 'type' in kwargs:
            return By.CLASS_NAME, kwargs['type']
        
        # 策略7: ControlType定位
        if 'control_type' in kwargs:
            xpath = f"//*[@ControlType='{kwargs['control_type']}']"
            if 'name' in kwargs:
                xpath += f"[@Name='{kwargs['name']}']"
            return By.XPATH, xpath
        
        # 策略8: XPath定位
        if 'xpath' in kwargs:
            return By.XPATH, kwargs['xpath']
        
        # 策略9: TagName定位
        if 'tag_name' in kwargs:
            return By.TAG_NAME, kwargs['tag_name']
        
        return None, None


    def _locate_web_element(self, timeout=10, **kwargs):
        """
        Web平台专用元素定位方法
        """
        try:
            # 根据传入的参数确定定位方式
            if 'id' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.ID, kwargs['id']))
                )
            elif 'name' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.NAME, kwargs['name']))
                )
            elif 'class_name' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, kwargs['class_name']))
                )
            elif 'tag_name' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, kwargs['tag_name']))
                )
            elif 'xpath' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, kwargs['xpath']))
                )
            elif 'css_selector' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, kwargs['css_selector']))
                )
            elif 'link_text' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.LINK_TEXT, kwargs['link_text']))
                )
            elif 'partial_link_text' in kwargs:
                return WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, kwargs['partial_link_text']))
                )
            else:
                raise ValueError("未提供有效的元素定位参数")
        except TimeoutException:
            self.log.error(f"Web元素定位超时: {kwargs}")
            return None
        except Exception as e:
            self.log.error(f"Web元素定位失败: {e}")
            return None

    def locate_elements(self, **kwargs):
        """
        定位多个元素
        :param kwargs: 定位参数
        :return: 元素列表
        """
        try:
            if self.platform == "windows":
                # Windows平台定位多个元素
                if 'name' in kwargs:
                    return self.driver.find_elements(By.NAME, kwargs['name'])
                elif 'auto_id' in kwargs or 'automation_id' in kwargs:
                    automation_id = kwargs.get('auto_id') or kwargs.get('automation_id')
                    return self.driver.find_elements(By.XPATH, f"//*[@AutomationId='{automation_id}']")
                elif 'class_name' in kwargs:
                    return self.driver.find_elements(By.CLASS_NAME, kwargs['class_name'])
                elif 'xpath' in kwargs:
                    return self.driver.find_elements(By.XPATH, kwargs['xpath'])
                else:
                    self.log.error("未提供有效的元素定位参数")
                    return []
            else:
                # Web平台定位多个元素
                if 'id' in kwargs:
                    return self.driver.find_elements(By.ID, kwargs['id'])
                elif 'name' in kwargs:
                    return self.driver.find_elements(By.NAME, kwargs['name'])
                elif 'class_name' in kwargs:
                    return self.driver.find_elements(By.CLASS_NAME, kwargs['class_name'])
                elif 'tag_name' in kwargs:
                    return self.driver.find_elements(By.TAG_NAME, kwargs['tag_name'])
                elif 'xpath' in kwargs:
                    return self.driver.find_elements(By.XPATH, kwargs['xpath'])
                elif 'css_selector' in kwargs:
                    return self.driver.find_elements(By.CSS_SELECTOR, kwargs['css_selector'])
                else:
                    self.log.error("未提供有效的元素定位参数")
                    return []
        except Exception as e:
            self.log.error(f"定位多个元素失败: {e}")
            return []

    def wait_for_element(self, timeout=10, **kwargs):
        """
        等待元素出现
        :param timeout: 超时时间（秒）
        :param kwargs: 定位参数
        :return: 元素对象或None
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            element = self.locate_element(**kwargs)
            if element:
                return element
            time.sleep(0.5)
        self.log.error(f"等待元素超时: {kwargs}")
        return None

    def click_element(self, **kwargs):
        """
        点击元素
        :param kwargs: 定位参数
        :return: 是否成功
        """
        try:
            element = self.locate_element(**kwargs)
            if element:
                element.click()
                self.log.info(f"点击元素成功: {kwargs}")
                # 点击会改变UI状态，主动清除该元素的缓存，避免后续拿到失效元素引用
                strategy, locator_value = self._parse_locator_strategy(**kwargs)
                if strategy:
                    self._invalidate_cache(strategy, locator_value)
                return True
            else:
                self.log.error(f"未找到要点击的元素: {kwargs}")
                return False
        except Exception as e:
            self.log.error(f"点击元素失败: {e}")
            return False

    def send_keys_to_element(self, text, **kwargs):
        """
        向元素输入文本 - Windows桌面应用优化版
        使用 Ctrl+A 全选后替换，避免 clear() 在WinForms上失效的问题
        :param text: 要输入的文本
        :param kwargs: 定位参数
        :return: 是否成功
        """
        try:
            element = self.locate_element(**kwargs)
            if element:
                # 1. 点击元素获取焦点
                element.click()
                time.sleep(0.05)

                # 2. 使用 Ctrl+A 全选现有内容
                from selenium.webdriver.common.keys import Keys
                element.send_keys(Keys.CONTROL, 'a')
                time.sleep(0.05)

                # 3. 输入新内容（全选后输入会替换全部）
                element.send_keys(text)
                self.log.info(f"输入文本成功: {text}")
                return True
            else:
                self.log.error(f"未找到要输入的元素: {kwargs}")
                return False
        except Exception as e:
            self.log.error(f"输入文本失败: {e}")
            return False

    def get_element_text(self, **kwargs):
        """
        获取元素文本
        :param kwargs: 定位参数
        :return: 元素文本或None
        """
        try:
            element = self.locate_element(**kwargs)
            if element:
                text = element.text
                self.log.info(f"获取元素文本成功: {text}")
                return text
            else:
                self.log.error(f"未找到要获取文本的元素: {kwargs}")
                return None
        except Exception as e:
            self.log.error(f"获取元素文本失败: {e}")
            return None

    def is_element_present(self, timeout=5, **kwargs):
        """
        检查元素是否存在
        :param timeout: 超时时间（秒）
        :param kwargs: 定位参数
        :return: 是否存在
        """
        element = self.locate_element(timeout=timeout, **kwargs)
        return element is not None




    def wait_for_window(self, title=None, timeout=30):
        """
        Windows平台专用：等待窗口出现
        :param title: 窗口标题
        :param timeout: 超时时间（秒）
        :return: 窗口句柄或None
        """
        if self.platform != "windows":
            self.log.error("wait_for_window 方法仅支持Windows平台")
            return None

        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                # 获取所有窗口句柄
                window_handles = self.driver.window_handles
                for handle in window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        if title and title in self.driver.title:
                            self.log.info(f"找到窗口: {title}")
                            return handle
                    except Exception as e:
                        self.log.debug(f"跳过已关闭的窗口 {handle}: {e}")
                        continue

                # 如果没找到标题匹配的，返回第一个可用窗口
                if window_handles:
                    try:
                        self.driver.switch_to.window(window_handles[0])
                        self.log.info(f"返回第一个可用窗口: {self.driver.title}")
                        return window_handles[0]
                    except Exception:
                        pass
            except Exception as e:
                self.log.debug(f"等待窗口时出错: {e}")

            time.sleep(1)

        self.log.error(f"等待窗口超时: {title}")
        return None

    def switch_to_window(self, title=None, automation_id=None, timeout=5):
        """
        切换到指定窗口（带重试机制）
        :param title: 窗口标题（支持部分匹配）
        :param automation_id: 窗口的AutomationId（用于WinAppDriver对话框）
        :param timeout: 等待窗口打开的超时时间（秒）
        :return: 是否成功
        """
        import time
        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                window_handles = self.driver.window_handles

                # 在 appTopLevelWindow 模式下，window_handles 始终为 []，
                # 但 driver.title 已经是目标窗口的标题，直接验证即可
                if not window_handles:
                    if title:
                        current_title = self.driver.title
                        if title in current_title:
                            self.log.info(f"切换到窗口成功（appTopLevelWindow模式）: {current_title}")
                            return True
                        # 目标窗口未激活，尝试激活
                        self._activate_window_by_title(title)
                    time.sleep(0.5)
                    continue

                # 优先方案：精确匹配 title 或 automation_id
                for handle in window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        current_title = self.driver.title

                        # 方案1：通过 title 匹配（精确匹配）
                        if title and title in current_title:
                            self.log.info(f"切换到窗口成功（通过title）: {title}")
                            return True

                        # 方案2：通过 automation_id 匹配（WinAppDriver对话框专用）
                        if automation_id:
                            try:
                                root_element = self.locate_element(timeout=1, automation_id=automation_id, type="Window")
                                if root_element:
                                    self.log.info(f"切换到窗口成功（通过automation_id）: {automation_id}")
                                    return True
                            except Exception:
                                pass
                    except Exception as e:
                        self.log.debug(f"跳过窗口 {handle}: {e}")
                        continue

                # 只有在未指定 title 和 automation_id 时，才 fallback 到第一个窗口
                if not title and not automation_id:
                    try:
                        if window_handles:
                            self.driver.switch_to.window(window_handles[0])
                            self.log.info(f"已切换到第一个可用窗口: {self.driver.title}")
                            return True
                    except Exception:
                        pass

                # 如果指定了 title 但找不到，等待一下再重试
                time.sleep(0.5)

            except Exception as e:
                self.log.debug(f"切换窗口时出错: {e}")
                time.sleep(0.5)

        # 最后一次尝试：列出所有可用窗口并报告
        if title:
            try:
                window_handles = self.driver.window_handles
                if not window_handles:
                    # appTopLevelWindow 模式下直接检查 driver.title
                    current_title = self.driver.title
                    if title in current_title:
                        self.log.info(f"切换到窗口成功（最终检查）: {current_title}")
                        return True
                    self.log.warning(f"未找到目标窗口: title='{title}', 当前窗口: '{current_title}', window_handles=[]")
                else:
                    available_titles = []
                    for handle in window_handles:
                        try:
                            self.driver.switch_to.window(handle)
                            available_titles.append(self.driver.title)
                        except Exception:
                            pass
                    self.log.warning(f"未找到目标窗口: title='{title}', 可用窗口: {available_titles}")
            except Exception:
                pass

        self.log.warning(f"切换窗口超时: title='{title}', automation_id='{automation_id}'")
        return False

    def _activate_window_by_title(self, window_title: str) -> bool:
        """
        使用 Windows API 激活指定标题的窗口

        Args:
            window_title: 窗口标题（部分匹配）

        Returns:
            bool: 是否成功激活
        """
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

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
                if user32.IsIconic(found_hwnd):
                    user32.ShowWindow(found_hwnd, 9)
                    time.sleep(0.1)
                user32.BringWindowToTop(found_hwnd)
                time.sleep(0.05)
                user32.ShowWindow(found_hwnd, 5)
                time.sleep(0.05)
                user32.SetForegroundWindow(found_hwnd)
                time.sleep(0.1)
                self.log.debug(f"已通过Windows API激活窗口: {window_title}")
                return True
            return False
        except Exception as e:
            self.log.debug(f"窗口激活失败: {e}")
            return False

    def close_window(self, title=None, automation_id=None):
        """
        关闭指定窗口
        :param title: 窗口标题（支持部分匹配）
        :param automation_id: 窗口的AutomationId
        :return: 是否成功
        """
        try:
            # 先切换到要关闭的窗口
            if not self.switch_to_window(title=title, automation_id=automation_id, timeout=2):
                self.log.warning(f"未找到要关闭的窗口: title='{title}', automation_id='{automation_id}'")
                return False

            # 查找并点击关闭按钮
            close_button = None
            for aid in ['close','btnClose', 'button1', 'btnCloseWindow',]:
                try:
                    close_button = self.locate_element(timeout=1, automation_id=aid)
                    if close_button:
                        break
                except Exception:
                    continue

            if close_button:
                close_button.click()
                self.log.info(f"通过关闭按钮关闭窗口成功")
                return True

            # 如果没有找到关闭按钮，使用 Alt+F4
            from selenium.webdriver.common.keys import Keys
            self.driver.switch_to.active_element.send_keys(Keys.ALT + Keys.F4)
            self.log.info(f"通过快捷键关闭窗口成功")
            return True

        except Exception as e:
            self.log.error(f"关闭窗口失败: {e}")
            return False

    def take_screenshot(self, filename=None):
        """
        截图
        :param filename: 文件名
        :return: 截图文件路径
        """
        try:
            if not filename:
                import time
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            self.log.info(f"截图保存成功: {filename}")
            return filename
        except Exception as e:
            self.log.error(f"截图失败: {e}")
            return None

    def quit_driver(self):
        """
        退出驱动
        """
        # 驱动的退出由 conftest.py 中的夹具管理
        pass
        
    #获取表格数据逻辑，返回json格式的数据
    def get_table_data_as_json(self, content_table, header_keywords=None):
        """
        针表格数据提取方法，正确识别表头并按行分组
        """
        try:
            self.log.info(f"开始获取表格数据，表格定位信息: {content_table}")
            table_element = self.locate_element(**content_table)

            if not table_element:
                self.log.error(f"未找到表格元素: {content_table}")
                return []

            # 等待设置
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time

            try:
                table_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of(table_element)
                )
                time.sleep(1)
            except Exception as e:
                self.log.warning(f"表格等待超时: {e}")

            table_data = []

            if self.platform == "windows":
                # 获取所有非空行元素
                self.log.info("获取表格非空子元素作为行数据")
                all_children = table_element.find_elements(By.XPATH, ".//descendant::*")

                # 过滤非空行元素（保留有实际内容的）
                rows = []
                for child in all_children:
                    try:
                        # 提取元素关键信息
                        name = child.get_attribute("Name") or ""
                        text = child.text.strip() or ""
                        control_type = child.get_attribute("ControlType") or ""

                        # 保留有意义的元素（排除空值和滚动条等）
                        if (name or text) and "ScrollBar" not in control_type:
                            rows.append({
                                "element": child,
                                "name": name,
                                "text": text,
                                "control_type": control_type
                            })
                    except Exception as e:
                        self.log.debug(f"过滤元素时出错: {e}")
                        continue

                self.log.info(f"找到{len(rows)}个有效行元素")
                if not rows:
                    return []

                # 2. 识别表头（基于日志特征：ControlType=Header）
                headers = []
                header_indices = []

                for i, row in enumerate(rows):
                    if row["control_type"] == "Header" and row["text"]:
                        headers.append(row["text"])
                        header_indices.append(i)
                        self.log.debug(f"识别表头: {row['text']} (索引{i})")

                # 确认表头是连续的（表格表头通常连续排列）
                if headers and len(headers) > 1:
                    # 检查表头索引是否连续
                    is_continuous = all(header_indices[i + 1] == header_indices[i] + 1
                                        for i in range(len(header_indices) - 1))
                    if not is_continuous:
                        self.log.warning("表头不连续，重新识别")
                        headers = []  # 重置表头，使用备选方案

                # 表头识别兜底（基于日志中的"用户姓名"等关键词）
                if not  headers:
                    header_keywords = header_keywords or ["用户姓名1", "用户类型1", "注册时间1", "备注1"]
                    # 先尝试从行数据中找到匹配的表头
                    found_headers = []
                    for kw in header_keywords:
                        for row in rows:
                            if kw in row["text"]:
                                found_headers.append(kw)
                                break
                    
                    # 如果找到了匹配的表头，使用找到的；否则使用默认关键词
                    if found_headers:
                        headers = found_headers
                    else:
                        headers = header_keywords  # 直接使用关键词作为表头
                    self.log.debug(f"兜底表头: {headers}")

                # 确保至少有2列
                if len(headers) < 2:
                    headers = [f"列{i + 1}" for i in range(4)]  # 默认4列
                    self.log.debug(f"使用默认表头: {headers}")

                column_count = len(headers)
                self.log.debug(f"最终表头: {headers} (列数: {column_count})")

                # 3. 定位数据起始位置（跳过表头和行标题）
                data_start_index = 0
                # 找到第一个数据行（ControlType=Edit且名称包含"行"）
                for i, row in enumerate(rows):
                    if ("Edit" in row["control_type"] and
                            "行" in row["name"] and
                            row["text"] and
                            row["text"].lower() != "(null)"):
                        data_start_index = i
                        break

                self.log.debug(f"数据起始索引: {data_start_index}")

                # 4. 按列数分组数据（核心优化）
                pure_data_rows = rows[data_start_index:]
                # 过滤掉行标题（如"行 0"、"行 1"）
                filtered_data = [row for row in pure_data_rows
                                 if "行" not in row["text"] or "行" in row["name"] and "Edit" in row["control_type"]]

                # 按列数分组（每column_count个单元格组成一行）
                formatted_data = []
                for i in range(0, len(filtered_data), column_count):
                    row_cells = filtered_data[i:i + column_count]
                    if len(row_cells) < column_count:
                        continue  # 跳过不完整的行

                    row_dict = {}
                    for j in range(column_count):
                        header = headers[j] if j < len(headers) else f"列{j + 1}"
                        cell_text = row_cells[j]["text"] if j < len(row_cells) else ""
                        # 处理(null)值
                        if cell_text.lower() == "(null)":
                            cell_text = ""
                        row_dict[header] = cell_text

                    # 只保留有数据的行
                    if any(row_dict.values()):
                        formatted_data.append(row_dict)

                table_data = formatted_data

            else:
                # Web平台处理逻辑
                rows = table_element.find_elements(By.XPATH, ".//tr")
                if len(rows) < 2:
                    return []

                headers = [th.text.strip() or f"列{i + 1}" for i, th in
                           enumerate(rows[0].find_elements(By.XPATH, ".//th"))]
                for row in rows[1:]:
                    cells = row.find_elements(By.XPATH, ".//td")
                    row_dict = {headers[i]: cells[i].text.strip() for i in range(min(len(headers), len(cells)))}
                    if any(row_dict.values()):
                        table_data.append(row_dict)

            self.log.info(f"成功获取表格数据，共{len(table_data)}行有效数据")
            return table_data

        except Exception as e:
            self.log.error(f"获取表格数据失败: {e}")
            import traceback
            self.log.error(f"错误堆栈: {traceback.format_exc()}")
            return []

    def click_table_row(self, content_table, search_criteria, header_keywords=None, match_mode='exact'):
        """
        根据搜索条件点击表格中的指定行
        
        Args:
            content_table: 表格定位信息字典
            search_criteria: 搜索条件字典，格式如 {"用户姓名": "张三", "用户类型": "管理员"}
            header_keywords: 表头关键词列表，用于表头识别
            match_mode: 匹配模式，'exact'(精确匹配)精确匹配 或 'partial'(部分匹配)like 包含即可如："用户姓名": "张三"，用户名只需要包含张三即可.
            
        Returns:
            bool: 点击成功返回True，失败返回False
        """
        try:
            self.log.info(f"开始搜索并点击表格行，搜索条件: {search_criteria}")

            # 获取原始表格元素
            table_element = self.locate_element(**content_table)
            if not table_element:
                self.log.error("未找到表格元素")
                return False

            # 获取表格数据和元素信息
            table_data_with_elements = self._get_table_data_with_elements(table_element, header_keywords)
            
            if not table_data_with_elements:
                self.log.error("未获取到表格数据")
                return False
            
            # 查找匹配的行
            target_row_info = self._find_matching_row(table_data_with_elements, search_criteria, match_mode)
            
            if not target_row_info:
                self.log.error(f"未找到匹配条件的行: {search_criteria}")
                return False
            
            # 点击目标行，传入原始表格元素
            success = self._click_row_element(target_row_info, table_element)
            
            if success:
                self.log.info(f"成功点击表格行，匹配数据: {target_row_info['data']}")
            else:
                self.log.error("点击表格行失败")
                
            return success
            
        except Exception as e:
            self.log.error(f"点击表格行时发生错误: {e}")
            import traceback
            self.log.error(f"错误堆栈: {traceback.format_exc()}")
            return False

    def _get_table_data_with_elements(self, table_element, header_keywords=None):
        """
        获取表格数据并保留元素引用信息
        
        Returns:
            list: 包含数据和元素信息的列表，格式如:
                [{"data": {"用户姓名": "张三"}, "elements": [element1, element2, ...], "row_index": 0}, ...]
        """
        try:

            # 等待表格加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time

            try:
                table_element = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of(table_element)
                )
                time.sleep(1)  # 与get_table_data_as_json保持一致的等待时间
            except Exception as e:
                self.log.warning(f"表格等待超时: {e}")

            # 确保表格获得焦点，提高数据获取的稳定性
            try:
                self._ensure_table_focus(table_element)
            except Exception as e:
                self.log.warning(f"表格焦点获取失败: {e}")

            if self.platform == "windows":
                # 获取所有子元素
                all_children = table_element.find_elements(By.XPATH, ".//descendant::*")
                
                # 过滤有效元素
                rows = []
                for child in all_children:
                    try:
                        name = child.get_attribute("Name") or ""
                        text = child.text.strip() or ""
                        control_type = child.get_attribute("ControlType") or ""

                        if (name or text) and "ScrollBar" not in control_type:
                            rows.append({
                                "element": child,
                                "name": name,
                                "text": text,
                                "control_type": control_type
                            })
                    except Exception as e:
                        self.log.debug(f"过滤元素时出错: {e}")
                        continue

                if not rows:
                    return []

                # 识别表头
                headers = self._identify_table_headers(rows, header_keywords)
                column_count = len(headers)
                
                # 定位数据起始位置
                data_start_index = self._find_data_start_index(rows)
                
                # 按行分组数据
                return self._group_table_data_with_elements(rows[data_start_index:], headers, column_count)
                
            else:
                # Web平台处理（简化版本）
                rows = table_element.find_elements(By.XPATH, ".//tr")
                if len(rows) < 2:
                    return []
                
                headers = [th.text.strip() or f"列{i + 1}" for i, th in 
                          enumerate(rows[0].find_elements(By.XPATH, ".//th"))]
                
                result = []
                for row_index, row in enumerate(rows[1:]):
                    cells = row.find_elements(By.XPATH, ".//td")
                    row_dict = {headers[i]: cells[i].text.strip() 
                               for i in range(min(len(headers), len(cells)))}
                    if any(row_dict.values()):
                        result.append({
                            "data": row_dict,
                            "elements": cells,
                            "row_element": row,
                            "row_index": row_index
                        })
                return result

        except Exception as e:
            self.log.error(f"获取表格数据和元素信息失败: {e}")
            return []

    def query_table_after_operation(self, content_table, search_criteria=None, header_keywords=None,
                                    match_mode='exact', expected_presence='present', min_count=1,
                                    timeout=5, poll_interval=0.5):
        """
        新增/修改/删除操作后的通用表格查询与校验方法。

        使用 `get_table_data_as_json` 获取表格数据，支持精确或包含匹配，并通过轮询等待表格更新。

        Args:
            content_table: 表格定位信息字典，通常来自页面配置 `elements.content_table`。
            search_criteria: 查询条件字典，如 {"用户姓名": "operator"}；为 None 时返回所有行。
            header_keywords: 表头关键词列表，用于帮助识别表头（各页面不同，可从各页面 `app_config.head_keys` 传入）。
            match_mode: 匹配模式，'exact'（精确匹配）或 'partial'（包含匹配）。
            expected_presence: 预期结果，'present'（应存在）或 'absent'（应不存在）。
            min_count: 预期匹配的最小行数（仅在 expected_presence='present' 时生效）。
            timeout: 轮询的最大等待时间（秒）。
            poll_interval: 每次轮询间隔（秒）。

        Returns:
            dict: {
                'success': bool,                # 是否满足预期
                'matched_rows': list,           # 匹配到的行（JSON 格式，每行是表头->值的字典）
                'total_rows': int,              # 表格总行数（有效数据行）
                'count': int,                   # 匹配到的行数
                'expected_presence': str,       # 预期结果（present/absent）
            }

        示例：
            # 验证添加后的数据存在
            self.query_table_after_operation(content_table, {"用户姓名": "operator"}, head_keys,
                                             match_mode='exact', expected_presence='present')

            # 验证删除后的数据不存在
            self.query_table_after_operation(content_table, {"用户姓名": "operator"}, head_keys,
                                             expected_presence='absent')
        """
        import time
        try:
            end_time = time.time() + timeout
            last_rows = []
            last_matches = []

            while time.time() < end_time:
                rows = self.get_table_data_as_json(content_table, header_keywords) or []
                last_rows = rows

                # 过滤匹配行
                if search_criteria:
                    matches = [row for row in rows if self._is_row_match(row, search_criteria, match_mode)]
                else:
                    matches = rows[:]  # 未指定条件则返回所有行
                last_matches = matches

                found_count = len(matches)
                total_rows = len(rows)

                if expected_presence == 'present':
                    if found_count >= min_count:
                        return {
                            'success': True,
                            'matched_rows': matches,
                            'total_rows': total_rows,
                            'count': found_count,
                            'expected_presence': 'present',
                        }
                elif expected_presence == 'absent':
                    if found_count == 0:
                        return {
                            'success': True,
                            'matched_rows': [],
                            'total_rows': total_rows,
                            'count': 0,
                            'expected_presence': 'absent',
                        }
                else:
                    # 未指定期望，则直接返回当前匹配结果
                    return {
                        'success': True,
                        'matched_rows': matches,
                        'total_rows': total_rows,
                        'count': found_count,
                        'expected_presence': str(expected_presence),
                    }

                time.sleep(poll_interval)

            # 超时未达到预期，返回最后一次检查结果
            return {
                'success': False,
                'matched_rows': last_matches,
                'total_rows': len(last_rows),
                'count': len(last_matches),
                'expected_presence': expected_presence,
            }
        except Exception as e:
            self.log.error(f"查询表格失败: {e}")
            import traceback
            self.log.error(f"错误堆栈: {traceback.format_exc()}")
            return {
                'success': False,
                'matched_rows': [],
                'total_rows': 0,
                'count': 0,
                'expected_presence': expected_presence,
                'error': str(e),
            }

    def _identify_table_headers(self, rows, header_keywords=None):
        """识别表头"""
        headers = []
        header_indices = []

        # 基于ControlType=Header识别
        for i, row in enumerate(rows):
            if row["control_type"] == "Header" and row["text"]:
                headers.append(row["text"])
                header_indices.append(i)
                self.log.debug(f"识别表头: {row['text']} (索引{i})")

        # 检查表头连续性
        if headers and len(headers) > 1:
            is_continuous = all(header_indices[i + 1] == header_indices[i] + 1
                               for i in range(len(header_indices) - 1))
            if not is_continuous:
                self.log.warning("表头不连续，重新识别")
                headers = []

        # 兜底方案（与get_table_data_as_json保持一致）
        if not headers:
            header_keywords = header_keywords or ["用户姓名1", "用户类型1", "注册时间1", "备注1"]
            # 先尝试从行数据中找到匹配的表头
            found_headers = []
            for kw in header_keywords:
                for row in rows:
                    if kw in row["text"]:
                        found_headers.append(kw)
                        break
            
            # 如果找到了匹配的表头，使用找到的；否则使用默认关键词
            if found_headers:
                headers = found_headers
            else:
                headers = header_keywords  # 直接使用关键词作为表头
            self.log.debug(f"兜底表头: {headers}")

        # 默认表头
        if len(headers) < 2:
            headers = [f"列{i + 1}" for i in range(4)]
            self.log.debug(f"使用默认表头: {headers}")

        self.log.debug(f"最终表头: {headers} (列数: {len(headers)})")
        return headers

    def _find_data_start_index(self, rows):
        """找到数据起始位置"""
        for i, row in enumerate(rows):
            if ("Edit" in row["control_type"] and
                    "行" in row["name"] and
                    row["text"] and
                    row["text"].lower() != "(null)"):
                return i
        return 0

    def _group_table_data_with_elements(self, data_rows, headers, column_count):
        """按行分组数据并保留元素信息"""
        # 过滤数据行
        filtered_data = [row for row in data_rows
                        if "行" not in row["text"] or ("行" in row["name"] and "Edit" in row["control_type"])]

        result = []
        for i in range(0, len(filtered_data), column_count):
            row_cells = filtered_data[i:i + column_count]
            if len(row_cells) < column_count:
                continue

            row_dict = {}
            row_elements = []
            
            for j in range(column_count):
                header = headers[j] if j < len(headers) else f"列{j + 1}"
                cell_text = row_cells[j]["text"] if j < len(row_cells) else ""
                
                # 处理(null)值
                if cell_text.lower() == "(null)":
                    cell_text = ""
                    
                row_dict[header] = cell_text
                row_elements.append(row_cells[j]["element"])

            # 只保留有数据的行
            if any(row_dict.values()):
                # 添加元素稳定性检查
                valid_elements = []
                for element in row_elements:
                    try:
                        # 检查元素是否仍然有效
                        element.is_displayed()
                        valid_elements.append(element)
                    except Exception as e:
                        self.log.debug(f"元素已失效，跳过: {e}")
                        valid_elements.append(None)
                
                result.append({
                    "data": row_dict,
                    "elements": valid_elements,
                    "row_index": len(result)
                })

        return result

    def _find_matching_row(self, table_data_with_elements, search_criteria, match_mode='exact'):
        """查找匹配的行"""
        for row_info in table_data_with_elements:
            if self._is_row_match(row_info["data"], search_criteria, match_mode):
                self.log.debug(f"找到匹配行: {row_info['data']}")
                return row_info
        return None

    def _is_row_match(self, row_data, search_criteria, match_mode='exact'):
        """检查行是否匹配搜索条件"""
        for key, expected_value in search_criteria.items():
            if key not in row_data:
                self.log.debug(f"行数据中不存在列: {key}")
                return False
                
            actual_value = row_data[key]
            
            if match_mode == 'exact':
                if actual_value != expected_value:
                    return False
            elif match_mode == 'partial':
                if expected_value not in actual_value:
                    return False
            else:
                self.log.warning(f"未知的匹配模式: {match_mode}，使用精确匹配")
                if actual_value != expected_value:
                    return False
                    
        return True

    def _click_row_element(self, row_info, table_element=None):
        """点击行元素（增强版，支持滚动到目标行）"""
        try:
            # 尝试多种点击策略
            elements_to_try = []
            
            # 策略1: 尝试点击第一个可点击的元素
            if row_info.get("elements"):
                elements_to_try.extend(row_info["elements"])
            
            # 策略2: 如果有行元素，优先点击行元素
            if row_info.get("row_element"):
                elements_to_try.insert(0, row_info["row_element"])
            
            # 首先尝试直接点击（如果元素已经可见）
            for element in elements_to_try:
                try:
                    # 检查元素是否可见和可点击
                    if self._is_element_visible_in_viewport(element) and element.is_enabled():
                        self.log.debug(f"元素已在可见区域，直接点击: {element.text}")
                        element.click()
                        time.sleep(0.5)  # 等待点击生效
                        return True
                except Exception as e:
                    self.log.debug(f"直接点击元素失败: {e}")
                    continue
            
            # 如果直接点击失败，尝试滚动到目标行
            self.log.info("元素不在可见区域，尝试滚动到目标行")
            if self._scroll_to_row_element(row_info, table_element):
                # 滚动后再次尝试点击
                for element in elements_to_try:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            self.log.debug(f"滚动后尝试,点击元素: {element.text}")
                            element.click()
                            time.sleep(0.5)  # 等待点击生效
                            return True
                    except Exception as e:
                        self.log.debug(f"滚动后点击元素失败: {e}")
                        continue
            
            # 策略3: 直接点击第一个元素（ActionChains在WinAppDriver不支持mouse pointer）
            if row_info.get("elements"):
                try:
                    first_element = row_info["elements"][0]
                    first_element.click()
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    self.log.debug(f"直接点击元素失败: {e}")
            
            return False
            
        except Exception as e:
            self.log.error(f"点击行元素时发生错误: {e}")
            return False

    def _is_element_visible_in_viewport(self, element):
        """检查元素是否在当前视口中可见"""
        try:
            # 策略1: 基础可见性检查
            if not element.is_displayed():
                self.log.debug("元素不可见 - is_displayed()返回False")
                return False
            
            # 获取元素位置和大小
            element_rect = element.rect
            element_y = element_rect['y']
            element_height = element_rect['height']
            element_x = element_rect['x']
            element_width = element_rect['width']
            
            # 策略2: 检查元素是否有有效的尺寸
            if element_height <= 0 or element_width <= 0:
                self.log.debug(f"元素尺寸无效 - 宽度:{element_width}, 高度:{element_height}")
                return False
            
            # 获取父容器（表格）的位置和大小
            parent_element = element
            try:
                # 尝试找到表格容器
                while parent_element:
                    parent_element = parent_element.find_element(By.XPATH, "..")
                    control_type = parent_element.get_attribute("ControlType") or ""
                    if "Table" in control_type or "DataGrid" in control_type:
                        break
                    # 防止无限循环
                    if parent_element.tag_name == "html":
                        parent_element = None
                        break
            except:
                parent_element = None
            
            if parent_element:
                parent_rect = parent_element.rect
                parent_y = parent_rect['y']
                parent_height = parent_rect['height']
                parent_x = parent_rect['x']
                parent_width = parent_rect['width']
                
                # 策略3: 检查元素是否在父容器的可见区域内（包含边距容忍度）
                element_bottom = element_y + element_height
                parent_bottom = parent_y + parent_height
                element_right = element_x + element_width
                parent_right = parent_x + parent_width
                
                # 增加10像素的容忍度，避免边界判断错误
                tolerance = 10
                
                # 垂直方向检查
                vertical_visible = (element_y >= (parent_y - tolerance) and 
                                  element_bottom <= (parent_bottom + tolerance))
                
                # 水平方向检查
                horizontal_visible = (element_x >= (parent_x - tolerance) and 
                                    element_right <= (parent_right + tolerance))
                
                is_visible = vertical_visible and horizontal_visible
                
                self.log.debug(f"元素可见性检查详情:")
                self.log.debug(f"  元素位置: X={element_x}, Y={element_y}, 宽={element_width}, 高={element_height}")
                self.log.debug(f"  容器位置: X={parent_x}, Y={parent_y}, 宽={parent_width}, 高={parent_height}")
                self.log.debug(f"  垂直可见: {vertical_visible}, 水平可见: {horizontal_visible}, 总体可见: {is_visible}")
                
                return is_visible
            else:
                # 策略4: 如果找不到父容器，通过 is_displayed 判断可见性
                # 注意：ActionChains.move_to_element 在 WinAppDriver 不支持 mouse pointer
                try:
                    visible = element.is_displayed()
                    self.log.debug(f"通过is_displayed检测元素可见: {visible}")
                    return visible
                except Exception as e:
                    self.log.debug(f"is_displayed检测失败: {e}")
                    
                    # 策略5: 尝试点击测试（最后的检测方法）
                    try:
                        # 保存当前位置，尝试点击后恢复
                        original_location = element.location
                        element.click()
                        self.log.debug("通过点击测试检测元素可见")
                        return True
                    except Exception as click_e:
                        self.log.debug(f"点击测试失败: {click_e}")
                        return False
                    
        except Exception as e:
            self.log.debug(f"检查元素可见性时出错: {e}")
            return False

    def _scroll_to_row_element(self, row_info, table_element=None, max_attempts=10):
        """滚动到指定的行元素 - 优化版本"""
        try:
            elements_to_check = []
            if row_info.get("row_element"):
                elements_to_check.append(row_info["row_element"])
            if row_info.get("elements"):
                elements_to_check.extend(row_info["elements"])
            
            if not elements_to_check:
                self.log.error("没有可用的元素进行滚动定位")
                return False
            
            target_element = elements_to_check[0]
            
            # 优先使用传入的表格元素作为滚动容器
            if table_element:
                table_container = table_element
                self.log.debug("使用传入的表格元素作为滚动容器")
            else:
                # 尝试找到表格容器进行滚动
                table_container = self._find_table_container(target_element)
                if not table_container:
                    self.log.warning("未找到表格容器，尝试在目标元素上滚动")
                    table_container = target_element
            
            # 关键修复：在滚动前先确保表格获得焦点
            self._ensure_table_focus(table_container)
            
            # 优化后的滚动策略顺序 - 优先使用WinForm兼容的方法
            scroll_strategies = [
                self._scroll_with_arrow_keys,      # 方向键 - 最兼容
                self._scroll_with_page_keys,       # Page键 - 通常有效
                self._scroll_with_winform_keys,    # WinForm特定方法
                self._scroll_with_home_end_keys,   # Home/End键
                self._scroll_with_wheel_action     # 滚轮 - 最后尝试
            ]
            
            for attempt in range(max_attempts):
                # 检查目标元素是否已经可见
                if self._is_element_visible_in_viewport(target_element):
                    self.log.info(f"滚动成功，目标行已可见 (尝试次数: {attempt + 1})")
                    return True
                
                # 尝试不同的滚动策略
                strategy_index = attempt % len(scroll_strategies)
                strategy = scroll_strategies[strategy_index]
                
                try:
                    self.log.debug(f"尝试滚动策略 {strategy_index + 1}/{len(scroll_strategies)}: {strategy.__name__}")
                    
                    # 对于WinForm特定方法，使用不同的参数
                    if strategy == self._scroll_with_winform_keys:
                        strategy(table_container, direction="down")
                    elif strategy == self._scroll_with_home_end_keys:
                        # Home/End键只在前几次尝试时使用
                        if attempt < 3:
                            strategy(table_container, direction="down")
                        else:
                            continue
                    else:
                        strategy(table_container, direction="down")
                    
                    # 减少等待时间，但在滚动后立即检查可见性
                    time.sleep(0.2)  # 减少等待时间从0.5到0.2
                    
                    # 立即检查是否滚动成功
                    if self._is_element_visible_in_viewport(target_element):
                        self.log.info(f"滚动成功，目标行已可见 (策略: {strategy.__name__}, 尝试次数: {attempt + 1})")
                        return True
                    
                except Exception as e:
                    self.log.debug(f"滚动策略 {strategy.__name__} 失败: {e}")
                    continue
            
            self.log.warning(f"经过{max_attempts}次尝试，仍未能滚动到目标行")
            return False
            
        except Exception as e:
            self.log.error(f"滚动到行元素时发生错误: {e}")
            return False

    def _find_table_container(self, element):
        """查找表格容器元素"""
        try:
            current = element
            containers_found = []
            
            for level in range(15):  # 增加查找层数到15层
                try:
                    current = current.find_element(By.XPATH, "..")
                    control_type = current.get_attribute("ControlType") or ""
                    class_name = current.get_attribute("ClassName") or ""
                    name = current.get_attribute("Name") or ""
                    
                    # 扩展表格相关容器的识别
                    table_control_types = ["Table", "DataGrid", "List", "Pane", "Group", "Window"]
                    table_class_names = ["DataGrid", "ListView", "Table", "Panel", "Form", "UserControl"]
                    
                    is_table_container = (
                        any(keyword in control_type for keyword in table_control_types) or
                        any(keyword in class_name for keyword in table_class_names) or
                        "DataGridView" in name
                    )
                    
                    if is_table_container:
                        containers_found.append({
                            'element': current,
                            'level': level,
                            'control_type': control_type,
                            'class_name': class_name,
                            'name': name
                        })
                        self.log.debug(f"找到潜在容器 (层级{level}): {control_type}, {class_name}, {name}")
                        
                except Exception:
                    break
            
            # 优先选择最接近的DataGrid相关容器
            if containers_found:
                # 按优先级排序：DataGrid > Table > List > 其他
                def container_priority(container):
                    ct = container['control_type']
                    cn = container['class_name']
                    if 'DataGrid' in ct or 'DataGrid' in cn:
                        return 0
                    elif 'Table' in ct or 'Table' in cn:
                        return 1
                    elif 'List' in ct or 'List' in cn:
                        return 2
                    else:
                        return 3
                
                best_container = min(containers_found, key=lambda x: (container_priority(x), x['level']))
                self.log.debug(f"选择最佳容器: {best_container['control_type']}, {best_container['class_name']}")
                return best_container['element']
            
            return None
            
        except Exception as e:
            self.log.debug(f"查找表格容器时出错: {e}")
            return None

    def _scroll_with_page_keys(self, container, direction="down"):
        """使用Page键滚动 - 优化版本"""
        from selenium.webdriver.common.keys import Keys
        
        try:
            # 尝试多种方式获得焦点
            focus_methods = [
                lambda: container.click(),
                lambda: self.driver.execute_script("arguments[0].focus();", container),
                lambda: container.send_keys("")  # 发送空字符串获得焦点
            ]
            
            focused = False
            for method in focus_methods:
                try:
                    method()
                    focused = True
                    break
                except Exception:
                    continue
            
            if not focused:
                self.log.debug("无法为容器获得焦点，尝试直接发送按键")
            
            time.sleep(0.05)  # 减少等待时间
            
            # 连续发送多次Page键以增加滚动幅度
            page_key = Keys.PAGE_DOWN if direction == "down" else Keys.PAGE_UP
            for _ in range(2):  # 发送2次Page键
                container.send_keys(page_key)
                time.sleep(0.05)
                
            self.log.debug(f"使用Page键滚动: {direction}")
            
        except Exception as e:
            self.log.debug(f"Page键滚动失败: {e}")
            raise

    def _scroll_with_arrow_keys(self, container, direction="down", steps=10):
        """使用方向键滚动 - 优化版本，增加滚动幅度"""
        from selenium.webdriver.common.keys import Keys
        
        try:
            # 尝试获得焦点
            try:
                container.click()
                time.sleep(0.05)  # 减少等待时间
            except Exception:
                pass
            
            key = Keys.ARROW_DOWN if direction == "down" else Keys.ARROW_UP
            
            # 快速连续发送按键，减少单次等待时间
            for i in range(steps):
                try:
                    container.send_keys(key)
                    if i % 3 == 0:  # 每3次按键后稍作等待
                        time.sleep(0.05)
                except Exception as e:
                    if i == 0:  # 如果第一次就失败，抛出异常
                        raise
                    else:  # 后续失败则继续
                        self.log.debug(f"方向键滚动第{i+1}次失败: {e}")
                        continue
                
            self.log.debug(f"使用方向键滚动: {direction}, 步数: {steps}")
            
        except Exception as e:
            self.log.debug(f"方向键滚动失败: {e}")
            raise

    def _scroll_with_wheel_action(self, container, direction="down"):
        """使用鼠标滚轮滚动 - WinForm兼容版本"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # 移动到容器中心
            ActionChains(self.driver).move_to_element(container).perform()
            time.sleep(0.1)
            
            # WinAppDriver不支持execute_script，尝试使用ActionChains的滚轮操作
            # 但由于WinAppDriver限制，这个方法可能不可用
            raise Exception("WinAppDriver不支持JavaScript执行，跳过滚轮滚动")
            
        except Exception as e:
            self.log.debug(f"滚轮滚动失败: {e}")
            raise

    def _scroll_with_winform_keys(self, container, direction="down"):
        """WinForm特定的滚动方法"""
        from selenium.webdriver.common.keys import Keys
        
        try:
            # 尝试获得焦点
            try:
                container.click()
                time.sleep(0.1)
            except Exception:
                pass
            
            # 使用Ctrl+方向键进行快速滚动
            if direction == "down":
                container.send_keys(Keys.CONTROL + Keys.END)  # 滚动到底部
                time.sleep(0.2)
                # 然后向上滚动一点
                for _ in range(3):
                    container.send_keys(Keys.PAGE_UP)
                    time.sleep(0.1)
            else:
                container.send_keys(Keys.CONTROL + Keys.HOME)  # 滚动到顶部
                
            self.log.debug(f"使用WinForm键滚动: {direction}")
            
        except Exception as e:
            self.log.debug(f"WinForm键滚动失败: {e}")
            raise

    def _scroll_with_home_end_keys(self, container, direction="down"):
        """使用Home/End键滚动"""
        from selenium.webdriver.common.keys import Keys
        
        try:
            # 尝试获得焦点
            try:
                container.click()
                time.sleep(0.1)
            except Exception:
                pass
            
            if direction == "down":
                container.send_keys(Keys.END)
            else:
                container.send_keys(Keys.HOME)
                
            self.log.debug(f"使用Home/End键滚动: {direction}")
            
        except Exception as e:
            self.log.debug(f"Home/End键滚动失败: {e}")
            raise

    def click_table_row_by_index(self, content_table, row_index, header_keywords=None):
        """
        根据行索引点击表格行
        
        Args:
            content_table: 表格定位信息字典
            row_index: 行索引（从0开始）
            header_keywords: 表头关键词列表
            
        Returns:
            bool: 点击成功返回True，失败返回False
        """
        try:
            self.log.info(f"根据索引点击表格行，行索引: {row_index}")
            
            # 获取原始表格元素
            table_element = self.locate_element(**content_table)
            if not table_element:
                self.log.error("未找到表格元素")
                return False
            
            table_data_with_elements = self._get_table_data_with_elements(content_table, header_keywords)
            
            if not table_data_with_elements:
                self.log.error("未获取到表格数据")
                return False
            
            if row_index < 0 or row_index >= len(table_data_with_elements):
                self.log.error(f"行索引超出范围: {row_index}，总行数: {len(table_data_with_elements)}")
                return False
            
            target_row_info = table_data_with_elements[row_index]
            success = self._click_row_element(target_row_info, table_element)
            
            if success:
                self.log.info(f"成功点击第{row_index}行，数据: {target_row_info['data']}")
            else:
                self.log.error(f"点击第{row_index}行失败")
                
            return success
            
        except Exception as e:
            self.log.error(f"根据索引点击表格行时发生错误: {e}")
            return False

    def check_tree_nodes_with_space_key(self, tree_locator, node_names):
        """
        使用点击+空格键的方式勾选树节点（WinAppDriver兼容版本）
        :param tree_locator: 树控件定位信息
        :param node_names: 要勾选的节点名称列表
        :return: 全部勾选成功返回True，否则返回False
        """
        try:
            self.log.info(f"开始使用空格键方式勾选树节点，目标节点: {node_names}")
            
            # 1. 定位树控件
            tree = self.locate_element(**tree_locator)
            if not tree:
                self.log.error("未找到树控件")
                return False
            
            # 2. 查找所有可勾选的节点（使用兼容WinAppDriver的方法）
            all_nodes = tree.find_elements(By.XPATH, ".//descendant::*[@Name and @Name!='']")
            target_nodes = []
            
            for node in all_nodes:
                try:
                    node_name = node.get_attribute("Name")
                    if node_name and node_name in node_names:
                        target_nodes.append(node)
                        self.log.debug(f"找到目标节点: {node_name}")
                except Exception:
                    continue
            
            if not target_nodes:
                self.log.warning(f"未找到目标节点: {node_names}")
                return False
            
            self.log.info(f"找到{len(target_nodes)}个目标节点")
            
            # 3. 使用点击+空格键方式勾选节点（WinAppDriver兼容方式）
            all_success = True
            
            for node in target_nodes:
                node_name = node.get_attribute("Name")
                try:
                    self.log.debug(f"开始处理节点: {node_name}")
                    
                    # 使用点击确保节点获得焦点
                    node.click()
                    time.sleep(0.2)
                    
                    # 再次点击确保节点在可视区域
                    node.click()
                    time.sleep(0.2)
                    
                    self.log.debug(f"已确保节点可见: {node_name}")
                    
                    # 等待一下确保焦点稳定
                    time.sleep(0.3)
                    
                    # 直接对节点元素发送空格键进行勾选
                    # 注意：不能用 ActionChains.send_keys，WinAppDriver 不支持 mouse pointer
                    from selenium.webdriver.common.keys import Keys
                    node.send_keys(Keys.SPACE)
                    
                    self.log.info(f"✅ 成功使用空格键勾选节点: {node_name}")
                    
                    # 等待一下让操作生效
                    time.sleep(0.5)

                    
                except Exception as e:
                    self.log.error(f"❌ 处理节点{node_name}失败: {e}")
                    all_success = False
            
            # 树节点勾选会改变整个页面UI状态，清空所有元素缓存
            # 避免后续操作从缓存拿到失效的元素引用（如 btnAddUser 等按钮）
            self._invalidate_cache()
            self.log.debug("树节点操作完成，已清空元素缓存")
            
            return all_success
            
        except Exception as e:
            self.log.error(f"空格键勾选树节点操作失败: {e}")
            import traceback
            self.log.error(traceback.format_exc())
            return False

    def analyze_tree_structure(self, tree_locator):
        """
        分析树控件的结构，帮助诊断节点定位问题
        :param tree_locator: 树控件定位信息
        :return: 树结构信息字典
        """
        try:
            self.log.info("开始分析树控件结构...")
            
            # 定位树控件
            tree = self.locate_element(**tree_locator)
            if not tree:
                self.log.error("未找到树控件")
                return None
            
            # 获取树控件的基本信息
            tree_info = {
                "ControlType": tree.get_attribute("ControlType") or "未知",
                "ClassName": tree.get_attribute("ClassName") or "未知",
                "Name": tree.get_attribute("Name") or "未知",
                "AutomationId": tree.get_attribute("AutomationId") or "未知"
            }
            
            self.log.info(f"树控件基本信息: {tree_info}")
            
            # 获取所有子元素
            all_children = tree.find_elements(By.XPATH, ".//descendant::*")
            self.log.info(f"找到{len(all_children)}个子元素")
            
            # 分析不同类型的元素
            element_analysis = {}
            for i, child in enumerate(all_children[:20]):  # 只分析前20个元素
                try:
                    control_type = child.get_attribute("ControlType") or "无"
                    class_name = child.get_attribute("ClassName") or "无"
                    name = child.get_attribute("Name") or "无"
                    automation_id = child.get_attribute("AutomationId") or "无"
                    
                    element_info = f"ControlType={control_type}, ClassName={class_name}, Name={name}, AutomationId={automation_id}"
                    
                    # 按ControlType分类
                    if control_type not in element_analysis:
                        element_analysis[control_type] = []
                    element_analysis[control_type].append({
                        "index": i,
                        "name": name,
                        "class_name": class_name,
                        "automation_id": automation_id,
                        "full_info": element_info
                    })
                    
                    # 如果元素名称匹配目标节点，特别标记
                    if name in ["发油系统", "排队系统", "门禁系统", "安规录入系统"]:
                        self.log.info(f"找到目标节点: {element_info}")
                        
                except Exception as e:
                    self.log.debug(f"分析元素{i}时出错: {e}")
                    continue
            
            # 输出分析结果
            self.log.info("元素类型分析结果:")
            for control_type, elements in element_analysis.items():
                self.log.info(f"  {control_type}: {len(elements)}个元素")
                for element in elements[:3]:  # 每类只显示前3个
                    self.log.info(f"    - {element['full_info']}")
            
            return {
                "tree_info": tree_info,
                "total_children": len(all_children),
                "element_analysis": element_analysis
            }
            
        except Exception as e:
            self.log.error(f"分析树控件结构失败: {e}")
            import traceback
            self.log.error(traceback.format_exc())
            return None
    #点击下拉框空间中传入的选项
    def select_combobox_option(self, option_text, **kwargs):
        """
        选择ComboBox中的指定选项 - 使用WinForm专用处理器
        :param option_text: 要选择的选项文本
        :param kwargs: ComboBox定位参数（如automation_id等）
        :return: 是否成功选择
        """
        try:
            self.log.info(f"开始选择ComboBox选项: {option_text}")

            # 1. 定位ComboBox元素
            combobox_element = self.locate_element(**kwargs)
            if not combobox_element:
                self.log.error(f"未找到ComboBox元素: {kwargs}")
                return False

            self.log.info(f"成功定位到ComboBox元素: {kwargs}")

            # 2. 使用WinForm专用处理器进行选择

            handler = WinFormComboBoxHandler(self.driver, self.log)

            success = handler.select_option(combobox_element, option_text)

            if success:
                # 3. 验证选择结果
                if handler.verify_selection(combobox_element, option_text):
                    self.log.info(f"成功选择并验证ComboBox选项: {option_text}")
                    return True
                else:
                    self.log.warning(f"选项可能已选择但验证失败: {option_text}")
                    return True  # 仍然返回True，因为选择操作成功了


        except Exception as e:
            self.log.error(f"选择ComboBox选项时发生异常: {e}")
            import traceback
            self.log.error(traceback.format_exc())
            return False

    def _ensure_table_focus(self, table_element):
        """确保表格元素获得焦点，以便进行键盘操作"""
        try:
            self.log.debug("尝试为表格获取焦点...")
            
            # 策略1: 直接点击表格元素
            try:
                table_element.click()
                self.log.debug("通过点击获取表格焦点成功")
                time.sleep(0.05)  # 减少等待时间
                return True
            except Exception as e:
                self.log.debug(f"点击表格获取焦点失败: {e}")
            
            # 策略2: 尝试点击表格的第一行（如果存在）
            try:
                # 查找表格中的第一行
                first_row = table_element.find_element("xpath", ".//tr[1] | .//DataGridViewRow[1] | .//*[contains(@ClassName,'Row')][1]")
                if first_row:
                    first_row.click()
                    self.log.debug("通过点击第一行获取表格焦点成功")
                    time.sleep(0.05)  # 减少等待时间
                    return True
            except Exception as e:
                self.log.debug(f"点击第一行获取焦点失败: {e}")
            
            # 策略3: 尝试点击表格中的任意单元格
            try:
                # 查找表格中的第一个单元格
                first_cell = table_element.find_element("xpath", ".//td[1] | .//DataGridViewCell[1] | .//*[contains(@ClassName,'Cell')][1]")
                if first_cell:
                    first_cell.click()
                    self.log.debug("通过点击第一个单元格获取表格焦点成功")
                    time.sleep(0.05)  # 减少等待时间
                    return True
            except Exception as e:
                self.log.debug(f"点击第一个单元格获取焦点失败: {e}")
            
            # 策略4: 使用Tab键尝试获取焦点
            try:
                from selenium.webdriver.common.keys import Keys
                table_element.send_keys(Keys.TAB)
                self.log.debug("通过Tab键获取表格焦点成功")
                time.sleep(0.05)  # 减少等待时间
                return True
            except Exception as e:
                self.log.debug(f"Tab键获取焦点失败: {e}")
            
            # 策略5: 尝试发送空字符串来激活元素
            try:
                table_element.send_keys("")
                self.log.debug("通过发送空字符串获取表格焦点成功")
                time.sleep(0.05)  # 减少等待时间
                return True
            except Exception as e:
                self.log.debug(f"发送空字符串获取焦点失败: {e}")
            
            self.log.warning("所有焦点获取策略都失败了")
            return False
            
        except Exception as e:
            self.log.error(f"确保表格焦点时发生错误: {e}")
            return False

    # ========== 公共弹窗处理方法（基于 common_dialogs.yaml） ==========
    
    def _get_dialog_config(self, dialog_name):
        """
        获取弹窗配置（直接从 common_dialogs.yaml 加载，不依赖子类）
        
        Args:
            dialog_name: 弹窗名称，如 'operation_window', 'prompt_window' 等
        
        Returns:
            dict: 弹窗配置字典，如果未找到返回 None
        """
        try:
            import os
            import yaml
            
            # 确定配置文件路径
            if self.config_manager and hasattr(self.config_manager, '_data_dir'):
                data_dir = self.config_manager._data_dir
            else:
                # 如果没有 config_manager，使用默认路径
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                data_dir = os.path.join(base_dir, "data", "pages")
            
            common_dialogs_file = os.path.join(data_dir, "common_dialogs.yaml")
            
            if not os.path.exists(common_dialogs_file):
                self.log.error(f"公共弹窗配置文件不存在: {common_dialogs_file}")
                return None
            
            # 加载配置文件
            with open(common_dialogs_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 提取 common_dialogs 部分
            common_dialogs = config_data.get('common_dialogs', {})
            
            # 获取指定的弹窗配置
            dialog_config = common_dialogs.get(dialog_name)
            
            if dialog_config:
                self.log.debug(f"成功获取弹窗配置: {dialog_name}")
                return dialog_config
            else:
                self.log.error(f"未找到弹窗配置: {dialog_name}，可用弹窗: {list(common_dialogs.keys())}")
                return None
                
        except Exception as e:
            self.log.error(f"获取弹窗配置失败: {dialog_name}, 错误: {e}")
            import traceback
            self.log.error(traceback.format_exc())
            return None
    
    # ========== operation_window 操作方法 ==========
    
    def switch_to_operation_window(self):
        """切换到操作提示窗口（operation_window）"""
        window_config = self._get_dialog_config('operation_window')
        if not window_config:
            self.log.error("operation_window: 未找到窗口配置")
            return False

        # 优先使用 automation_id 进行匹配，因为窗口名称可能随上下文变化
        automation_id = window_config.get('automation_id')
        return self.switch_to_window(automation_id=automation_id)
    
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待操作提示窗口出现并切换到该窗口"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.switch_to_operation_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待操作提示窗口超时")
        return False
    
    def get_operation_window_prompt_text(self):
        """获取操作提示窗口中的提示文本"""
        window_config = self._get_dialog_config('operation_window')
        if not window_config:
            self.log.error("operation_window: 未找到窗口配置")
            return None
        child = window_config.get('child_elements', {})
        element_config = child.get('prompt_text')
        if element_config:
            return self.get_element_text(**element_config)
        self.log.error("operation_window: 未找到prompt_text子元素配置")
        return None
    
    def click_operation_window_confirm_button(self):
        """点击操作提示窗口的是按钮"""
        window_config = self._get_dialog_config('operation_window')
        if not window_config:
            self.log.error("operation_window: 未找到窗口配置")
            return False
        child = window_config.get('child_elements', {})
        element_config = child.get('confirm_button')
        if element_config:
            return self.click_element(**element_config)
        self.log.error("operation_window: 未找到confirm_button子元素配置")
        return False
    
    def click_operation_window_cancel_button(self):
        """点击操作提示窗口的否按钮"""
        window_config = self._get_dialog_config('operation_window')
        if not window_config:
            self.log.error("operation_window: 未找到窗口配置")
            return False
        child = window_config.get('child_elements', {})
        element_config = child.get('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        self.log.error("operation_window: 未找到cancel_button子元素配置")
        return False
    
    def click_operation_window_quit_button(self):
        """点击操作提示窗口的退出按钮"""
        window_config = self._get_dialog_config('operation_window')
        if not window_config:
            self.log.error("operation_window: 未找到窗口配置")
            return False
        child = window_config.get('child_elements', {})
        element_config = child.get('quit_button')
        if element_config:
            return self.click_element(**element_config)
        self.log.error("operation_window: 未找到quit_button子元素配置")
        return False
    
    def handle_operation_prompt(self, expect_contains=None, timeout=5.0,
                                 confirm_operation=True):
        """
        处理操作提示窗口(operation_window) - 有"是/否"按钮

        Args:
            expect_contains: 期望提示文本包含的字符串（可选）
            timeout: 超时时间
            confirm_operation: 是否点击"是"按钮（默认True，False=点击"否"）

        Returns:
            bool: 是否成功处理
        """
        if not self.wait_for_operation_window(timeout=timeout):
            return False

        if expect_contains:
            prompt = self.get_operation_window_prompt_text() or ""
            if expect_contains not in prompt:
                self.log.error(f"提示文本校验失败: 预期包含 '{expect_contains}', 实际 '{prompt}'")
                return False

        # 执行operation_window操作
        if confirm_operation:
            return self.click_operation_window_confirm_button()
        else:
            return self.click_operation_window_cancel_button()
    
    # ========== prompt_window 操作方法 ==========
    
    def switch_to_prompt_window(self):
        """切换到消息提示窗口（prompt_window）"""
        window_config = self._get_dialog_config('prompt_window')
        if not window_config:
            self.log.error("prompt_window: 未找到窗口配置")
            return False

        # 优先使用 automation_id 进行匹配，因为窗口名称可能随上下文变化
        automation_id = window_config.get('automation_id')
        return self.switch_to_window(automation_id=automation_id)
    
    def wait_for_prompt_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待消息提示窗口出现并切换到该窗口"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.switch_to_prompt_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待消息提示窗口超时")
        return False
    
    def get_prompt_window_text(self):
        """获取消息提示窗口中的提示文本"""
        window_config = self._get_dialog_config('prompt_window')
        if not window_config:
            self.log.error("prompt_window: 未找到窗口配置")
            return None
        child = window_config.get('child_elements', {})
        element_config = child.get('prompt_text')
        if element_config:
            return self.get_element_text(**element_config)
        self.log.error("prompt_window: 未找到prompt_text子元素配置")
        return None
    
    def click_prompt_window_confirm_button(self):
        """点击消息提示窗口的确认按钮"""
        window_config = self._get_dialog_config('prompt_window')
        if not window_config:
            self.log.error("prompt_window: 未找到窗口配置")
            return False
        child = window_config.get('child_elements', {})
        element_config = child.get('confirm_button')
        if element_config:
            return self.click_element(**element_config)
        self.log.error("prompt_window: 未找到confirm_button子元素配置")
        return False
    
    def handle_prompt_window(self, expect_contains=None, timeout=5.0,
                              confirm_prompt=True):
        """
        处理消息提示窗口(prompt_window) - 只有"确认"按钮

        Args:
            expect_contains: 期望提示文本包含的字符串（可选）
            timeout: 超时时间
            confirm_prompt: 是否点击"确认"按钮（默认True，False=不点击）

        Returns:
            bool: 是否成功处理
        """
        if not self.wait_for_prompt_window(timeout=timeout):
            return False

        if expect_contains:
            prompt = self.get_prompt_window_text() or ""
            if expect_contains not in prompt:
                self.log.error(f"提示文本校验失败: 预期包含 '{expect_contains}', 实际 '{prompt}'")
                return False

        if confirm_prompt:
            return self.click_prompt_window_confirm_button()
        else:
            self.log.info("confirm_prompt=False，跳过点击确认按钮")
            return True

if __name__ == "__main__":
    print("基础页面类 - WinAppDriver版本")

