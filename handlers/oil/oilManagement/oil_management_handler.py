"""
油品信息管理业务逻辑处理类
负责油品信息管理的业务逻辑流程封装
"""
import logging
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class OilManagementHandler(BaseHandler, NavigationMixin):
    """
    油品信息管理 Handler - 业务逻辑处理类
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
        self.oil_management_page = self.page_instance

        logging.info("OilManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 业务流方法：添加油品 ====================
    @allure.step("添加油品并验证")
    def add_oil_and_verify(self, short_name, name, code, oil_type=None, color=None,
                          former_name=None, confirm=True, timeout=10.0):
        """
        添加油品并验证结果

        Args:
            short_name: 油品简称
            name: 油品名称
            code: 油品编码
            oil_type: 油品类型（可选）
            color: 对应颜色（可选）
            former_name: 曾用名（可选）
            confirm: 是否确认添加
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到油品信息管理页面
            if not self.navigate_to_oil_management():
                return {'success': False, 'error': '导航到油品信息管理页面失败'}

            # 2. 点击添加按钮
            with allure.step("点击添加油品按钮"):
                if not self.oil_management_page.click_add_oil_button():
                    return {'success': False, 'error': '点击添加油品按钮失败'}

            # 3. 填写油品信息
            with allure.step("填写油品信息"):
                if not self.oil_management_page.set_oil_short_name_edit(short_name):
                    return {'success': False, 'error': '输入油品简称失败'}
                if not self.oil_management_page.set_oil_name_edit(name):
                    return {'success': False, 'error': '输入油品名称失败'}
                if not self.oil_management_page.set_oil_code_edit(code):
                    return {'success': False, 'error': '输入油品编码失败'}

                # 可选字段
                if oil_type:
                    if not self.oil_management_page.select_oil_type_combo(oil_type):
                        self.log.warning(f"选择油品类型失败: {oil_type}")
                if color:
                    if not self.oil_management_page.select_oil_color_combo(color):
                        self.log.warning(f"选择对应颜色失败: {color}")
                if former_name:
                    if not self.oil_management_page.select_oil_former_name_combo(former_name):
                        self.log.warning(f"选择曾用名失败: {former_name}")

            # 4. 处理确认弹窗
            with allure.step(f"处理添加确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理添加确认弹窗失败'}

            # 5. 验证结果
            with allure.step("验证添加结果"):
                if confirm:
                    return self.verify_oil_in_table({'油品简称': short_name}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_oil_in_table({'油品简称': short_name}, expected_presence='absent', timeout=timeout)

        except Exception as e:
            self.log.error(f"添加油品异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改油品 ====================
    @allure.step("修改油品并验证")
    def alter_oil_and_verify(self, search_key, new_short_name=None, new_name=None, new_code=None,
                             new_oil_type=None, new_color=None, new_former_name=None,
                             confirm=True, timeout=10.0):
        """
        修改油品并验证结果

        Args:
            search_key: 要修改的油品搜索关键字
            new_short_name: 新油品简称（可选）
            new_name: 新油品名称（可选）
            new_code: 新油品编码（可选）
            new_oil_type: 新油品类型（可选）
            new_color: 新对应颜色（可选）
            new_former_name: 新曾用名（可选）
            confirm: 是否确认修改
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到油品信息管理页面
            if not self.navigate_to_oil_management():
                return {'success': False, 'error': '导航到油品信息管理页面失败'}

            # 2. 点击要修改的行
            with allure.step(f"选择要修改的油品: {search_key}"):
                if not self.oil_management_page.click_table_row({'油品简称': search_key}):
                    return {'success': False, 'error': '选择要修改的油品失败'}

            # 3. 点击修改按钮
            with allure.step("点击修改油品按钮"):
                if not self.oil_management_page.click_alter_oil_button():
                    return {'success': False, 'error': '点击修改油品按钮失败'}

            # 4. 修改油品信息
            with allure.step("填写修改后的油品信息"):
                if new_short_name:
                    if not self.oil_management_page.set_alter_oil_short_name_edit(new_short_name):
                        return {'success': False, 'error': '修改油品简称失败'}
                if new_name:
                    if not self.oil_management_page.set_alter_oil_name_edit(new_name):
                        return {'success': False, 'error': '修改油品名称失败'}
                if new_code:
                    if not self.oil_management_page.set_alter_oil_code_edit(new_code):
                        return {'success': False, 'error': '修改油品编码失败'}
                if new_oil_type:
                    if not self.oil_management_page.select_alter_oil_type_combo(new_oil_type):
                        self.log.warning(f"修改油品类型失败: {new_oil_type}")
                if new_color:
                    if not self.oil_management_page.select_alter_oil_color_combo(new_color):
                        self.log.warning(f"修改对应颜色失败: {new_color}")
                if new_former_name:
                    if not self.oil_management_page.select_alter_oil_former_name_combo(new_former_name):
                        self.log.warning(f"修改曾用名失败: {new_former_name}")

            # 5. 处理确认弹窗
            with allure.step(f"处理修改确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理修改确认弹窗失败'}

            # 6. 验证结果
            with allure.step("验证修改结果"):
                if confirm and new_short_name:
                    return self.verify_oil_in_table({'油品简称': new_short_name}, expected_presence='present', timeout=timeout)
                elif confirm:
                    return self.verify_oil_in_table({'油品简称': search_key}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_oil_in_table({'油品简称': search_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"修改油品异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：删除油品 ====================
    @allure.step("删除油品并验证")
    def delete_oil_and_verify(self, search_key, confirm=True, timeout=10.0):
        """
        删除油品并验证结果

        Args:
            search_key: 要删除的油品搜索关键字
            confirm: 是否确认删除
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        try:
            # 1. 导航到油品信息管理页面
            if not self.navigate_to_oil_management():
                return {'success': False, 'error': '导航到油品信息管理页面失败'}

            # 2. 点击要删除的行
            with allure.step(f"选择要删除的油品: {search_key}"):
                if not self.oil_management_page.click_table_row({'油品简称': search_key}):
                    return {'success': False, 'error': '选择要删除的油品失败'}

            # 3. 点击删除按钮
            with allure.step("点击删除油品按钮"):
                if not self.oil_management_page.click_delete_oil_button():
                    return {'success': False, 'error': '点击删除油品按钮失败'}

            # 4. 处理删除确认弹窗
            with allure.step(f"处理删除确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_delete_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理删除确认弹窗失败'}

            # 5. 验证结果
            with allure.step("验证删除结果"):
                if confirm:
                    return self.verify_oil_in_table({'油品简称': search_key}, expected_presence='absent', timeout=timeout)
                else:
                    return self.verify_oil_in_table({'油品简称': search_key}, expected_presence='present', timeout=timeout)

        except Exception as e:
            self.log.error(f"删除油品异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：查询油品 ====================
    @allure.step("查询油品")
    def query_oil(self, search_key, timeout=10.0):
        """
        查询油品

        Args:
            search_key: 搜索关键字
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        try:
            # 1. 导航到油品信息管理页面
            if not self.navigate_to_oil_management():
                return {'success': False, 'error': '导航到油品信息管理页面失败'}

            # 2. 设置搜索条件
            with allure.step(f"设置搜索条件: {search_key}"):
                if not self.oil_management_page.set_oil_name_search(search_key):
                    return {'success': False, 'error': '设置搜索条件失败'}

            # 3. 获取表格数据
            with allure.step("获取油品表格数据"):
                table_data = self.oil_management_page.get_content_table()
                return {'success': True, 'data': table_data, 'count': len(table_data)}

        except Exception as e:
            self.log.error(f"查询油品异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 公共方法：处理删除确认弹窗 ====================
    def handle_delete_prompt(self, action='confirm', timeout=5.0):
        """
        删除确认弹窗处理方法

        Args:
            action: 'confirm' (是/yes) / 'cancel' (否/no) / 'quit' (退出) / 'all_confirm' (确认)
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        # 等待删除确认窗口
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.oil_management_page.switch_to_delete_oil_window():
                break
            time.sleep(0.5)
        else:
            self.log.error("等待删除确认窗口超时")
            return False

        if action == 'confirm':
            return self.oil_management_page.click_delete_confirm_button()
        elif action == 'cancel':
            return self.oil_management_page.click_delete_cancel_button()
        elif action == 'quit':
            return self.oil_management_page.click_delete_quit_button()
        elif action == 'all_confirm':
            return self.oil_management_page.click_delete_all_confirm_button()

        self.log.error(f"未知操作: {action}")
        return False

    # ==================== 表格验证方法 ====================
    def verify_oil_in_table(self, search_criteria, expected_presence='present',
                           match_mode='exact', timeout=10.0):
        """
        验证油品在表格中是否存在

        Args:
            search_criteria: 搜索条件，例如 {'油品简称': 'XXX'}
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
        self.oil_management_page.switch_to_page_window()

        content_table = self.oil_management_page._get_element_config('content_table')
        header_keywords = self.oil_management_page.app_config.get('head_keys')

        return self.oil_management_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )

