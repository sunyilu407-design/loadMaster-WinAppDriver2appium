"""
主页面Handler - 业务逻辑处理
组合页面操作实现复杂的业务逻辑

修改记录：
2025-12-31 12:00:00 (功能修复更新)
- ✅ 修复MainHandler构造函数参数名与SuperHandlerFactory不匹配问题
- ✅ 将参数名从'main_page'改为'page_instance'以保持一致性
"""

import logging
import time
import allure
from handlers.base_handler import BaseHandler
from pageObject.main_page import MainPage
from utils.driver_factory import DriverFactory

class MainHandler(BaseHandler):
    """
    主页面Handler - 业务逻辑处理类
    """
    
    def __init__(self, page_instance=None, config_manager=None):
        """
        初始化主页面Handler

        Args:
            page_instance: 主页面对象（可为None）
            config_manager: 配置管理器
        """
        super().__init__(page_instance, config_manager)

        # 赋值主页面对象（自动创建）
        self.main_page = self.page_instance

    def _create_page_instance(self, config_manager):
        """
        创建主页面对象实例

        Args:
            config_manager: 配置管理器

        Returns:
            MainPage: 主页面对象实例
        """
        from pageObject.main_page import MainPage
        from utils.driver_factory import DriverFactory

        # 获取驱动实例
        driver = DriverFactory.get_windows_driver()
        if driver is None:
            raise Exception("无法获取Windows驱动实例")

        # 创建主页面对象
        return MainPage(driver, config_manager)
    
    
    def verify_user_login(self, expected_username):
        """
        验证用户登录状态 - 业务逻辑验证
        """
        self.log.info(f"验证用户 {expected_username} 的登录状态")
        
        # 获取欢迎信息
        welcome_message = self.main_page.get_welcome_message()
        
        # 验证欢迎信息包含用户名
        if expected_username not in welcome_message:
            raise Exception(f"欢迎信息验证失败: 预期包含'{expected_username}', 实际'{welcome_message}'")
        
        self.log.info(f"用户 {expected_username} 登录状态验证通过")
        return True

        #用户管理菜单导航函数
    def navigate_to_user_info_management(self):
        """
        导航到用户信息管理 - 业务逻辑
        添加等待和验证逻辑，确保子菜单能够正确展开和点击
        """
        import time
        with allure.step("导航到用户信息管理页面"):
            self.log.info("执行导航到用户信息管理的业务逻辑")

            self.log.info("等待主界面跳转...")

            # 验证当前页面是主页面
            with allure.step("验证当前页面状态"):
                if not self.is_main_page_displayed():
                    raise Exception("当前不在主页面，无法导航到用户信息管理")

            # 点击用户管理主菜单并验证
            with allure.step("点击用户管理主菜单"):
                self.log.info("点击用户管理主菜单...")
                self.main_page.click_user_management_parent_menu()

            # 关键改进：等待主菜单展开，给子菜单足够的显示时间
            with allure.step("等待子菜单展开"):
                self.log.info("等待子菜单展开...")
                time.sleep(0.5)  # 等待1秒让子菜单完全展开

            # 点击用户信息管理子菜单并验证
            with allure.step("点击用户信息管理子菜单"):
                self.log.info("点击用户信息管理子菜单...")
                if not self.main_page.click_user_management_child_menu():
                    self.log.error("用户信息管理子菜单点击失败")
                    return False

            self.log.info("成功导航到用户信息管理页面")
            return True
    
    def navigate_to_password_change(self):
        """
        导航到密码修改 - 业务逻辑
        """
        self.log.info("执行导航到密码修改的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到密码修改")
        
        # 点击用户管理主菜单
        self.main_page.click_user_management_parent_menu()

        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击密码修改菜单
        self.main_page.click_passWord_change_menu()
        
        self.log.info("成功导航到密码修改页面")
    
    def navigate_to_username_change(self):
        """
        导航到用户名修改 - 业务逻辑
        """
        self.log.info("执行导航到用户名修改的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到用户名修改")
        
        # 点击用户管理主菜单
        self.main_page.click_user_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击用户名修改菜单
        self.main_page.click_userName_change_menu()
        
        self.log.info("成功导航到用户名修改页面")
    
    def navigate_to_user_login(self):
        """
        导航到用户登录 - 业务逻辑
        """
        self.log.info("执行导航到用户登录的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到用户登录")
        
        # 点击用户管理主菜单
        self.main_page.click_user_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击用户登录菜单
        self.main_page.click_user_login_menu()
        
        self.log.info("成功导航到用户登录页面")
    
    def navigate_to_user_logout(self):
        """
        导航到退出登录 - 业务逻辑
        """
        self.log.info("执行导航到退出登录的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到退出登录")
        
        # 点击用户管理主菜单
        self.main_page.click_user_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击退出登录菜单
        self.main_page.click_user_logout_menu()
        
        self.log.info("成功导航到退出登录页面")
    
    def is_main_page_present(self):
        """
        检查主页面是否存在 - 业务逻辑判断
        """
        return self.main_page.is_main_page_present()

    def is_main_page_displayed(self):
        """
        检查主页面是否显示 - 业务逻辑判断（向后兼容）
        """
        return self.is_main_page_present()
    
        #系统配置菜单导航函数
    def navigate_to_customer_management(self):
        """
        导航到客户信息管理 - 业务逻辑
        """
        with allure.step("导航到客户信息管理页面"):
            self.log.info("执行导航到客户信息管理的业务逻辑")

            # 验证当前页面是主页面
            with allure.step("验证当前页面状态"):
                if not self.main_page.is_main_page_present():
                    raise Exception("当前不在主页面，无法导航到客户信息管理")

            # 点击系统管理主菜单
            with allure.step("点击系统管理主菜单"):
                self.main_page.click_system_management_parent_menu()

            # 关键改进：等待主菜单展开，给子菜单足够的显示时间
            with allure.step("等待子菜单展开"):
                self.log.info("等待子菜单展开...")
                time.sleep(1)  # 等待1秒让子菜单完全展开

            # 点击客户信息管理菜单
            with allure.step("点击客户信息管理菜单"):
                self.main_page.click_customer_menu()

            self.log.info("成功导航到客户信息管理页面")
    
    def navigate_to_serial_port_management(self):
        """
        导航到串口信息管理 - 业务逻辑
        """
        self.log.info("执行导航到串口信息管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到串口信息管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击串口信息管理菜单
        self.main_page.click_serial_port_menu()
        
        self.log.info("成功导航到串口信息管理页面")
    
    def navigate_to_station_management(self):
        """
        导航到货位信息管理 - 业务逻辑
        """
        self.log.info("执行导航到货位信息管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到货位信息管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击货位信息管理菜单
        self.main_page.click_station_menu()
        
        self.log.info("成功导航到货位信息管理页面")
    
    def navigate_to_oil_management(self):
        """
        导航到油品信息管理 - 业务逻辑
        """
        self.log.info("执行导航到油品信息管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到油品信息管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击油品信息管理菜单
        self.main_page.click_oil_menu()
        
        self.log.info("成功导航到油品信息管理页面")
    
    def navigate_to_configuration_settings(self):
        """
        导航到配置设定 - 业务逻辑
        """
        self.log.info("执行导航到配置设定的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到配置设定")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击配置设定菜单
        self.main_page.click_configuration_settings_menu()
        
        self.log.info("成功导航到配置设定页面")
    
    def navigate_to_oil_density(self):
        """
        导航到发油密度 - 业务逻辑
        """
        self.log.info("执行导航到发油密度的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发油密度")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发油密度菜单
        self.main_page.click_oil_density_menu()
        
        self.log.info("成功导航到发油密度页面")
    
    def navigate_to_station_tank_configuration(self):
        """
        导航到货位油罐配置 - 业务逻辑
        """
        self.log.info("执行导航到货位油罐配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到货位油罐配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击货位油罐配置菜单
        self.main_page.click_station_tank_menu()
        
        self.log.info("成功导航到货位油罐配置页面")
    
    def navigate_to_oil_distribution_rules(self):
        """
        导航到发油规则设置 - 业务逻辑
        """
        self.log.info("执行导航到发油规则设置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发油规则设置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发油规则设置菜单
        self.main_page.click_oil_distribution_rules_menu()
        
        self.log.info("成功导航到发油规则设置页面")
    
    def navigate_to_system_decimal_settings(self):
        """
        导航到系统单位小数设置 - 业务逻辑
        """
        self.log.info("执行导航到系统单位小数设置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到系统单位小数设置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击系统单位小数设置菜单
        self.main_page.click_system_decimal_settings_menu()
        
        self.log.info("成功导航到系统单位小数设置页面")
    
    def navigate_to_marginal_box_configuration(self):
        """
        导航到边缘盒子配置 - 业务逻辑
        """
        self.log.info("执行导航到边缘盒子配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到边缘盒子配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击边缘盒子配置子菜单
        self.main_page.click_marginal_box_menu()
        
        self.log.info("成功导航到边缘盒子配置页面")
    
    def navigate_to_job_position_configuration(self):
        """
        导航到作业位配置 - 业务逻辑
        """
        self.log.info("执行导航到作业位配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到作业位配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击作业位配置子菜单
        self.main_page.click_job_position_menu()
        
        self.log.info("成功导航到作业位配置页面")
    
    def navigate_to_camera_configuration(self):
        """
        导航到摄像头配置 - 业务逻辑
        """
        self.log.info("执行导航到摄像头配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到摄像头配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击摄像头配置子菜单
        self.main_page.click_camera_menu()
        
        self.log.info("成功导航到摄像头配置页面")
    
    def navigate_to_claude_server_configuration(self):
        """
        导航到云服务器配置 - 业务逻辑
        """
        self.log.info("执行导航到云服务器配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到云服务器配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击云服务器配置子菜单
        self.main_page.click_claude_server_menu()
        
        self.log.info("成功导航到云服务器配置页面")
    
    def navigate_to_self_developed_algorithm_parameter(self):
        """
        导航到自研算法配置 - 业务逻辑
        """
        self.log.info("执行导航到自研算法配置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到自研算法配置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击自研算法配置子菜单
        self.main_page.click_self_developed_algorithm_parameter_menu()
        
        self.log.info("成功导航到自研算法配置页面")
    
    def navigate_to_self_developed_AI_task_start_and_stop(self):
        """
        导航到自研算法任务启停 - 业务逻辑
        """
        self.log.info("执行导航到自研算法任务启停的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到自研算法任务启停")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击AI配置菜单
        self.main_page.click_AI_configuration_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击自研算法任务启停子菜单
        self.main_page.click_self_developed_AI_task_start_and_stop_menu()
        
        self.log.info("成功导航到自研算法任务启停页面")
    
    def navigate_to_station_oil_extraction_limit(self):
        """
        导航到货位提油限制 - 业务逻辑
        """
        self.log.info("执行导航到货位提油限制的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到货位提油限制")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击货位提油限制菜单
        self.main_page.click_station_oil_extraction_limit_menu()
        
        self.log.info("成功导航到货位提油限制页面")
    
    def navigate_to_car_management(self):
        """
        导航到车辆管理 - 业务逻辑
        """
        self.log.info("执行导航到车辆管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到车辆管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击车辆管理菜单
        self.main_page.click_car_menu()
        
        self.log.info("成功导航到车辆管理页面")
    
    def navigate_to_document_management(self):
        """
        导航到文档管理 - 业务逻辑
        """
        self.log.info("执行导航到文档管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到文档管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击文档管理菜单
        self.main_page.click_document_menu()
        
        self.log.info("成功导航到文档管理页面")
    
    def navigate_to_score_management(self):
        """
        导航到评分管理 - 业务逻辑
        """
        self.log.info("执行导航到评分管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到评分管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击评分管理菜单
        self.main_page.click_score_menu()
        
        self.log.info("成功导航到评分管理页面")
    
    def navigate_to_voice_settings(self):
        """
        导航到语音播报设置 - 业务逻辑
        """
        self.log.info("执行导航到语音播报设置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到语音播报设置")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击语音播报设置菜单
        self.main_page.click_voice_menu()
        
        self.log.info("成功导航到语音播报设置页面")
    
    def navigate_to_device_management(self):
        """
        导航到设备信息管理 - 业务逻辑
        """
        self.log.info("执行导航到设备信息管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到设备信息管理")
        
        # 点击系统管理主菜单
        self.main_page.click_system_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击设备信息管理菜单
        self.main_page.click_device_menu()
        
        self.log.info("成功导航到设备信息管理页面")


        #装车仪菜单导航函数
    def navigate_to_read_write_standard_density(self):
        """
        导航到读写标准密度 - 业务逻辑
        """
        self.log.info("执行导航到读写标准密度的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写标准密度")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写标准密度菜单
        self.main_page.click_read_write_standard_density_menu()
        
        self.log.info("成功导航到读写标准密度页面")
    
    def navigate_to_read_write_ethanol_ratio(self):
        """
        导航到读写乙醇比 - 业务逻辑
        """
        self.log.info("执行导航到读写乙醇比的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写乙醇比")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写乙醇比菜单
        self.main_page.click_read_write_ethanol_ratio_menu()
        
        self.log.info("成功导航到读写乙醇比页面")
    
    def navigate_to_read_write_flow_rate(self):
        """
        导航到读写流速参数 - 业务逻辑
        """
        self.log.info("执行导航到读写流速参数的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写流速参数")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写流速参数菜单
        self.main_page.click_read_write_flow_rate_menu()
        
        self.log.info("成功导航到读写流速参数页面")
    
    def navigate_to_read_write_cumulative_amount(self):
        """
        导航到读写累积量 - 业务逻辑
        """
        self.log.info("执行导航到读写累积量的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写累积量")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写累积量菜单
        self.main_page.click_read_write_cumulative_amount_menu()
        
        self.log.info("成功导航到读写累积量页面")
    
    def navigate_to_read_write_pulse_parameters(self):
        """
        导航到读写脉冲参数 - 业务逻辑
        """
        self.log.info("执行导航到读写脉冲参数的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写脉冲参数")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写脉冲参数菜单
        self.main_page.click_read_write_pulse_parameters_menu()
        
        self.log.info("成功导航到读写脉冲参数页面")
    
    def navigate_to_read_write_temperature_change(self):
        """
        导航到读写温变参数 - 业务逻辑
        """
        self.log.info("执行导航到读写温变参数的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写温变参数")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写温变参数菜单
        self.main_page.click_read_write_temperature_change_menu()
        
        self.log.info("成功导航到读写温变参数页面")
    
    def navigate_to_read_write_password(self):
        """
        导航到读写密码 - 业务逻辑
        """
        self.log.info("执行导航到读写密码的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写密码")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写密码菜单
        self.main_page.click_read_write_passWrod_menu()
        
        self.log.info("成功导航到读写密码页面")
    
    def navigate_to_read_history(self):
        """
        导航到读写历史记录 - 业务逻辑
        """
        self.log.info("执行导航到读写历史记录的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写历史记录")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写历史记录菜单
        self.main_page.click_read_history_menu()
        
        self.log.info("成功导航到读写历史记录页面")
    
    def navigate_to_read_write_average_temperature(self):
        """
        导航到读写平均温度修正量 - 业务逻辑
        """
        self.log.info("执行导航到读写平均温度修正量的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写平均温度修正量")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写平均温度修正量菜单
        self.main_page.click_read_write_average_temperature_menu()
        
        self.log.info("成功导航到读写平均温度修正量页面")
    
    def navigate_to_read_write_additive_ratio(self):
        """
        导航到读写添加剂配比 - 业务逻辑
        """
        self.log.info("执行导航到读写添加剂配比的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写添加剂配比")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击添加剂菜单
        self.main_page.click_additive_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写添加剂配比子菜单
        self.main_page.click_read_write_additive_ratio_menu()
        
        self.log.info("成功导航到读写添加剂配比页面")
    
    def navigate_to_read_write_additive_meter(self):
        """
        导航到读写添加剂计密 - 业务逻辑
        """
        self.log.info("执行导航到读写添加剂计密的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到读写添加剂计密")
        
        # 点击装车仪主菜单
        self.main_page.click_loading_instrument_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击添加剂菜单
        self.main_page.click_additive_menu()
        
        # 关键改进：等待子菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击读写添加剂计密子菜单
        self.main_page.click_read_write_additive_meter_menu()
        
        self.log.info("成功导航到读写添加剂计密页面")
    
      # 报表管理导航函数
    def navigate_to_distribution_record_report(self):
        """
        导航到发放记录报表 - 业务逻辑
        """
        self.log.info("执行导航到发放记录报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发放记录报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发放记录报表菜单
        self.main_page.click_distribution_record_report_menu()
        
        self.log.info("成功导航到发放记录报表页面")
    
    def navigate_to_oil_dispensing_platform_statistics_report(self):
        """
        导航到付油台提油统计表 - 业务逻辑
        """
        self.log.info("执行导航到付油台提油统计表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到付油台提油统计表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击付油台提油统计表菜单
        self.main_page.click_oil_dispensing_platform_statistics_report_menu()
        
        self.log.info("成功导航到付油台提油统计表页面")
    
    def navigate_to_oil_depot_flowmeter_oil_dispensing_report(self):
        """
        导航到油库流量计发油记录 - 业务逻辑
        """
        self.log.info("执行导航到油库流量计发油记录的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到油库流量计发油记录")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击油库流量计发油记录菜单
        self.main_page.click_oil_depot_flowmeter_oil_dispensing_report_menu()
        
        self.log.info("成功导航到油库流量计发油记录页面")
    
    def navigate_to_station_alarm_record_report(self):
        """
        导航到货位报警记录 - 业务逻辑
        """
        self.log.info("执行导航到货位报警记录的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到货位报警记录")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击货位报警记录菜单
        self.main_page.click_station_alarm_record_report_menu()
        
        self.log.info("成功导航到货位报警记录页面")
    
    def navigate_to_flowmeter_summary_report(self):
        """
        导航到流量计汇总报表 - 业务逻辑
        """
        self.log.info("执行导航到流量计汇总报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到流量计汇总报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击流量计汇总报表菜单
        self.main_page.click_flowmeter_summary_report_menu()
        
        self.log.info("成功导航到流量计汇总报表页面")
    
    def navigate_to_logistics_density_confirmation_issued_log_report(self):
        """
        导航到物流密度确认下发日志 - 业务逻辑
        """
        self.log.info("执行导航到物流密度确认下发日志的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到物流密度确认下发日志")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击物流密度确认下发日志菜单
        self.main_page.click_logistics_density_confirmation_issued_log_menu()
        
        self.log.info("成功导航到物流密度确认下发日志页面")
    
    def navigate_to_oil_application_work_report(self):
        """
        导航到发油作业报告单 - 业务逻辑
        """
        self.log.info("执行导航到发油作业报告单的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发油作业报告单")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发油作业报告单菜单
        self.main_page.click_oil_application_work_report_menu()
        
        self.log.info("成功导航到发油作业报告单页面")
    
    def navigate_to_data_upload_liquid_level_deepen_platform_report(self):
        """
        导航到数据上传液位深化平台报表 - 业务逻辑
        """
        self.log.info("执行导航到数据上传液位深化平台报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到数据上传液位深化平台报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击数据上传液位深化平台报表菜单
        self.main_page.click_data_upload_liquid_level_deepen_platform_report_menu()
        
        self.log.info("成功导航到数据上传液位深化平台报表页面")
    
    def navigate_to_temperature_density_record_inquiry_report(self):
        """
        导航到温度密度记录查询报表 - 业务逻辑
        """
        self.log.info("执行导航到温度密度记录查询报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到温度密度记录查询报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击温度密度记录查询报表菜单
        self.main_page.click_temperature_density_record_inquiry_report_menu()
        
        self.log.info("成功导航到温度密度记录查询报表页面")
    
    def navigate_to_online_oil_delivery_report(self):
        """
        导航到联机发油报表 - 业务逻辑
        """
        self.log.info("执行导航到联机发油报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到联机发油报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击联机发油报表菜单
        self.main_page.click_online_oil_delivery_report_menu()
        
        self.log.info("成功导航到联机发油报表页面")
    
    def navigate_to_offline_oil_delivery_report(self):
        """
        导航到脱机发油报表 - 业务逻辑
        """
        self.log.info("执行导航到脱机发油报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到脱机发油报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击脱机发油报表菜单
        self.main_page.click_offline_oil_delivery_report_menu()
        
        self.log.info("成功导航到脱机发油报表页面")
    
    def navigate_to_check_in_record_report(self):
        """
        导航到打卡记录查询报表 - 业务逻辑
        """
        self.log.info("执行导航到打卡记录查询报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到打卡记录查询报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击打卡记录查询报表菜单
        self.main_page.click_check_in_record_report_menu()
        
        self.log.info("成功导航到打卡记录查询报表页面")
    
    def navigate_to_flow_meter_loss_and_gain_report(self):
        """
        导航到流量计班结损溢报表 - 业务逻辑
        """
        self.log.info("执行导航到流量计班结损溢报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到流量计班结损溢报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击流量计班结损溢报表菜单
        self.main_page.click_flow_meter_loss_and_gain_report_menu()
        
        self.log.info("成功导航到流量计班结损溢报表页面")
    
    def navigate_to_operation_log_report(self):
        """
        导航到操作日志查询 - 业务逻辑
        """
        self.log.info("执行导航到操作日志查询的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到操作日志查询")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击操作日志查询菜单
        self.main_page.click_operation_log_report_menu()
        
        self.log.info("成功导航到操作日志查询页面")
    
    def navigate_to_outbound_daily_summary_report(self):
        """
        导航到出库日结表 - 业务逻辑
        """
        self.log.info("执行导航到出库日结表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到出库日结表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击出库日结表菜单
        self.main_page.click_outbound_daily_summary_report_menu()
        
        self.log.info("成功导航到出库日结表页面")
    
    def navigate_to_oil_dispensing_data_statistics_report(self):
        """
        导航到发油数据统计 - 业务逻辑
        """
        self.log.info("执行导航到发油数据统计的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发油数据统计")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发油数据统计菜单
        self.main_page.click_oil_dispensing_data_statistics_report_menu()
        
        self.log.info("成功导航到发油数据统计页面")
    
    def navigate_to_posting_intermediate_report(self):
        """
        导航到过账中间表 - 业务逻辑
        """
        self.log.info("执行导航到过账中间表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到过账中间表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击过账中间表菜单
        self.main_page.click_posting_intermediate_report_menu()
        
        self.log.info("成功导航到过账中间表页面")
    
    def navigate_to_logistics_density_confirmation_issued_report(self):
        """
        导航到物流密度确认下发 - 业务逻辑
        """
        self.log.info("执行导航到物流密度确认下发的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到物流密度确认下发")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击物流密度确认下发菜单
        self.main_page.click_logistics_density_confirmation_issued_report_menu()
        
        self.log.info("成功导航到物流密度确认下发页面")
    
    def navigate_to_oil_dispensing_density_inquiry_report(self):
        """
        导航到发油密度查询 - 业务逻辑
        """
        self.log.info("执行导航到发油密度查询的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发油密度查询")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击发油密度查询菜单
        self.main_page.click_oil_dispensing_density_inquiry_report_menu()
        
        self.log.info("成功导航到发油密度查询页面")
    
    def navigate_to_microcomputer_oil_dispensing_report(self):
        """
        导航到微机发油报表 - 业务逻辑
        """
        self.log.info("执行导航到微机发油报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到微机发油报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击微机发油报表菜单
        self.main_page.click_microcomputer_oil_dispensing_report_menu()
        
        self.log.info("成功导航到微机发油报表页面")
    
    def navigate_to_crane_position_statistics_report(self):
        """
        导航到鹤位统计报表 - 业务逻辑
        """
        self.log.info("执行导航到鹤位统计报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到鹤位统计报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击鹤位统计报表菜单
        self.main_page.click_crane_position_statistics_report_menu()
        
        self.log.info("成功导航到鹤位统计报表页面")
    
    def navigate_to_alarm_record_report(self):
        """
        导航到告警记录报表 - 业务逻辑
        """
        self.log.info("执行导航到告警记录报表的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到告警记录报表")
        
        # 点击报表管理主菜单
        self.main_page.click_report_management_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击告警记录报表菜单
        self.main_page.click_alarm_record_report_menu()
        
        self.log.info("成功导航到告警记录报表页面")
    

    # 系统工具菜单导航函数
    def navigate_to_working_card_management(self):
        """
        导航到工作卡管理 - 业务逻辑
        """
        self.log.info("执行导航到工作卡管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到工作卡管理")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击工作卡管理菜单
        self.main_page.click_working_card_management_menu()
        
        self.log.info("成功导航到工作卡管理页面")
    
    def navigate_to_key_card_management(self):
        """
        导航到钥匙卡管理 - 业务逻辑
        """
        self.log.info("执行导航到钥匙卡管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到钥匙卡管理")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击钥匙卡管理菜单
        self.main_page.click_key_card_management_menu()
        
        self.log.info("成功导航到钥匙卡管理页面")
    
    def navigate_to_joint_venture_card_management(self):
        """
        导航到合资卡管理 - 业务逻辑
        """
        self.log.info("执行导航到合资卡管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到合资卡管理")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击合资卡管理菜单
        self.main_page.click_joint_venture_card_management_menu()
        
        self.log.info("成功导航到合资卡管理页面")
    
    def navigate_to_managed_card_management(self):
        """
        导航到代管卡管理 - 业务逻辑
        """
        self.log.info("执行导航到代管卡管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到代管卡管理")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击代管卡管理菜单
        self.main_page.click_managed_card_management_menu()
        
        self.log.info("成功导航到代管卡管理页面")
    
    def navigate_to_vehicle_card_binding_management(self):
        """
        导航到车辆绑卡管理 - 业务逻辑
        """
        self.log.info("执行导航到车辆绑卡管理的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到车辆绑卡管理")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击车辆绑卡管理菜单
        self.main_page.click_vehicle_card_binding_management_menu()
        
        self.log.info("成功导航到车辆绑卡管理页面")
    
    def navigate_to_backup_database(self):
        """
        导航到备份数据库 - 业务逻辑
        """
        self.log.info("执行导航到备份数据库的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到备份数据库")
        
        # 点击系统工具主菜单
        self.main_page.click_system_tools_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击备份数据库菜单
        self.main_page.click_backup_database_menu()
        
        self.log.info("成功导航到备份数据库页面")
    
    # 帮助菜单导航函数
    def navigate_to_register(self):
        """
        导航到注册 - 业务逻辑
        """
        self.log.info("执行导航到注册的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到注册")
        
        # 点击帮助主菜单
        self.main_page.click_help_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击注册菜单
        self.main_page.click_register_menu()
        
        self.log.info("成功导航到注册页面")
    
    def navigate_to_version(self):
        """
        导航到版本 - 业务逻辑
        """
        self.log.info("执行导航到版本的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到版本")
        
        # 点击帮助主菜单
        self.main_page.click_help_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击版本菜单
        self.main_page.click_version_menu()
        
        self.log.info("成功导航到版本页面")
    
    def navigate_to_manual(self):
        """
        导航到手册 - 业务逻辑
        """
        self.log.info("执行导航到手册的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到手册")
        
        # 点击帮助主菜单
        self.main_page.click_help_parent_menu()
        
        # 关键改进：等待主菜单展开，给子菜单足够的显示时间
        self.log.info("等待子菜单展开...")
        time.sleep(1)  # 等待1秒让子菜单完全展开
        
        # 点击手册菜单
        self.main_page.click_manual_menu()
        
        self.log.info("成功导航到手册页面")
    
    # 左侧菜单栏导航函数
    def navigate_to_home_page(self):
        """
        导航到首页 - 业务逻辑
        """
        self.log.info("执行导航到首页的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到首页")
        
        # 点击首页菜单
        self.main_page.click_home_page_menu()
        
        self.log.info("成功导航到首页页面")
    
    def navigate_to_monitoring_page(self):
        """
        导航到监控页面 - 业务逻辑
        监控页面是右侧 panel，不是新窗口
        """
        import time
        self.log.info("执行导航到监控页面的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到监控页面")
        
        # 激活主窗口（确保窗口在前台，否则可能导致内容不渲染）
        self._activate_main_window()
        
        # 点击监控页面菜单
        self.main_page.click_monitoring_page_menu()
        
        # 等待监控页面 panel 出现（右侧区域，不会弹出新窗口）
        self.log.info("等待监控页面 panel 加载...")
        time.sleep(2)  # 增加等待时间，确保窗口切换完成
        
        # 再次激活窗口（点击菜单后窗口可能失去焦点）
        self._activate_main_window()
        
        # 切换到主窗口
        self.main_page.switch_to_window(title="装车管理系统", timeout=3)
        
        # 等待 panel1 元素出现（监控页面的特征元素）
        monitor_panel = self.main_page.wait_for_element(
            timeout=5,
            automation_id="panel1"
        )
        
        if monitor_panel:
            self.log.info("监控页面已加载（panel1 已出现）")
        else:
            self.log.warning("未检测到 panel1，但继续执行")
        
        self.log.info("成功导航到监控页面")
        return True
    
    def _activate_main_window(self):
        """激活主窗口，确保在前台"""
        try:
            from utils.driver_factory import _activate_window
            _activate_window("装车管理系统")
        except Exception as e:
            self.log.warning(f"窗口激活失败: {e}")
    
    def navigate_to_loading_and_invoicing(self):
        """
        导航到装车开票 - 业务逻辑
        如果当前已在装车开票窗口，直接切换并返回，避免重复点击菜单
        """
        import time
        self.log.info("执行导航到装车开票的业务逻辑")

        # 快速检查：是否已经在装车开票窗口
        from pageObject.invoiceManagement.invoice_management_page import InvoiceManagementPage
        quick_check_page = InvoiceManagementPage(self.main_page.driver, self.config_manager)
        if quick_check_page.switch_to_invoice_window():
            self.log.info("已在装车开票窗口，跳过菜单导航")
            return True

        # 不在目标窗口，执行完整导航流程
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到装车开票")

        self.main_page.click_loading_and_invoicing_menu()

        time.sleep(2)

        invoice_page = InvoiceManagementPage(self.main_page.driver, self.config_manager)

        for attempt in range(5):
            if invoice_page.switch_to_invoice_window():
                self.log.info("成功切换到装车开票窗口")
                return True
            time.sleep(1)

        self.log.error("无法切换到装车开票窗口")
        return False
    
    def navigate_to_customer_management_left(self):
        """
        导航到客户管理（左侧菜单） - 业务逻辑
        """
        self.log.info("执行导航到客户管理（左侧菜单）的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到客户管理（左侧菜单）")
        
        # 点击客户管理菜单
        self.main_page.click_customer_management_menu()
        
        self.log.info("成功导航到客户管理（左侧菜单）页面")
    
    def navigate_to_oil_information(self):
        """
        导航到油品信息 - 业务逻辑
        """
        self.log.info("执行导航到油品信息的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到油品信息")
        
        # 点击油品信息菜单
        self.main_page.click_oil_information_menu()
        
        self.log.info("成功导航到油品信息页面")
    
    def navigate_to_configuration_settings_left(self):
        """
        导航到配置设定（左侧菜单） - 业务逻辑
        """
        self.log.info("执行导航到配置设定（左侧菜单）的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到配置设定（左侧菜单）")
        
        # 点击配置设定菜单
        self.main_page.click_configuration_settings_menu()
        
        self.log.info("成功导航到配置设定（左侧菜单）页面")
    
    def navigate_to_station_ticket_verification_settings(self):
        """
        导航到货位验票设置 - 业务逻辑
        """
        self.log.info("执行导航到货位验票设置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到货位验票设置")
        
        # 点击货位验票设置菜单
        self.main_page.click_station_ticket_verification_settings_menu()
        
        self.log.info("成功导航到货位验票设置页面")
    
    def navigate_to_delivery_notification_setting(self):
        """
        导航到发货通知设置 - 业务逻辑
        """
        self.log.info("执行导航到发货通知设置的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到发货通知设置")
        
        # 点击发货通知设置菜单
        self.main_page.click_delivery_notification_setting_menu()
        
        self.log.info("成功导航到发货通知设置页面")
    
    def navigate_to_queuing_vehicle(self):
        """
        导航到排队车辆 - 业务逻辑
        """
        self.log.info("执行导航到排队车辆的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到排队车辆")
        
        # 点击排队车辆菜单
        self.main_page.click_queuing_vehicle_menu()
        
        self.log.info("成功导航到排队车辆页面")
    
    def navigate_to_emergency_stop(self):
        """
        导航到急停 - 业务逻辑
        """
        self.log.info("执行导航到急停的业务逻辑")
        
        # 验证当前页面是主页面
        if not self.main_page.is_main_page_present():
            raise Exception("当前不在主页面，无法导航到急停")
        
        # 点击急停菜单
        self.main_page.click_emergency_stop_menu()
        
        self.log.info("成功导航到急停页面")
    
    
  
    