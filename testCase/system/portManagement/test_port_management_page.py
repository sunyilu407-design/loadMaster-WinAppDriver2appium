"""
串口信息管理测试用例
Port Management Page Test Cases
"""
import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.epic("串口信息管理")
@allure.feature("串口 CRUD 操作")
class TestPortManagementPage:
    """串口信息管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """测试资源初始化"""
        self.port_handler = create_handler('port_management_page')
        yield

    # ==================== 添加串口测试 ====================
    @allure.story("添加串口")
    @allure.title("测试添加串口成功（完整参数）")
    def test_add_port_success(self):
        """测试添加串口成功场景（完整参数）"""
        result = self.port_handler.add_port_and_verify(
            port_name="COM1",
            baudrate="9600",
            port_type="地磅串口",
            remark="测试串口",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加串口失败: {result.get('error', '未知错误')}"

    @allure.story("添加串口")
    @allure.title("测试添加串口成功（最小参数）")
    def test_add_port_minimal(self):
        """测试添加串口成功场景（最小参数）"""
        result = self.port_handler.add_port_and_verify(
            port_name="COM2",
            baudrate="9600",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加串口失败: {result.get('error', '未知错误')}"

    @allure.story("添加串口")
    @allure.title("测试添加串口取消")
    def test_add_port_cancel(self):
        """测试添加串口取消场景"""
        result = self.port_handler.add_port_and_verify(
            port_name="COM3",
            baudrate="19200",
            port_type="读卡器串口",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"添加串口取消失败: {result.get('error', '未知错误')}"

    # ==================== 修改串口测试 ====================
    @allure.story("修改串口")
    @allure.title("测试修改串口成功")
    def test_alter_port_success(self):
        """测试修改串口成功场景"""
        # 先添加一条记录
        self.port_handler.add_port_and_verify(
            port_name="COM4",
            baudrate="9600",
            port_type="地磅串口",
            remark="原始备注",
            confirm=True,
            timeout=10.0
        )
        # 再修改
        result = self.port_handler.alter_port_and_verify(
            search_key="COM4",
            new_baudrate="19200",
            new_remark="已修改",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改串口失败: {result.get('error', '未知错误')}"

    @allure.story("修改串口")
    @allure.title("测试修改串口取消")
    def test_alter_port_cancel(self):
        """测试修改串口取消场景"""
        result = self.port_handler.alter_port_and_verify(
            search_key="COM4",
            new_remark="不应存在的修改",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改串口取消失败: {result.get('error', '未知错误')}"

    # ==================== 删除串口测试 ====================
    @allure.story("删除串口")
    @allure.title("测试删除串口成功")
    def test_delete_port_success(self):
        """测试删除串口成功场景"""
        # 先添加一条待删除记录
        self.port_handler.add_port_and_verify(
            port_name="COM5",
            baudrate="9600",
            port_type="红外串口",
            confirm=True,
            timeout=10.0
        )
        # 再删除
        result = self.port_handler.delete_port_and_verify(
            search_key="COM5",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"删除串口失败: {result.get('error', '未知错误')}"

    @allure.story("删除串口")
    @allure.title("测试删除串口取消")
    def test_delete_port_cancel(self):
        """测试删除串口取消场景"""
        result = self.port_handler.delete_port_and_verify(
            search_key="COM4",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"删除串口取消失败: {result.get('error', '未知错误')}"

    # ==================== 查询串口测试 ====================
    @allure.story("查询串口")
    @allure.title("测试查询所有串口")
    def test_query_port(self):
        """测试查询所有串口功能"""
        result = self.port_handler.query_port(timeout=10.0)
        assert result['success'], f"查询串口失败: {result.get('error', '未知错误')}"
        assert 'data' in result, "查询结果应包含 data 字段"
