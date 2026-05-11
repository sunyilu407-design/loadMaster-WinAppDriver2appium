"""
油品信息管理页面对象类
负责油品信息管理页面的元素定位和基本操作
"""
import allure
from pageObject.base_page import BasePage


class OilManagementPage(BasePage):
    """
    油品信息管理页面
    职责：元素定位和基本交互，不包含业务逻辑
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('oil_management_page')

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
    @allure.step("切换到油品信息管理窗口")
    def switch_to_page_window(self):
        """切换到油品信息管理主窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    # ==================== 按钮点击方法 ====================
    @allure.step("点击添加油品按钮")
    def click_add_oil_button(self):
        """点击添加油品按钮"""
        self.switch_to_page_window()
        element_config = self._get_element_config('add_oil_button')
        return self.click_element(**element_config)

    @allure.step("点击修改油品按钮")
    def click_alter_oil_button(self):
        """点击修改油品按钮"""
        self.switch_to_page_window()
        element_config = self._get_element_config('alter_oil_button')
        return self.click_element(**element_config)

    @allure.step("点击删除油品按钮")
    def click_delete_oil_button(self):
        """点击删除油品按钮"""
        self.switch_to_page_window()
        element_config = self._get_element_config('delete_oil_button')
        return self.click_element(**element_config)

    # ==================== 查询方法 ====================
    @allure.step("设置油品名称搜索条件")
    def set_oil_name_search(self, text):
        """设置油品名称搜索条件"""
        self.switch_to_page_window()
        element_config = self._get_element_config('customer_name_search')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    # ==================== 表格操作方法 ====================
    @allure.step("获取油品信息表格数据")
    def get_content_table(self):
        """获取油品信息表格内容"""
        self.switch_to_page_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    @allure.step("点击油品表格指定行")
    def click_table_row(self, search_criteria, match_mode='exact'):
        """点击油品表格中指定的行"""
        self.switch_to_page_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 添加油品窗口方法 ====================
    @allure.step("切换到添加油品窗口")
    def switch_to_add_oil_window(self):
        """切换到添加油品窗口"""
        window_config = self._get_element_config('add_oil_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("设置油品简称")
    def set_oil_short_name_edit(self, text):
        """设置油品简称"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_short_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("设置油品名称")
    def set_oil_name_edit(self, text):
        """设置油品名称"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("设置油品编码")
    def set_oil_code_edit(self, text):
        """设置油品编码"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_code_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择油品类型")
    def select_oil_type_combo(self, option_text):
        """选择油品类型"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_type_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择对应颜色")
    def select_oil_color_combo(self, option_text):
        """选择对应颜色"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_color_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择曾用名")
    def select_oil_former_name_combo(self, option_text):
        """选择曾用名"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_former_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("点击添加油品窗口的确定按钮")
    def click_add_window_add_button(self):
        """点击添加油品窗口的确定按钮"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加油品窗口的取消按钮")
    def click_add_window_cancel_button(self):
        """点击添加油品窗口的取消按钮"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加油品窗口的关闭按钮")
    def click_add_window_quit_button(self):
        """点击添加油品窗口的关闭按钮"""
        element_config = self._get_element_config('add_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改油品窗口方法 ====================
    @allure.step("切换到修改油品窗口")
    def switch_to_alter_oil_window(self):
        """切换到修改油品窗口"""
        window_config = self._get_element_config('alter_oil_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    # 修改窗口的子元素使用与添加窗口相同的 automation_id，可复用
    def set_alter_oil_short_name_edit(self, text):
        """修改油品简称"""
        return self.set_oil_short_name_edit(text)

    def set_alter_oil_name_edit(self, text):
        """修改油品名称"""
        return self.set_oil_name_edit(text)

    def set_alter_oil_code_edit(self, text):
        """修改油品编码"""
        return self.set_oil_code_edit(text)

    def select_alter_oil_type_combo(self, option_text):
        """修改油品类型"""
        return self.select_oil_type_combo(option_text)

    def select_alter_oil_color_combo(self, option_text):
        """修改对应颜色"""
        return self.select_oil_color_combo(option_text)

    def select_alter_oil_former_name_combo(self, option_text):
        """修改曾用名"""
        return self.select_oil_former_name_combo(option_text)

    @allure.step("点击修改油品窗口的确定按钮")
    def click_alter_window_add_button(self):
        """点击修改油品窗口的确定按钮"""
        element_config = self._get_element_config('alter_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改油品窗口的取消按钮")
    def click_alter_window_cancel_button(self):
        """点击修改油品窗口的取消按钮"""
        element_config = self._get_element_config('alter_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改油品窗口的关闭按钮")
    def click_alter_window_quit_button(self):
        """点击修改油品窗口的关闭按钮"""
        element_config = self._get_element_config('alter_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除油品窗口方法 ====================
    @allure.step("切换到删除油品确认窗口")
    def switch_to_delete_oil_window(self):
        """切换到删除油品确认窗口"""
        window_config = self._get_element_config('delete_oil_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取删除确认窗口的提示文本")
    def get_delete_prompt_text(self):
        """获取删除确认窗口的提示文本"""
        element_config = self._get_element_config('delete_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击删除确认按钮（是/Yes）")
    def click_delete_confirm_button(self):
        """点击删除确认按钮（是/Yes）"""
        element_config = self._get_element_config('delete_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('yes_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除取消按钮（否/No）")
    def click_delete_cancel_button(self):
        """点击删除取消按钮（否/No）"""
        element_config = self._get_element_config('delete_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('no_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除关闭按钮")
    def click_delete_quit_button(self):
        """点击删除关闭按钮"""
        element_config = self._get_element_config('delete_oil_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除确认按钮（confirm）")
    def click_delete_all_confirm_button(self):
        """点击删除确认按钮（confirm 按钮）"""
        element_config = self._get_element_config('delete_oil_window')
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

