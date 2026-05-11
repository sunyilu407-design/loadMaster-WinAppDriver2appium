"""
导航能力混入类 - 为Handler提供统一的导航功能
"""

import logging
from utils.super_handler_factory import create_handler


class NavigationMixin:
    """
    导航能力混入类
    为业务Handler提供统一的导航功能，通过MainHandler实现所有导航操作
    """

    def __init__(self):
        """
        初始化导航混入
        自动创建MainHandler实例来提供导航功能
        """
        self.log = logging.getLogger(f"{self.__class__.__name__}_navigation")
        self._main_handler = None

    def _get_main_handler(self):
        """
        获取主处理器实例（惰性初始化）

        Returns:
            MainHandler实例
        """
        if self._main_handler is None:
            # 尝试重用当前实例的driver（如果存在）
            driver = getattr(self, 'driver', None)
            if driver is None:
                # 尝试从页面对象获取driver
                if hasattr(self, 'page_instance') and self.page_instance is not None:
                    driver = getattr(self.page_instance, 'driver', None)

            if driver is not None:
                self._main_handler = create_handler('main_page', driver=driver)
                self.log.info("✅ 创建主处理器实例用于导航（重用现有driver）")
            else:
                self._main_handler = create_handler('main_page')
                self.log.info("✅ 创建主处理器实例用于导航")
        return self._main_handler

    # ========== 用户管理菜单导航 ==========
    def navigate_to_user_info_management(self):
        """导航到用户信息管理"""
        return self._get_main_handler().navigate_to_user_info_management()

    def navigate_to_password_change(self):
        """导航到密码修改"""
        return self._get_main_handler().navigate_to_password_change()

    def navigate_to_username_change(self):
        """导航到用户名修改"""
        return self._get_main_handler().navigate_to_username_change()

    def navigate_to_user_login(self):
        """导航到用户登录"""
        return self._get_main_handler().navigate_to_user_login()

    def navigate_to_user_logout(self):
        """导航到退出登录"""
        return self._get_main_handler().navigate_to_user_logout()

    # ========== 系统管理菜单导航 ==========
    def navigate_to_customer_management(self):
        """导航到客户信息管理"""
        return self._get_main_handler().navigate_to_customer_management()

    def navigate_to_serial_port_management(self):
        """导航到串口信息管理"""
        return self._get_main_handler().navigate_to_serial_port_management()

    def navigate_to_station_management(self):
        """导航到货位信息管理"""
        return self._get_main_handler().navigate_to_station_management()

    def navigate_to_oil_management(self):
        """导航到油品信息管理"""
        return self._get_main_handler().navigate_to_oil_management()

    def navigate_to_configuration_settings(self):
        """导航到配置设定"""
        return self._get_main_handler().navigate_to_configuration_settings()

    def navigate_to_config_settings(self):
        """导航到配置设定（专用）"""
        return self._get_main_handler().navigate_to_configuration_settings()

    def navigate_to_invoice_management(self):
        """导航到装车开票"""
        return self._get_main_handler().navigate_to_loading_and_invoicing()

    def navigate_to_oil_density(self):
        """导航到发油密度"""
        return self._get_main_handler().navigate_to_oil_density()

    def navigate_to_station_tank_configuration(self):
        """导航到货位油罐配置"""
        return self._get_main_handler().navigate_to_station_tank_configuration()

    def navigate_to_oil_distribution_rules(self):
        """导航到发油规则设置"""
        return self._get_main_handler().navigate_to_oil_distribution_rules()

    def navigate_to_system_decimal_settings(self):
        """导航到系统单位小数设置"""
        return self._get_main_handler().navigate_to_system_decimal_settings()

    def navigate_to_marginal_box_configuration(self):
        """导航到边缘盒子配置"""
        return self._get_main_handler().navigate_to_marginal_box_configuration()

    def navigate_to_job_position_configuration(self):
        """导航到作业位配置"""
        return self._get_main_handler().navigate_to_job_position_configuration()

    def navigate_to_camera_configuration(self):
        """导航到摄像头配置"""
        return self._get_main_handler().navigate_to_camera_configuration()

    def navigate_to_claude_server_configuration(self):
        """导航到云服务器配置"""
        return self._get_main_handler().navigate_to_claude_server_configuration()

    def navigate_to_self_developed_algorithm_parameter(self):
        """导航到自研算法配置"""
        return self._get_main_handler().navigate_to_self_developed_algorithm_parameter()

    def navigate_to_self_developed_AI_task_start_and_stop(self):
        """导航到自研算法任务启停"""
        return self._get_main_handler().navigate_to_self_developed_AI_task_start_and_stop()

    def navigate_to_station_oil_extraction_limit(self):
        """导航到货位提油限制"""
        return self._get_main_handler().navigate_to_station_oil_extraction_limit()

    def navigate_to_car_management(self):
        """导航到车辆管理"""
        return self._get_main_handler().navigate_to_car_management()

    def navigate_to_document_management(self):
        """导航到文档管理"""
        return self._get_main_handler().navigate_to_document_management()

    def navigate_to_score_management(self):
        """导航到评分管理"""
        return self._get_main_handler().navigate_to_score_management()

    def navigate_to_voice_settings(self):
        """导航到语音播报设置"""
        return self._get_main_handler().navigate_to_voice_settings()

    def navigate_to_device_management(self):
        """导航到设备信息管理"""
        return self._get_main_handler().navigate_to_device_management()

    # ========== 装车仪菜单导航 ==========
    def navigate_to_read_write_standard_density(self):
        """导航到读写标准密度"""
        return self._get_main_handler().navigate_to_read_write_standard_density()

    def navigate_to_read_write_ethanol_ratio(self):
        """导航到读写乙醇比"""
        return self._get_main_handler().navigate_to_read_write_ethanol_ratio()

    def navigate_to_read_write_flow_rate(self):
        """导航到读写流速参数"""
        return self._get_main_handler().navigate_to_read_write_flow_rate()

    def navigate_to_read_write_cumulative_amount(self):
        """导航到读写累积量"""
        return self._get_main_handler().navigate_to_read_write_cumulative_amount()

    def navigate_to_read_write_pulse_parameters(self):
        """导航到读写脉冲参数"""
        return self._get_main_handler().navigate_to_read_write_pulse_parameters()

    def navigate_to_read_write_temperature_change(self):
        """导航到读写温变参数"""
        return self._get_main_handler().navigate_to_read_write_temperature_change()

    def navigate_to_read_write_password(self):
        """导航到读写密码"""
        return self._get_main_handler().navigate_to_read_write_password()

    def navigate_to_read_history(self):
        """导航到读写历史记录"""
        return self._get_main_handler().navigate_to_read_history()

    def navigate_to_read_write_average_temperature(self):
        """导航到读写平均温度修正量"""
        return self._get_main_handler().navigate_to_read_write_average_temperature()

    def navigate_to_read_write_additive_ratio(self):
        """导航到读写添加剂配比"""
        return self._get_main_handler().navigate_to_read_write_additive_ratio()

    def navigate_to_read_write_additive_meter(self):
        """导航到读写添加剂计密"""
        return self._get_main_handler().navigate_to_read_write_additive_meter()

    # ========== 报表管理菜单导航 ==========
    def navigate_to_distribution_record_report(self):
        """导航到发放记录报表"""
        return self._get_main_handler().navigate_to_distribution_record_report()

    def navigate_to_oil_dispensing_platform_statistics_report(self):
        """导航到付油台提油统计表"""
        return self._get_main_handler().navigate_to_oil_dispensing_platform_statistics_report()

    def navigate_to_oil_depot_flowmeter_oil_dispensing_report(self):
        """导航到油库流量计发油记录"""
        return self._get_main_handler().navigate_to_oil_depot_flowmeter_oil_dispensing_report()

    def navigate_to_station_alarm_record_report(self):
        """导航到货位报警记录"""
        return self._get_main_handler().navigate_to_station_alarm_record_report()

    def navigate_to_flowmeter_summary_report(self):
        """导航到流量计汇总报表"""
        return self._get_main_handler().navigate_to_flowmeter_summary_report()

    def navigate_to_logistics_density_confirmation_issued_log_report(self):
        """导航到物流密度确认下发日志"""
        return self._get_main_handler().navigate_to_logistics_density_confirmation_issued_log_report()

    def navigate_to_oil_application_work_report(self):
        """导航到发油作业报告单"""
        return self._get_main_handler().navigate_to_oil_application_work_report()

    def navigate_to_data_upload_liquid_level_deepen_platform_report(self):
        """导航到数据上传液位深化平台报表"""
        return self._get_main_handler().navigate_to_data_upload_liquid_level_deepen_platform_report()

    def navigate_to_temperature_density_record_inquiry_report(self):
        """导航到温度密度记录查询报表"""
        return self._get_main_handler().navigate_to_temperature_density_record_inquiry_report()

    def navigate_to_online_oil_delivery_report(self):
        """导航到联机发油报表"""
        return self._get_main_handler().navigate_to_online_oil_delivery_report()

    def navigate_to_offline_oil_delivery_report(self):
        """导航到脱机发油报表"""
        return self._get_main_handler().navigate_to_offline_oil_delivery_report()

    def navigate_to_check_in_record_report(self):
        """导航到打卡记录查询报表"""
        return self._get_main_handler().navigate_to_check_in_record_report()

    def navigate_to_flow_meter_loss_and_gain_report(self):
        """导航到流量计班结损溢报表"""
        return self._get_main_handler().navigate_to_flow_meter_loss_and_gain_report()

    def navigate_to_operation_log_report(self):
        """导航到操作日志查询"""
        return self._get_main_handler().navigate_to_operation_log_report()

    def navigate_to_outbound_daily_summary_report(self):
        """导航到出库日结表"""
        return self._get_main_handler().navigate_to_outbound_daily_summary_report()

    def navigate_to_oil_dispensing_data_statistics_report(self):
        """导航到发油数据统计"""
        return self._get_main_handler().navigate_to_oil_dispensing_data_statistics_report()

    def navigate_to_posting_intermediate_report(self):
        """导航到过账中间表"""
        return self._get_main_handler().navigate_to_posting_intermediate_report()

    def navigate_to_logistics_density_confirmation_issued_report(self):
        """导航到物流密度确认下发"""
        return self._get_main_handler().navigate_to_logistics_density_confirmation_issued_report()

    def navigate_to_oil_dispensing_density_inquiry_report(self):
        """导航到发油密度查询"""
        return self._get_main_handler().navigate_to_oil_dispensing_density_inquiry_report()

    def navigate_to_microcomputer_oil_dispensing_report(self):
        """导航到微机发油报表"""
        return self._get_main_handler().navigate_to_microcomputer_oil_dispensing_report()

    def navigate_to_crane_position_statistics_report(self):
        """导航到鹤位统计报表"""
        return self._get_main_handler().navigate_to_crane_position_statistics_report()

    def navigate_to_alarm_record_report(self):
        """导航到告警记录报表"""
        return self._get_main_handler().navigate_to_alarm_record_report()

    # ========== 系统工具菜单导航 ==========
    def navigate_to_working_card_management(self):
        """导航到工作卡管理"""
        return self._get_main_handler().navigate_to_working_card_management()

    def navigate_to_key_card_management(self):
        """导航到钥匙卡管理"""
        return self._get_main_handler().navigate_to_key_card_management()

    def navigate_to_joint_venture_card_management(self):
        """导航到合资卡管理"""
        return self._get_main_handler().navigate_to_joint_venture_card_management()

    def navigate_to_managed_card_management(self):
        """导航到代管卡管理"""
        return self._get_main_handler().navigate_to_managed_card_management()

    def navigate_to_vehicle_card_binding_management(self):
        """导航到车辆绑卡管理"""
        return self._get_main_handler().navigate_to_vehicle_card_binding_management()

    def navigate_to_backup_database(self):
        """导航到备份数据库"""
        return self._get_main_handler().navigate_to_backup_database()

    # ========== 帮助菜单导航 ==========
    def navigate_to_register(self):
        """导航到注册"""
        return self._get_main_handler().navigate_to_register()

    def navigate_to_version(self):
        """导航到版本"""
        return self._get_main_handler().navigate_to_version()

    def navigate_to_manual(self):
        """导航到手册"""
        return self._get_main_handler().navigate_to_manual()

    # ========== 左侧菜单栏导航 ==========
    def navigate_to_home_page(self):
        """导航到首页"""
        return self._get_main_handler().navigate_to_home_page()

    def navigate_to_monitoring_page(self):
        """导航到监控页面"""
        return self._get_main_handler().navigate_to_monitoring_page()

    def navigate_to_loading_and_invoicing(self):
        """导航到装车开票"""
        return self._get_main_handler().navigate_to_loading_and_invoicing()

    def navigate_to_customer_management_left(self):
        """导航到客户管理（左侧菜单）"""
        return self._get_main_handler().navigate_to_customer_management_left()

    def navigate_to_oil_information(self):
        """导航到油品信息"""
        return self._get_main_handler().navigate_to_oil_information()

    def navigate_to_configuration_settings_left(self):
        """导航到配置设定（左侧菜单）"""
        return self._get_main_handler().navigate_to_configuration_settings_left()

    def navigate_to_station_ticket_verification_settings(self):
        """导航到货位验票设置"""
        return self._get_main_handler().navigate_to_station_ticket_verification_settings()

    def navigate_to_delivery_notification_setting(self):
        """导航到发货通知设置"""
        return self._get_main_handler().navigate_to_delivery_notification_setting()

    def navigate_to_queuing_vehicle(self):
        """导航到排队车辆"""
        return self._get_main_handler().navigate_to_queuing_vehicle()

    def navigate_to_emergency_stop(self):
        """导航到急停"""
        return self._get_main_handler().navigate_to_emergency_stop()

    # ========== 通用方法 ==========
    def is_main_page_present(self):
        """检查主页面是否存在"""
        return self._get_main_handler().is_main_page_present()

