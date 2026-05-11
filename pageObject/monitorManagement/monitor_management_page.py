"""
监控管理页面对象类
Monitor Management Page Object
职责：元素定位和基本交互，不包含业务逻辑
"""

import allure
from pageObject.base_page import BasePage


class MonitorManagementPage(BasePage):
    """监控管理页面 - 负责监控和远程控制操作"""

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")
        self.config = self.config_manager.load_page_config('monitor_management_page')
        if self.config is None:
            self.log.error("MonitorManagementPage: 页面配置加载失败")
            raise Exception("MonitorManagementPage: 页面配置加载失败")
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
    def switch_to_monitor_window(self):
        """切换到监控页面窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])

    def switch_to_page_window(self):
        """切换到监控页面窗口（兼容别名）"""
        return self.switch_to_monitor_window()

    # ==================== 监控页面表格操作 ====================
    @allure.step("获取待发单列表数据")
    def get_content_table(self):
        """获取监控页面待发单列表数据"""
        self.switch_to_monitor_window()
        content_table = self._get_element_config('monitor_page')
        if content_table and 'child_elements' in content_table:
            table_config = content_table['child_elements'].get('data_grid_view')
            if table_config:
                head_keys = self.app_config.get('head_keys')
                return self.get_table_data_as_json(table_config, head_keys)
        return []

    @allure.step("点击待发单列表中的行")
    def click_invoice_table_row(self, search_criteria, match_mode='exact'):
        """点击待发单列表中的指定行"""
        self.switch_to_monitor_window()
        content_table = self._get_element_config('monitor_page')
        if content_table and 'child_elements' in content_table:
            table_config = content_table['child_elements'].get('data_grid_view')
            if table_config:
                header_keywords = self.app_config.get('head_keys')
                return self.click_table_row(table_config, search_criteria, header_keywords, match_mode)
        return False

    # ==================== 货位控件操作（动态控件） ====================
    @allure.step("双击货位控件打开远程设定")
    def double_click_station_control(self, station_no):
        """
        双击指定货位号的货位控件，打开远程设定窗口

        Args:
            station_no: 货位号（如 '01', '02'）

        Returns:
            bool: 是否成功打开远程设定窗口
        """
        self.switch_to_monitor_window()
        try:
            # 查找货位控件（通过货位号标签定位）
            station_xpath = "//*[@AutomationId='CtrLoadMasterKJ']//*[@AutomationId='label4' and contains(@Name, '{station_no}')]/..".replace('{station_no}', station_no)
            station_xpath_jd = "//*[@AutomationId='CtrLoadMasterJD']//*[@AutomationId='label4' and contains(@Name, '{station_no}')]/..".replace('{station_no}', station_no)

            element = None
            try:
                element = self.driver.find_element('xpath', station_xpath)
            except Exception:
                try:
                    element = self.driver.find_element('xpath', station_xpath_jd)
                except Exception:
                    pass

            if element:
                # 双击打开远程设定
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).double_click(element).perform()
                self.log.info(f"双击货位 {station_no} 成功")
                return True
            else:
                self.log.error(f"未找到货位控件: {station_no}")
                return False

        except Exception as e:
            self.log.error(f"双击货位控件失败: {e}")
            return False

    @allure.step("获取货位控件状态信息")
    def get_station_control_status(self, station_no):
        """
        获取指定货位号的控件状态信息

        Args:
            station_no: 货位号

        Returns:
            dict: 货位状态信息
        """
        self.switch_to_monitor_window()
        status = {}
        try:
            station_xpath = "//*[@AutomationId='CtrLoadMasterKJ']//*[@AutomationId='label4' and contains(@Name, '{station_no}')]/ancestor::*[@AutomationId='CtrLoadMasterKJ']".replace('{station_no}', station_no)
            station_xpath_jd = "//*[@AutomationId='CtrLoadMasterJD']//*[@AutomationId='label4' and contains(@Name, '{station_no}')]/ancestor::*[@AutomationId='CtrLoadMasterJD']".replace('{station_no}', station_no)

            container = None
            try:
                container = self.driver.find_element('xpath', station_xpath)
            except Exception:
                try:
                    container = self.driver.find_element('xpath', station_xpath_jd)
                except Exception:
                    pass

            if container:
                labels = ['lblYCL', 'lblSZL', 'lblZFL', 'lblLS1', 'lblLS2', 'lblWD1', 'lblWD2',
                         'lblBZMD1', 'lblBZMD2', 'lblTDH', 'lblYZL', 'lblJinDu', 'lblZT', 'lblCP', 'lblYPM']
                for label_id in labels:
                    try:
                        label = container.find_element('xpath', ".//*[@AutomationId='{label_id}']".replace('{label_id}', label_id))
                        status[label_id] = label.text if label else ''
                    except Exception:
                        status[label_id] = ''

        except Exception as e:
            self.log.error(f"获取货位控件状态失败: {e}")

        return status

    # ==================== 远程设定窗口操作 ====================
    @allure.step("切换到远程设定窗口")
    def switch_to_remote_control_window(self):
        """切换到远程设定窗口"""
        window_config = self._get_element_config('remote_control_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取远程设定窗口的提单号")
    def get_remote_bill_num(self):
        """获取远程设定窗口的提单号"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('bill_num_text')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("获取远程设定窗口的计划发油量")
    def get_remote_plan_out_oil(self):
        """获取远程设定窗口的计划发油量"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('plan_out_oil_text')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("获取发油模式")
    def get_remote_load_mode(self):
        """获取远程设定窗口的发油模式"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('load_mode_combo')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("选择发油模式")
    def select_remote_load_mode(self, option_text):
        """选择远程设定窗口的发油模式"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('load_mode_combo')
                if child:
                    return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("点击启动按钮")
    def click_remote_start_button(self):
        """点击远程设定窗口的启动按钮"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('start_button')
                if child:
                    return self.click_element(**child)
        return False

    @allure.step("点击暂停按钮")
    def click_remote_pause_button(self):
        """点击远程设定窗口的暂停按钮"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('pause_button')
                if child:
                    return self.click_element(**child)
        return False

    @allure.step("点击结束按钮")
    def click_remote_end_button(self):
        """点击远程设定窗口的结束按钮"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('end_button')
                if child:
                    return self.click_element(**child)
        return False

    @allure.step("点击设定按钮")
    def click_remote_set_button(self):
        """点击远程设定窗口的设定按钮"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('set_button')
                if child:
                    return self.click_element(**child)
        return False

    @allure.step("获取远程设定窗口的百分比")
    def get_remote_percent(self):
        """获取远程设定窗口的百分比显示"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('percent_label')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("获取远程设定窗口的状态提示")
    def get_remote_status_label(self):
        """获取远程设定窗口的状态提示标签"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('status_label')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("获取远程设定窗口的启动/结束提示")
    def get_remote_start_end_label(self):
        """获取远程设定窗口的启动或结束提示"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('start_end_label')
                if child:
                    return self.get_element_text(**child)
        return ""

    @allure.step("点击远程设定窗口的关闭按钮")
    def click_remote_close_button(self):
        """点击远程设定窗口的关闭按钮"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('close_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 远程下发提单面板操作 ====================
    @allure.step("获取远程下发提单表格数据")
    def get_remote_bill_table(self):
        """获取远程下发提单面板的表格数据"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('remote下发_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('data_grid')
                if child:
                    return self.get_table_data_as_json(child, None)
        return []