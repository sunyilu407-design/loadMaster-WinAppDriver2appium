"""
用户个人中心页面 - 页面元素操作
只包含页面元素定位和基础交互，不包含业务逻辑
"""

import allure
from pageObject.base_page import BasePage


class UserProfilePage(BasePage):
    """
    用户个人中心页面 - 页面元素操作类
    包含修改密码和修改用户名窗口的元素操作
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置, user/user_profile_page.yaml
        self.config = self.config_manager.load_page_config('user/user_profile_page')

        # 检查配置加载是否成功
        if self.config is None:
            self.log.error("user_profile_page: 配置加载失败")
            raise Exception("user_profile_page: 配置加载失败")

        # 检查驱动是否初始化成功
        if self.driver is None:
            self.log.warning("user_profile_page: 驱动未初始化，将在使用时延迟初始化")
            # 不抛出异常，允许延迟初始化
        else:
            self.log.info("user_profile_page: 驱动初始化成功")
            self.elements = self.config.get('elements', {})
            self.test_data = self.config.get('test_data', {})
            self.app_config = self.config.get('app_config', {})

    def _get_element_config(self, element_name):
        """
        获取元素配置
        :param element_name: 元素名称
        :return: 元素配置字典
        """
        # 递归查找元素配置
        def find_element(config, name):
            if name in config:
                return config[name]
            for key, value in config.items():
                if isinstance(value, dict):
                    if key == 'child_elements' and name in value:
                        return value[name]
                    result = find_element(value, name)
                    if result:
                        return result
            return None

        element_config = find_element(self.elements, element_name)
        if element_config:
            return element_config
        self.log.error(f"未找到元素配置: {element_name}")
        return None

    # ========== 窗口切换方法 ==========

    def switch_to_alter_username_window(self):
        """
        切换到修改用户名窗口
        """
        window_config = self._get_element_config('alter_username_window')
        if window_config and 'name' in window_config:
            return self.switch_to_window(title=window_config['name'])
        return False

    def switch_to_alter_password_window(self):
        """
        切换到修改密码窗口
        """
        window_config = self._get_element_config('alter_password_window')
        if window_config and 'name' in window_config:
            return self.switch_to_window(title=window_config['name'])
        return False

    # ========== 修改用户名窗口元素操作 ==========

    def set_alter_username_old_password(self, text):
        """
        输入旧密码（修改用户名窗口）
        """
        with allure.step("输入修改用户名窗口的旧密码"):
            self.switch_to_alter_username_window()
            element_config = self._get_element_config('old_password_input')
            if element_config:
                return self.send_keys_to_element(text, **element_config)
            return False

    def set_alter_username_new_username(self, text):
        """
        输入新用户名（修改用户名窗口）
        """
        with allure.step("输入修改用户名窗口的新用户名"):
            self.switch_to_alter_username_window()
            element_config = self._get_element_config('new_username_input')
            if element_config:
                return self.send_keys_to_element(text, **element_config)
            return False

    def set_alter_username_confirm_username(self, text):
        """
        输入确认新用户名（修改用户名窗口）
        """
        self.switch_to_alter_username_window()
        element_config = self._get_element_config('confirm_username_input')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def click_alter_username_save_button(self):
        """
        点击保存按钮（修改用户名窗口）
        """
        self.switch_to_alter_username_window()
        element_config = self._get_element_config('save_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_username_cancel_button(self):
        """
        点击取消按钮（修改用户名窗口）
        """
        self.switch_to_alter_username_window()
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_username_quit_button(self):
        """
        点击退出按钮（修改用户名窗口）
        """
        self.switch_to_alter_username_window()
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    # ========== 修改密码窗口元素操作 ==========

    def set_alter_password_old_password(self, text):
        """
        输入旧密码（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('old_password_input')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def set_alter_password_new_password(self, text):
        """
        输入新密码（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('new_password_input')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def set_alter_password_confirm_password(self, text):
        """
        输入确认新密码（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('confirm_password_input')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def click_alter_password_save_button(self):
        """
        点击保存按钮（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('save_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_password_cancel_button(self):
        """
        点击取消按钮（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_password_quit_button(self):
        """
        点击退出按钮（修改密码窗口）
        """
        self.switch_to_alter_password_window()
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False