"""
串口信息管理业务逻辑处理类
负责串口信息管理的业务逻辑流程封装
"""
import logging
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class PortManagementHandler(BaseHandler, NavigationMixin):
    """
    串口信息管理 Handler - 业务逻辑处理类
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
        self.port_management_page = self.page_instance

        logging.info("PortManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 业务流方法：添加串口 ====================
    @allure.step("添加串口并验证")
    def add_port_and_verify(self, port_name, baudrate, port_type=None, remark=None,
                           confirm=True, timeout=10.0):
        """
        添加串口并验证结果

        Args:
            port_name: 串口名称（如 COM1、COM2 等）
            baudrate: 波特率（如 9600、19200 等）
            port_type: 串口类型（可选，如地磅串口、读卡器串口等）
            remark: 备注（可选）
            confirm: 是否确认添加
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到串口信息管理页面
            if not self.navigate_to_serial_port_management():
                return {'success': False, 'error': '导航到串口信息管理页面失败'}

            # 2. 点击添加按钮
            with allure.step("点击添加串口按钮"):
                if not self.port_management_page.click_add_port_button():
                    return {'success': False, 'error': '点击添加串口按钮失败'}

            # 3. 切换到添加串口窗口
            with allure.step("切换到添加串口窗口"):
                if not self.port_management_page.switch_to_add_port_window():
                    return {'success': False, 'error': '切换到添加串口窗口失败'}

            # 4. 填写串口信息
            with allure.step("填写串口信息"):
                if not self.port_management_page.select_add_portname_combo(port_name):
                    return {'success': False, 'error': '选择串口名称失败'}
                if not self.port_management_page.select_add_baudrate_combo(baudrate):
                    return {'success': False, 'error': '选择波特率失败'}
                if port_type:
                    if not self.port_management_page.select_add_porttype_combo(port_type):
                        self.log.warning(f"选择串口类型失败: {port_type}")
                if remark:
                    if not self.port_management_page.set_add_remark_edit(remark):
                        self.log.warning(f"输入备注失败: {remark}")

            # 5. 点击添加按钮
            with allure.step("点击添加窗口的添加按钮"):
                if not self.port_management_page.click_add_window_add_button():
                    return {'success': False, 'error': '点击添加按钮失败'}

            # 6. 处理确认弹窗
            with allure.step(f"处理添加确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理添加确认弹窗失败'}

            # 7. 验证结果
            with allure.step("验证添加结果"):
                if confirm:
                    return self.verify_port_in_table({'串口名称': port_name}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_port_in_table({'串口名称': port_name}, expected_presence='absent', timeout=timeout)

        except Exception as e:
            self.log.error(f"添加串口异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改串口 ====================
    @allure.step("修改串口并验证")
    def alter_port_and_verify(self, search_key, new_port_name=None, new_baudrate=None,
                              new_port_type=None, new_remark=None,
                              confirm=True, timeout=10.0):
        """
        修改串口并验证结果

        Args:
            search_key: 要修改的串口搜索关键字（串口名称）
            new_port_name: 新串口名称（可选）
            new_baudrate: 新波特率（可选）
            new_port_type: 新串口类型（可选）
            new_remark: 新备注（可选）
            confirm: 是否确认修改
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到串口信息管理页面
            if not self.navigate_to_serial_port_management():
                return {'success': False, 'error': '导航到串口信息管理页面失败'}

            # 2. 点击要修改的行
            with allure.step(f"选择要修改的串口: {search_key}"):
                if not self.port_management_page.click_port_table_row({'串口名称': search_key}):
                    return {'success': False, 'error': '选择要修改的串口失败'}

            # 3. 点击修改按钮
            with allure.step("点击修改串口按钮"):
                if not self.port_management_page.click_alter_port_button():
                    return {'success': False, 'error': '点击修改串口按钮失败'}

            # 4. 切换到修改串口窗口
            with allure.step("切换到修改串口窗口"):
                if not self.port_management_page.switch_to_alter_port_window():
                    return {'success': False, 'error': '切换到修改串口窗口失败'}

            # 5. 修改串口信息
            with allure.step("填写修改后的串口信息"):
                if new_port_name:
                    if not self.port_management_page.select_alter_portname_combo(new_port_name):
                        self.log.warning(f"修改串口名称失败: {new_port_name}")
                if new_baudrate:
                    if not self.port_management_page.select_alter_baudrate_combo(new_baudrate):
                        self.log.warning(f"修改波特率失败: {new_baudrate}")
                if new_port_type:
                    if not self.port_management_page.select_alter_porttype_combo(new_port_type):
                        self.log.warning(f"修改串口类型失败: {new_port_type}")
                if new_remark is not None:
                    if not self.port_management_page.set_alter_remark_edit(new_remark):
                        self.log.warning(f"修改备注失败: {new_remark}")

            # 6. 点击修改按钮
            with allure.step("点击修改窗口的修改按钮"):
                if not self.port_management_page.click_alter_window_alter_button():
                    return {'success': False, 'error': '点击修改按钮失败'}

            # 7. 处理确认弹窗
            with allure.step(f"处理修改确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理修改确认弹窗失败'}

            # 8. 验证结果
            with allure.step("验证修改结果"):
                verify_key = new_port_name if new_port_name else search_key
                return self.verify_port_in_table({'串口名称': verify_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"修改串口异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：删除串口 ====================
    @allure.step("删除串口并验证")
    def delete_port_and_verify(self, search_key, confirm=True, timeout=10.0):
        """
        删除串口并验证结果

        Args:
            search_key: 要删除的串口搜索关键字（串口名称）
            confirm: 是否确认删除
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到串口信息管理页面
            if not self.navigate_to_serial_port_management():
                return {'success': False, 'error': '导航到串口信息管理页面失败'}

            # 2. 点击要删除的行
            with allure.step(f"选择要删除的串口: {search_key}"):
                if not self.port_management_page.click_port_table_row({'串口名称': search_key}):
                    return {'success': False, 'error': '选择要删除的串口失败'}

            # 3. 点击删除按钮
            with allure.step("点击删除串口按钮"):
                if not self.port_management_page.click_delete_port_button():
                    return {'success': False, 'error': '点击删除串口按钮失败'}

            # 4. 处理删除确认弹窗
            with allure.step(f"处理删除确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_delete_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理删除确认弹窗失败'}

            # 5. 验证结果
            with allure.step("验证删除结果"):
                if confirm:
                    return self.verify_port_in_table({'串口名称': search_key}, expected_presence='absent', timeout=timeout)
                else:
                    return self.verify_port_in_table({'串口名称': search_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"删除串口异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：查询串口 ====================
    @allure.step("查询串口")
    def query_port(self, timeout=10.0):
        """
        查询串口（获取全部串口信息）

        Args:
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        try:
            # 1. 导航到串口信息管理页面
            if not self.navigate_to_serial_port_management():
                return {'success': False, 'error': '导航到串口信息管理页面失败'}

            # 2. 获取表格数据
            with allure.step("获取串口表格数据"):
                table_data = self.port_management_page.get_content_table()
                return {'success': True, 'data': table_data, 'count': len(table_data)}

        except Exception as e:
            self.log.error(f"查询串口异常: {e}")
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
            if self.port_management_page.switch_to_delete_port_window():
                break
            time.sleep(0.5)
        else:
            self.log.error("等待删除确认窗口超时")
            return False

        if action == 'confirm':
            return self.port_management_page.click_delete_confirm_button()
        elif action == 'cancel':
            return self.port_management_page.click_delete_cancel_button()
        elif action == 'quit':
            return self.port_management_page.click_delete_quit_button()

        self.log.error(f"未知操作: {action}")
        return False

    # ==================== 表格验证方法 ====================
    def verify_port_in_table(self, search_criteria, expected_presence='present',
                            match_mode='exact', timeout=10.0):
        """
        验证串口在表格中是否存在

        Args:
            search_criteria: 搜索条件，例如 {'串口名称': 'COM1'}
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
        self.port_management_page.switch_to_port_management_window()

        content_table = self.port_management_page._get_element_config('content_table')
        header_keywords = self.port_management_page.app_config.get('head_keys')

        return self.port_management_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )
