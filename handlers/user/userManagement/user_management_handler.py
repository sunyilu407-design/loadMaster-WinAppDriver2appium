"""
用户管理Handler - 业务逻辑处理
组合页面操作实现复杂的业务逻辑
"""

import logging
import time
import allure

from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class UserManagementHandler(BaseHandler, NavigationMixin):
    """
    用户信息管理Handler - 业务逻辑处理类

    页面状态管理机制：
    - 页面对象初始化和用户信息管理页面导航只执行一次
    - 所有业务方法（添加、删除、查询）共享同一个页面会话
    - 适用于批量自动化操作场景，避免重复页面切换

    使用模式：
    1. handler = UserManagementHandler()
    2. handler.add_user_and_verify(...)  # 自动处理页面准备
    3. handler.delete_user_and_verify(...)  # 复用已准备的页面
    4. handler.verify_user_in_table(...)  # 继续使用同一页面
    """
    def __init__(self, page_instance=None, config_manager=None):
        """初始化用户信息管理处理器"""
        super().__init__(page_instance, config_manager)
        # 初始化NavigationMixin
        NavigationMixin.__init__(self)

        # 赋值页面对象（自动创建）
        self.user_management_page = self.page_instance

        # 页面状态跟踪
        self._page_initialized = False
        self._navigated_to_user_management = False

        logging.info("用户信息管理处理器初始化完成")

    def _create_page_instance(self, config_manager):
        """
        创建用户信息管理页面对象实例

        Args:
            config_manager: 配置管理器

        Returns:
            UserManagementPage: 用户信息管理页面对象实例
        """
        from pageObject.user.userManagement.user_management_page import UserManagementPage
        from utils.driver_factory import DriverFactory

        # 获取驱动实例
        driver = DriverFactory.get_windows_driver()
        if driver is None:
            raise Exception("无法获取Windows驱动实例")

        # 创建用户信息管理页面对象
        return UserManagementPage(driver, config_manager)

    def _ensure_page_ready(self):
        """
        确保用户信息管理页面已准备就绪
        包括页面对象初始化、导航到用户管理页面、切换到用户信息管理窗口
        """
        try:
            # 1. 确保页面对象已初始化
            if not self._page_initialized:
                self._initialize_page_objects()
                self._page_initialized = True
                self.log.info("✅ 页面对象初始化完成")

            # 2. 确保已导航到用户管理页面
            if not self._navigated_to_user_management:
                self._navigate_to_user_management_page()
                self._navigated_to_user_management = True
                self.log.info("✅ 已导航到用户信息管理页面")

        except Exception as e:
            self.log.error(f"页面准备失败: {e}")
            raise

    def _initialize_page_objects(self):
        """初始化页面相关对象"""
        # 确保页面对象可用
        if self.user_management_page is None:
            raise Exception("用户信息管理页面对象未初始化")

        # 确保驱动可用
        if not hasattr(self.user_management_page, 'driver') or self.user_management_page.driver is None:
            raise Exception("页面驱动未初始化")

        self.log.info("页面对象初始化检查通过")

    def _navigate_to_user_management_page(self):
        """
        导航到用户信息管理页面并切换窗口
        """
        # 1. 检查是否在主页面
        if not self.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到用户信息管理")

        # 2. 导航到用户信息管理页面
        if not self.navigate_to_user_info_management():
            raise Exception("导航到用户信息管理页面失败")

        # 3. 切换到用户信息管理窗口
        self.user_management_page.switch_to_user_info_management_window()

        # 4. 等待页面完全加载
        time.sleep(1)

        self.log.info("✅ 成功导航并切换到用户信息管理页面")

    def is_user_management_page_ready(self):
        """
        检查用户信息管理页面是否已准备就绪
        """
        return self._page_initialized and self._navigated_to_user_management

    def reset_page_state(self):
        """
        重置页面状态，用于重新初始化页面
        """
        self._page_initialized = False
        self._navigated_to_user_management = False
        self.log.info("页面状态已重置")

    def ensure_user_management_ready(self):
        """
        公开方法：确保用户信息管理页面已准备就绪
        供外部调用或测试使用
        """
        self._ensure_page_ready()
        return True


    # 表格查询与校验（新增/修改/删除后的验证），复用 BasePage 的通用方法
    def verify_user_in_table(self, search_criteria: dict, expected_presence: str = 'present',
                             match_mode: str = 'exact', min_count: int = 1,
                             timeout: float = 5.0, poll_interval: float = 0.5) -> dict:
        """验证用户是否在表格中，支持存在/不存在与精确/包含匹配
        return  'success': bool,                # 是否满足预期
                'matched_rows': list,           # 匹配到的行（JSON 格式，每行是表头->值的字典）
                'total_rows': int,              # 表格总行数（有效数据行）
                'count': int,                   # 匹配到的行数
                'expected_presence': str,       # 预期结果（present/absent）
        """

        self._ensure_page_ready()

        content_table = self.user_management_page._get_element_config('content_table')
        header_keywords = (self.user_management_page.app_config or {}).get('head_keys', None)

        return self.user_management_page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            min_count=min_count,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    # 示例：添加用户并校验（不修改现有add_user，新增一个流程封装）
    def add_user_and_verify(self, username: str, usertype: str, remark: str, affiliated_system: list,
                            confirm: bool = True, confirm_operation: bool = True,
                            timeout: float = 5.0) -> dict:
        """
        添加用户→处理操作提示弹窗→校验表格中用户是否存在

        Args:
            username: 用户名
            usertype: 用户类型
            remark: 备注
            affiliated_system: 所属系统列表
            confirm: 是否点击添加窗口的确认按钮（True=确认提交，False=取消不提交）
            confirm_operation: 是否点击operation_window的"是"按钮（True=是，False=否）
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'matched_rows': list, 'total_rows': int, 'count': int}
        """
        with allure.step(f"添加用户并验证 (用户名: {username}, 确认提交: {confirm}, operation确认: {confirm_operation})"):
            try:
                # 确保用户信息管理页面已准备就绪
                with allure.step("准备用户信息管理页面"):
                    self._ensure_page_ready()

                # 执行添加用户操作
                with allure.step("填写用户信息表单"):
                    # 按既有风格调用页面方法
                    self.user_management_page.click_add_user_button()
                    #切换到添加用户窗体
                    self.user_management_page.switch_to_add_user_window()
                    #填写用户信息
                    self.user_management_page.set_user_name_edit(username)
                    self.user_management_page.select_user_type(usertype)
                    self.user_management_page.set_remark_edit(remark)
                    self.user_management_page.check_add_user_affiliated_system_tree_with_space_key(affiliated_system)

                # 处理添加窗口的确认/取消按钮
                with allure.step(f"处理添加窗口 ({'确认' if confirm else '取消'})"):
                    if confirm:
                        self.user_management_page.click_add_window_add_button()
                    else:
                        self.user_management_page.click_add_window_cancel_button()

                # 如果取消了添加，验证用户不存在
                if not confirm:
                    with allure.step("切换到用户信息管理窗口"):
                        self.user_management_page.switch_to_user_info_management_window()
                    with allure.step("验证用户未添加（已取消）"):
                        return self.verify_user_in_table({"用户姓名": username}, expected_presence='absent',
                                                         match_mode='exact', timeout=timeout)

                # 处理operation_window（是/否按钮）
                # 添加用户只有操作提示窗体
                with allure.step(f"处理操作提示窗口 (confirm_operation={confirm_operation})"):

                    if not self.handle_operation_prompt(
                            confirm_operation=confirm_operation, timeout=timeout):
                        logging.error(f"❌ 处理操作提示窗口异常:")
                        return {
                            'success': False,
                            'error': '处理操作提示弹窗失败'

                        }

                with allure.step("切换到用户信息管理窗口"):
                    #切换到用户信息管理窗口
                    self.user_management_page.switch_to_user_info_management_window()

                # 校验表格结果（确认操作提示则验证存在，取消则验证不存在）
                expected_presence = 'present' if confirm_operation else 'absent'
                with allure.step(f"验证用户是否添加成功 (期望存在: {expected_presence})"):
                    return self.verify_user_in_table({"用户姓名": username}, expected_presence=expected_presence,
                                                     match_mode='exact', timeout=timeout)

            except Exception as e:
                error_msg = f"添加用户操作异常: {str(e)}"
                self.log.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'matched_rows': [],
                    'total_rows': 0,
                    'count': 0
                }

    # 示例：删除用户并校验
    def delete_user_and_verify(self, username: str, confirm: bool = True,
                               confirm_operation: bool = True, confirm_prompt: bool = True,
                               timeout: float = 5.0) -> dict:
        """
        删除用户后进行校验：确认后应不存在；取消后仍存在

        Args:
            username: 用户名
            confirm: 是否点击删除确认窗口的"是"按钮（True=确认删除，False=取消不删除）
            confirm_operation: 是否点击operation_window的"是"按钮（True=是，False=否）
            confirm_prompt: 是否点击prompt_window的"确认"按钮（True=确认，False=跳过）
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'matched_rows': list, 'total_rows': int, 'count': int}
        """
        try:
            # 确保用户信息管理页面已准备就绪
            self._ensure_page_ready()

            # 步骤1: 在表格中点击指定用户行（选中要删除的用户）
            self.log.info(f"开始删除用户: {username}")
            if not self.user_management_page.click_table_one_row({'用户姓名': username}):
                return {
                    'success': False,
                    'error': f'未找到用户: {username}'
                }

            # 步骤2: 执行删除用户操作
            if not self.user_management_page.click_delete_user_button():
                return {
                    'success': False,
                    'error': '点击删除按钮失败'
                }

            # 步骤3: 处理operation_window（是/否按钮）
            if not self.user_management_page.handle_operation_prompt(confirm_operation=confirm_operation, timeout=timeout):
                return {
                    'success': False,
                    'error': '处理操作提示弹窗失败'
                }

            # 步骤2: 如果确认删除，处理prompt_window（确认按钮）
            if confirm_operation:
                if not self.user_management_page.handle_prompt_window(confirm_prompt=confirm_prompt, timeout=timeout):
                    return {
                        'success': False,
                        'error': '处理消息提示弹窗失败'
                    }

            expected = 'absent' if confirm_operation else 'present'
            return self.verify_user_in_table({"用户姓名": username}, expected_presence=expected,
                                             match_mode='exact', timeout=timeout)

        except Exception as e:
            error_msg = f"删除用户操作异常: {str(e)}"
            self.log.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'matched_rows': [],
                'total_rows': 0,
                'count': 0
            }


    # ========== 修改用户并验证方法 ==========
    def alter_user_and_verify(self, old_username: str, new_username: str = None,
                              new_usertype: str = None, new_remark: str = None,
                              new_affiliated_system: list = None, confirm: bool = True,
                              confirm_prompt: bool = True, timeout: float = 5.0) -> dict:
        """
        修改用户并验证

        Args:
            old_username: 原用户名（用于查找表格中的用户）
            new_username: 新用户名（如果需要修改用户名）
            new_usertype: 新用户类型（如"管理员"、"操作员"等）
            new_remark: 新备注
            new_affiliated_system: 新所属系统列表
            confirm: 是否点击修改窗口的确认按钮（True=确认提交，False=取消不提交）
            confirm_prompt: 是否点击prompt_window的"确认"按钮（True=确认，False=跳过）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'error': str,
                'matched_rows': list,
                'total_rows': int,
                'count': int
            }
        """
        try:
            # 确保用户信息管理页面已准备就绪
            self._ensure_page_ready()
            # 步骤1: 在表格中点击指定用户行
            self.log.info(f"开始修改用户: {old_username}")
            if not self.user_management_page.click_table_one_row({'用户姓名': old_username}):
                return {
                    'success': False,
                    'error': f'未找到用户: {old_username}'
                }

            # 步骤2: 点击修改用户按钮
            if not self.user_management_page.click_alter_user_button():
                return {
                    'success': False,
                    'error': '点击修改用户按钮失败'
                }

            # 步骤3: 切换到修改用户窗口并进行修改操作
            time.sleep(0.5)  # 等待窗口加载
            self.user_management_page.switch_to_alter_user_window()

            # 修改用户名（如果提供）
            if new_username:

                # 清空原用户名并输入新用户名
                if not self.user_management_page.set_user_name_edit(new_username):
                    return {
                        'success': False,
                        'error': '设置新用户名失败'
                    }

            # 修改用户类型（如果提供）
            if new_usertype:
                if not self.user_management_page.select_alter_user_type(new_usertype):
                    return {
                        'success': False,
                        'error': f'选择新用户类型失败: {new_usertype}'
                    }

            # 修改备注（如果提供）
            if new_remark:
                self.user_management_page.switch_to_alter_user_window()
                if not self.user_management_page.set_remark_edit(new_remark):
                    return {
                        'success': False,
                        'error': '设置新备注失败'
                    }

            # 修改所属系统（如果提供）
            if new_affiliated_system:
                if not self.user_management_page.check_alter_user_affiliated_system_tree_with_space_key(new_affiliated_system):
                    return {
                        'success': False,
                        'error': f'勾选新所属系统失败: {new_affiliated_system}'
                    }

            # 步骤4: 点击修改/取消按钮
            self.user_management_page.switch_to_alter_user_window()
            if confirm:
                if not self.user_management_page.click_alter_window_alter_button():
                    return {
                        'success': False,
                        'error': '点击修改窗口的修改按钮失败'
                    }
            else:
                if not self.user_management_page.click_alter_window_cancel_button():
                    return {
                        'success': False,
                        'error': '点击修改窗口的取消按钮失败'
                    }

            # 如果取消了修改，验证用户数据未变
            if not confirm:
                self.user_management_page.switch_to_user_info_management_window()
                return self.verify_user_in_table(
                    {'用户姓名': old_username},
                    expected_presence='present',
                    match_mode='exact',
                    timeout=timeout
                )

            # 步骤5: 处理prompt_window（确认按钮）
            # 修改用户只有消息提示窗体
            if not self.user_management_page.handle_prompt_window(confirm_prompt=confirm_prompt, timeout=timeout):
                return {
                    'success': False,
                    'error': '处理消息提示弹窗失败'
                }

            # 步骤6: 验证表格中的数据是否已更新
            self.user_management_page.switch_to_user_info_management_window()

            # 构建验证条件（只验证实际修改的字段）
            verify_username = new_username if new_username else old_username
            search_criteria = {'用户姓名': verify_username}

            # 查询表格数据
            expected_presence = 'present' if confirm_prompt else 'absent'
            result = self.verify_user_in_table(
                search_criteria,
                expected_presence=expected_presence,
                match_mode='exact',
                timeout=timeout
            )

            if not result['success']:
                return result

            # 如果确认了操作提示，进一步验证修改的字段是否正确
            if confirm_prompt and result['matched_rows']:
                matched_row = result['matched_rows'][0]

                # 验证用户类型
                if new_usertype and matched_row.get('用户类型') != new_usertype:
                    return {
                        'success': False,
                        'error': f"用户类型验证失败: 期望 {new_usertype}, 实际 {matched_row.get('用户类型')}"
                    }

                # 验证备注
                if new_remark and matched_row.get('备注') != new_remark:
                    return {
                        'success': False,
                        'error': f"备注验证失败: 期望 {new_remark}, 实际 {matched_row.get('备注')}"
                    }

                self.log.info(f"用户修改验证成功: {verify_username}")

            return result

        except Exception as e:
            error_msg = f"修改用户操作异常: {str(e)}"
            self.log.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'matched_rows': [],
                'total_rows': 0,
                'count': 0
            }

    # ========== 设置权限并验证方法 ==========
    def set_permission_and_verify(self, username: str, permissions: list,
                                  confirm: bool = True, confirm_prompt: bool = True,
                                  timeout: float = 5.0) -> dict:
        """
        设置用户权限并验证

        Args:
            username: 用户名（用于查找表格中的用户）
            permissions: 权限节点名称列表（如["用户信息", "添加用户", "修改用户"]）
            confirm: 是否点击设置权限窗口的保存按钮（True=保存，False=取消不保存）
            confirm_prompt: 是否点击prompt_window的"确认"按钮（True=确认，False=跳过）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'error': str,
                'message': str  # 提示消息内容
            }
        """
        try:
            # 确保用户信息管理页面已准备就绪
            self._ensure_page_ready()

            # 步骤1: 在表格中点击指定用户行
            self.log.info(f"开始为用户设置权限: {username}")
            if not self.user_management_page.click_table_one_row({'用户姓名': username}):
                return {
                    'success': False,
                    'error': f'未找到用户: {username}'
                }

            # 步骤2: 点击设置权限按钮
            if not self.user_management_page.click_set_permission_button():
                return {
                    'success': False,
                    'error': '点击设置权限按钮失败'
                }

            # 步骤3: 等待设置权限窗口出现
            time.sleep(0.5)  # 等待窗口加载
            if not self.user_management_page.switch_to_set_permission_window():
                return {
                    'success': False,
                    'error': '切换到设置权限窗口失败'
                }

            # 步骤4: 勾选权限树节点
            if not self.user_management_page.check_permission_tree_with_space_key(permissions):
                return {
                    'success': False,
                    'error': f'勾选权限节点失败: {permissions}'
                }

            # 步骤5: 点击保存或取消按钮
            self.user_management_page.switch_to_set_permission_window()
            if confirm:
                if not self.user_management_page.click_save_permission_button():
                    return {
                        'success': False,
                        'error': '点击保存权限按钮失败'
                    }
            else:
                if not self.user_management_page.click_set_permission_window_cancel_button():
                    return {
                        'success': False,
                        'error': '点击取消权限按钮失败'
                    }
                # 如果取消了，直接返回
                return {
                    'success': True,
                    'message': '已取消权限设置',
                    'error': None
                }

            # 步骤6: 处理prompt_window（确认按钮）
            # 设置权限只有消息提示窗体，没有操作提示窗体
            if not self.user_management_page.handle_prompt_window(confirm_prompt=confirm_prompt, timeout=timeout):
                return {
                    'success': False,
                    'error': '处理消息提示弹窗失败'
                }

            # 步骤7: 获取提示文本并验证
            self.user_management_page.switch_to_prompt_window()
            prompt_text = self.user_management_page.get_prompt_window_text()

            expected_message = "配置权限成功！"
            if expected_message in (prompt_text or ''):
                self.log.info(f"权限设置成功，提示信息: {prompt_text}")
                return {
                    'success': True,
                    'message': prompt_text,
                    'error': None
                }
            else:
                self.log.error(f"权限设置失败，提示信息: {prompt_text}")
                return {
                    'success': False,
                    'error': f'提示信息不匹配，期望包含: {expected_message}, 实际: {prompt_text}',
                    'message': prompt_text
                }

        except Exception as e:
            error_msg = f"设置用户权限操作异常: {str(e)}"
            self.log.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': None
            }

    # ========== 重置密码并验证方法 ==========
    def reset_password_and_verify(self, username: str, confirm: bool = True,
                                  confirm_operation: bool = True, confirm_prompt: bool = True,
                                  timeout: float = 5.0) -> dict:
        """
        重置用户密码并验证

        Args:
            username: 用户名（用于查找表格中的用户）
            confirm: 是否点击重置密码确认窗口的"是"按钮（True=确认重置，False=取消不重置）
            confirm_operation: 是否点击operation_window的"是"按钮（True=是，False=否）
            confirm_prompt: 是否点击prompt_window的"确认"按钮（True=确认，False=跳过）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'error': str,
                'message': str  # 提示消息内容
            }
        """
        try:
            # 确保用户信息管理页面已准备就绪
            self._ensure_page_ready()

            # 步骤1: 在表格中点击指定用户行
            self.log.info(f"开始重置用户密码: {username}")
            if not self.user_management_page.click_table_one_row({'用户姓名': username}):
                return {
                    'success': False,
                    'error': f'未找到用户: {username}'
                }

            # 步骤2: 点击重置密码按钮
            if not self.user_management_page.click_reset_password_button():
                return {
                    'success': False,
                    'error': '点击重置密码按钮失败'
                }

            # 步骤3: 等待重置密码确认窗口出现
            time.sleep(0.5)  # 等待窗口加载

            # 轮询等待重置密码窗口
            import time as time_module
            end_time = time_module.time() + timeout
            window_found = False

            while time_module.time() < end_time:
                if self.user_management_page.switch_to_reset_password_window():
                    window_found = True
                    self.log.info("重置密码确认窗口已出现")
                    break
                time_module.sleep(0.5)

            if not window_found:
                return {
                    'success': False,
                    'error': '重置密码确认窗口未出现'
                }

            # 步骤4: 点击确认或取消按钮
            if confirm:
                if not self.user_management_page.click_reset_password_confirm_button():
                    return {
                        'success': False,
                        'error': '点击重置密码确认按钮失败'
                    }
            else:
                if not self.user_management_page.click_reset_password_cancel_button():
                    return {
                        'success': False,
                        'error': '点击重置密码取消按钮失败'
                    }

                # 如果取消，直接返回成功
                return {
                    'success': True,
                    'message': '已取消重置密码',
                    'error': None
                }

            # 步骤5: 处理operation_window（是/否按钮）
            if not self.user_management_page.handle_operation_prompt(confirm_operation=confirm_operation, timeout=timeout):
                return {
                    'success': False,
                    'error': '处理操作提示弹窗失败'
                }

            # 步骤6: 处理prompt_window（确认按钮）
            if not self.user_management_page.handle_prompt_window(confirm_prompt=confirm_prompt, timeout=timeout):
                return {
                    'success': False,
                    'error': '处理消息提示弹窗失败'
                }

            # 步骤7: 获取提示文本并验证
            self.user_management_page.switch_to_prompt_window()
            prompt_text = self.user_management_page.get_prompt_window_text()

            expected_message = "密码重置成功！"
            if expected_message in (prompt_text or ''):
                self.log.info(f"密码重置成功，提示信息: {prompt_text}")
                return {
                    'success': True,
                    'message': prompt_text,
                    'error': None
                }
            else:
                self.log.error(f"密码重置失败，提示信息: {prompt_text}")
                return {
                    'success': False,
                    'error': f'提示信息不匹配，期望包含: {expected_message}, 实际: {prompt_text}',
                    'message': prompt_text
                }

        except Exception as e:
            error_msg = f"重置密码操作异常: {str(e)}"
            self.log.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': None
            }


    def handle_operation_prompt(self, expect_contains: str | None = None,
                                timeout: float = 5.0, confirm_operation: bool = True) -> bool:
        """
        处理操作提示窗口(operation_window)
        注意：调用此方法前应确保页面已准备就绪

        Args:
            confirm_operation: 是否点击"是"按钮（默认True，False=点击"否"）
        """
        return self.user_management_page.handle_operation_prompt(
            expect_contains=expect_contains,
            timeout=timeout,
            confirm_operation=confirm_operation
        )