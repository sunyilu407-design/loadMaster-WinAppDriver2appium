"""
客户信息管理测试用例
Customer Management Page Test Cases
"""
import pytest
import allure

from utils import ConfigManager
from utils.super_handler_factory import create_handler


@allure.epic("客户信息管理")
@allure.feature("客户 CRUD 操作")
class TestCustomerManagementPage:
    """客户信息管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """测试资源初始化"""
        self.resources = page_test_factory
        self.log = self.resources['log']  # 日志记录器
        self.config_manager = ConfigManager()
        self.customer_handler = create_handler('customer_management_page')
        self.customer_management_data = self.config_manager.get_test_data('customer_management_page')
        yield

    @allure.story("添加客户")
    @allure.title("测试添加客户成功")
    def test_add_customer_success(self):
        """测试添加客户成功场景"""
        add_customer_scenario = self.customer_management_data.get("add_customer_scenario", {})
        add_result = self.customer_handler.add_customer_and_verify(
            short_name=add_customer_scenario.get("short_name", ""),
            full_name=add_customer_scenario.get("full_name", ""),
            code=add_customer_scenario.get("code", ""),
            link_man=add_customer_scenario.get("link_man", ""),
            link_phone=add_customer_scenario.get("link_phone", ""),
            confirm=add_customer_scenario.get("confirm", ""),
            timeout=10.0
        )
        if add_result["success"]:
            self.log.info("✓ 新增客户成功")
        else:
            self.log.error("✗ 新增客户失败")
        assert add_result['success'], f"添加客户失败: {add_result.get('error', '未知错误')}"

    @allure.story("修改客户")
    @allure.title("测试修改客户成功")
    def test_alter_customer_success(self):
        """测试修改客户成功场景"""
        # 先添加
        add_customer_scenario = self.customer_management_data.get("add_customer_scenario", {})
        self.customer_handler.add_customer_and_verify(
            short_name=add_customer_scenario.get("short_name", ""),
            full_name=add_customer_scenario.get("full_name", ""),
            code=add_customer_scenario.get("code", ""),
            link_man=add_customer_scenario.get("link_man", ""),
            link_phone=add_customer_scenario.get("link_phone", ""),
            confirm=add_customer_scenario.get("confirm", ""),
            timeout=10.0
        )
        # 再修改
        alter_customer_success_scenario = self.customer_management_data.get("alter_customer_success", {})
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
        assert alter_result['success'], f"修改客户失败: {alter_result.get('error', '未知错误')}"

    @allure.story("删除客户")
    @allure.title("测试删除客户成功")
    def test_delete_customer_success(self):
        """测试删除客户成功场景"""
        # 先添加
        add_customer_scenario = self.customer_management_data.get("add_customer_scenario", {})
        self.customer_handler.add_customer_and_verify(
            short_name=add_customer_scenario.get("short_name", ""),
            full_name=add_customer_scenario.get("full_name", ""),
            code=add_customer_scenario.get("code", ""),
            link_man=add_customer_scenario.get("link_man", ""),
            link_phone=add_customer_scenario.get("link_phone", ""),
            confirm=add_customer_scenario.get("confirm", ""),
            timeout=10.0
        )
        # 再删除
        delete_customer_scenario = self.customer_management_data.get("delete_customer_success", {})
        delete_result = self.customer_handler.delete_customer_and_verify(
            search_key=delete_customer_scenario.get("search_key", ""))
        if delete_result["success"]:
            self.log.info("✓ 删除客户成功")
        else:
            self.log.error("✗ 删除客户失败")
        assert delete_result['success'], f"删除客户失败: {delete_result.get('error', '未知错误')}"

    @allure.story("查询客户")
    @allure.title("测试查询客户")
    def test_query_customer(self):
        """测试查询客户功能"""
        query_customer_scenario = self.customer_management_data.get("query_customer", {})
        query_customer_result = self.customer_handler.query_customer(search_key=query_customer_scenario.search_key,
                                                                     timeout=10.0)
        if query_customer_result["success"]:
            self.log.info("✓ 查询客户成功")
        else:
            self.log.error("✗ 查询客户失败")
        assert query_customer_result['success'], f"查询客户失败: {query_customer_result.get('error', '未知错误')}"

