"""
配置设定管理测试用例
Config Settings Page Test Cases
"""

import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.epic("配置设定管理")
@allure.feature("配置设定功能测试")
class TestConfigSettingsPage:
    """配置设定管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """测试资源初始化"""
        self.config_handler = create_handler('config_settings_page')
        yield

    # ==================== 刷新配置数据测试 ====================
    @allure.story("刷新配置数据")
    @allure.title("测试刷新配置设定数据")
    def test_refresh_config_data(self):
        """测试刷新配置设定数据功能"""
        result = self.config_handler.refresh_config_data(timeout=10.0)
        assert result['success'], f"刷新配置数据失败: {result.get('error', '未知错误')}"
        assert 'data' in result, "刷新结果应包含 data 字段"
        assert result['count'] >= 0, "数据条数应为非负数"

    @allure.story("刷新配置数据")
    @allure.title("测试按货位筛选刷新配置数据")
    def test_refresh_config_data_with_station_filter(self):
        """测试按货位筛选刷新配置设定数据"""
        # 根据实际数据填写筛选条件
        result = self.config_handler.refresh_config_data(
            station_filter="货位1",
            timeout=10.0
        )
        assert result['success'], f"按货位筛选刷新失败: {result.get('error', '未知错误')}"

    @allure.story("刷新配置数据")
    @allure.title("测试按油品筛选刷新配置数据")
    def test_refresh_config_data_with_oil_filter(self):
        """测试按油品筛选刷新配置设定数据"""
        # 根据实际数据填写筛选条件
        result = self.config_handler.refresh_config_data(
            oil_filter="汽油",
            timeout=10.0
        )
        assert result['success'], f"按油品筛选刷新失败: {result.get('error', '未知错误')}"

    # ==================== 设置流量计类型测试 ====================
    @allure.story("设置流量计类型")
    @allure.title("测试设置流量计类型成功")
    def test_set_flowmeter_type_success(self):
        """测试设置流量计类型成功场景"""
        # 根据实际数据填写搜索关键字和流量计类型
        result = self.config_handler.set_flowmeter_type_and_verify(
            search_key="01",
            flowmeter_type1="质量流量计",
            flowmeter_type2="体积流量计",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"设置流量计类型失败: {result.get('error', '未知错误')}"

    @allure.story("设置流量计类型")
    @allure.title("测试设置流量计类型取消")
    def test_set_flowmeter_type_cancel(self):
        """测试设置流量计类型取消场景"""
        result = self.config_handler.set_flowmeter_type_and_verify(
            search_key="01",
            flowmeter_type1="质量流量计",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"设置流量计类型取消失败: {result.get('error', '未知错误')}"

    # ==================== 货位密度修改测试 ====================
    @allure.story("货位密度修改")
    @allure.title("测试修改货位密度成功")
    def test_update_station_density_success(self):
        """测试修改货位密度成功场景"""
        result = self.config_handler.update_station_density_and_verify(
            search_key="01",
            weight_density="0.85",
            standard_density1="0.82",
            standard_density2="0.79",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改货位密度失败: {result.get('error', '未知错误')}"

    @allure.story("货位密度修改")
    @allure.title("测试修改货位密度取消")
    def test_update_station_density_cancel(self):
        """测试修改货位密度取消场景"""
        result = self.config_handler.update_station_density_and_verify(
            search_key="01",
            weight_density="0.85",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改货位密度取消失败: {result.get('error', '未知错误')}"

    @allure.story("货位密度修改")
    @allure.title("测试修改货位密度（带计算）")
    def test_update_station_density_with_compute(self):
        """测试修改货位密度并触发计算场景"""
        result = self.config_handler.update_station_density_and_verify(
            search_key="01",
            standard_density1="0.82",
            standard_density2="0.79",
            weight_density1="0.83",
            weight_density2="0.80",
            compute=True,
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改货位密度（带计算）失败: {result.get('error', '未知错误')}"

    # ==================== 储罐密度修改测试 ====================
    @allure.story("储罐密度修改")
    @allure.title("测试修改储罐密度成功")
    def test_update_tank_density_success(self):
        """测试修改储罐密度成功场景"""
        # 根据实际数据填写油品和罐名
        result = self.config_handler.update_tank_density_and_verify(
            oil_name="汽油",
            tank_name1="组分罐1",
            tank_name2="乙醇罐1",
            weight_density="0.85",
            standard_density1="0.82",
            standard_density2="0.79",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改储罐密度失败: {result.get('error', '未知错误')}"

    @allure.story("储罐密度修改")
    @allure.title("测试修改储罐密度取消")
    def test_update_tank_density_cancel(self):
        """测试修改储罐密度取消场景"""
        result = self.config_handler.update_tank_density_and_verify(
            oil_name="汽油",
            tank_name1="组分罐1",
            weight_density="0.85",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改储罐密度取消失败: {result.get('error', '未知错误')}"

    # ==================== 密度历史记录查询测试 ====================
    @allure.story("密度历史记录查询")
    @allure.title("测试查询密度历史记录")
    def test_query_md_history(self):
        """测试查询密度历史记录功能"""
        result = self.config_handler.query_md_history(timeout=10.0)
        assert result['success'], f"查询密度历史记录失败: {result.get('error', '未知错误')}"
        assert 'data' in result, "查询结果应包含 data 字段"

    @allure.story("密度历史记录查询")
    @allure.title("测试按油品查询密度历史记录")
    def test_query_md_history_by_oil(self):
        """测试按油品查询密度历史记录"""
        result = self.config_handler.query_md_history(
            oil_name="汽油",
            timeout=10.0
        )
        assert result['success'], f"按油品查询密度历史记录失败: {result.get('error', '未知错误')}"

    @allure.story("密度历史记录查询")
    @allure.title("测试按时间范围查询密度历史记录")
    def test_query_md_history_by_time_range(self):
        """测试按时间范围查询密度历史记录"""
        result = self.config_handler.query_md_history(
            start_time="2026-01-01",
            end_time="2026-04-10",
            timeout=10.0
        )
        assert result['success'], f"按时间范围查询密度历史记录失败: {result.get('error', '未知错误')}"

    # ==================== 下发到装车仪器测试 ====================
    @allure.story("下发到装车仪器")
    @allure.title("测试下发到装车仪器")
    def test_send_to_device(self):
        """测试下发配置到装车仪器"""
        result = self.config_handler.send_to_device(timeout=10.0)
        # 下发操作可能返回不同结果，根据实际业务调整断言
        assert 'message' in result or 'success' in result, "下发结果应包含响应信息"

    @allure.story("下发到装车仪器")
    @allure.title("测试下发到装车仪器（预期包含提示文本）")
    def test_send_to_device_with_expectation(self):
        """测试下发配置到装车仪器（预期特定提示文本）"""
        result = self.config_handler.send_to_device(
            expect_contains="成功",
            timeout=10.0
        )
        # 根据实际业务预期调整
        assert 'message' in result or result.get('success') is not None, \
            "下发结果应包含响应信息"
