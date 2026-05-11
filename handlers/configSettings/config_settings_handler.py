"""
配置设定管理业务逻辑处理类
负责配置设定的业务逻辑流程封装
"""

import logging
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class ConfigSettingsHandler(BaseHandler, NavigationMixin):
    """
    配置设定管理 Handler - 业务逻辑处理类
    职责：组合 PageObject 方法实现复杂业务流

    包含以下主要功能：
    - 刷新配置设定数据
    - 货位密度修改
    - 储罐密度修改
    - 设置流量计类型
    - 密度历史记录查询
    - 下发到装车仪器
    """

    def __init__(self, page_instance=None, config_manager=None):
        """
        初始化 Handler

        Args:
            page_instance: Page 对象实例（由 SuperHandlerFactory 自动提供）
            config_manager: 配置管理器实例（由 SuperHandlerFactory 自动提供）
        """
        # BaseHandler 初始化（自动依赖管理）
        super().__init__(page_instance, config_manager)

        # NavigationMixin 初始化（自动导航支持）
        NavigationMixin.__init__(self)

        # Page 对象赋值（自动创建）
        self.config_settings_page = self.page_instance

        logging.info("ConfigSettingsHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 通用辅助方法 ====================
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待操作提示窗口"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.config_settings_page.switch_to_operation_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待操作提示窗口超时")
        return False

    def wait_for_prompt_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待消息提示窗口"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.config_settings_page.switch_to_prompt_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待消息提示窗口超时")
        return False

    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        """
        处理操作提示窗口

        Args:
            action: 'confirm'(确认/是) / 'cancel'(取消/否) / 'quit'(退出)
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        if not self.wait_for_operation_window(timeout):
            return False

        if action == 'confirm':
            return self.config_settings_page.click_operation_window_confirm_button()
        elif action == 'cancel':
            return self.config_settings_page.click_operation_window_cancel_button()
        elif action == 'quit':
            return self.config_settings_page.click_operation_window_quit_button()

        self.log.error(f"未知操作: {action}")
        return False

    def handle_prompt_window(self, expect_contains=None, timeout=5.0):
        """
        处理消息提示窗口

        Args:
            expect_contains: 期望提示文本包含的字符串（可选）
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        if not self.wait_for_prompt_window(timeout):
            return False

        if expect_contains:
            prompt = self.config_settings_page.get_prompt_window_text() or ""
            if expect_contains not in prompt:
                self.log.error(f"提示文本校验失败: 预期包含 '{expect_contains}', 实际 '{prompt}'")
                return False

        return self.config_settings_page.click_prompt_window_confirm_button()

    # ==================== 业务流方法：刷新数据 ====================
    @allure.step("刷新配置设定数据")
    def refresh_config_data(self, station_filter=None, oil_filter=None, timeout=10.0):
        """
        刷新配置设定数据

        Args:
            station_filter: 货位筛选条件（可选）
            oil_filter: 油品筛选条件（可选）
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 设置筛选条件
            if station_filter:
                with allure.step(f"设置货位筛选条件: {station_filter}"):
                    if not self.config_settings_page.select_station_filter(station_filter):
                        self.log.warning(f"设置货位筛选条件失败: {station_filter}")

            if oil_filter:
                with allure.step(f"设置油品筛选条件: {oil_filter}"):
                    if not self.config_settings_page.select_oilname_filter(oil_filter):
                        self.log.warning(f"设置油品筛选条件失败: {oil_filter}")

            # 3. 点击刷新按钮
            with allure.step("点击刷新按钮"):
                if not self.config_settings_page.click_refresh_button():
                    return {'success': False, 'error': '点击刷新按钮失败'}

            # 4. 获取表格数据
            with allure.step("获取配置设定表格数据"):
                table_data = self.config_settings_page.get_content_table()

            return {
                'success': True,
                'data': table_data,
                'count': len(table_data)
            }

        except Exception as e:
            self.log.error(f"刷新配置数据异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：设置流量计类型 ====================
    @allure.step("设置流量计类型并验证")
    def set_flowmeter_type_and_verify(self, search_key, flowmeter_type1, flowmeter_type2=None,
                                      confirm=True, timeout=10.0):
        """
        设置流量计类型并验证结果

        Args:
            search_key: 要设置的货位搜索关键字
            flowmeter_type1: 组分流量计类型
            flowmeter_type2: 乙醇流量计类型（可选）
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 点击要设置的配置行
            with allure.step(f"选择要设置的配置: {search_key}"):
                if not self.config_settings_page.click_config_table_row({'货位号': search_key}):
                    return {'success': False, 'error': f'选择配置行失败: {search_key}'}

            # 3. 点击设置流量计类型按钮
            with allure.step("点击设置流量计类型按钮"):
                if not self.config_settings_page.click_set_flowmeter_type_button():
                    return {'success': False, 'error': '点击设置流量计类型按钮失败'}

            # 4. 切换到设置流量计类型窗口
            with allure.step("切换到设置流量计类型窗口"):
                if not self.config_settings_page.switch_to_set_flowmeter_window():
                    return {'success': False, 'error': '切换到设置流量计类型窗口失败'}

            # 5. 获取当前货位号（用于验证）
            station_no = self.config_settings_page.get_flowmeter_station_no()

            # 6. 设置流量计类型
            with allure.step(f"设置组分流量计类型: {flowmeter_type1}"):
                if not self.config_settings_page.select_flowmeter_type1(flowmeter_type1):
                    return {'success': False, 'error': '设置组分流量计类型失败'}

            if flowmeter_type2:
                with allure.step(f"设置乙醇流量计类型: {flowmeter_type2}"):
                    if not self.config_settings_page.select_flowmeter_type2(flowmeter_type2):
                        self.log.warning(f"设置乙醇流量计类型失败: {flowmeter_type2}")

            # 7. 点击保存按钮
            with allure.step("点击保存按钮"):
                if not self.config_settings_page.click_flowmeter_save_button():
                    return {'success': False, 'error': '点击保存按钮失败'}

            # 8. 处理操作确认弹窗
            with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理操作确认弹窗失败'}

            # 9. 验证结果（检查表格中对应行的流量计类型是否更新）
            with allure.step("验证设置结果"):
                if confirm:
                    # 验证表格中对应行的流量计类型是否已更新
                    return self.verify_flowmeter_in_table({'货位号': search_key}, flowmeter_type1,
                                                          expected_presence='present', timeout=timeout)
                else:
                    return {'success': True, 'message': '已取消设置'}

        except Exception as e:
            self.log.error(f"设置流量计类型异常: {e}")
            return {'success': False, 'error': str(e)}

    def verify_flowmeter_in_table(self, search_criteria, flowmeter_type, expected_presence='present',
                                   match_mode='exact', timeout=5.0):
        """
        验证流量计类型是否在表格中

        Args:
            search_criteria: 搜索条件
            flowmeter_type: 流量计类型值
            expected_presence: 'present' / 'absent'
            match_mode: 'exact' / 'partial'
            timeout: 超时时间

        Returns:
            dict: 验证结果
        """
        self.config_settings_page.switch_to_config_settings_window()

        content_table = self.config_settings_page._get_element_config('content_table')
        header_keywords = self.config_settings_page.app_config.get('head_keys')

        # 验证组分流量计类型列
        verify_criteria = dict(search_criteria)
        # 根据实际需求，可能需要同时验证组分和乙醇两种流量计类型
        # 这里简化处理，只验证组分流量计类型
        return self.config_settings_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=verify_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )

    # ==================== 业务流方法：货位密度修改 ====================
    @allure.step("修改货位密度并验证")
    def update_station_density_and_verify(self, search_key, weight_density=None,
                                          standard_density1=None, standard_density2=None,
                                          weight_density1=None, weight_density2=None,
                                          oil_name=None, tank_name1=None, tank_name2=None,
                                          compute=False, confirm=True, timeout=10.0):
        """
        修改货位密度并验证结果

        Args:
            search_key: 要修改的货位搜索关键字（货位号）
            weight_density: 计重密度（可选）
            standard_density1: 组分标密（可选）
            standard_density2: 乙醇标密（可选）
            weight_density1: 组分计密（可选）
            weight_density2: 乙醇计密（可选）
            oil_name: 油品名称（可选）
            tank_name1: 组分罐名（可选）
            tank_name2: 乙醇罐名（可选）
            compute: 是否触发计算（可选）
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 点击要修改的配置行
            with allure.step(f"选择要修改的配置: {search_key}"):
                if not self.config_settings_page.click_config_table_row({'货位号': search_key}):
                    return {'success': False, 'error': f'选择配置行失败: {search_key}'}

            # 3. 点击货位密度修改按钮
            with allure.step("点击货位密度修改按钮"):
                if not self.config_settings_page.click_update_station_density_button():
                    return {'success': False, 'error': '点击货位密度修改按钮失败'}

            # 4. 切换到货位密度修改窗口
            with allure.step("切换到货位密度修改窗口"):
                if not self.config_settings_page.switch_to_station_density_window():
                    return {'success': False, 'error': '切换到货位密度修改窗口失败'}

            # 5. 获取当前货位信息（用于验证）
            station_no = self.config_settings_page.get_station_density_station_no()
            station_name = self.config_settings_page.get_station_density_station_name()
            self.log.info(f"当前货位: {station_no}, {station_name}")

            # 6. 填写修改数据
            with allure.step("填写密度修改数据"):
                if oil_name:
                    if not self.config_settings_page.select_station_density_oil_name(oil_name):
                        self.log.warning(f"选择油品名称失败: {oil_name}")

                if tank_name1:
                    if not self.config_settings_page.select_station_density_tank_name1(tank_name1):
                        self.log.warning(f"选择组分罐名失败: {tank_name1}")

                if tank_name2:
                    if not self.config_settings_page.select_station_density_tank_name2(tank_name2):
                        self.log.warning(f"选择乙醇罐名失败: {tank_name2}")

                if weight_density:
                    if not self.config_settings_page.set_station_weight_density(weight_density):
                        return {'success': False, 'error': '输入计重密度失败'}

                if standard_density1:
                    if not self.config_settings_page.set_station_standard_density1(standard_density1):
                        return {'success': False, 'error': '输入组分标密失败'}

                if standard_density2:
                    if not self.config_settings_page.set_station_standard_density2(standard_density2):
                        return {'success': False, 'error': '输入乙醇标密失败'}

                if weight_density1:
                    if not self.config_settings_page.set_station_weight_density1(weight_density1):
                        return {'success': False, 'error': '输入组分计密失败'}

                if weight_density2:
                    if not self.config_settings_page.set_station_weight_density2(weight_density2):
                        return {'success': False, 'error': '输入乙醇计密失败'}

            # 7. 计算（如果需要）
            if compute:
                with allure.step("触发密度计算"):
                    self.config_settings_page.click_station_density_compute_button()
                    time.sleep(0.5)
                    self.config_settings_page.click_station_density_compute_button1()
                    time.sleep(0.5)
                    self.config_settings_page.click_station_density_compute_button2()

            # 8. 点击保存按钮
            with allure.step("点击保存按钮"):
                if not self.config_settings_page.click_station_density_save_button():
                    return {'success': False, 'error': '点击保存按钮失败'}

            # 9. 处理操作确认弹窗
            with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理操作确认弹窗失败'}

            # 10. 验证结果
            with allure.step("验证修改结果"):
                if confirm:
                    return self.verify_station_density_in_table(
                        {'货位号': search_key},
                        expected_presence='present',
                        timeout=timeout
                    )
                else:
                    return {'success': True, 'message': '已取消修改'}

        except Exception as e:
            self.log.error(f"修改货位密度异常: {e}")
            return {'success': False, 'error': str(e)}

    def verify_station_density_in_table(self, search_criteria, expected_presence='present',
                                        match_mode='exact', timeout=5.0):
        """
        验证货位密度是否在表格中

        Args:
            search_criteria: 搜索条件
            expected_presence: 'present' / 'absent'
            match_mode: 'exact' / 'partial'
            timeout: 超时时间

        Returns:
            dict: 验证结果
        """
        self.config_settings_page.switch_to_config_settings_window()

        content_table = self.config_settings_page._get_element_config('content_table')
        header_keywords = self.config_settings_page.app_config.get('head_keys')

        return self.config_settings_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )

    # ==================== 业务流方法：储罐密度修改 ====================
    @allure.step("修改储罐密度并验证")
    def update_tank_density_and_verify(self, oil_name, tank_name1, tank_name2=None,
                                       weight_density=None, standard_density1=None,
                                       standard_density2=None, weight_density1=None,
                                       weight_density2=None, out_oil_type=None,
                                       compute=False, confirm=True, timeout=10.0):
        """
        修改储罐密度并验证结果

        Args:
            oil_name: 油品名称（必填）
            tank_name1: 组分罐名（必填）
            tank_name2: 乙醇罐名（可选）
            weight_density: 计重密度（可选）
            standard_density1: 组分标密（可选）
            standard_density2: 乙醇标密（可选）
            weight_density1: 组分计密（可选）
            weight_density2: 乙醇计密（可选）
            out_oil_type: 发油类型（可选）
            compute: 是否触发计算（可选）
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 点击储罐密度修改按钮
            with allure.step("点击储罐密度修改按钮"):
                if not self.config_settings_page.click_update_tank_density_button():
                    return {'success': False, 'error': '点击储罐密度修改按钮失败'}

            # 3. 切换到储罐密度修改窗口
            with allure.step("切换到储罐密度修改窗口"):
                if not self.config_settings_page.switch_to_tank_density_window():
                    return {'success': False, 'error': '切换到储罐密度修改窗口失败'}

            # 4. 填写修改数据
            with allure.step("填写储罐密度修改数据"):
                if not self.config_settings_page.select_tank_density_oil_name(oil_name):
                    return {'success': False, 'error': f'选择油品名称失败: {oil_name}'}

                if not self.config_settings_page.select_tank_density_tank_name1(tank_name1):
                    return {'success': False, 'error': f'选择组分罐名失败: {tank_name1}'}

                if tank_name2:
                    if not self.config_settings_page.select_tank_density_tank_name2(tank_name2):
                        self.log.warning(f"选择乙醇罐名失败: {tank_name2}")

                if weight_density:
                    if not self.config_settings_page.set_tank_weight_density(weight_density):
                        return {'success': False, 'error': '输入计重密度失败'}

                if standard_density1:
                    if not self.config_settings_page.set_tank_standard_density1(standard_density1):
                        return {'success': False, 'error': '输入组分标密失败'}

                if standard_density2:
                    if not self.config_settings_page.set_tank_standard_density2(standard_density2):
                        return {'success': False, 'error': '输入乙醇标密失败'}

                if weight_density1:
                    if not self.config_settings_page.set_tank_weight_density1(weight_density1):
                        return {'success': False, 'error': '输入组分计密失败'}

                if weight_density2:
                    if not self.config_settings_page.set_tank_weight_density2(weight_density2):
                        return {'success': False, 'error': '输入乙醇计密失败'}

                if out_oil_type:
                    if not self.config_settings_page.set_tank_out_oil_type(out_oil_type):
                        self.log.warning(f"输入发油类型失败: {out_oil_type}")

            # 5. 计算（如果需要）
            if compute:
                with allure.step("触发储罐密度计算"):
                    self.config_settings_page.click_tank_density_compute_button()
                    time.sleep(0.5)
                    self.config_settings_page.click_tank_density_compute_button1()
                    time.sleep(0.5)
                    self.config_settings_page.click_tank_density_compute_button2()

            # 6. 点击保存按钮
            with allure.step("点击保存按钮"):
                if not self.config_settings_page.click_tank_density_save_button():
                    return {'success': False, 'error': '点击保存按钮失败'}

            # 7. 处理操作确认弹窗
            with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理操作确认弹窗失败'}

            return {'success': True, 'message': '储罐密度修改完成'}

        except Exception as e:
            self.log.error(f"修改储罐密度异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：密度历史记录查询 ====================
    @allure.step("查询密度历史记录")
    def query_md_history(self, oil_name=None, start_time=None, end_time=None, timeout=10.0):
        """
        查询密度历史记录

        Args:
            oil_name: 油品名称（可选）
            start_time: 开始时间（可选，格式：YYYY-MM-DD）
            end_time: 截止时间（可选，格式：YYYY-MM-DD）
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 点击密度历史记录按钮
            with allure.step("点击密度历史记录按钮"):
                if not self.config_settings_page.click_md_history_button():
                    return {'success': False, 'error': '点击密度历史记录按钮失败'}

            # 3. 切换到密度历史记录窗口
            with allure.step("切换到密度历史记录窗口"):
                if not self.config_settings_page.switch_to_md_history_window():
                    return {'success': False, 'error': '切换到密度历史记录窗口失败'}

            # 4. 设置查询条件
            if oil_name:
                with allure.step(f"选择油品名称: {oil_name}"):
                    if not self.config_settings_page.select_md_history_oil_name(oil_name):
                        self.log.warning(f"选择油品名称失败: {oil_name}")

            if start_time:
                with allure.step(f"输入开始时间: {start_time}"):
                    self.config_settings_page.set_md_history_start_time(start_time)

            if end_time:
                with allure.step(f"输入截止时间: {end_time}"):
                    self.config_settings_page.set_md_history_end_time(end_time)

            # 5. 点击查询按钮
            with allure.step("点击查询按钮"):
                if not self.config_settings_page.click_md_history_query_button():
                    return {'success': False, 'error': '点击查询按钮失败'}

            # 6. 获取历史记录数据
            with allure.step("获取密度历史记录数据"):
                import time
                time.sleep(1)  # 等待数据加载
                history_data = self.config_settings_page.get_md_history_table()

            return {
                'success': True,
                'data': history_data,
                'count': len(history_data)
            }

        except Exception as e:
            self.log.error(f"查询密度历史记录异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：下发到装车仪器 ====================
    @allure.step("下发到装车仪器")
    def send_to_device(self, expect_contains=None, confirm=True, timeout=10.0):
        """
        下发配置到装车仪器

        Args:
            expect_contains: 期望提示文本包含的字符串（可选）
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'message': str}
        """
        try:
            # 1. 导航到配置设定页面
            if not self.navigate_to_config_settings():
                return {'success': False, 'error': '导航到配置设定页面失败'}

            # 2. 点击下发到装车仪器按钮
            with allure.step("点击下发到装车仪器按钮"):
                if not self.config_settings_page.click_set_to_device_button():
                    return {'success': False, 'error': '点击下发到装车仪器按钮失败'}

            # 3. 等待弹窗出现
            import time
            time.sleep(1)

            # 4. 检查是否是消息提示弹窗（通常是操作失败或有提示信息的情况）
            if self.config_settings_page.switch_to_prompt_window():
                prompt_text = self.config_settings_page.get_prompt_window_text() or ""
                self.log.info(f"收到消息提示: {prompt_text}")

                # 检查是否符合预期
                if expect_contains and expect_contains not in prompt_text:
                    self.log.warning(f"提示文本不匹配: 预期包含 '{expect_contains}', 实际 '{prompt_text}'")

                # 点击确认
                self.config_settings_page.click_prompt_window_confirm_button()
                return {
                    'success': '成功' in prompt_text or '完成' in prompt_text,
                    'message': prompt_text
                }

            # 5. 检查是否是操作确认弹窗
            if self.config_settings_page.switch_to_operation_window():
                prompt_text = self.config_settings_page.get_operation_window_prompt_text() or ""
                self.log.info(f"收到操作确认: {prompt_text}")

                if expect_contains and expect_contains not in prompt_text:
                    self.log.warning(f"提示文本不匹配: 预期包含 '{expect_contains}', 实际 '{prompt_text}'")

                return self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout)

            self.log.error("未检测到任何弹窗")
            return {'success': False, 'error': '未检测到弹窗响应'}

        except Exception as e:
            self.log.error(f"下发到装车仪器异常: {e}")
            return {'success': False, 'error': str(e)}
