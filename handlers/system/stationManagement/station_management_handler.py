"""
货位信息管理业务逻辑处理类
负责货位信息管理的业务逻辑流程封装
"""
import logging
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class StationManagementHandler(BaseHandler, NavigationMixin):
    """
    货位信息管理 Handler - 业务逻辑处理类
    职责：组合 PageObject 方法实现复杂业务流

    由 SuperHandlerFactory 自动创建 - 请勿手动实例化
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
        self.station_management_page = self.page_instance

        logging.info("StationManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 业务流方法：添加货位 ====================
    @allure.step("添加货位并验证")
    def add_station_and_verify(self, station_no, station_name, work_station=None, accu_version=None,
                               port=None, use_state=None, real_calc_mode=None, density_mode=None,
                               station_no_for_density=None, density_mode2=None, station_no2=None,
                               restrict_out_oil_type=None, zcq_ai_status=None, cwsb_ai_status=None,
                               formula=None, confirm=True, timeout=10.0):
        """
        添加货位并验证结果

        Args:
            station_no: 货位号
            station_name: 货位名称
            work_station: 所属作业位（可选）
            accu_version: 通讯协议版本号（可选）
            port: 所属串口（可选）
            use_state: 货位状态（可选）
            real_calc_mode: 实发量计算公式（可选）
            density_mode: 标密设定方式（可选）
            station_no_for_density: 指定货位（可选）
            density_mode2: 乙醇标密设定方式（可选）
            station_no2: 乙醇指定货位（可选）
            restrict_out_oil_type: 限制发油类型（可选）
            zcq_ai_status: 阻车器AI启用状态（可选）
            cwsb_ai_status: 仓位识别AI启用状态（可选）
            formula: 公式（可选）
            confirm: 是否确认添加
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到货位信息管理页面
            if not self.navigate_to_station_management():
                return {'success': False, 'error': '导航到货位信息管理页面失败'}

            # 2. 点击添加货位按钮
            with allure.step("点击添加货位按钮"):
                if not self.station_management_page.click_add_station_button():
                    return {'success': False, 'error': '点击添加货位按钮失败'}

            # 3. 切换到添加货位窗口
            with allure.step("切换到添加货位窗口"):
                if not self.station_management_page.switch_to_add_station_window():
                    return {'success': False, 'error': '切换到添加货位窗口失败'}

            # 4. 填写货位信息
            with allure.step("填写货位信息"):
                if not self.station_management_page.set_add_station_no_edit(station_no):
                    return {'success': False, 'error': '输入货位号失败'}
                if not self.station_management_page.set_add_station_name_edit(station_name):
                    return {'success': False, 'error': '输入货位名称失败'}

                if work_station and not self.station_management_page.select_add_work_station_combo(work_station):
                    self.log.warning(f"选择所属作业位失败: {work_station}")
                if accu_version and not self.station_management_page.select_add_accu_version_combo(accu_version):
                    self.log.warning(f"选择通讯协议版本号失败: {accu_version}")
                if port and not self.station_management_page.select_add_port_combo(port):
                    self.log.warning(f"选择所属串口失败: {port}")
                if use_state and not self.station_management_page.select_add_use_state_combo(use_state):
                    self.log.warning(f"选择货位状态失败: {use_state}")
                if real_calc_mode and not self.station_management_page.select_add_real_calc_mode_combo(real_calc_mode):
                    self.log.warning(f"选择实发量计算公式失败: {real_calc_mode}")
                if density_mode and not self.station_management_page.select_add_density_mode_combo(density_mode):
                    self.log.warning(f"选择标密设定方式失败: {density_mode}")
                if station_no_for_density and not self.station_management_page.select_add_station_no_combo(station_no_for_density):
                    self.log.warning(f"选择指定货位失败: {station_no_for_density}")
                if density_mode2 and not self.station_management_page.select_add_density_mode2_combo(density_mode2):
                    self.log.warning(f"选择乙醇标密设定方式失败: {density_mode2}")
                if station_no2 and not self.station_management_page.select_add_station_no2_combo(station_no2):
                    self.log.warning(f"选择乙醇指定货位失败: {station_no2}")
                if restrict_out_oil_type and not self.station_management_page.select_add_restrict_out_oil_type_combo(restrict_out_oil_type):
                    self.log.warning(f"选择限制发油类型失败: {restrict_out_oil_type}")
                if zcq_ai_status and not self.station_management_page.select_add_zcq_ai_status_combo(zcq_ai_status):
                    self.log.warning(f"选择阻车器AI启用状态失败: {zcq_ai_status}")
                if cwsb_ai_status and not self.station_management_page.select_add_cwsb_ai_status_combo(cwsb_ai_status):
                    self.log.warning(f"选择仓位识别AI启用状态失败: {cwsb_ai_status}")
                if formula and not self.station_management_page.set_add_formula_edit(formula):
                    self.log.warning(f"输入公式失败: {formula}")

            # 5. 点击添加按钮
            with allure.step("点击添加窗口的添加按钮"):
                if not self.station_management_page.click_add_window_add_button():
                    return {'success': False, 'error': '点击添加按钮失败'}

            # 6. 处理确认弹窗
            with allure.step(f"处理添加确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理添加确认弹窗失败'}

            # 7. 验证结果
            with allure.step("验证添加结果"):
                if confirm:
                    return self.verify_station_in_table({'货位号': station_no}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_station_in_table({'货位号': station_no}, expected_presence='absent', timeout=timeout)

        except Exception as e:
            self.log.error(f"添加货位异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改货位 ====================
    @allure.step("修改货位并验证")
    def alter_station_and_verify(self, search_key, new_station_no=None, new_station_name=None,
                                new_work_station=None, new_accu_version=None, new_port=None,
                                new_use_state=None, new_real_calc_mode=None, new_density_mode=None,
                                new_station_no_for_density=None, new_density_mode2=None, new_station_no2=None,
                                new_restrict_out_oil_type=None, new_zcq_ai_status=None, new_cwsb_ai_status=None,
                                new_formula=None, confirm=True, timeout=10.0):
        """
        修改货位并验证结果

        Args:
            search_key: 要修改的货位搜索关键字（货位号）
            new_station_no: 新货位号（可选）
            new_station_name: 新货位名称（可选）
            new_work_station: 新所属作业位（可选）
            new_accu_version: 新通讯协议版本号（可选）
            new_port: 新所属串口（可选）
            new_use_state: 新货位状态（可选）
            new_real_calc_mode: 新实发量计算公式（可选）
            new_density_mode: 新标密设定方式（可选）
            new_station_no_for_density: 新指定货位（可选）
            new_density_mode2: 新乙醇标密设定方式（可选）
            new_station_no2: 新乙醇指定货位（可选）
            new_restrict_out_oil_type: 新限制发油类型（可选）
            new_zcq_ai_status: 新阻车器AI启用状态（可选）
            new_cwsb_ai_status: 新仓位识别AI启用状态（可选）
            new_formula: 新公式（可选）
            confirm: 是否确认修改
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到货位信息管理页面
            if not self.navigate_to_station_management():
                return {'success': False, 'error': '导航到货位信息管理页面失败'}

            # 2. 点击要修改的行
            with allure.step(f"选择要修改的货位: {search_key}"):
                if not self.station_management_page.click_station_table_row({'货位号': search_key}):
                    return {'success': False, 'error': '选择要修改的货位失败'}

            # 3. 点击修改货位按钮
            with allure.step("点击修改货位按钮"):
                if not self.station_management_page.click_alter_station_button():
                    return {'success': False, 'error': '点击修改货位按钮失败'}

            # 4. 切换到修改货位窗口
            with allure.step("切换到修改货位窗口"):
                if not self.station_management_page.switch_to_alter_station_window():
                    return {'success': False, 'error': '切换到修改货位窗口失败'}

            # 5. 修改货位信息
            with allure.step("填写修改后的货位信息"):
                if new_station_no and not self.station_management_page.set_alter_station_no_edit(new_station_no):
                    self.log.warning(f"修改货位号失败: {new_station_no}")
                if new_station_name and not self.station_management_page.set_alter_station_name_edit(new_station_name):
                    self.log.warning(f"修改货位名称失败: {new_station_name}")
                if new_work_station and not self.station_management_page.select_alter_work_station_combo(new_work_station):
                    self.log.warning(f"修改所属作业位失败: {new_work_station}")
                if new_accu_version and not self.station_management_page.select_alter_accu_version_combo(new_accu_version):
                    self.log.warning(f"修改通讯协议版本号失败: {new_accu_version}")
                if new_port and not self.station_management_page.select_alter_port_combo(new_port):
                    self.log.warning(f"修改所属串口失败: {new_port}")
                if new_use_state and not self.station_management_page.select_alter_use_state_combo(new_use_state):
                    self.log.warning(f"修改货位状态失败: {new_use_state}")
                if new_real_calc_mode and not self.station_management_page.select_alter_real_calc_mode_combo(new_real_calc_mode):
                    self.log.warning(f"修改实发量计算公式失败: {new_real_calc_mode}")
                if new_density_mode and not self.station_management_page.select_alter_density_mode_combo(new_density_mode):
                    self.log.warning(f"修改标密设定方式失败: {new_density_mode}")
                if new_station_no_for_density and not self.station_management_page.select_alter_station_no_combo(new_station_no_for_density):
                    self.log.warning(f"修改指定货位失败: {new_station_no_for_density}")
                if new_density_mode2 and not self.station_management_page.select_alter_density_mode2_combo(new_density_mode2):
                    self.log.warning(f"修改乙醇标密设定方式失败: {new_density_mode2}")
                if new_station_no2 and not self.station_management_page.select_alter_station_no2_combo(new_station_no2):
                    self.log.warning(f"修改乙醇指定货位失败: {new_station_no2}")
                if new_restrict_out_oil_type and not self.station_management_page.select_alter_restrict_out_oil_type_combo(new_restrict_out_oil_type):
                    self.log.warning(f"修改限制发油类型失败: {new_restrict_out_oil_type}")
                if new_zcq_ai_status and not self.station_management_page.select_alter_zcq_ai_status_combo(new_zcq_ai_status):
                    self.log.warning(f"修改阻车器AI启用状态失败: {new_zcq_ai_status}")
                if new_cwsb_ai_status and not self.station_management_page.select_alter_cwsb_ai_status_combo(new_cwsb_ai_status):
                    self.log.warning(f"修改仓位识别AI启用状态失败: {new_cwsb_ai_status}")
                if new_formula and not self.station_management_page.set_alter_formula_edit(new_formula):
                    self.log.warning(f"修改公式失败: {new_formula}")

            # 6. 点击修改按钮
            with allure.step("点击修改窗口的修改按钮"):
                if not self.station_management_page.click_alter_window_alter_button():
                    return {'success': False, 'error': '点击修改按钮失败'}

            # 7. 处理确认弹窗
            with allure.step(f"处理修改确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理修改确认弹窗失败'}

            # 8. 验证结果
            with allure.step("验证修改结果"):
                verify_key = new_station_no if new_station_no else search_key
                return self.verify_station_in_table({'货位号': verify_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"修改货位异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：删除货位 ====================
    @allure.step("删除货位并验证")
    def delete_station_and_verify(self, search_key, confirm=True, timeout=10.0):
        """
        删除货位并验证结果

        Args:
            search_key: 要删除的货位搜索关键字（货位号）
            confirm: 是否确认删除
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到货位信息管理页面
            if not self.navigate_to_station_management():
                return {'success': False, 'error': '导航到货位信息管理页面失败'}

            # 2. 点击要删除的行
            with allure.step(f"选择要删除的货位: {search_key}"):
                if not self.station_management_page.click_station_table_row({'货位号': search_key}):
                    return {'success': False, 'error': '选择要删除的货位失败'}

            # 3. 点击删除货位按钮
            with allure.step("点击删除货位按钮"):
                if not self.station_management_page.click_delete_station_button():
                    return {'success': False, 'error': '点击删除货位按钮失败'}

            # 4. 处理删除确认弹窗
            with allure.step(f"处理删除确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_delete_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理删除确认弹窗失败'}

            # 5. 验证结果
            with allure.step("验证删除结果"):
                if confirm:
                    return self.verify_station_in_table({'货位号': search_key}, expected_presence='absent', timeout=timeout)
                else:
                    return self.verify_station_in_table({'货位号': search_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"删除货位异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改货位基础参数 ====================
    @allure.step("修改货位基础参数并验证")
    def alter_station_base_param_and_verify(self, search_key, new_station_no=None, new_station_name=None,
                                           new_oil_name=None, new_out_oil_mode=None, new_is_blend=None,
                                           new_is_enable_key_ic_card=None, new_is_enable_cw=None,
                                           new_restrict_out_oil_type=None, confirm=True, timeout=10.0):
        """
        修改货位基础参数并验证结果

        Args:
            search_key: 要修改的货位搜索关键字（货位号）
            new_station_no: 新货位号（可选）
            new_station_name: 新货位名称（可选）
            new_oil_name: 新油品名称（可选）
            new_out_oil_mode: 新发油方式（可选）
            new_is_blend: 新是否调和（可选）
            new_is_enable_key_ic_card: 新是否启用钥匙卡（可选）
            new_is_enable_cw: 新是否启用仓位识别（可选）
            new_restrict_out_oil_type: 新限制发油类型（可选）
            confirm: 是否确认修改
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到货位信息管理页面
            if not self.navigate_to_station_management():
                return {'success': False, 'error': '导航到货位信息管理页面失败'}

            # 2. 点击要修改的行
            with allure.step(f"选择要修改基础参数的货位: {search_key}"):
                if not self.station_management_page.click_station_table_row({'货位号': search_key}):
                    return {'success': False, 'error': '选择要修改基础参数的货位失败'}

            # 3. 点击修改基础参数按钮
            with allure.step("点击修改基础参数按钮"):
                if not self.station_management_page.click_alter_base_param_button():
                    return {'success': False, 'error': '点击修改基础参数按钮失败'}

            # 4. 切换到修改基础参数窗口
            with allure.step("切换到修改基础参数窗口"):
                if not self.station_management_page.switch_to_alter_base_param_window():
                    return {'success': False, 'error': '切换到修改基础参数窗口失败'}

            # 5. 修改基础参数
            with allure.step("填写修改后的基础参数"):
                if new_station_no and not self.station_management_page.set_base_param_station_no_edit(new_station_no):
                    self.log.warning(f"修改货位号失败: {new_station_no}")
                if new_station_name and not self.station_management_page.set_base_param_station_name_edit(new_station_name):
                    self.log.warning(f"修改货位名称失败: {new_station_name}")
                if new_oil_name and not self.station_management_page.select_base_param_oil_name_combo(new_oil_name):
                    self.log.warning(f"修改油品名称失败: {new_oil_name}")
                if new_out_oil_mode and not self.station_management_page.select_base_param_out_oil_mode_combo(new_out_oil_mode):
                    self.log.warning(f"修改发油方式失败: {new_out_oil_mode}")
                if new_is_blend and not self.station_management_page.select_base_param_is_blend_combo(new_is_blend):
                    self.log.warning(f"修改是否调和失败: {new_is_blend}")
                if new_is_enable_key_ic_card and not self.station_management_page.select_base_param_is_enable_key_ic_card_combo(new_is_enable_key_ic_card):
                    self.log.warning(f"修改是否启用钥匙卡失败: {new_is_enable_key_ic_card}")
                if new_is_enable_cw and not self.station_management_page.select_base_param_is_enable_cw_combo(new_is_enable_cw):
                    self.log.warning(f"修改是否启用仓位识别失败: {new_is_enable_cw}")
                if new_restrict_out_oil_type and not self.station_management_page.select_base_param_restrict_out_oil_type_combo(new_restrict_out_oil_type):
                    self.log.warning(f"修改限制发油类型失败: {new_restrict_out_oil_type}")

            # 6. 点击保存按钮
            with allure.step("点击修改基础参数窗口的保存按钮"):
                if not self.station_management_page.click_base_param_save_button():
                    return {'success': False, 'error': '点击保存按钮失败'}

            # 7. 处理确认弹窗
            with allure.step(f"处理修改确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理修改确认弹窗失败'}

            # 8. 验证结果
            with allure.step("验证修改基础参数结果"):
                verify_key = new_station_no if new_station_no else search_key
                return self.verify_station_in_table({'货位号': verify_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"修改货位基础参数异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：查询货位 ====================
    @allure.step("查询货位")
    def query_station(self, timeout=10.0):
        """
        查询货位（获取全部货位信息）

        Args:
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        try:
            # 1. 导航到货位信息管理页面
            if not self.navigate_to_station_management():
                return {'success': False, 'error': '导航到货位信息管理页面失败'}

            # 2. 获取表格数据
            with allure.step("获取货位表格数据"):
                table_data = self.station_management_page.get_content_table()
                return {'success': True, 'data': table_data, 'count': len(table_data)}

        except Exception as e:
            self.log.error(f"查询货位异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 公共方法：处理删除确认弹窗 ====================
    def handle_delete_prompt(self, action='confirm', timeout=5.0):
        """
        删除确认弹窗处理方法

        Args:
            action: 'confirm' (是/yes) / 'cancel' (否/no) / 'quit' (退出)
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.station_management_page.switch_to_delete_station_window():
                break
            time.sleep(0.5)
        else:
            self.log.error("等待删除确认窗口超时")
            return False

        if action == 'confirm':
            return self.station_management_page.click_delete_confirm_button()
        elif action == 'cancel':
            return self.station_management_page.click_delete_cancel_button()
        elif action == 'quit':
            return self.station_management_page.click_delete_quit_button()

        self.log.error(f"未知操作: {action}")
        return False

    # ==================== 表格验证方法 ====================
    def verify_station_in_table(self, search_criteria, expected_presence='present',
                               match_mode='exact', timeout=10.0):
        """
        验证货位在表格中是否存在

        Args:
            search_criteria: 搜索条件，例如 {'货位号': '001'}
            expected_presence: 'present'（应该存在）或 'absent'（应该不存在）
            match_mode: 'exact'（精确匹配）或 'partial'（包含匹配）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'matched_rows': list,
                'total_rows': int,
                'count': int
            }
        """
        self.station_management_page.switch_to_station_management_window()

        content_table = self.station_management_page._get_element_config('content_table')
        header_keywords = self.station_management_page.app_config.get('head_keys')

        return self.station_management_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )
