"""
配置设定管理页面对象类
Config Settings Page Object
职责：元素定位和基本交互，不包含业务逻辑
"""

import allure
from pageObject.base_page import BasePage


class ConfigSettingsPage(BasePage):
    """
    配置设定管理页面
    负责配置设定的查看、修改、流量计类型设置、密度管理等操作
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('config_settings_page')

        # 检查配置
        if self.config is None:
            self.log.error("ConfigSettingsPage: 页面配置加载失败")
            raise Exception("ConfigSettingsPage: 页面配置加载失败")

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
    def switch_to_config_settings_window(self):
        """切换到配置设定主窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    def switch_to_page_window(self):
        """切换到配置设定主窗口（兼容别名）"""
        return self.switch_to_config_settings_window()

    # ==================== 主页面按钮点击方法 ====================
    @allure.step("选择货位筛选条件")
    def select_station_filter(self, option_text):
        """选择货位筛选条件下拉框"""
        element_config = self._get_element_config('station_filter_combo')
        if element_config:
            return self.select_combobox_option(option_text, **element_config)
        return False

    @allure.step("选择油品筛选条件")
    def select_oilname_filter(self, option_text):
        """选择油品筛选条件下拉框"""
        element_config = self._get_element_config('oilname_filter_combo')
        if element_config:
            return self.select_combobox_option(option_text, **element_config)
        return False

    @allure.step("点击刷新按钮")
    def click_refresh_button(self):
        """点击刷新按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('refresh_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击货位密度修改按钮")
    def click_update_station_density_button(self):
        """点击货位密度修改按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('update_station_density_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击设置流量计类型按钮")
    def click_set_flowmeter_type_button(self):
        """点击设置流量计类型按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('set_flowmeter_type_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击储罐密度修改按钮")
    def click_update_tank_density_button(self):
        """点击储罐密度修改按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('update_tank_density_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击密度历史记录按钮")
    def click_md_history_button(self):
        """点击密度历史记录按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('md_history_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击下发到装车仪器按钮")
    def click_set_to_device_button(self):
        """点击下发到装车仪器按钮"""
        self.switch_to_config_settings_window()
        element_config = self._get_element_config('set_to_device_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("勾选同时修改相同油品配置")
    def check_same_oil_checkbox(self):
        """勾选同时修改相同油品的配置设定信息"""
        element_config = self._get_element_config('same_oil_checkbox')
        if element_config:
            element = self.locate_element(**element_config)
            if element:
                if element.is_selected():
                    self.log.debug("复选框已勾选")
                    return True
                return self.click_element(**element_config)
        return False

    @allure.step("获取结果文本")
    def get_result_text(self):
        """获取结果文本内容"""
        element_config = self._get_element_config('result_text')
        if element_config:
            return self.get_element_text(**element_config)
        return ""

    # ==================== 表格操作方法 ====================
    @allure.step("获取配置设定表格数据")
    def get_content_table(self):
        """获取配置设定表格数据"""
        self.switch_to_config_settings_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    @allure.step("点击表格中的配置行")
    def click_config_table_row(self, search_criteria, match_mode='exact'):
        """点击指定的配置行"""
        self.switch_to_config_settings_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 设置流量计类型窗口方法 ====================
    @allure.step("切换到设置流量计类型窗口")
    def switch_to_set_flowmeter_window(self):
        """切换到设置流量计类型窗口"""
        window_config = self._get_element_config('set_flowmeter_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取设置流量计窗口的货位号")
    def get_flowmeter_station_no(self):
        """获取设置流量计窗口的货位号"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no_edit')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("选择组分流量计类型")
    def select_flowmeter_type1(self, option_text):
        """选择组分流量计类型下拉框"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('flowmeter_type1_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择乙醇流量计类型")
    def select_flowmeter_type2(self, option_text):
        """选择乙醇流量计类型下拉框"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('flowmeter_type2_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("点击流量计窗口的保存按钮")
    def click_flowmeter_save_button(self):
        """点击设置流量计类型窗口的保存按钮"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击流量计窗口的取消按钮")
    def click_flowmeter_cancel_button(self):
        """点击设置流量计类型窗口的取消按钮"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击流量计窗口的关闭按钮")
    def click_flowmeter_close_button(self):
        """点击设置流量计类型窗口的关闭按钮"""
        element_config = self._get_element_config('set_flowmeter_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 货位密度修改窗口方法 ====================
    @allure.step("切换到货位密度修改窗口")
    def switch_to_station_density_window(self):
        """切换到货位密度修改窗口"""
        window_config = self._get_element_config('station_density_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取货位密度修改窗口的货位号")
    def get_station_density_station_no(self):
        """获取货位密度修改窗口的货位号"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no_edit')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("获取货位密度修改窗口的货位名称")
    def get_station_density_station_name(self):
        """获取货位密度修改窗口的货位名称"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_name_edit')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("选择货位密度窗口的油品名称")
    def select_station_density_oil_name(self, option_text):
        """选择货位密度修改窗口的油品名称下拉框"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择组分罐名")
    def select_station_density_tank_name1(self, option_text):
        """选择货位密度修改窗口的组分罐名下拉框"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('tank_name1_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择乙醇罐名")
    def select_station_density_tank_name2(self, option_text):
        """选择货位密度修改窗口的乙醇罐名下拉框"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('tank_name2_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入计重密度")
    def set_station_weight_density(self, text):
        """输入货位密度修改窗口的计重密度"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入组分标密")
    def set_station_standard_density1(self, text):
        """输入货位密度修改窗口的组分标密"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('standard_density1_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入乙醇标密")
    def set_station_standard_density2(self, text):
        """输入货位密度修改窗口的乙醇标密"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('standard_density2_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入组分计密")
    def set_station_weight_density1(self, text):
        """输入货位密度修改窗口的组分计密"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density1_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入乙醇计密")
    def set_station_weight_density2(self, text):
        """输入货位密度修改窗口的乙醇计密"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density2_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击货位密度计算按钮")
    def click_station_density_compute_button(self):
        """点击货位密度修改窗口的计算按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击组分计密计算按钮")
    def click_station_density_compute_button1(self):
        """点击货位密度修改窗口的组分计密计算按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button1')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击乙醇计密计算按钮")
    def click_station_density_compute_button2(self):
        """点击货位密度修改窗口的乙醇计密计算按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button2')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击货位密度窗口的保存按钮")
    def click_station_density_save_button(self):
        """点击货位密度修改窗口的保存按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击货位密度窗口的取消按钮")
    def click_station_density_cancel_button(self):
        """点击货位密度修改窗口的取消按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击货位密度窗口的关闭按钮")
    def click_station_density_close_button(self):
        """点击货位密度修改窗口的关闭按钮"""
        element_config = self._get_element_config('station_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 储罐密度修改窗口方法 ====================
    @allure.step("切换到储罐密度修改窗口")
    def switch_to_tank_density_window(self):
        """切换到储罐密度修改窗口"""
        window_config = self._get_element_config('tank_density_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("选择储罐密度窗口的油品名称")
    def select_tank_density_oil_name(self, option_text):
        """选择储罐密度修改窗口的油品名称下拉框"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择储罐组分罐名")
    def select_tank_density_tank_name1(self, option_text):
        """选择储罐密度修改窗口的组分罐名下拉框"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('tank_name1_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择储罐乙醇罐名")
    def select_tank_density_tank_name2(self, option_text):
        """选择储罐密度修改窗口的乙醇罐名下拉框"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('tank_name2_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入储罐计重密度")
    def set_tank_weight_density(self, text):
        """输入储罐密度修改窗口的计重密度"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入储罐组分标密")
    def set_tank_standard_density1(self, text):
        """输入储罐密度修改窗口的组分标密"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('standard_density1_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入储罐乙醇标密")
    def set_tank_standard_density2(self, text):
        """输入储罐密度修改窗口的乙醇标密"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('standard_density2_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入储罐组分计密")
    def set_tank_weight_density1(self, text):
        """输入储罐密度修改窗口的组分计密"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density1_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入储罐乙醇计密")
    def set_tank_weight_density2(self, text):
        """输入储罐密度修改窗口的乙醇计密"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_density2_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入发油类型")
    def set_tank_out_oil_type(self, text):
        """输入储罐密度修改窗口的发油类型"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('out_oil_type_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("获取储罐密度表格数据")
    def get_tank_density_table(self):
        """获取储罐密度修改窗口的表格数据"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('content_table')
            if child:
                return self.get_table_data_as_json(child, None)
        return []

    @allure.step("点击储罐密度计算按钮")
    def click_tank_density_compute_button(self):
        """点击储罐密度修改窗口的计算按钮"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击储罐密度计算按钮1")
    def click_tank_density_compute_button1(self):
        """点击储罐密度修改窗口的计算按钮1"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button1')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击储罐密度计算按钮2")
    def click_tank_density_compute_button2(self):
        """点击储罐密度修改窗口的计算按钮2"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('compute_button2')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击储罐密度窗口的保存按钮")
    def click_tank_density_save_button(self):
        """点击储罐密度修改窗口的保存按钮"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击储罐密度窗口的取消按钮")
    def click_tank_density_cancel_button(self):
        """点击储罐密度修改窗口的取消按钮"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击储罐密度窗口的关闭按钮")
    def click_tank_density_close_button(self):
        """点击储罐密度修改窗口的关闭按钮"""
        element_config = self._get_element_config('tank_density_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 密度历史记录窗口方法 ====================
    @allure.step("切换到密度历史记录窗口")
    def switch_to_md_history_window(self):
        """切换到密度历史记录窗口"""
        window_config = self._get_element_config('md_history_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("选择密度历史记录的油品名称")
    def select_md_history_oil_name(self, option_text):
        """选择密度历史记录窗口的油品名称下拉框"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入密度历史记录开始时间")
    def set_md_history_start_time(self, text):
        """输入密度历史记录窗口的开始时间"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('start_time_picker')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入密度历史记录截止时间")
    def set_md_history_end_time(self, text):
        """输入密度历史记录窗口的截止时间"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('end_time_picker')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击密度历史记录查询按钮")
    def click_md_history_query_button(self):
        """点击密度历史记录窗口的查询按钮"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('query_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("获取密度历史记录表格数据")
    def get_md_history_table(self):
        """获取密度历史记录窗口的表格数据"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('content_table')
            if child:
                # 密度历史记录表头固定，使用固定表头
                history_headers = ["油品名称", "混合计重密度", "组分计密", "乙醇计密",
                                   "组分标密", "乙醇标密", "影响货位", "写入时间", "数据来源"]
                return self.get_table_data_as_json(child, history_headers)
        return []

    @allure.step("点击密度历史记录窗口的关闭按钮")
    def click_md_history_close_button(self):
        """点击密度历史记录窗口的关闭按钮"""
        element_config = self._get_element_config('md_history_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 下发到装车仪器弹窗方法 ====================
    @allure.step("切换到下发到装车仪器弹窗")
    def switch_to_send_to_device_prompt(self):
        """切换到下发到装车仪器弹窗"""
        window_config = self._get_element_config('send_to_device_prompt')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("获取下发到装车仪器的提示文本")
    def get_send_to_device_prompt_text(self):
        """获取下发到装车仪器弹窗的提示文本"""
        element_config = self._get_element_config('send_to_device_prompt')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击下发到装车仪器弹窗的确认按钮")
    def click_send_to_device_confirm_button(self):
        """点击下发到装车仪器弹窗的确认按钮"""
        element_config = self._get_element_config('send_to_device_prompt')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除确认窗口方法 ====================
    @allure.step("切换到删除确认窗口")
    def switch_to_delete_confirm_window(self):
        """切换到删除确认窗口"""
        window_config = self._get_element_config('delete_confirm_window')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("获取删除确认窗口的提示文本")
    def get_delete_confirm_prompt_text(self):
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
