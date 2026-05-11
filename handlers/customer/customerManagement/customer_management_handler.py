"""
客户信息管理处理器
Customer Management Handler
职责：业务流程编排，组合PageObject方法实现复杂业务流
由 SuperHandlerFactory 自动创建 - 请勿手动实例化
"""
import logging
import time
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class CustomerManagementHandler(BaseHandler, NavigationMixin):
    """
    客户信息管理处理器
    负责客户信息的增删改查业务逻辑
    """

    def __init__(self, page_instance=None, config_manager=None):
        """
        初始化 Handler

        Args:
            page_instance: 页面对象实例（由 SuperHandlerFactory 自动提供）
            config_manager: 配置管理器实例（由 SuperHandlerFactory 自动提供）
        """
        # BaseHandler 初始化（自动依赖管理）
        super().__init__(page_instance, config_manager)

        # NavigationMixin 初始化（自动导航支持）
        NavigationMixin.__init__(self)

        # 页面对象赋值（自动创建）
        self.customer_management_page = self.page_instance

        logging.info("CustomerManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 业务方法：添加客户 ====================
    @allure.step("添加客户并验证")
    def add_customer_and_verify(self, short_name, full_name, code, link_man, link_phone,
                                 msg_phone="", msg_phone2="", is_priority="", remark="",
                                 confirm=True, timeout=5.0):
        """
        添加客户并验证结果

        Args:
            short_name: 客户简称
            full_name: 客户全称
            code: 客户编码
            link_man: 联系人
            link_phone: 联系电话
            msg_phone: 短信息号码（可选）
            msg_phone2: 短信息备用号码（可选）
            is_priority: 是否优先（可选）
            remark: 备注（可选）
            confirm: 是否确认添加
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        with allure.step(f"添加客户 (简称: {short_name}, 全称: {full_name})"):
            # 1. 导航到客户管理页面
            with allure.step("导航到客户信息管理页面"):
                if not self.navigate_to_customer_management():
                    return {'success': False, 'error': '导航到客户管理页面失败'}

            # 2. 点击添加按钮
            with allure.step("点击添加客户按钮"):
                if not self.customer_management_page.click_add_customer_button():
                    return {'success': False, 'error': '点击添加客户按钮失败'}

            # 3. 填写客户信息
            with allure.step("填写客户信息"):
                self.customer_management_page.set_customer_short_name_edit(short_name)
                self.customer_management_page.set_customer_name_edit(full_name)
                self.customer_management_page.set_customer_code_edit(code)
                self.customer_management_page.set_customer_link_man_edit(link_man)
                self.customer_management_page.set_customer_link_phone_edit(link_phone)

                if msg_phone:
                    self.customer_management_page.set_customer_message_phone_edit(msg_phone)
                if msg_phone2:
                    self.customer_management_page.set_customer_spare_message_phone_edit(msg_phone2)
                if is_priority:
                    self.customer_management_page.select_is_priority_combo(is_priority)
                if remark:
                    self.customer_management_page.set_customer_remark_edit(remark)

            # 4. 点击确定按钮
            with allure.step("点击确定按钮"):
                if not self.customer_management_page.click_add_window_add_button():
                    return {'success': False, 'error': '点击确定按钮失败'}

            # 5. 处理操作提示弹窗
            with allure.step(f"处理操作提示弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理操作提示弹窗失败'}

            # 6. 验证结果
            with allure.step("验证添加结果"):
                if confirm:
                    return self.verify_customer_in_table({'客户简称': short_name}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_customer_in_table({'客户简称': short_name}, expected_presence='absent', timeout=timeout)

    # ==================== 业务方法：修改客户 ====================
    @allure.step("修改客户并验证")
    def alter_customer_and_verify(self, search_key, new_short_name="", new_full_name="",
                                   new_code="", new_link_man="", new_link_phone="",
                                   new_msg_phone="", new_msg_phone2="", new_is_priority="",
                                   new_remark="", confirm=True, timeout=5.0):
        """
        修改客户信息并验证结果

        Args:
            search_key: 要修改的客户名称（搜索关键字）
            new_short_name: 新客户简称
            new_full_name: 新客户全称
            new_code: 新客户编码
            new_link_man: 新联系人
            new_link_phone: 新联系电话
            new_msg_phone: 新短信息号码
            new_msg_phone2: 新短信息备用号码
            new_is_priority: 新是否优先
            new_remark: 新备注
            confirm: 是否确认修改
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        with allure.step(f"修改客户 (搜索: {search_key})"):
            # 1. 导航到客户管理页面
            with allure.step("导航到客户信息管理页面"):
                if not self.navigate_to_customer_management():
                    return {'success': False, 'error': '导航到客户管理页面失败'}

            # 2. 查找并点击要修改的客户行
            with allure.step(f"查找并点击客户行: {search_key}"):
                if not self.customer_management_page.click_customer_table_row({'客户简称': search_key}):
                    return {'success': False, 'error': '查找客户行失败'}

            # 3. 点击修改按钮
            with allure.step("点击修改客户按钮"):
                if not self.customer_management_page.click_alter_customer_button():
                    return {'success': False, 'error': '点击修改客户按钮失败'}

            # 4. 填写新客户信息
            with allure.step("填写新客户信息"):
                if new_short_name:
                    self.customer_management_page.set_alter_customer_short_name_edit(new_short_name)
                if new_full_name:
                    self.customer_management_page.set_alter_customer_name_edit(new_full_name)
                if new_code:
                    self.customer_management_page.set_alter_customer_code_edit(new_code)
                if new_link_man:
                    self.customer_management_page.set_alter_customer_link_man_edit(new_link_man)
                if new_link_phone:
                    self.customer_management_page.set_alter_customer_link_phone_edit(new_link_phone)
                if new_msg_phone:
                    self.customer_management_page.set_alter_customer_message_phone_edit(new_msg_phone)
                if new_msg_phone2:
                    self.customer_management_page.set_alter_customer_spare_message_phone_edit(new_msg_phone2)
                if new_is_priority:
                    self.customer_management_page.select_alter_is_priority_combo(new_is_priority)
                if new_remark:
                    self.customer_management_page.set_alter_customer_remark_edit(new_remark)

            # 5. 点击确定按钮
            with allure.step("点击确定按钮"):
                if not self.customer_management_page.click_alter_window_add_button():
                    return {'success': False, 'error': '点击确定按钮失败'}

            # 6. 处理操作提示弹窗
            with allure.step(f"处理操作提示弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理操作提示弹窗失败'}

            # 7. 验证结果
            with allure.step("验证修改结果"):
                verify_key = new_short_name if new_short_name else search_key
                if confirm:
                    return self.verify_customer_in_table({'客户简称': verify_key}, expected_presence='present', timeout=timeout)
                else:
                    return self.verify_customer_in_table({'客户简称': search_key}, expected_presence='present', timeout=timeout)

    # ==================== 业务方法：删除客户 ====================
    @allure.step("删除客户并验证")
    def delete_customer_and_verify(self, search_key, confirm=True, timeout=5.0):
        """
        删除客户并验证结果

        Args:
            search_key: 要删除的客户名称（搜索关键字）
            confirm: 是否确认删除
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, ...}
        """
        with allure.step(f"删除客户 (搜索: {search_key})"):
            # 1. 导航到客户管理页面
            with allure.step("导航到客户信息管理页面"):
                if not self.navigate_to_customer_management():
                    return {'success': False, 'error': '导航到客户管理页面失败'}

            # 2. 查找并点击要删除的客户行
            with allure.step(f"查找并点击客户行: {search_key}"):
                if not self.customer_management_page.click_customer_table_row({'客户简称': search_key}):
                    return {'success': False, 'error': '查找客户行失败'}

            # 3. 点击删除按钮
            with allure.step("点击删除客户按钮"):
                if not self.customer_management_page.click_delete_customer_button():
                    return {'success': False, 'error': '点击删除客户按钮失败'}

            # 4. 处理删除确认弹窗
            with allure.step(f"处理删除确认弹窗 ({'确认' if confirm else '取消'})"):
                if not self.handle_delete_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                    return {'success': False, 'error': '处理删除确认弹窗失败'}

            # 5. 验证结果
            with allure.step("验证删除结果"):
                if confirm:
                    return self.verify_customer_in_table({'客户简称': search_key}, expected_presence='absent', timeout=timeout)
                else:
                    return self.verify_customer_in_table({'客户简称': search_key}, expected_presence='present', timeout=timeout)

    # ==================== 业务方法：查询客户 ====================
    @allure.step("查询客户信息")
    def query_customer(self, search_key, timeout=5.0):
        """
        查询客户信息

        Args:
            search_key: 搜索关键字
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'data': list}
        """
        with allure.step(f"查询客户 (关键字: {search_key})"):
            # 1. 导航到客户管理页面
            with allure.step("导航到客户信息管理页面"):
                if not self.navigate_to_customer_management():
                    return {'success': False, 'error': '导航到客户管理页面失败'}

            # 2. 输入搜索关键字
            with allure.step("输入搜索关键字"):
                if not self.customer_management_page.set_customer_name_search(search_key):
                    return {'success': False, 'error': '输入搜索关键字失败'}

            # 3. 获取表格数据
            with allure.step("获取表格数据"):
                table_data = self.customer_management_page.get_content_table()
                return {'success': True, 'data': table_data, 'count': len(table_data)}

    # ==================== 公共方法：验证客户在表格中 ====================
    def verify_customer_in_table(self, search_criteria, expected_presence='present',
                                  match_mode='exact', timeout=5.0):
        """
        验证客户是否在表格中

        Args:
            search_criteria: 搜索条件，如 {'客户简称': '张三'}
            expected_presence: 'present'（应该存在）或 'absent'（应该不存在）
            match_mode: 'exact'（精确匹配）或 'partial'（模糊匹配）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'matched_rows': list,
                'total_rows': int,
                'count': int
            }
        """
        self.customer_management_page.switch_to_customer_management_window()

        content_table = self.customer_management_page._get_element_config('content_table')
        header_keywords = self.customer_management_page.app_config.get('head_keys')

        return self.customer_management_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )

    # ==================== 公共方法：等待操作窗口 ====================
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待操作窗口出现"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.customer_management_page.switch_to_operation_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待操作窗口超时")
        return False

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
            if self.customer_management_page.switch_to_delete_customer_window():
                break
            time.sleep(0.5)
        else:
            self.log.error("等待删除确认窗口超时")
            return False

        if action == 'confirm':
            return self.customer_management_page.click_delete_confirm_button()
        elif action == 'cancel':
            return self.customer_management_page.click_delete_cancel_button()
        elif action == 'quit':
            return self.customer_management_page.click_delete_quit_button()
        elif action == 'all_confirm':
            return self.customer_management_page.click_delete_all_confirm_button()

        self.log.error(f"未知操作: {action}")
        return False

