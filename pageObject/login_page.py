from pageObject.base_page import BasePage
from utils.config_manager import ConfigManager
from utils.logger import Logger
from selenium.webdriver.common.keys import Keys
import logging
import time
import allure


class LoginPage(BasePage):
    def __init__(self, driver, config_manager):
        """
        初始化登录页面对象
        :param driver: WebDriver实例
        :param config_manager: 配置管理器实例
        """
        # 调用父类构造函数初始化驱动和配置管理器
        super().__init__(driver, config_manager, "windows")
        
        # 加载页面配置
        self.config = self.config_manager.load_page_config('login_page')
        
        # 检查配置加载是否成功
        if self.config is None:
            self.log.error("LoginPage: 配置加载失败")
            raise Exception("LoginPage: 配置加载失败")
            
        # 检查驱动是否初始化成功
        if self.driver is None:
            self.log.error("LoginPage: 驱动未初始化")
            raise Exception("LoginPage: 驱动未初始化")
        else:
            self.log.info("LoginPage: 驱动初始化成功")
            self.elements = self.config.get('elements', {})
            self.test_data = self.config.get('test_data', [])
            self.app_config = self.config.get('app_config', [])

            # 日志记录
            self.log = logging.getLogger("log")
            self.log.info("登录页面初始化完成")
    
    def input_username(self, username):
        """
        输入用户名
        :param username: 用户名
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法执行输入用户名操作")
                return False
            
            # 切换到登录窗口
            status = self.switch_to_window(self.app_config.get('main_window_title', ''))
            if not status:
                self.log.error("切换到登录窗口失败")
                return False

            username_locator = self.elements.get('username_input', {})
            self.log.info(f"尝试输入用户名: {username}")
            element = self.locate_element(**username_locator)
            if element:
                # 确保元素可操作
                element.click()
                time.sleep(0.2)
                
                # 清空输入框 - 使用多次清空确保干净
                for _ in range(3):
                    element.send_keys(Keys.CONTROL, 'a')
                    time.sleep(0.05)
                    element.send_keys(Keys.DELETE)
                    time.sleep(0.05)
                
                time.sleep(0.1)
                
                # 输入新用户名
                element.send_keys(username)
                time.sleep(0.1)
                
                # 验证输入结果
                actual_value = element.text if hasattr(element, 'text') else ''
                if not actual_value and hasattr(element, 'get_attribute'):
                    actual_value = element.get_attribute('Value') or ''
                
                self.log.info(f"输入用户名成功: {username}")
                return True
            else:
                self.log.error(f"未找到用户名输入框: {username_locator}. 使用的定位器: {username_locator}")
                return False
        except Exception as e:
            self.log.error(f"输入用户名失败: {e}")
            return False
    
    def input_password(self, password):
        """
        输入密码
        :param password: 密码
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法执行输入密码操作")
                return False
            
            # 切换到登录窗口
            status = self.switch_to_window(self.app_config.get('main_window_title', ''))
            if not status:
                self.log.error("切换到登录窗口失败")
                return False

            password_locator = self.elements.get('password_input', {})
            self.log.info("尝试输入密码")
            element = self.locate_element(**password_locator)
            if element:
                # 确保元素可操作
                element.click()
                time.sleep(0.2)
                
                # 清空输入框 - 使用多次清空确保干净
                for _ in range(3):
                    element.send_keys(Keys.CONTROL, 'a')
                    time.sleep(0.05)
                    element.send_keys(Keys.DELETE)
                    time.sleep(0.05)
                
                time.sleep(0.1)
                
                # 输入密码
                element.send_keys(password)
                time.sleep(0.1)
                
                self.log.info("输入密码成功")
                return True
            else:
                self.log.error(f"未找到密码输入框: {password_locator}. 使用的定位器: {password_locator}")
                return False
        except Exception as e:
            self.log.error(f"输入密码失败: {e}")
            return False
    
    def click_login_button(self):
        """
        点击登录按钮
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法执行点击登录按钮操作")
                return False

            # 切换到登录窗口
            status = self.switch_to_window(self.app_config.get('main_window_title', ''))
            if not status:
                self.log.error("切换到登录窗口失败")
                return False

            login_button_locator = self.elements.get('login_button', {})
            self.log.info("尝试点击登录按钮")
            element = self.locate_element(**login_button_locator)
            if element:
                self.log.info(f"成功定位到登录按钮: {element}")
                element.click()
                self.log.info("点击登录按钮成功")
                return True
            else:
                self.log.error(f"未找到登录按钮: {login_button_locator}. 使用的定位器: {login_button_locator}")
                return False
        except Exception as e:
            self.log.error(f"点击登录按钮失败: {e}")
            return False
    
    def get_error_message(self):
        """
        获取错误提示信息
        :return: 错误提示文本
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法获取错误提示信息")
                return None
                
            error_window_locator = self.elements.get('error_message_window', {}).get('automation_id', {})
            error_window_name = self.elements.get('error_message_window', {}).get('name', {})
            error_locator = self.elements.get('error_message', {}).get('automation_id', {})

            # 切换到错误提示窗口
            error_window_change_status = self.switch_to_window(error_window_name)
            if not error_window_change_status:
                self.log.error("切换到错误提示窗口失败")
                return None

            # 定位错误提示元素
            error_element = self.locate_element(error_locator)
            if not error_element:
                self.log.error("未找到错误提示元素")
                return None
            # 点击确认按钮
            confirm_button_status = self.click_confirm_button()
            if not confirm_button_status:
                self.log.error("点击确认按钮失败")
                return None
            # 返回错误提示文本
            self.log.info(f"获取错误提示信息: {error_element.text}")
            return error_element.text if error_element else None
        except Exception as e:
            self.log.error(f"获取错误提示信息失败: {e}")
            self.take_screenshot("get_error_message_error")
            return None
    
    def click_confirm_button(self):
        """
        点击确认按钮
        :return: 是否点击成功
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法执行点击确认按钮操作")
                return False
                
            confirm_button_locator = self.elements.get('confirm_button', {})
            self.log.info("点击确认按钮")
            return self.locate_element(confirm_button_locator).click()
        except Exception as e:
            self.log.error(f"点击确认按钮失败: {e}")
            self.take_screenshot("click_confirm_button_error")
            return False
    
    def is_login_page_displayed(self):
        """
        检查登录页面是否显示
        :return: 布尔值
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法检查登录页面状态")
                return False
                
            # 尝试定位用户名输入框来判断页面是否加载
            username_locator = self.elements.get('username_input', {})
            element = self.locate_element(**username_locator)
            return element is not None
        except Exception as e:
            self.log.error(f"检查登录页面显示状态失败: {e}")
            return False
    
    def wait_for_login_page(self, timeout=30):
        """
        等待登录页面加载完成
        :param timeout: 超时时间（秒）
        :return: 布尔值
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法等待登录页面加载")
                return False
                
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_login_page_displayed():
                    self.log.info("登录页面加载完成")
                    return True
                time.sleep(1)
            self.log.warning("登录页面加载超时")
            return False
        except Exception as e:
            self.log.error(f"等待登录页面加载失败: {e}")
            return False
    
    def clear_input_fields(self):
        """
        清空输入框 - Windows桌面应用优化版
        使用多次 Ctrl+A 全选后删除，确保干净清空
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法清空输入框")
                return False

            # 切换到登录窗口
            status = self.switch_to_window(self.app_config.get('main_window_title', ''))
            if not status:
                self.log.warning("切换到登录窗口失败，跳过清空输入框")
                return False

            username_locator = self.elements.get('username_input', {})
            password_locator = self.elements.get('password_input', {})

            # 清空用户名输入框 - 使用多次清空确保干净
            username_element = self.locate_element(**username_locator)
            if username_element:
                username_element.click()
                time.sleep(0.1)
                for _ in range(3):
                    username_element.send_keys(Keys.CONTROL, 'a')
                    time.sleep(0.05)
                    username_element.send_keys(Keys.DELETE)
                    time.sleep(0.05)
                self.log.debug("已清空用户名输入框")

            # 清空密码输入框 - 使用多次清空确保干净
            password_element = self.locate_element(**password_locator)
            if password_element:
                password_element.click()
                time.sleep(0.1)
                for _ in range(3):
                    password_element.send_keys(Keys.CONTROL, 'a')
                    time.sleep(0.05)
                    password_element.send_keys(Keys.DELETE)
                    time.sleep(0.05)
                self.log.debug("已清空密码输入框")

            self.log.info("清空输入框完成")
            return True
        except Exception as e:
            self.log.error(f"清空输入框失败: {e}")
            return False
    
    def is_login_successful(self):
        """
        检查是否登录成功
        :return: 布尔值
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法检查登录状态")
                return False

            # 首先检查是否出现主窗口（优先判断）
            is_success = self.check_main_window()

            if is_success:
                self.log.info("登录成功,并跳转到主页面")
                return True

            # 如果主窗口未出现，再检查登录页面是否还显示
            try:
                if self.is_login_page_displayed():
                    self.log.info("登录失败：主窗口未出现且登录页面仍显示")
                    return False
                else:
                    self.log.warning("登录状态不确定：主窗口未出现但登录页面已消失")
                    # 尝试等待主窗口出现
                    self.log.info("等待主窗口出现...")
                    time.sleep(3)
                    return self.check_main_window()
            except Exception as e:
                self.log.warning(f"检查登录状态时出错: {e}")
                return False
        except Exception as e:
            self.log.error(f"检查登录状态失败: {e}")
            return False
    def check_main_window(self):
        """
        检查是否在主窗口
        :return: 布尔值
        """
        try:
            main_window_config = self.elements.get('main_window', {})
            main_window_name = main_window_config.get('name', '')
            self.log.info(f"尝试等待主窗口: {main_window_name}")

            # 先获取当前所有窗口句柄
            try:
                all_handles = self.driver.window_handles
                self.log.info(f"当前所有窗口句柄数量: {len(all_handles)}")
            except Exception as e:
                self.log.warning(f"获取窗口句柄失败: {e}")
                # 尝试刷新窗口句柄
                time.sleep(1)
                try:
                    all_handles = self.driver.window_handles
                    self.log.info(f"重试获取窗口句柄: {len(all_handles)}")
                except Exception:
                    self.log.error("无法获取窗口句柄")
                    return False

            if not all_handles:
                self.log.warning("当前没有窗口句柄，尝试等待...")
                time.sleep(2)
                try:
                    all_handles = self.driver.window_handles
                except Exception:
                    pass

            # 遍历所有窗口，查找标题匹配的
            for handle in all_handles:
                try:
                    self.driver.switch_to.window(handle)
                    current_title = self.driver.title
                    self.log.info(f"检查窗口: '{current_title}'")
                    if main_window_name and main_window_name in current_title:
                        self.log.info(f"已切换到主窗口: {current_title}")
                        return True
                except Exception as e:
                    self.log.debug(f"切换到窗口 {handle} 失败: {e}")
                    continue

            # 如果精确匹配失败，尝试模糊匹配（查找包含"装车"或"管理"的窗口）
            fallback_keywords = ['装车', '管理', '系统']
            for handle in all_handles:
                try:
                    self.driver.switch_to.window(handle)
                    current_title = self.driver.title
                    for keyword in fallback_keywords:
                        if keyword in current_title:
                            self.log.info(f"模糊匹配到主窗口: {current_title}")
                            return True
                except Exception:
                    continue

            self.log.warning(f"未找到主窗口 '{main_window_name}'")
            return False

        except Exception as e:
            self.log.error(f"检查主窗口时发生异常: {e}")
            return False

    def handle_startup_prompt(self):
        """
        处理应用启动时的提示窗口
        :return: 布尔值，表示是否成功处理了提示窗口
        """
        try:
            with allure.step("检查提示窗口是否存在"):
                # 检查当前窗口是否是提示窗口
                current_title = self.driver.title
                self.log.info(f"当前窗口标题: {current_title}")

                if "提示" in current_title:
                    self.log.info("检测到启动提示窗口，尝试关闭")
                    # 尝试点击确认按钮
                    confirm_button_config = self.elements.get('confirm_button', {})
                    if self.is_element_present(**confirm_button_config):
                        self.log.info("找到确认按钮，点击关闭提示窗口")
                        return self.click_element(**confirm_button_config)
                    else:
                        self.log.warning("未找到确认按钮，尝试按Enter键")
                        # 尝试发送Enter键
                        from selenium.webdriver.common.keys import Keys
                        # 发送Enter键到当前活动元素
                        try:
                            active_element = self.driver.switch_to.active_element
                            active_element.send_keys(Keys.RETURN)
                            self.log.info("发送Enter键成功")
                            return True
                        except Exception as e:
                            self.log.error(f"发送Enter键失败: {e}")
                            return False
                else:
                    self.log.info("当前不是提示窗口，无需处理")
                    return True

        except Exception as e:
            self.log.error(f"处理启动提示窗口异常: {e}")
            return False

    def login(self, username, password):
        """
        执行登录操作
        :param username: 用户名
        :param password: 密码
        :return: 布尔值，表示是否登录成功
        """
        with allure.step(f"执行登录操作 (用户名: {username})"):
            try:
                if not self.driver:
                    self.log.error("驱动未初始化，无法执行登录操作")
                    return False

                self.log.info(f"开始登录，用户名: {username}")

                # 检查并处理启动提示窗口
                with allure.step("检查并处理启动提示窗口"):
                    if self.handle_startup_prompt():
                        self.log.info("成功处理启动提示窗口")
                        # 等待主窗口加载
                        self.log.info("等待主窗口加载...")
                        time.sleep(3)

                        # 调试：打印当前窗口信息（在 appTopLevelWindow 模式下 window_handles=[]）
                        try:
                            current_title = self.driver.title
                            all_handles = self.driver.window_handles
                            self.log.info(f"当前窗口标题: '{current_title}', window_handles: {all_handles}")
                        except Exception as e:
                            self.log.error(f"获取窗口信息失败: {e}")
                    else:
                        self.log.warning("未发现启动提示窗口或处理失败，继续登录流程")

                # 输入用户名和密码
                with allure.step("输入登录信息"):
                    if not self.input_username(username):
                        self.log.error("输入用户名失败")
                        return False

                    if not self.input_password(password):
                        self.log.error("输入密码失败")
                        return False

                # 点击登录按钮
                with allure.step("点击登录按钮"):
                    if not self.click_login_button():
                        self.log.error("点击登录按钮失败")
                        return False

                # 等待登录结果
                with allure.step("等待登录结果"):
                    time.sleep(3)

                # 检查登录是否成功
                with allure.step("验证登录结果"):
                    success = self.is_login_successful()
                    if success:
                        self.log.info("登录成功")
                        return True # 如果登录成功，立即返回True
                    else:
                        self.log.info("登录失败")

                return success
            except Exception as e:
                self.log.error(f"登录过程出现异常: {e}")
                self.take_screenshot("login_error")
                return False