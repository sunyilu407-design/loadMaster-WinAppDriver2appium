"""
监控管理业务逻辑处理类
负责监控和远程控制的业务逻辑流程封装
"""

import logging
import allure
import time
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class MonitorManagementHandler(BaseHandler, NavigationMixin):
    """
    监控管理 Handler - 业务逻辑处理类
    职责：组合 PageObject 方法实现复杂业务流

    主要功能：
    - 双击货位打开远程设定窗口
    - 远程启动/暂停/结束发油操作
    - 获取货位状态信息
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
        self.monitor_page = self.page_instance

        logging.info("MonitorManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 通用辅助方法 ====================
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待操作提示窗口"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.monitor_page.switch_to_operation_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待操作提示窗口超时")
        return False

    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        """
        处理操作提示窗口

        Args:
            action: 'confirm'(确认/是) / 'cancel'(取消/否) / 'quit'(退出)
            timeout: 超时时间

        Returns:
            bool: 是否成功处理
        """
        if not self.wait_for_operation_window(timeout):
            return False

        if action == 'confirm':
            return self.monitor_page.click_operation_window_confirm_button()
        elif action == 'cancel':
            return self.monitor_page.click_operation_window_cancel_button()
        elif action == 'quit':
            return self.monitor_page.click_operation_window_quit_button()

        self.log.error(f"未知操作: {action}")
        return False

    # ==================== 业务流方法：打开远程设定 ====================
    @allure.step("打开远程设定窗口")
    def open_remote_control(self, station_no, timeout=10.0):
        """
        双击货位控件打开远程设定窗口

        Args:
            station_no: 货位号（如 '01', '02'）
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'bill_num': str}
        """
        try:
            # 1. 切换到监控页面
            self.monitor_page.switch_to_monitor_window()

            # 2. 双击货位控件
            with allure.step(f"双击货位 {station_no} 打开远程设定"):
                if not self.monitor_page.double_click_station_control(station_no):
                    return {'success': False, 'error': f'双击货位 {station_no} 失败'}

            # 3. 等待远程设定窗口出现
            with allure.step("等待远程设定窗口出现"):
                end_time = time.time() + timeout
                while time.time() < end_time:
                    if self.monitor_page.switch_to_remote_control_window():
                        self.log.info(f"远程设定窗口已打开")
                        break
                    time.sleep(0.5)
                else:
                    return {'success': False, 'error': '等待远程设定窗口超时'}

            # 4. 获取提单号（用于验证）
            bill_num = self.monitor_page.get_remote_bill_num()
            self.log.info(f"当前提单号: {bill_num}")

            return {
                'success': True,
                'bill_num': bill_num,
                'station_no': station_no
            }

        except Exception as e:
            self.log.error(f"打开远程设定窗口异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：远程启动发油 ====================
    @allure.step("远程启动发油")
    def remote_start_oil(self, station_no, confirm=True, timeout=10.0):
        """
        远程启动发油操作

        Args:
            station_no: 货位号
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'message': str}
        """
        try:
            # 1. 打开远程设定窗口
            result = self.open_remote_control(station_no, timeout)
            if not result['success']:
                return result

            # 2. 获取当前状态
            load_mode = self.monitor_page.get_remote_load_mode()
            plan_oil = self.monitor_page.get_remote_plan_out_oil()
            self.log.info(f"当前发油模式: {load_mode}, 计划发油量: {plan_oil}")

            # 3. 点击启动按钮
            with allure.step("点击启动按钮"):
                if not self.monitor_page.click_remote_start_button():
                    return {'success': False, 'error': '点击启动按钮失败'}

            # 4. 等待处理
            time.sleep(1)

            # 5. 检查是否有操作确认弹窗
            if self.monitor_page.switch_to_operation_window():
                with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                    return self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout)

            return {
                'success': True,
                'message': '启动发油指令已发送'
            }

        except Exception as e:
            self.log.error(f"远程启动发油异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：远程暂停发油 ====================
    @allure.step("远程暂停发油")
    def remote_pause_oil(self, station_no, confirm=True, timeout=10.0):
        """
        远程暂停发油操作

        Args:
            station_no: 货位号
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'message': str}
        """
        try:
            # 1. 打开远程设定窗口
            result = self.open_remote_control(station_no, timeout)
            if not result['success']:
                return result

            # 2. 点击暂停按钮
            with allure.step("点击暂停按钮"):
                if not self.monitor_page.click_remote_pause_button():
                    return {'success': False, 'error': '点击暂停按钮失败'}

            # 3. 等待处理
            time.sleep(1)

            # 4. 检查是否有操作确认弹窗
            if self.monitor_page.switch_to_operation_window():
                with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                    return self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout)

            return {
                'success': True,
                'message': '暂停发油指令已发送'
            }

        except Exception as e:
            self.log.error(f"远程暂停发油异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：远程结束发油 ====================
    @allure.step("远程结束发油")
    def remote_end_oil(self, station_no, confirm=True, timeout=10.0):
        """
        远程结束发油操作

        Args:
            station_no: 货位号
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'message': str}
        """
        try:
            # 1. 打开远程设定窗口
            result = self.open_remote_control(station_no, timeout)
            if not result['success']:
                return result

            # 2. 点击结束按钮
            with allure.step("点击结束按钮"):
                if not self.monitor_page.click_remote_end_button():
                    return {'success': False, 'error': '点击结束按钮失败'}

            # 3. 等待处理
            time.sleep(1)

            # 4. 检查是否有操作确认弹窗
            if self.monitor_page.switch_to_operation_window():
                with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                    return self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout)

            return {
                'success': True,
                'message': '结束发油指令已发送'
            }

        except Exception as e:
            self.log.error(f"远程结束发油异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：设置发油模式 ====================
    @allure.step("设置发油模式并验证")
    def set_load_mode_and_verify(self, station_no, load_mode, confirm=True, timeout=10.0):
        """
        设置发油模式并验证结果

        Args:
            station_no: 货位号
            load_mode: 新的发油模式
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'message': str}
        """
        try:
            # 1. 打开远程设定窗口
            result = self.open_remote_control(station_no, timeout)
            if not result['success']:
                return result

            # 2. 选择发油模式
            with allure.step(f"设置发油模式: {load_mode}"):
                if not self.monitor_page.select_remote_load_mode(load_mode):
                    return {'success': False, 'error': f'选择发油模式 {load_mode} 失败'}

            # 3. 点击设定按钮
            with allure.step("点击设定按钮"):
                if not self.monitor_page.click_remote_set_button():
                    return {'success': False, 'error': '点击设定按钮失败'}

            # 4. 等待处理
            time.sleep(1)

            # 5. 检查是否有操作确认弹窗
            if self.monitor_page.switch_to_operation_window():
                with allure.step(f"处理操作确认弹窗 ({'确认' if confirm else '取消'})"):
                    return self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout)

            # 6. 验证设置结果
            current_mode = self.monitor_page.get_remote_load_mode()
            if load_mode in current_mode or current_mode in load_mode:
                return {
                    'success': True,
                    'message': f'发��模式已设置为 {load_mode}'
                }
            else:
                return {
                    'success': False,
                    'error': f'发油模式设置未生效，期望: {load_mode}, 实际: {current_mode}'
                }

        except Exception as e:
            self.log.error(f"设置发油模式异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：获取货位状态 ====================
    @allure.step("获取货位状态信息")
    def get_station_status(self, station_no, timeout=10.0):
        """
        获取指定货位的状态信息

        Args:
            station_no: 货位号
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'status': dict}
        """
        try:
            # 获取货位控件状态
            status = self.monitor_page.get_station_control_status(station_no)

            if not status:
                return {
                    'success': False,
                    'error': f'未获取到货位 {station_no} 的状态信息',
                    'status': {}
                }

            return {
                'success': True,
                'station_no': station_no,
                'status': status
            }

        except Exception as e:
            self.log.error(f"获取货位状态异常: {e}")
            return {'success': False, 'error': str(e), 'status': {}}

    # ==================== 业务流方法：关闭远程设定窗口 ====================
    @allure.step("关闭远程设定窗口")
    def close_remote_window(self, timeout=5.0):
        """
        关闭远程设定窗口

        Args:
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            if self.monitor_page.switch_to_remote_control_window():
                if self.monitor_page.click_remote_close_button():
                    time.sleep(0.5)
                    return {'success': True, 'message': '远程设定窗口已关闭'}

            return {'success': False, 'error': '关闭窗口失败'}

        except Exception as e:
            self.log.error(f"关闭远程设定窗口异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：完整的发油流程 ====================
    @allure.step("执行完整的发油流程")
    def execute_oil_process(self, station_no, load_mode=None, confirm=True, timeout=30.0):
        """
        执行完整的发油流程：打开远程设定 -> 设置模式 -> 启动 -> 暂停 -> 结束

        Args:
            station_no: 货位号
            load_mode: 发油模式（可选）
            confirm: 是否确认操作
            timeout: 超时时间

        Returns:
            dict: {'success': bool, 'error': str, 'results': dict}
        """
        results = {}

        # 1. 打开远程设定窗口
        with allure.step("1. 打开远程设定窗口"):
            open_result = self.open_remote_control(station_no, timeout=10)
            if not open_result['success']:
                return {'success': False, 'error': open_result['error'], 'results': results}
            results['open'] = open_result

        # 2. 设置发油模式（如果指定）
        if load_mode:
            with allure.step(f"2. 设置发油模式: {load_mode}"):
                set_result = self.set_load_mode_and_verify(station_no, load_mode, confirm, timeout=10)
                results['set_mode'] = set_result

        # 3. 启动发油
        with allure.step("3. 启动发油"):
            start_result = self.remote_start_oil(station_no, confirm, timeout=10)
            results['start'] = start_result
            # 如果启动失败，可能是因为已经在运行或其他原因，继续执行暂停

        # 4. 暂停发油
        with allure.step("4. 暂停发油"):
            pause_result = self.remote_pause_oil(station_no, confirm, timeout=10)
            results['pause'] = pause_result

        # 5. 结束发油
        with allure.step("5. 结束发油"):
            end_result = self.remote_end_oil(station_no, confirm, timeout=10)
            results['end'] = end_result

        # 汇总结果
        all_success = all(r.get('success', False) for r in results.values())
        return {
            'success': all_success,
            'message': '发油流程执行完成',
            'results': results
        }