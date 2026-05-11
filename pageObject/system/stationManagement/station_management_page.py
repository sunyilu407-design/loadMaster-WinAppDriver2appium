"""
货位信息管理页面对象类
Station Management Page Object
职责：元素定位和基本交互，不包含业务逻辑
"""
import allure
from pageObject.base_page import BasePage


class StationManagementPage(BasePage):
    """
    货位信息管理页面
    负责货位信息的增删改及基础参数修改等元素操作
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('station_management_page')

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
    def switch_to_station_management_window(self):
        """切换到货位信息管理窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    def switch_to_page_window(self):
        """切换到货位信息管理窗口（兼容别名）"""
        return self.switch_to_station_management_window()

    # ==================== 主页按钮点击方法 ====================
    @allure.step("点击添加货位按钮")
    def click_add_station_button(self):
        """点击添加货位按钮"""
        self.switch_to_station_management_window()
        element_config = self._get_element_config('add_station_button')
        return self.click_element(**element_config)

    @allure.step("点击修改货位按钮")
    def click_alter_station_button(self):
        """点击修改货位按钮"""
        self.switch_to_station_management_window()
        element_config = self._get_element_config('alter_station_button')
        return self.click_element(**element_config)

    @allure.step("点击删除货位按钮")
    def click_delete_station_button(self):
        """点击删除货位按钮"""
        self.switch_to_station_management_window()
        element_config = self._get_element_config('delete_station_button')
        return self.click_element(**element_config)

    @allure.step("点击修改基础参数按钮")
    def click_alter_base_param_button(self):
        """点击修改基础参数按钮"""
        self.switch_to_station_management_window()
        element_config = self._get_element_config('alter_base_param_button')
        return self.click_element(**element_config)

    # ==================== 表格操作方法 ====================
    @allure.step("获取货位信息表格数据")
    def get_content_table(self):
        """获取货位信息表格数据"""
        self.switch_to_station_management_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    @allure.step("点击表格中的货位行")
    def click_station_table_row(self, search_criteria, match_mode='exact'):
        """点击指定的货位行"""
        self.switch_to_station_management_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 添加货位窗口方法 ====================
    @allure.step("切换到添加货位窗口")
    def switch_to_add_station_window(self):
        """切换到添加货位窗口"""
        window_config = self._get_element_config('add_station_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("输入添加窗口的货位号")
    def set_add_station_no_edit(self, text):
        """输入添加窗口的货位号"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入添加窗口的货位名称")
    def set_add_station_name_edit(self, text):
        """输入添加窗口的货位名称"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择添加窗口的所属作业位")
    def select_add_work_station_combo(self, option_text):
        """选择添加窗口的所属作业位下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('work_station_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的通讯协议版本号")
    def select_add_accu_version_combo(self, option_text):
        """选择添加窗口的通讯协议版本号下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('accu_version_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的所属串口")
    def select_add_port_combo(self, option_text):
        """选择添加窗口的所属串口下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('port_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的货位状态")
    def select_add_use_state_combo(self, option_text):
        """选择添加窗口的货位状态下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('use_state_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的实发量计算公式")
    def select_add_real_calc_mode_combo(self, option_text):
        """选择添加窗口的实发量计算公式下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('real_calc_mode_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的标密设定方式")
    def select_add_density_mode_combo(self, option_text):
        """选择添加窗口的标密设定方式下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('density_mode_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的指定货位")
    def select_add_station_no_combo(self, option_text):
        """选择添加窗口的指定货位下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的乙醇标密设定方式")
    def select_add_density_mode2_combo(self, option_text):
        """选择添加窗口的乙醇标密设定方式下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('density_mode2_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的乙醇指定货位")
    def select_add_station_no2_combo(self, option_text):
        """选择添加窗口的乙醇指定货位下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no2_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的限制发油类型")
    def select_add_restrict_out_oil_type_combo(self, option_text):
        """选择添加窗口的限制发油类型下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('restrict_out_oil_type_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的阻车器AI启用")
    def select_add_zcq_ai_status_combo(self, option_text):
        """选择添加窗口的阻车器AI启用下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('zcq_ai_status_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择添加窗口的仓位识别AI启用")
    def select_add_cwsb_ai_status_combo(self, option_text):
        """选择添加窗口的仓位识别AI启用下拉框"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cwsb_ai_status_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入添加窗口的公式")
    def set_add_formula_edit(self, text):
        """输入添加窗口的公式"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('formula_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击添加货位窗口的添加按钮")
    def click_add_window_add_button(self):
        """点击添加货位窗口的添加按钮"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加货位窗口的取消按钮")
    def click_add_window_cancel_button(self):
        """点击添加货位窗口的取消按钮"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加货位窗口的关闭按钮")
    def click_add_window_close_button(self):
        """点击添加货位窗口的关闭按钮"""
        element_config = self._get_element_config('add_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改货位窗口方法 ====================
    @allure.step("切换到修改货位窗口")
    def switch_to_alter_station_window(self):
        """切换到修改货位窗口"""
        window_config = self._get_element_config('alter_station_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    # 修改窗口的子元素使用与添加窗口相同的 automation_id，可复用
    def set_alter_station_no_edit(self, text):
        """输入修改窗口的货位号"""
        return self.set_add_station_no_edit(text)

    def set_alter_station_name_edit(self, text):
        """输入修改窗口的货位名称"""
        return self.set_add_station_name_edit(text)

    def select_alter_work_station_combo(self, option_text):
        """选择修改窗口的所属作业位下拉框"""
        return self.select_add_work_station_combo(option_text)

    def select_alter_accu_version_combo(self, option_text):
        """选择修改窗口的通讯协议版本号下拉框"""
        return self.select_add_accu_version_combo(option_text)

    def select_alter_port_combo(self, option_text):
        """选择修改窗口的所属串口下拉框"""
        return self.select_add_port_combo(option_text)

    def select_alter_use_state_combo(self, option_text):
        """选择修改窗口的货位状态下拉框"""
        return self.select_add_use_state_combo(option_text)

    def select_alter_real_calc_mode_combo(self, option_text):
        """选择修改窗口的实发量计算公式下拉框"""
        return self.select_add_real_calc_mode_combo(option_text)

    def select_alter_density_mode_combo(self, option_text):
        """选择修改窗口的标密设定方式下拉框"""
        return self.select_add_density_mode_combo(option_text)

    def select_alter_station_no_combo(self, option_text):
        """选择修改窗口的指定货位下拉框"""
        return self.select_add_station_no_combo(option_text)

    def select_alter_density_mode2_combo(self, option_text):
        """选择修改窗口的乙醇标密设定方式下拉框"""
        return self.select_add_density_mode2_combo(option_text)

    def select_alter_station_no2_combo(self, option_text):
        """选择修改窗口的乙醇指定货位下拉框"""
        return self.select_add_station_no2_combo(option_text)

    def select_alter_restrict_out_oil_type_combo(self, option_text):
        """选择修改窗口的限制发油类型下拉框"""
        return self.select_add_restrict_out_oil_type_combo(option_text)

    def select_alter_zcq_ai_status_combo(self, option_text):
        """选择修改窗口的阻车器AI启用下拉框"""
        return self.select_add_zcq_ai_status_combo(option_text)

    def select_alter_cwsb_ai_status_combo(self, option_text):
        """选择修改窗口的仓位识别AI启用下拉框"""
        return self.select_add_cwsb_ai_status_combo(option_text)

    def set_alter_formula_edit(self, text):
        """输入修改窗口的公式"""
        return self.set_add_formula_edit(text)

    @allure.step("点击修改货位窗口的修改按钮")
    def click_alter_window_alter_button(self):
        """点击修改货位窗口的修改按钮"""
        element_config = self._get_element_config('alter_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('alter_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改货位窗口的取消按钮")
    def click_alter_window_cancel_button(self):
        """点击修改货位窗口的取消按钮"""
        element_config = self._get_element_config('alter_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改货位窗口的关闭按钮")
    def click_alter_window_close_button(self):
        """点击修改货位窗口的关闭按钮"""
        element_config = self._get_element_config('alter_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改基础参数窗口方法 ====================
    @allure.step("切换到修改基础参数窗口")
    def switch_to_alter_base_param_window(self):
        """切换到修改基础参数窗口"""
        window_config = self._get_element_config('alter_base_param_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("输入修改基础参数窗口的货位号")
    def set_base_param_station_no_edit(self, text):
        """输入修改基础参数窗口的货位号"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_no_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择修改基础参数窗口的油品名称")
    def select_base_param_oil_name_combo(self, option_text):
        """选择修改基础参数窗口的油品名称下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("输入修改基础参数窗口的货位名称")
    def set_base_param_station_name_edit(self, text):
        """输入修改基础参数窗口的货位名称"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_name_edit')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择修改基础参数窗口的发油方式")
    def select_base_param_out_oil_mode_combo(self, option_text):
        """选择修改基础参数窗口的发油方式下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('out_oil_mode_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择修改基础参数窗口的是否调和")
    def select_base_param_is_blend_combo(self, option_text):
        """选择修改基础参数窗口的是否调和下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('is_blend_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择修改基础参数窗口的是否启用钥匙卡")
    def select_base_param_is_enable_key_ic_card_combo(self, option_text):
        """选择修改基础参数窗口的是否启用钥匙卡下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('is_enable_key_ic_card_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择修改基础参数窗口的是否启用仓位识别")
    def select_base_param_is_enable_cw_combo(self, option_text):
        """选择修改基础参数窗口的是否启用仓位识别下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('is_enable_cw_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择修改基础参数窗口的限制发油类型")
    def select_base_param_restrict_out_oil_type_combo(self, option_text):
        """选择修改基础参数窗口的限制发油类型下拉框"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('restrict_out_oil_type_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("点击修改基础参数窗口的保存按钮")
    def click_base_param_save_button(self):
        """点击修改基础参数窗口的保存按钮"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改基础参数窗口的取消按钮")
    def click_base_param_cancel_button(self):
        """点击修改基础参数窗口的取消按钮"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改基础参数窗口的关闭按钮")
    def click_base_param_close_button(self):
        """点击修改基础参数窗口的关闭按钮"""
        element_config = self._get_element_config('alter_base_param_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除确认窗口方法 ====================
    @allure.step("切换到删除货位确认窗口")
    def switch_to_delete_station_window(self):
        """切换到删除货位确认窗口"""
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
