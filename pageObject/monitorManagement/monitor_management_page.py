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
        """切换到监控页面（右侧 panel 区域，在主窗口内）"""
        # 监控页面不是独立窗口，而是主窗口右侧的 panel 区域
        # 直接切换回主窗口即可
        return self.switch_to_window(title="装车管理系统", timeout=3)

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
    def _find_label13_by_station(self, station_no):
        """
        根据货位号，从 YAML 配置中读取 label_hw 的 automation_id，
        用 locate_elements 找到所有 label13，逐一对比 Name 找到匹配的货位。

        Args:
            station_no: 货位号

        Returns:
            WebElement: 匹配的 label13 元素，未找到返回 None
        """
        label_hw_cfg = self._get_element_config('label_hw')
        if not label_hw_cfg:
            self.log.error("未找到 label_hw 配置")
            return None

        label_hw_id = label_hw_cfg.get('automation_id', 'label13')
        elements = self.locate_elements(automation_id=label_hw_id, type='Text')
        self.log.debug(f"共找到 {len(elements)} 个 label13 元素")

        for el in elements:
            try:
                name = el.get_attribute('Name')
                if name == station_no:
                    self.log.info(f"找到货位号 {station_no} 对应的 label13")
                    return el
            except Exception:
                continue

        self.log.error(f"未找到货位号 {station_no} 对应的 label13")
        return None

    def _get_click_offset(self, element):
        """
        获取元素的中心点坐标，向下偏移一定像素。

        Returns:
            tuple: (x, y) 目标点击坐标
        """
        panel_cfg = self._get_element_config('panel_ex_remote')
        offset_y = (panel_cfg or {}).get('click_offset_y', 30)

        rect = element.rect
        center_x = rect['x'] + rect['width'] // 2
        target_y = rect['y'] + rect['height'] + offset_y
        self.log.debug(f"label13 rect: {rect}, 偏移后点击坐标: ({center_x}, {target_y})")
        return center_x, target_y

    @allure.step("双击货位控件打开远程设定")
    def double_click_station_control(self, station_no):
        """
        双击指定货位号的货位控件，打开远程设定窗口

        策略：
        1. 找到货位号对应的 label13，用其坐标筛选同组的 panelEx1
        2. 方式1（优先）：windows: click 坐标双击（appium-windows-driver 原生支持）
        3. 方式2：两次 WebElement.click()
        4. 方式3：click + ENTER

        Args:
            station_no: 货位号（如 '1', '2'）

        Returns:
            bool: 是否成功打开远程设定窗口
        """
        try:
            # 1. 找到货位号对应的 label13，用于确定货位坐标
            label_el = self._find_label13_by_station(station_no)
            if not label_el:
                return False

            label_bottom = label_el.rect['y'] + label_el.rect['height']
            label_center_x = label_el.rect['x'] + label_el.rect['width'] // 2

            # 2. 在 label13 下方区域内找 panelEx1（同组兄弟控件）
            panel_cfg = self._get_element_config('panel_ex_remote')
            panel_id = (panel_cfg or {}).get('automation_id', 'panelEx1')
            all_panels = self.locate_elements(automation_id=panel_id)
            self.log.debug(f"共找到 {len(all_panels)} 个 panelEx1")

            target_panel = None
            for panel in all_panels:
                p_rect = panel.rect
                self.log.debug(f"panelEx1 rect: {p_rect}, label13.bottom={label_bottom}")
                if p_rect['y'] >= label_bottom - 5:
                    target_panel = panel
                    self.log.info(f"找到货位 {station_no} 对应的 panelEx1: {p_rect}")
                    break

            if not target_panel:
                self.log.error(f"未找到货位 {station_no} 对应的 panelEx1")
                return False

            # 3. 方式1：windows: click（appium-windows-driver原生命令，支持坐标双击）
            try:
                x = p_rect['x'] + p_rect['width'] // 2
                y = p_rect['y'] + p_rect['height'] // 2
                # 用windows:click发两次点击，间隔50ms使系统识别为双击
                self.driver.execute_script(
                    "mobile: click",
                    {"x": x, "y": y}
                )
                import time as _time
                _time.sleep(0.05)
                self.driver.execute_script(
                    "mobile: click",
                    {"x": x, "y": y}
                )
                self.log.info(f"windows:click×2 双击货位 {station_no} 成功 (坐标: {x},{y})")
                return True
            except Exception as e1:
                self.log.warning(f"windows:click×2 失败: {e1}")

            # 4. 方式2：两次 click（Selenium WebElement API）
            try:
                target_panel.click()
                import time as _time
                _time.sleep(0.05)
                target_panel.click()
                self.log.info(f"click×2 货位 {station_no} 完成")
                return True
            except Exception as e2:
                self.log.warning(f"click×2 失败: {e2}")

            # 5. 方式3：先 click 再 send_keys ENTER
            try:
                target_panel.click()
                from selenium.webdriver.common.keys import Keys
                target_panel.send_keys(Keys.ENTER)
                self.log.info(f"click+ENTER 货位 {station_no} 完成")
                return True
            except Exception as e3:
                self.log.warning(f"click+ENTER 失败: {e3}")

            self.log.error(f"所有双击策略均失败，货位 {station_no}")
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
            # 找到 label13，再以其 rect 为基准，向下偏移定位 panelEx1 容器
            label_el = self._find_label13_by_station(station_no)
            if not label_el:
                return status

            x, y = self._get_click_offset(label_el)
            # 向下偏移区域内找 panelEx1
            panel_cfg = self._get_element_config('panel_ex_remote')
            panel_id = (panel_cfg or {}).get('automation_id', 'panelEx1')

            # 在 label13 下方区域内查找 panelEx1
            panel_xpath = (
                f"//*[@AutomationId='{panel_id}']"
                f"[@BoundingBox[. > {label_el.rect['y']}]]"
            )
            self.log.debug(f"panelEx1 查找 XPath: {panel_xpath}")

            # 尝试用相对定位：在 label13 附近找 panelEx1
            try:
                # 先找所有 panelEx1，再筛选 y 坐标大于 label13.bottom 的
                all_panels = self.locate_elements(automation_id=panel_id, type='Custom')
                label_bottom = label_el.rect['y'] + label_el.rect['height']
                for panel in all_panels:
                    p_rect = panel.rect
                    if p_rect['y'] >= label_bottom - 10:  # 允许少量误差
                        container = panel
                        self.log.debug(f"找到 panelEx1 container: {p_rect}")
                        break
                else:
                    container = None
            except Exception:
                container = None

            if container:
                label_ids = ['lblYCL', 'lblSZL', 'lblZFL', 'lblLS1', 'lblLS2', 'lblWD1', 'lblWD2',
                             'lblBZMD1', 'lblBZMD2', 'lblTDH', 'lblYZL', 'lblJinDu', 'lblZT', 'lblCP', 'lblYPM']
                for label_id in label_ids:
                    try:
                        label = container.find_element('xpath', f".//*[@AutomationId='{label_id}']")
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

    @allure.step("输入提单号")
    def set_remote_bill_num(self, bill_num):
        """向远程设定窗口的提单号输入框写入文本"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('bill_num_text')
                if child:
                    element = self.locate_element(**child)
                    if element:
                        from selenium.webdriver.common.action_chains import ActionChains
                        from selenium.webdriver.common.keys import Keys
                        # 点击聚焦 → Ctrl+A 全选 → 输入覆盖
                        ActionChains(self.driver).click(element).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(bill_num).perform()
                        self.log.info(f"已输入提单号: {bill_num}")
                        return True
        return False

    @allure.step("输入计划发油量")
    def set_remote_plan_out_oil(self, amount):
        """向远程设定窗口的计划发油量输入框写入文本"""
        element_config = self._get_element_config('remote_control_window')
        if element_config and 'child_elements' in element_config:
            panel_config = element_config['child_elements'].get('real_time_panel')
            if panel_config and 'child_elements' in panel_config:
                child = panel_config['child_elements'].get('plan_out_oil_text')
                if child:
                    element = self.locate_element(**child)
                    if element:
                        from selenium.webdriver.common.action_chains import ActionChains
                        from selenium.webdriver.common.keys import Keys
                        ActionChains(self.driver).click(element).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(amount).perform()
                        self.log.info(f"已输入计划发油量: {amount}")
                        return True
        return False

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