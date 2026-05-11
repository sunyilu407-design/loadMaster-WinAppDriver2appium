"""
货位信息管理测试用例
Station Management Page Test Cases
"""
import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.epic("货位信息管理")
@allure.feature("货位 CRUD 操作")
class TestStationManagementPage:
    """货位信息管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """测试资源初始化"""
        self.station_handler = create_handler('station_management_page')
        yield

    # ==================== 添加货位测试 ====================
    @allure.story("添加货位")
    @allure.title("测试添加货位成功（完整参数）")
    def test_add_station_success(self):
        """测试添加货位成功场景（完整参数）"""
        result = self.station_handler.add_station_and_verify(
            station_no="HW001",
            station_name="测试货位1",
            work_station="作业位1",
            accu_version="V1.0",
            port="COM1",
            use_state="启用",
            real_calc_mode="体积模式",
            density_mode="手动输入",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加货位失败: {result.get('error', '未知错误')}"

    @allure.story("添加货位")
    @allure.title("测试添加货位成功（最小参数）")
    def test_add_station_minimal(self):
        """测试添加货位成功场景（最小参数）"""
        result = self.station_handler.add_station_and_verify(
            station_no="HW002",
            station_name="测试货位2",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加货位失败: {result.get('error', '未知错误')}"

    @allure.story("添加货位")
    @allure.title("测试添加货位取消")
    def test_add_station_cancel(self):
        """测试添加货位取消场景"""
        result = self.station_handler.add_station_and_verify(
            station_no="HW003",
            station_name="取消货位",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"添加货位取消失败: {result.get('error', '未知错误')}"

    # ==================== 修改货位测试 ====================
    @allure.story("修改货位")
    @allure.title("测试修改货位成功")
    def test_alter_station_success(self):
        """测试修改货位成功场景"""
        # 先添加一条记录
        self.station_handler.add_station_and_verify(
            station_no="HW004",
            station_name="待修改货位",
            work_station="作业位1",
            use_state="启用",
            confirm=True,
            timeout=10.0
        )
        # 再修改
        result = self.station_handler.alter_station_and_verify(
            search_key="HW004",
            new_station_name="已修改货位",
            new_use_state="启用",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改货位失败: {result.get('error', '未知错误')}"

    @allure.story("修改货位")
    @allure.title("测试修改货位取消")
    def test_alter_station_cancel(self):
        """测试修改货位取消场景"""
        result = self.station_handler.alter_station_and_verify(
            search_key="HW004",
            new_station_name="不应存在的修改",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改货位取消失败: {result.get('error', '未知错误')}"

    # ==================== 删除货位测试 ====================
    @allure.story("删除货位")
    @allure.title("测试删除货位成功")
    def test_delete_station_success(self):
        """测试删除货位成功场景"""
        # 先添加一条待删除记录
        self.station_handler.add_station_and_verify(
            station_no="HW005",
            station_name="待删除货位",
            use_state="启用",
            confirm=True,
            timeout=10.0
        )
        # 再删除
        result = self.station_handler.delete_station_and_verify(
            search_key="HW005",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"删除货位失败: {result.get('error', '未知错误')}"

    @allure.story("删除货位")
    @allure.title("测试删除货位取消")
    def test_delete_station_cancel(self):
        """测试删除货位取消场景"""
        result = self.station_handler.delete_station_and_verify(
            search_key="HW004",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"删除货位取消失败: {result.get('error', '未知错误')}"

    # ==================== 修改货位基础参数测试 ====================
    @allure.story("修改货位基础参数")
    @allure.title("测试修改货位基础参数成功")
    def test_alter_station_base_param_success(self):
        """测试修改货位基础参数成功场景"""
        # 先添加一条记录
        self.station_handler.add_station_and_verify(
            station_no="HW006",
            station_name="基础参数测试货位",
            use_state="启用",
            confirm=True,
            timeout=10.0
        )
        # 再修改基础参数
        result = self.station_handler.alter_station_base_param_and_verify(
            search_key="HW006",
            new_oil_name="柴油",
            new_out_oil_mode="自动发油",
            new_is_blend="否",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改货位基础参数失败: {result.get('error', '未知错误')}"

    @allure.story("修改货位基础参数")
    @allure.title("测试修改货位基础参数取消")
    def test_alter_station_base_param_cancel(self):
        """测试修改货位基础参数取消场景"""
        result = self.station_handler.alter_station_base_param_and_verify(
            search_key="HW006",
            new_oil_name="汽油",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改货位基础参数取消失败: {result.get('error', '未知错误')}"

    # ==================== 查询货位测试 ====================
    @allure.story("查询货位")
    @allure.title("测试查询所有货位")
    def test_query_station(self):
        """测试查询所有货位功能"""
        result = self.station_handler.query_station(timeout=10.0)
        assert result['success'], f"查询货位失败: {result.get('error', '未知错误')}"
        assert 'data' in result, "查询结果应包含 data 字段"
