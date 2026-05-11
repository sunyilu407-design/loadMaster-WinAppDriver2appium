"""
示例测试用例 - 展示正确的架构使用方法
演示如何使用Page + Handler的分离架构
"""

import pytest
import allure
import time


@allure.feature("主页面功能")
@allure.story("主页面业务逻辑测试")
class TestMainPage:
    """
    主页面测试类 - 展示正确的架构使用
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """
        设置测试资源 - 使用通用夹具
        """
        self.resources = page_test_factory
        self.driver = self.resources['driver']
        self.main_page = self.resources['page']      # MainPage实例（页面元素操作）
        self.main_handler = self.resources['handler']       # MainHandler实例（业务逻辑）
        self.test_data = self.resources['test_data']    # 测试数据
        self.main_config = self.resources['page_config']
        self.log = self.resources['log']                    # 日志记录器

    def setup_method(self):
        """每个测试方法执行前的设置"""
        pass

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        pass


    @allure.title("测试主页面导航功能")
    def test_main_page_navigation(self):
        """
        测试主页面导航功能 - 使用Handler执行业务逻辑
        """
        # 验证主页面显示（业务逻辑验证）
        assert self.main_handler.is_main_page_displayed(), "主页面未正确显示"
        
        # 使用Handler执行导航操作（业务逻辑）
        self.main_handler.navigate_to_settings()
        
        # 这里可以继续验证是否成功导航到设置页面
        self.log.info("✓ 主页面导航功能测试通过")
    
    @allure.title("测试用户登录状态验证")
    def test_user_login_verification(self):
        """
        测试用户登录状态验证 - 使用Handler进行业务逻辑验证
        """
        # 获取测试数据中的用户名
        expected_username = self.test_data.get('current_user', 'admin')
        
        # 使用Handler验证用户登录状态（业务逻辑验证）
        login_verified = self.main_handler.verify_user_login(expected_username)
        
        assert login_verified, f"用户 {expected_username} 登录状态验证失败"
        self.log.info(f"✓ 用户 {expected_username} 登录状态验证通过")
    
    @allure.title("测试退出登录功能")
    def test_logout_functionality(self):
        """
        测试退出登录功能 - 使用Handler执行完整业务逻辑
        """
        # 验证当前在主页面
        assert self.main_handler.is_main_page_displayed(), "测试开始前应在主页面"
        
        # 使用Handler执行退出登录（完整业务逻辑）
        self.main_handler.perform_logout()
        
        # 这里可以继续验证是否成功退出到登录页面
        self.log.info("✓ 退出登录功能测试通过")
    
    @allure.title("演示直接页面元素操作")
    def test_direct_page_element_operations(self):
        """
        演示直接页面元素操作 - 仅用于特殊情况
        """
        # 直接操作页面元素（仅用于特殊情况，不推荐）
        welcome_text = self.main_page.get_welcome_message()
        
        # 基础断言，不涉及复杂业务逻辑
        assert len(welcome_text) > 0, "欢迎信息为空"
        
        self.log.info(f"欢迎信息: {welcome_text}")
        self.log.info("✓ 直接页面元素操作演示完成")


