#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理页面测试用例
"""

import pytest

from utils.config_manager import ConfigManager
from utils.super_handler_factory import create_handler


class TestUserManagementPage:
    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """自动设置测试资源"""
        self.resources = page_test_factory
        self.driver = self.resources['driver']
        self.user_management_page = self.resources['page']  # UserManagementPage实例（页面对象）
        self.user_management_handler = self.resources['handler']  # UserManagementHandler实例（业务逻辑）
        self.user_management_config = self.resources['page_config']
        self.log = self.resources['log']  # 日志记录器
        self.config_manager = ConfigManager()

        # 创建其他需要的handler
        self.main_handler = create_handler('main_page', driver=self.driver)
        self.login_handler = create_handler('login_page', driver=self.driver)

        # 获取测试数据
        self.user_management_data = self.config_manager.get_test_data('user_management_page')

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 确保页面处于正确状态
        if hasattr(self, 'user_management_page') and self.user_management_page is not None:
            # 可以在这里添加页面初始化逻辑
            pass

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 可以在这里添加清理逻辑
        pass

    def test_user_management_basic_flow(self):
        """测试用户管理基本流程（简化的版本）"""
        # 调试：打印当前会话信息和可用窗口
        self.log.warning(f"当前WebDriver会话: {self.driver}")
        try:
            # 获取当前页面标题
            current_title = self.driver.title
            self.log.warning(f"当前页面标题: {current_title}")
        except Exception as e:
            self.log.error(f"获取页面标题失败: {e}")

        # 获取登录测试数据
        login_credentials = self.config_manager.get_test_data('login_page').get('valid_login', {})
        username = login_credentials.get('username', 'admin')
        password = login_credentials.get('password', '1')

        self.log.info(f"开始测试用户管理基本流程，登录用户: {username}")

        # 执行登录
        login_result = self.login_handler.login(username, password)
        if not login_result:
            self.log.error("登录失败，无法继续用户管理测试")
            pytest.fail("登录失败")

        self.log.info("✓ 登录成功，开始用户管理操作")

        try:
            # 新增用户
            add_user_scenario = self.user_management_data.get("add_user_scenario", {})
            add_username = add_user_scenario.get("username", "")
            add_usertype = add_user_scenario.get("usertype", "")
            add_remark = add_user_scenario.get("remark", "")
            add_affiliated_system = add_user_scenario.get("affiliated_system", [])
            add_confirm = add_user_scenario.get("confirm", True)
            add_confirm_operation = add_user_scenario.get("confirm_operation", True)
            add_result = self.user_management_handler.add_user_and_verify(
                username=add_username,
                usertype=add_usertype,
                remark=add_remark,
                affiliated_system=add_affiliated_system,
                confirm=add_confirm,
                confirm_operation=add_confirm_operation
            )
            if add_result["success"]:
                self.log.info("✓ 新增用户成功")
            else:
                self.log.error("✗ 新增用户失败")

            # 修改用户
            alter_user_scenario = self.user_management_data.get("alter_user_scenario_1", {})
            alter_old_username = alter_user_scenario.get("old_username", "")
            alter_new_username = alter_user_scenario.get("new_username", "")
            alter_new_usertype = alter_user_scenario.get("new_usertype", "")
            alter_new_remark = alter_user_scenario.get("new_remark", "")
            alter_new_affiliated_system = alter_user_scenario.get("new_affiliated_system", [])
            alter_confirm = alter_user_scenario.get("confirm", True)
            alter_confirm_prompt = alter_user_scenario.get("confirm_prompt", True)
            alter_result = self.user_management_handler.alter_user_and_verify(
                alter_old_username, alter_new_username, alter_new_usertype, alter_new_remark,
                alter_new_affiliated_system, alter_confirm, alter_confirm_prompt
            )
            if alter_result["success"]:
                self.log.info("✓ 修改用户成功")
            else:
                self.log.error("✗ 修改用户失败")

            # 设置用户权限
            set_permission_scenario = self.user_management_data.get("set_permission_scenario_1", {})
            set_permission_scenario_username = set_permission_scenario.get("username", "")
            set_permission_scenario_permission = set_permission_scenario.get("permissions", [])
            set_permission_scenario_confirm = set_permission_scenario.get("confirm", True)
            set_permission_scenario_confirm_prompt = set_permission_scenario.get("confirm_prompt", True)
            set_permission_result = self.user_management_handler.set_permission_and_verify(
                set_permission_scenario_username, set_permission_scenario_permission,
                set_permission_scenario_confirm, set_permission_scenario_confirm_prompt
            )
            if set_permission_result["success"]:
                self.log.info("✓ 修改用户权限成功")
            else:
                self.log.error("✗ 修改用户权限失败")

            # 重置密码
            reset_password_scenario = self.user_management_data.get("reset_password_scenario_confirm", {})
            reset_password_scenario_username = reset_password_scenario.get("username", "")
            reset_password_scenario_confirm = reset_password_scenario.get("confirm", True)
            reset_password_scenario_confirm_operation = reset_password_scenario.get("confirm_operation", True)
            reset_password_scenario_confirm_prompt = reset_password_scenario.get("confirm_prompt", True)
            reset_password_result = self.user_management_handler.reset_password_and_verify(
                reset_password_scenario_username, reset_password_scenario_confirm,
                reset_password_scenario_confirm_operation, reset_password_scenario_confirm_prompt
            )
            if reset_password_result["success"]:
                self.log.info("✓ 重置密码成功")
            else:
                self.log.error("✗ 重置密码失败")

            # 删除用户
            delete_user_scenario = self.user_management_data.get("delete_user_scenario", {})
            delete_user_scenario_username = delete_user_scenario.get("username", "")
            delete_user_scenario_confirm_operation = delete_user_scenario.get("confirm_operation", True)
            delete_user_scenario_confirm_prompt = delete_user_scenario.get("confirm_prompt", True)
            delete_result = self.user_management_handler.delete_user_and_verify(
                delete_user_scenario_username,
                confirm_operation=delete_user_scenario_confirm_operation,
                confirm_prompt=delete_user_scenario_confirm_prompt
            )
            if delete_result["success"]:
                self.log.info("✓ 删除用户成功")
            else:
                self.log.error("✗ 删除用户失败")

            self.log.info("用户管理基本流程测试完成（新增、修改、删除用户功能）")

        except Exception as e:
            self.log.error(f"用户管理流程测试异常: {e}")
            pytest.fail(f"用户管理流程测试失败: {e}")

    def test_add_user_only(self):
        """只测试新增用户功能"""
        # 首先确保已登录
        login_credentials = self.config_manager.get_test_data('login_page').get('valid_login', {})
        username = login_credentials.get('username', 'admin')
        password = login_credentials.get('password', '1')

        login_result = self.login_handler.login(username, password)
        if not login_result:
            pytest.fail("登录失败")

        # 测试新增用户
        add_user_scenario = self.user_management_data.get("add_user_scenario", {})
        add_username = add_user_scenario.get("username", "")
        add_usertype = add_user_scenario.get("usertype", "")
        add_remark = add_user_scenario.get("remark", "")
        add_affiliated_system = add_user_scenario.get("affiliated_system", [])
        add_confirm = add_user_scenario.get("confirm", True)
        add_confirm_operation = add_user_scenario.get("confirm_operation", True)

        if add_username and add_usertype:
            add_result = self.user_management_handler.add_user_and_verify(
                add_username, add_usertype, add_remark, add_affiliated_system,
                add_confirm, add_confirm_operation
            )
            assert add_result["success"], "新增用户失败"
            self.log.info("✓ 新增用户测试通过")
        else:
            pytest.skip("新增用户测试数据不完整")
