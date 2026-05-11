"""
主页面 - 页面元素操作
只包含页面元素定位和基础交互，不包含业务逻辑
"""
import time
import allure

from .base_page import BasePage
from utils.logger import Logger
import logging


class MainPage(BasePage):
    """
    主页面 - 页面元素操作类
    """

    def __init__(self, driver, config_manager):
        """
        初始化主页面对象
        :param driver: WebDriver实例
        :param config_manager: 配置管理器实例
        """
        # 调用父类构造函数初始化驱动和配置管理器
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置,mian_page.yaml
        self.config = self.config_manager.load_page_config('main_page')

        # 检查配置加载是否成功
        if self.config is None:
            self.log.error("LoginPage: 配置加载失败")
            raise Exception("LoginPage: 配置加载失败")

        # 检查驱动是否初始化成功
        if self.driver is None:
            self.log.error("LoginPage: 驱动未初始化")
            raise Exception("LoginPage: 驱动未初始化")
        else:
            self.log.info("LoginPage: 驱动初始化成功")
            self.elements = self.config.get('elements', {})
            self.test_data = self.config.get('test_data', [])
            self.app_config = self.config.get('app_config', [])

            # 日志记录
            self.log = logging.getLogger("log")
            self.log.info("登录页面初始化完成")

    # 用户管理菜单导航函数
    def click_user_management_parent_menu(self):
        """点击用户管理主菜单"""
        with allure.step("点击用户管理主菜单"):
            return self._click_menu_element('user_management', 'user_management_parent_menu')

    def click_user_management_child_menu(self):
        """点击用户信息管理子菜单"""
        with allure.step("点击用户信息管理子菜单"):
            return self._click_menu_element('user_management', 'user_management_child_menu')

    def click_passWord_change_menu(self):
        """点击密码修改菜单"""
        with allure.step("点击密码修改菜单"):
            return self._click_menu_element('user_management', 'passWord_change_menu')

    def click_userName_change_menu(self):
        """点击用户名修改菜单"""
        with allure.step("点击用户名修改菜单"):
            return self._click_menu_element('user_management', 'userName_change_menu')

    def click_user_login_menu(self):
        """点击用户登录菜单"""
        with allure.step("点击用户登录菜单"):
            return self._click_menu_element('user_management', 'user_login_menu')

    def click_user_logout_menu(self):
        """点击退出登录菜单"""
        with allure.step("点击退出登录菜单"):
            return self._click_menu_element('user_management', 'user_logout_menu')

    # 系统管理菜单导航函数
    def click_system_management_parent_menu(self):
        """点击系统管理主菜单"""
        return self._click_menu_element('system_management', 'system_management_parent_menu')

    def click_customer_menu(self):
        """点击客户信息管理菜单"""
        return self._click_menu_element('system_management', 'customer_menu')

    def click_serial_port_menu(self):
        """点击串口信息管理菜单"""
        return self._click_menu_element('system_management', 'serial_port_menu')

    def click_station_menu(self):
        """点击货位信息管理菜单"""
        return self._click_menu_element('system_management', 'station_menu')

    def click_oil_menu(self):
        """点击油品信息管理菜单"""
        return self._click_menu_element('system_management', 'oil_menu')

    def click_configuration_settings_menu(self):
        """点击配置设定菜单"""
        return self._click_menu_element('system_management', 'configuration_settings_menu')

    def click_oil_density_menu(self):
        """点击发油密度菜单"""
        return self._click_menu_element('system_management', 'oil_density_menu')

    def click_station_tank_menu(self):
        """点击货位油罐配置菜单"""
        return self._click_menu_element('system_management', 'station_tank_menu')

    def click_oil_distribution_rules_menu(self):
        """点击发油规则设置菜单"""
        return self._click_menu_element('system_management', 'oil_distribution_rules_menu')

    def click_system_decimal_settings_menu(self):
        """点击系统单位小数设置菜单"""
        return self._click_menu_element('system_management', 'system_decimal_settings_menu')

    def click_AI_configuration_menu(self):
        """点击AI配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu')

    def click_marginal_box_menu(self):
        """点击边缘盒子配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'marginal_box_menu')

    def click_job_position_menu(self):
        """点击作业位配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'job_position_menu')

    def click_camera_menu(self):
        """点击摄像头配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'camera_menu')

    def click_claude_server_menu(self):
        """点击云服务器配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'claude_server_menu')

    def click_self_developed_algorithm_parameter_menu(self):
        """点击自研算法配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'self_developed_algorithm_parameter_menu')

    def click_self_developed_AI_task_start_and_stop_menu(self):
        """点击自研算法配置菜单"""
        return self._click_menu_element('system_management', 'AI_configuration_menu', 'child_menus', 'self_developed_AI_task_start_and_stop_menu')

    def click_station_oil_extraction_limit_menu(self):
        """点击货位提油限制菜单"""
        return self._click_menu_element('system_management', 'station_oil_extraction_limit_menu')

    def click_car_menu(self):
        """点击车辆管理菜单"""
        return self._click_menu_element('system_management', 'car_menu')

    def click_document_menu(self):
        """点击文档管理菜单"""
        return self._click_menu_element('system_management', 'document_menu')

    def click_score_menu(self):
        """点击评分管理菜单"""
        return self._click_menu_element('system_management', 'score_menu')

    def click_voice_menu(self):
        """点击语音播报设置菜单"""
        return self._click_menu_element('system_management', 'voice_menu')

    # ========== 高级导航方法 ==========

    def click_device_menu(self):
        """点击设备信息管理菜单"""
        return self._click_menu_element('system_management', 'device_menu')

    # 装车仪菜单导航函数
    def click_loading_instrument_parent_menu(self):
        """点击装车仪主菜单"""
        return self._click_menu_element('loading_instrument', 'loading_instrument_parent_menu')

    def click_read_write_standard_density_menu(self):
        """点击读写标准密度菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_standard_density_menu')

    def click_read_write_ethanol_ratio_menu(self):
        """点击读写乙醇比菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_ethanol_ratio_menu')

    def click_read_write_flow_rate_menu(self):
        """点击读写流速参数菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_flow_rate_menu')

    def click_read_write_cumulative_amount_menu(self):
        """点击读写累积量菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_cumulative_amount_menu')

    def click_read_write_pulse_parameters_menu(self):
        """点击读写脉冲参数菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_pulse_parameters_menu')

    def click_read_write_temperature_change_menu(self):
        """点击读写温变参数菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_temperature_change_menu')

    def click_read_write_passWrod_menu(self):
        """点击读写密码菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_passWrod_menu')

    def click_read_history_menu(self):
        """点击读写历史记录菜单"""
        return self._click_menu_element('loading_instrument', 'read_history_menu')

    def click_read_write_average_temperature_menu(self):
        """点击读写平均温度修正量菜单"""
        return self._click_menu_element('loading_instrument', 'read_write_average_temperature_menu')

    def click_additive_menu(self):
        """点击添加剂菜单"""
        return self._click_menu_element('loading_instrument', 'additive_menu')

    def click_read_write_additive_ratio_menu(self):
        """点击读写添加剂配比菜单"""
        return self._click_menu_element('loading_instrument', 'additive_menu', 'child_menus', 'read_write_additive_ratio_menu')

    def click_read_write_additive_meter_menu(self):
        """点击读写添加剂计密菜单"""
        return self._click_menu_element('loading_instrument', 'additive_menu', 'child_menus', 'read_write_additive_meter_menu')

    # 报表管理菜单导航函数
    def click_report_management_parent_menu(self):
        """点击报表管理主菜单"""
        return self._click_menu_element('report_management', 'report_management_parent_menu')

    def click_online_oil_delivery_report_menu(self):
        """点击联机发油报表菜单"""
        return self._click_menu_element('report_management', 'online_oil_delivery_report_menu')

    def click_offline_oil_delivery_report_menu(self):
        """点击脱机发油报表菜单"""
        return self._click_menu_element('report_management', 'offline_oil_delivery_report_menu')

    def click_check_in_record_report_menu(self):
        """点击打卡记录查询报表菜单"""
        return self._click_menu_element('report_management', 'check_in_record_report_menu')

    def click_flow_meter_loss_and_gain_report_menu(self):
        """点击流量计班结损溢报表菜单"""
        return self._click_menu_element('report_management', 'flow_meter_loss_and_gain_report_menu')

    def click_operation_log_report_menu(self):
        """点击操作日志查询菜单"""
        return self._click_menu_element('report_management', 'operation_log_report_menu')

    def click_outbound_daily_summary_report_menu(self):
        """点击出库日结表菜单"""
        return self._click_menu_element('report_management', 'outbound_daily_summary_report_menu')

    def click_oil_dispensing_data_statistics_report_menu(self):
        """点击发油数据统计菜单"""
        return self._click_menu_element('report_management', 'oil_dispensing_data_statistics_report_menu')

    def click_posting_intermediate_report_menu(self):
        """点击过账中间表菜单"""
        return self._click_menu_element('report_management', 'posting_intermediate_report_menu')

    def click_logistics_density_confirmation_issued_report_menu(self):
        """点击物流密度确认下发菜单"""
        return self._click_menu_element('report_management', 'logistics_density_confirmation_issued_report_menu')

    def click_logistics_density_confirmation_issued_log_menu(self):
        """点击物流密度确认下发日志菜单"""
        return self._click_menu_element('report_management', 'logistics_density_confirmation_issued_log_menu')

    def click_oil_dispensing_density_inquiry_report_menu(self):
        """点击发油密度查询菜单"""
        return self._click_menu_element('report_management', 'oil_dispensing_density_inquiry_report_menu')

    def click_microcomputer_oil_dispensing_report_menu(self):
        """点击微机发油报表菜单"""
        return self._click_menu_element('report_management', 'microcomputer_oil_dispensing_report_menu')

    def click_oil_application_work_report_menu(self):
        """点击发油作业报告单菜单"""
        return self._click_menu_element('report_management', 'oil_application_work_report_menu')

    def click_data_upload_liquid_level_deepen_platform_report_menu(self):
        """点击数据上传液位深化平台报表菜单"""
        return self._click_menu_element('report_management', 'data_upload_liquid_level_deepen_platform_report_menu')

    def click_temperature_density_record_inquiry_report_menu(self):
        """点击温度密度记录查询报表菜单"""
        return self._click_menu_element('report_management', 'temperature_density_record_inquiry_report_menu')

    def click_oil_dispensing_loss_and_gain_report_menu(self):
        """点击发油损溢报表菜单"""
        return self._click_menu_element('report_management', 'oil_dispensing_loss_and_gain_report_menu')

    def click_alarm_record_report_menu(self):
        """点击告警记录报表菜单"""
        return self._click_menu_element('report_management', 'alarm_record_report_menu')

    def click_crane_position_statistics_report_menu(self):
        """点击鹤位统计报表菜单"""
        return self._click_menu_element('report_management', 'crane_position_statistics_report_menu')

    def click_distribution_record_report_menu(self):
        """点击发放记录报表菜单"""
        return self._click_menu_element('report_management', 'distribution_record_report_menu')

    def click_oil_dispensing_platform_statistics_report_menu(self):
        """点击付油台提油统计表菜单"""
        return self._click_menu_element('report_management', 'oil_dispensing_platform_statistics_report_menu')

    def click_oil_depot_flowmeter_oil_dispensing_report_menu(self):
        """点击油库流量计发油记录菜单"""
        return self._click_menu_element('report_management', 'oil_depot_flowmeter_oil_dispensing_report_menu')

    def click_station_alarm_record_report_menu(self):
        """点击货位报警记录菜单"""
        return self._click_menu_element('report_management', 'station_alarm_record_report_menu')

    def click_flowmeter_summary_report_menu(self):
        """点击流量计汇总报表菜单"""
        return self._click_menu_element('report_management', 'flowmeter_summary_report_menu')

    # 系统工具菜单导航函数
    def click_system_tools_parent_menu(self):
        """点击系统工具主菜单"""
        return self._click_menu_element('system_tools', 'system_tools_parent_menu')

    def click_working_card_management_menu(self):
        """点击工作卡管理菜单"""
        return self._click_menu_element('system_tools', 'working_card_management_menu')

    def click_key_card_management_menu(self):
        """点击钥匙卡管理菜单"""
        return self._click_menu_element('system_tools', 'key_card_management_menu')

    def click_joint_venture_card_management_menu(self):
        """点击合资卡管理菜单"""
        return self._click_menu_element('system_tools', 'joint_venture_card_management_menu')

    def click_managed_card_management_menu(self):
        """点击代管卡管理菜单"""
        return self._click_menu_element('system_tools', 'managed_card_management_menu')

    def click_vehicle_card_binding_management_menu(self):
        """点击车辆绑卡管理菜单"""
        return self._click_menu_element('system_tools', 'vehicle_card_binding_management_menu')

    def click_backup_database_menu(self):
        """点击备份数据库菜单"""
        return self._click_menu_element('system_tools', 'backup_database_menu')

    # 帮助菜单导航函数
    def click_help_parent_menu(self):
        """点击帮助主菜单"""
        return self._click_menu_element('help', 'help_parent_menu')

    def click_register_menu(self):
        """点击注册菜单"""
        return self._click_menu_element('help', 'register_menu')

    def click_version_menu(self):
        """点击版本菜单"""
        return self._click_menu_element('help', 'version_menu')

    def click_manual_menu(self):
        """点击手册菜单"""
        return self._click_menu_element('help', 'manual_menu')

    # 左侧菜单栏导航函数
    def click_home_page_menu(self):
        """点击首页菜单"""
        return self._click_menu_element('left_menu', 'home_page_menu')

    def click_monitoring_page_menu(self):
        """点击监控页面菜单"""
        return self._click_menu_element('left_menu', 'monitoring_page_menu')

    def click_loading_and_invoicing_menu(self):
        """点击装车开票菜单"""
        return self._click_menu_element('left_menu', 'loading_and_invoicing_menu')

    def click_customer_management_menu(self):
        """点击客户管理菜单"""
        return self._click_menu_element('left_menu', 'customer_management_menu')

    def click_oil_information_menu(self):
        """点击油品信息菜单"""
        return self._click_menu_element('left_menu', 'oil_information_menu')

    def click_configuration_settings_menu(self):
        """点击配置设定菜单"""
        return self._click_menu_element('left_menu', 'configuration_settings_menu')

    def click_station_ticket_verification_settings_menu(self):
        """点击货位验票设置菜单"""
        return self._click_menu_element('left_menu', 'station_ticket_verification_settings_menu')

    def click_delivery_notification_setting_menu(self):
        """点击发货通知设置菜单"""
        return self._click_menu_element('left_menu', 'delivery_notification_setting_menu')

    def click_queuing_vehicle_menu(self):
        """点击排队车辆菜单"""
        return self._click_menu_element('left_menu', 'queuing_vehicle_menu')

    def click_emergency_stop_menu(self):
        """点击急停菜单"""
        return self._click_menu_element('left_menu', 'emergency_stop_menu')

    def _click_menu_element(self, menu_category, menu_name, *sub_menu_path):
        """
        通用的菜单点击方法
        :param menu_category: 菜单类别（如 user_management, system_management 等）
        :param menu_name: 菜单名称
        :param sub_menu_path: 多级菜单路径（可选）
        :return: 操作是否成功
        """
        try:
            if not self.driver:
                self.log.error("驱动未初始化，无法执行菜单点击操作")
                return False

            # 从self.elements中获取菜单定位器
            menu_config = self.elements.get(menu_category, {})
            if sub_menu_path:
                # 处理多级菜单路径
                current_config = menu_config
                for path_item in sub_menu_path:
                    current_config = current_config.get(path_item, {})
                menu_locator = current_config.get(menu_name, {})
            else:
                menu_locator = menu_config.get(menu_name, {})

            if not menu_locator:
                self.log.error(f"未找到菜单定位器: {menu_category} -> {menu_name}")
                return False

            self.log.info(f"尝试点击菜单: {menu_category} -> {menu_name}")
            element = self.locate_element(**menu_locator)
            if element:
                self.log.info(f"成功定位到菜单元素")
                element.click()
                self.log.info(f"点击菜单成功: {menu_category} -> {menu_name}")
                return True
            else:
                self.log.error(f"未找到菜单元素")
                return False

        except Exception as e:
            self.log.error(f"菜单点击操作发生异常: {str(e)}")
            return False


    def is_main_page_present(self):
        """
        检查主界面是否存在
        通过验证主界面上的关键元素是否可见来判断
        :return: True - 主界面存在, False - 主界面不存在
        """
        try:
            # 获取主界面上的关键元素，这里使用用户管理主菜单作为示例
            # 可以根据实际情况选择更合适的元素
            #添加等待，等待主界面加载

            main_menu_element = self.elements.get('user_management', {}).get('user_management_parent_menu')
            self.log.info("等待主界面加载")
            self.wait_for_element(timeout=3,**main_menu_element)
            
            if main_menu_element and self.locate_element(**main_menu_element):
                self.log.info("主界面存在，验证通过")
                return True
            else:
                self.log.warning("主界面不存在，未能找到关键元素")
                return False
        
        except Exception as e:
            self.log.error(f"检查主界面是否存在时发生异常: {str(e)}")
            return False


