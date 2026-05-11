"""
客户信息管理页面对象类
Customer Management Page Object
职责：元素定位和基本交互，不包含业务逻辑
"""
import allure
from pageObject.base_page import BasePage


class CustomerManagementPage(BasePage):
    """
    客户信息管理页面
    负责客户信息的增删改查等元素操作
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('customer_management_page')

        # 检查配置
        if self.config is None:
            self.log.error("页面配置加载失败")
            raise Exception("页面配置加载失败")

        # 初始化配置项
        self.elements = self.config.get('elements', {})
        self.test_data = self.config.get('test_data', {})
        self.app_config = self.config.get('app_config', {})

    def _get_element_config(self, element_name):
        """获取元素配置（支持嵌套 child_elements）"""
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

    # ==================== 窗口切换方法 ====================
    def switch_to_customer_management_window(self):
        """切换到客户信息管理窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    # ==================== 按钮点击方法 ====================
    @allure.step("点击添加客户按钮")
    def click_add_customer_button(self):
        """点击添加客户按钮"""
        self.switch_to_customer_management_window()
        element_config = self._get_element_config('add_customer_button')
        return self.click_element(**element_config)

    @allure.step("点击修改客户按钮")
    def click_alter_customer_button(self):
        """点击修改客户按钮"""
        self.switch_to_customer_management_window()
        element_config = self._get_element_config('alter_customer_button')
        return self.click_element(**element_config)

    @allure.step("点击删除客户按钮")
    def click_delete_customer_button(self):
        """点击删除客户按钮"""
        self.switch_to_customer_management_window()
        element_config = self._get_element_config('delete_customer_button')
        return self.click_element(**element_config)

    # ==================== 搜索方法 ====================
    @allure.step("输入客户名称搜索")
    def set_customer_name_search(self, text):
        """输入客户名称搜索"""
        self.switch_to_customer_management_window()
        element_config = self._get_element_config('customer_name_search')
        return self.send_keys_to_element(text, **element_config)

    # ==================== 表格操作方法 ====================
    @allure.step("获取客户信息表格数据")
    def get_content_table(self):
        """获取客户信息表格数据"""
        self.switch_to_customer_management_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    @allure.step("点击表格中的客户行")
    def click_customer_table_row(self, search_criteria, match_mode='exact'):
        """点击指定的客户行"""
        self.switch_to_customer_management_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 添加客户窗口方法 ====================
    @allure.step("切换到添加客户窗口")
    def switch_to_add_customer_window(self):
        """切换到添加客户窗口"""
        window_config = self._get_element_config('add_customer_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("输入客户简称")
    def set_customer_short_name_edit(self, text):
        """输入客户简称"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_short_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入客户全称")
    def set_customer_name_edit(self, text):
        """输入客户全称"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入客户编码")
    def set_customer_code_edit(self, text):
        """输入客户编码"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_code_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入联系人")
    def set_customer_link_man_edit(self, text):
        """输入联系人"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_link_man_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入联系电话")
    def set_customer_link_phone_edit(self, text):
        """输入联系电话"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_link_phone_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入短信息号码")
    def set_customer_message_phone_edit(self, text):
        """输入短信息号码"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_message_phone_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入短信息备用号码")
    def set_customer_spare_message_phone_edit(self, text):
        """输入短信息备用号码"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_spare_message_phone_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择是否优先")
    def select_is_priority_combo(self, option_text):
        """选择是否优先"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('is_priority_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入备注")
    def set_customer_remark_edit(self, text):
        """输入备注"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('customer_remark_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击添加客户窗口的确定按钮")
    def click_add_window_add_button(self):
        """点击添加客户窗口的确定按钮"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加客户窗口的取消按钮")
    def click_add_window_cancel_button(self):
        """点击添加客户窗口的取消按钮"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加客户窗口的关闭按钮")
    def click_add_window_quit_button(self):
        """点击添加客户窗口的关闭按钮"""
        element_config = self._get_element_config('add_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改客户窗口方法 ====================
    @allure.step("切换到修改客户窗口")
    def switch_to_alter_customer_window(self):
        """切换到修改客户窗口"""
        window_config = self._get_element_config('alter_customer_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    # 修改窗口的子元素使用与添加窗口相同的 automation_id，可复用
    def set_alter_customer_short_name_edit(self, text):
        """修改客户简称"""
        return self.set_customer_short_name_edit(text)

    def set_alter_customer_name_edit(self, text):
        """修改客户全称"""
        return self.set_customer_name_edit(text)

    def set_alter_customer_code_edit(self, text):
        """修改客户编码"""
        return self.set_customer_code_edit(text)

    def set_alter_customer_link_man_edit(self, text):
        """修改联系人"""
        return self.set_customer_link_man_edit(text)

    def set_alter_customer_link_phone_edit(self, text):
        """修改联系电话"""
        return self.set_customer_link_phone_edit(text)

    def set_alter_customer_message_phone_edit(self, text):
        """修改短信息号码"""
        return self.set_customer_message_phone_edit(text)

    def set_alter_customer_spare_message_phone_edit(self, text):
        """修改短信息备用号码"""
        return self.set_customer_spare_message_phone_edit(text)

    def select_alter_is_priority_combo(self, option_text):
        """修改是否优先"""
        return self.select_is_priority_combo(option_text)

    def set_alter_customer_remark_edit(self, text):
        """修改备注"""
        return self.set_customer_remark_edit(text)

    @allure.step("点击修改客户窗口的确定按钮")
    def click_alter_window_add_button(self):
        """点击修改客户窗口的确定按钮"""
        element_config = self._get_element_config('alter_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改客户窗口的取消按钮")
    def click_alter_window_cancel_button(self):
        """点击修改客户窗口的取消按钮"""
        element_config = self._get_element_config('alter_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改客户窗口的关闭按钮")
    def click_alter_window_quit_button(self):
        """点击修改客户窗口的关闭按钮"""
        element_config = self._get_element_config('alter_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除客户窗口方法 ====================
    @allure.step("切换到删除客户确认窗口")
    def switch_to_delete_customer_window(self):
        """切换到删除客户确认窗口"""
        window_config = self._get_element_config('delete_customer_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取删除确认窗口的提示文本")
    def get_delete_prompt_text(self):
        """获取删除确认窗口的提示文本"""
        element_config = self._get_element_config('delete_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击删除确认按钮")
    def click_delete_confirm_button(self):
        """点击删除确认按钮"""
        element_config = self._get_element_config('delete_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('yes_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除取消按钮")
    def click_delete_cancel_button(self):
        """点击删除取消按钮"""
        element_config = self._get_element_config('delete_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('no_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除关闭按钮")
    def click_delete_quit_button(self):
        """点击删除关闭按钮"""
        element_config = self._get_element_config('delete_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除确认按钮（confirm）")
    def click_delete_all_confirm_button(self):
        """点击删除确认按钮（confirm 按钮）"""
        element_config = self._get_element_config('delete_customer_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 公共弹窗方法（继承自 BasePage）====================
    # 以下方法直接使用 BasePage 已封装好的公共方法：
    # - switch_to_operation_window()
    # - click_operation_window_confirm_button()
    # - click_operation_window_cancel_button()
    # - click_operation_window_quit_button()
    # - switch_to_prompt_window()
    # - click_prompt_window_confirm_button()

