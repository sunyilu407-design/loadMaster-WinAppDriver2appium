"""
串口信息管理页面对象类
Port Management Page Object
职责：元素定位和基本交互，不包含业务逻辑
"""
import allure
from pageObject.base_page import BasePage


class PortManagementPage(BasePage):
    """
    串口信息管理页面
    负责串口信息的增删改等元素操作
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('port_management_page')

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
    def switch_to_port_management_window(self):
        """切换到串口信息管理窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    def switch_to_page_window(self):
        """切换到串口信息管理窗口（兼容别名）"""
        return self.switch_to_port_management_window()

    # ==================== 主页按钮点击方法 ====================
    @allure.step("点击添加串口按钮")
    def click_add_port_button(self):
        """点击添加串口按钮"""
        self.switch_to_port_management_window()
        element_config = self._get_element_config('add_port_button')
        return self.click_element(**element_config)

    @allure.step("点击修改串口按钮")
    def click_alter_port_button(self):
        """点击修改串口按钮"""
        self.switch_to_port_management_window()
        element_config = self._get_element_config('alter_port_button')
        return self.click_element(**element_config)

    @allure.step("点击删除串口按钮")
    def click_delete_port_button(self):
        """点击删除串口按钮"""
        self.switch_to_port_management_window()
        element_config = self._get_element_config('delete_port_button')
        return self.click_element(**element_config)

    # ==================== 表格操作方法 ====================
    @allure.step("获取串口信息表格数据")
    def get_content_table(self):
        """获取串口信息表格数据"""
        self.switch_to_port_management_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    @allure.step("点击表格中的串口行")
    def click_port_table_row(self, search_criteria, match_mode='exact'):
        """点击指定的串口行"""
        self.switch_to_port_management_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 添加串口窗口方法 ====================
    @allure.step("切换到添加串口窗口")
    def switch_to_add_port_window(self):
        """切换到添加串口窗口"""
        window_config = self._get_element_config('add_port_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("选择添加窗口的串口名称")
    def select_add_portname_combo(self, option_text):
        """选择添加窗口的串口名称下拉框"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('portname_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的波特率")
    def select_add_baudrate_combo(self, option_text):
        """选择添加窗口的波特率下拉框"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('baudrate_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的串口类型")
    def select_add_porttype_combo(self, option_text):
        """选择添加窗口的串口类型下拉框"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('porttype_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入添加窗口的备注")
    def set_add_remark_edit(self, text):
        """输入添加窗口的备注"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('remark_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击添加串口窗口的添加按钮")
    def click_add_window_add_button(self):
        """点击添加串口窗口的添加按钮"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加串口窗口的取消按钮")
    def click_add_window_cancel_button(self):
        """点击添加串口窗口的取消按钮"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加串口窗口的关闭按钮")
    def click_add_window_close_button(self):
        """点击添加串口窗口的关闭按钮"""
        element_config = self._get_element_config('add_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改串口窗口方法 ====================
    @allure.step("切换到修改串口窗口")
    def switch_to_alter_port_window(self):
        """切换到修改串口窗口"""
        window_config = self._get_element_config('alter_port_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    # 修改窗口的子元素使用与添加窗口相同的 automation_id，可复用
    def select_alter_portname_combo(self, option_text):
        """选择修改窗口的串口名称下拉框"""
        return self.select_add_portname_combo(option_text)

    def select_alter_baudrate_combo(self, option_text):
        """选择修改窗口的波特率下拉框"""
        return self.select_add_baudrate_combo(option_text)

    def select_alter_porttype_combo(self, option_text):
        """选择修改窗口的串口类型下拉框"""
        return self.select_add_porttype_combo(option_text)

    def set_alter_remark_edit(self, text):
        """输入修改窗口的备注"""
        return self.set_add_remark_edit(text)

    @allure.step("点击修改串口窗口的修改按钮")
    def click_alter_window_alter_button(self):
        """点击修改串口窗口的修改按钮"""
        element_config = self._get_element_config('alter_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('alter_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改串口窗口的取消按钮")
    def click_alter_window_cancel_button(self):
        """点击修改串口窗口的取消按钮"""
        element_config = self._get_element_config('alter_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改串口窗口的关闭按钮")
    def click_alter_window_close_button(self):
        """点击修改串口窗口的关闭按钮"""
        element_config = self._get_element_config('alter_port_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除确认窗口方法 ====================
    @allure.step("切换到删除串口确认窗口")
    def switch_to_delete_port_window(self):
        """切换到删除串口确认窗口"""
        window_config = self._get_element_config('delete_confirm_window')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("获取删除确认窗口的提示文本")
    def get_delete_prompt_text(self):
        """获取删除确认窗口的提示文本"""
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击删除确认按钮（是）")
    def click_delete_confirm_button(self):
        """点击删除确认窗口的是按钮"""
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除取消按钮（否）")
    def click_delete_cancel_button(self):
        """点击删除确认窗口的否按钮"""
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除退出按钮")
    def click_delete_quit_button(self):
        """点击删除确认窗口的退出按钮"""
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('quit_button')
            if child:
                return self.click_element(**child)
        return False
