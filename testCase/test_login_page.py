#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录页面测试用例
"""

import pytest

import pytest

from utils.config_manager import ConfigManager
from utils.super_handler_factory import create_handler



class TestLoginPage:
    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """自动设置测试资源"""
        self.resources = page_test_factory
        self.driver = self.resources['driver']
        self.login_page = self.resources['page']  # LoginPage实例（页面对象）
        self.login_handler = self.resources['handler']  # LoginHandler实例（业务逻辑）
        self.login_config = self.resources['page_config']
        self.log = self.resources['log']  # 日志记录器
        self.config_manager = ConfigManager()

        # 注意：main_handler等已在conftest.py中创建，这里不再重复创建
        # 如果需要其他handler，可以使用现有的driver实例

        self.customer_handler = create_handler('customer_management_page', driver=self.driver)
        self.customer_management_data = self.config_manager.get_test_data('customer_management_page')
        # 但通常情况下，一个测试类只专注于一个页面，跨页面操作应该在handler层完成


    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 确保输入框为空
        if hasattr(self, 'login_page') and self.login_page is not None:
            self.login_page.clear_input_fields()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass

    def test_valid_login_customer(self):
        """测试有效凭据登录"""
        # 添加调试信息
        self.log.info(f"valid_credentials value: {self.login_config}")
        
        # 检查login_config是否为None
        if self.login_config is None:
            self.log.error("login_config is None, 无法继续测试")
            pytest.fail("login_config is None, 无法继续测试")
        
        # 获取测试数据
        valid_credentials = self.login_config.get('test_data', {}).get('valid_login', {})
        self.log.info(f"valid_credentials: {valid_credentials}")
        
        if not valid_credentials:
            self.log.error("无法获取有效的登录凭据")
            pytest.fail("无法获取有效的登录凭据")
        
        # 执行登录操作
        username = valid_credentials.get('username', '')
        password = valid_credentials.get('password', '')
        
        self.log.info(f"使用用户名: {username}, 密码: {password} 进行登录测试")
        
        self.log.info("开始调用 login_handler.login_with_retry")
        login_result = self.login_handler.login(username, password)
        
        #打印日志登录结果
        self.log.info(f"login_result 值: {login_result}")
        if login_result:
            self.log.info("login_result 为 True，登录成功")
        else:
            self.log.error("login_result 为 False，登录失败")
            # 即使登录失败也继续执行，看看能否导航到装车开票
        #新增客户
        self.log.info("准备调用 add_customer_and_verify")
        add_customer_scenario=self.customer_management_data.get("add_customer_success",{})
        self.log.info(f"add_customer_scenario: {add_customer_scenario}")
        add_result = self.customer_handler.add_customer_and_verify(
            short_name=add_customer_scenario.get("short_name", ""),
            full_name=add_customer_scenario.get("full_name", ""),
            code=add_customer_scenario.get("code", ""),
            link_man=add_customer_scenario.get("link_man", ""),
            link_phone=add_customer_scenario.get("link_phone", ""),
            confirm=add_customer_scenario.get("confirm", True),
            timeout=10.0
        )
        self.log.info(f"add_customer_and_verify 返回: {add_result}")
        if add_result.get("success"):
            self.log.info("✓ 新增客户成功")
        else:
            self.log.error(f"✗ 新增客户失败: {add_result.get('error', '未知错误')}")
        #查询客户
        query_customer_scenario = self.customer_management_data.get("query_customer", {})
        query_customer_result = self.customer_handler.query_customer(search_key=query_customer_scenario.get("search_key", ""), timeout=10.0)
        if query_customer_result["success"]:
            self.log.info("✓ 查询客户成功")
        else:
            self.log.error("✗ 查询客户失败")
        #修改客户
        alter_customer_success_scenario=self.customer_management_data.get("alter_customer_success",{})
        alter_result = self.customer_handler.alter_customer_and_verify(
            short_name=alter_customer_success_scenario.get("short_name", ""),
            full_name=alter_customer_success_scenario.get("full_name", ""),
            code=alter_customer_success_scenario.get("code", ""),
            link_man=alter_customer_success_scenario.get("link_man", ""),
            link_phone=alter_customer_success_scenario.get("link_phone", ""),
        )
        if alter_result["success"]:
            self.log.info("✓ 修改客户成功")
        else:
            self.log.error("✗ 修改客户失败")
        #删除客户
        delete_customer_scenario=self.customer_management_data.get("delete_customer_success",{})
        delete_result = self.customer_handler.delete_customer_and_verify(search_key=delete_customer_scenario.get("search_key", ""))
        if delete_result["success"]:
            self.log.info("✓ 删除客户成功")
        else:
            self.log.error("✗ 删除客户失败")

    def test_valid_login_remote(self):
        """测试有效凭据登录 -> 装车开票添加新单 -> 审核 -> 远程发油"""
        # 添加调试信息
        self.log.info(f"valid_credentials value: {self.login_config}")

        # 检查login_config是否为None
        if self.login_config is None:
            self.log.error("login_config is None, 无法继续测试")
            pytest.fail("login_config is None, 无法继续测试")

        # 获取测试数据
        valid_credentials = self.login_config.get('test_data', {}).get('valid_login', {})
        self.log.info(f"valid_credentials: {valid_credentials}")

        if not valid_credentials:
            self.log.error("无法获取有效的登录凭据")
            pytest.fail("无法获取有效的登录凭据")

        # 执行登录操作
        username = valid_credentials.get('username', '')
        password = valid_credentials.get('password', '')

        self.log.info(f"使用用户名: {username}, 密码: {password} 进行登录测试")

        self.log.info("开始调用 login_handler.login_with_retry")
        login_result = self.login_handler.login(username, password)

        # 打印日志登录结果
        if login_result:
            self.log.info("login_result 为 True，登录成功")
        else:
            self.log.error("login_result 为 False，登录失败，跳过后续测试")
            pytest.fail("登录失败，跳过测试")

        # =====================================================
        # 创建所需 handler
        # =====================================================
        self.invoice_handler = create_handler('invoice_management_page', driver=self.driver)
        self.monitor_handler = create_handler('monitor_management_page', driver=self.driver)
        self.invoice_test_data = self.config_manager.get_test_data("invoice_management_page")

        # =====================================================
        # 步骤1：添加装车开票
        # =====================================================
        add_invoice_scenario = self.invoice_test_data.get('add_invoice_success_full', {})
        bill_num = add_invoice_scenario.get('bill_num', '26050801')
        vehicle_no = add_invoice_scenario.get('vehicle_no', '京A12345')
        oil_name = add_invoice_scenario.get('oil_name', '汽油')
        station = add_invoice_scenario.get('station', '1')
        weight = add_invoice_scenario.get('weight', '8500')
        load_mode = add_invoice_scenario.get('load_mode', '按重量发油')
        buyer = add_invoice_scenario.get('buyer', '测试客户')
        sort = add_invoice_scenario.get('sort', '销售')
        remark = add_invoice_scenario.get('remark', '测试开票')
        use_ic_card = add_invoice_scenario.get('use_ic_card', False)
        additive = add_invoice_scenario.get('additive', False)
        confirm = add_invoice_scenario.get('confirm', True)  # 改为 True，点击"是"确认添加

        self.log.info(f"开始添加开票，提货单号: {bill_num}, confirm={confirm}")
        add_result = self.invoice_handler.add_invoice_and_verify(
            bill_num=bill_num,
            vehicle_no=vehicle_no,
            oil_name=oil_name,
            station=station,
            weight=weight,
            load_mode=load_mode,
            buyer=buyer,
            sort=sort,
            remark=remark,
            use_ic_card=use_ic_card,
            additive=additive,
            confirm=confirm,
            timeout=10.0
        )
        self.log.info(f"添加开票结果: {add_result}")
        if add_result.get('success'):
            self.log.info(f"✓ 开票添加完成，提货单号: {bill_num}")
        else:
            self.log.error(f"✗ 开票添加失败: {add_result.get('error')}")
            # 添加失败时继续执行后续步骤（有些步骤可能不依赖添加结果）
            self.log.warning("添加失败，继续执行后续步骤...")

        # =====================================================
        # 步骤2：在表格中找到刚才添加的开票信息，选择该行
        # =====================================================
        self.log.info(f"在表格中选择开票信息: {bill_num}")
        select_result = self.invoice_handler.invoice_page.click_invoice_table_row(
            {'提货单号': bill_num}
        )
        if select_result:
            self.log.info(f"✓ 选中提货单号: {bill_num}")
        else:
            self.log.error(f"✗ 选中提货单号失败: {bill_num}")

        # =====================================================
        # 步骤3：点击审核按钮 -> 操作提示窗 -> 点击"是"
        #         -> 审核成功提示窗 -> 点击"确认"
        # =====================================================
        self.log.info(f"审核提货单号: {bill_num}")
        audit_result = self.invoice_handler.audit_invoice_and_verify(
            search_key=bill_num,
            timeout=10.0
        )
        if audit_result.get('success'):
            self.log.info(f"✓ 审核成功: {bill_num}")
        else:
            self.log.error(f"✗ 审核失败: {audit_result.get('error')}")

        # =====================================================
        # 步骤4：点击左侧"监控"菜单栏，切换到监控页面
        # 注意：审核成功后已在 audit_invoice_and_verify 中关闭装车开票页面
        # =====================================================
        self.log.info("导航到监控页面")
        if self.invoice_handler.navigate_to_monitoring_page():
            self.log.info("✓ 监控页面已打开")
        else:
            self.log.error("✗ 导航到监控页面失败")

        # =====================================================
        # 步骤6：在监控页面找到对应货位，双击进入远程控制页面
        # =====================================================
        self.log.info(f"双击货位 {station} 打开远程控制")
        remote_result = self.monitor_handler.open_remote_control(station_no=station, timeout=10.0)
        if not remote_result.get('success'):
            self.log.error(f"✗ 打开远程控制失败: {remote_result.get('error')}")
            pytest.fail(f"打开远程控制失败: {remote_result.get('error')}")
        self.log.info(f"✓ 远程控制窗口已打开，货位: {station}")

        # =====================================================
        # 步骤7：输入提货单号，点击设定按钮
        # =====================================================
        self.log.info(f"输入提货单号: {bill_num} 到远程设定窗口")
        self.monitor_handler.monitor_page.set_remote_bill_num(bill_num)
        self.log.info("点击设定按钮")
        self.monitor_handler.monitor_page.click_remote_set_button()

        # =====================================================
        # 步骤8：检查预装量输入框是否带出了刚才输入的值
        # =====================================================
        self.log.info("检查预装量是否带出")
        plan_out_oil = self.monitor_handler.monitor_page.get_remote_plan_out_oil()
        self.log.info(f"计划发油量显示: {plan_out_oil}")

        # weight 就是预装重量（预装量），plan_out_oil 应该等于它
        if plan_out_oil and str(plan_out_oil).strip() == str(weight).strip():
            self.log.info(f"✓ 预装量显示正确: {plan_out_oil} == {weight}")
        else:
            self.log.warning(f"⚠ 预装量显示异常: {plan_out_oil} != {weight}")

        # =====================================================
        # 步骤9：点击启动按钮
        # =====================================================
        self.log.info("点击启动按钮")
        start_result = self.monitor_handler.remote_start_oil(station_no=station, confirm=True, timeout=10.0)
        if start_result.get('success'):
            self.log.info("✓ 启动发油成功")
        else:
            self.log.warning(f"⚠ 启动发油结果: {start_result.get('error')}")



    def test_invalid_login(self):
        """测试无效凭据登录"""
        # 获取测试数据
        invalid_credentials = self.login_config.get('invalid_credentials', {})
        test_cases = invalid_credentials.get('test_cases', [])
        
        for i, test_case in enumerate(test_cases):
            self.log.info(f"开始测试: 无效凭据登录 - 场景{i+1} - 用户: {test_case.get('username', '空')}")
            
            # 执行登录操作
            username = test_case.get('username', '')
            password = test_case.get('password', '')
            
            login_result = self.login_handler.login_with_failure(
                username, password,
                max_retries=invalid_credentials.get('max_retries', 1),
                retry_delay=invalid_credentials.get('retry_delay', 1)
            )
            
            # 验证登录失败结果
            if login_result:
                self.log.info("✓ 登录失败,弹出提示框正确")
            else:
                self.log.error("✗ 登录失败，验证未通过")

    # def test_login_response_time(self):
    #     """测试登录响应时间"""
    #     self.log.info("测试登录响应时间")
    #
    #     # 获取测试数据
    #     performance_test = self.login_config.get('performance_test', {})
    #     test_username = performance_test.get('username', 'testuser')
    #     test_password = performance_test.get('password', 'testpass')
    #     max_response_time = performance_test.get('max_response_time', 5.0)  # 默认5秒
    #
    #     # 清空输入框
    #     self.login_page.clear_input_fields()
    #
    #     # 执行登录并测量响应时间
    #     start_time = time.time()
    #     login_success = self.login_page.login(test_username, test_password)
    #     end_time = time.time()
    #
    #     response_time = end_time - start_time
    #     self.log.info(f"登录响应时间: {response_time:.2f}秒")
    #
    #     # 验证响应时间
    #     assert response_time <= max_response_time, f"登录响应时间({response_time:.2f}s)超过最大允许时间({max_response_time}s)"
    #     self.log.info("✓ 登录性能测试通过")


if __name__ == '__main__':
    print("登录功能测试")
    print("运行命令: pytest test_login_page.py -v --alluredir=./reports")
    print("查看报告: allure serve ./reports")