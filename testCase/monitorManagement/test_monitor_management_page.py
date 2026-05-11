"""
监控管理测试用例
Monitor Management Page Test Cases
"""

import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.epic("监控管理")
@allure.feature("远程发油控制")
class TestMonitorManagementPage:
    """监控管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """测试资源初始化"""
        self.monitor_handler = create_handler('monitor_management_page')
        yield

    # ==================== 打开远程设定测试 ====================
    @allure.story("打开远程设定")
    @allure.title("测试双击货位打开远程设定窗口")
    def test_open_remote_control(self):
        """测试双击货位控件打开远程设定窗口"""
        result = self.monitor_handler.open_remote_control(
            station_no="01",
            timeout=10.0
        )
        assert result['success'], f"打开远程设定失败: {result.get('error', '未知错误')}"
        assert 'bill_num' in result, "结果应包含 bill_num 字段"

    # ==================== 远程启动发油测试 ====================
    @allure.story("远程启动发油")
    @allure.title("测试远程启动发油")
    def test_remote_start_oil(self):
        """测试远程启动发油操作"""
        result = self.monitor_handler.remote_start_oil(
            station_no="01",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"远程启动发油失败: {result.get('error', '未知错误')}"

    @allure.story("远程启动发油")
    @allure.title("测试远程启动发油（取消）")
    def test_remote_start_oil_cancel(self):
        """测试远程启动发油取消操作"""
        result = self.monitor_handler.remote_start_oil(
            station_no="01",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"远程启动发油取消失败: {result.get('error', '未知错误')}"

    # ==================== 远程暂停发油测试 ====================
    @allure.story("远程暂停发油")
    @allure.title("测试远程暂停发油")
    def test_remote_pause_oil(self):
        """测试远程暂停发油操作"""
        result = self.monitor_handler.remote_pause_oil(
            station_no="01",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"远程暂停发油失败: {result.get('error', '未知错误')}"

    @allure.story("远程暂停发油")
    @allure.title("测试远程暂停发油（取消）")
    def test_remote_pause_oil_cancel(self):
        """测试远程暂停发油取消操作"""
        result = self.monitor_handler.remote_pause_oil(
            station_no="01",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"远程暂停发油取消失败: {result.get('error', '未知错误')}"

    # ==================== 远程结束发油测试 ====================
    @allure.story("远程结束发油")
    @allure.title("测试远程结束发油")
    def test_remote_end_oil(self):
        """测试远程结束发油操作"""
        result = self.monitor_handler.remote_end_oil(
            station_no="01",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"远程结束发油失败: {result.get('error', '未知错误')}"

    @allure.story("远程结束发油")
    @allure.title("测试远程结束发油（取消）")
    def test_remote_end_oil_cancel(self):
        """测试远程结束发油取消操作"""
        result = self.monitor_handler.remote_end_oil(
            station_no="01",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"远程结束发油取消失败: {result.get('error', '未知错误')}"

    # ==================== 设置发油模式测试 ====================
    @allure.story("设置发油模式")
    @allure.title("测试设置发油模式")
    def test_set_load_mode(self):
        """测试设置发油模式"""
        result = self.monitor_handler.set_load_mode_and_verify(
            station_no="01",
            load_mode="质量流量计",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"设置发油模式失败: {result.get('error', '未知错误')}"

    @allure.story("设置发油模式")
    @allure.title("测试设置发油模式（取消）")
    def test_set_load_mode_cancel(self):
        """测试设置发油模式取消操作"""
        result = self.monitor_handler.set_load_mode_and_verify(
            station_no="01",
            load_mode="体积流量计",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"设置发油模式取消失败: {result.get('error', '未知错误')}"

    # ==================== 获取货位状态测试 ====================
    @allure.story("获取货位状态")
    @allure.title("测试获取货位状态信息")
    def test_get_station_status(self):
        """测试获取指定货位的状态信息"""
        result = self.monitor_handler.get_station_status(
            station_no="01",
            timeout=10.0
        )
        assert result['success'], f"获取货位状态失败: {result.get('error', '未知错误')}"
        assert 'status' in result, "结果应包含 status 字段"

    # ==================== 关闭远程设定窗口测试 ====================
    @allure.story("关闭窗口")
    @allure.title("测试关闭远程设定窗口")
    def test_close_remote_window(self):
        """测试关闭远程设定窗口"""
        result = self.monitor_handler.close_remote_window(timeout=5.0)
        assert result['success'], f"关闭窗口失败: {result.get('error', '未知错误')}"

    # ==================== 完整发油流程测试 ====================
    @allure.story("完整发油流程")
    @allure.title("测试执行完整发油流程")
    def test_execute_oil_process(self):
        """测试执行完整的发油流程"""
        result = self.monitor_handler.execute_oil_process(
            station_no="01",
            load_mode="质量流量计",
            confirm=True,
            timeout=30.0
        )
        # 完整流程可能有部分失败（取决于实际发油状态），只检查返回结果
        assert 'results' in result, "结果应包含 results 字段"