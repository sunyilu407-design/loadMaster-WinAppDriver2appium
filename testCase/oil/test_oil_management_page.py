"""
油品信息管理测试用例
"""
import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.story("油品信息管理")
@allure.feature("油品信息管理")
class TestOilManagementPage:
    """油品信息管理页面测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """设置测试资源"""
        # 使用 SuperHandlerFactory 自动创建 Handler
        self.oil_handler = create_handler('oil_management_page')

    @pytest.fixture(autouse=True)
    def test_setup(self, driver):
        """每个测试方法执行前的初始化"""
        yield
        # 测试后清理
        driver.clear_cache()

    @allure.title("添加油品成功")
    def test_add_oil_success(self):
        """测试添加油品成功场景"""
        result = self.oil_handler.add_oil_and_verify(
            short_name="汽油92",
            name="92号汽油",
            code="YL92",
            oil_type="汽油",
            color="蓝色",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加油品失败: {result.get('error')}"
        assert result['count'] > 0, "未找到添加的油品"

    @allure.title("添加油品取消")
    def test_add_oil_cancel(self):
        """测试添加油品取消场景"""
        result = self.oil_handler.add_oil_and_verify(
            short_name="柴油A",
            name="0号柴油",
            code="CY00",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"添加油品取消失败: {result.get('error')}"

    @allure.title("修改油品成功")
    def test_alter_oil_success(self):
        """测试修改油品成功场景"""
        # 先添加一个油品
        self.oil_handler.add_oil_and_verify(
            short_name="原柴油",
            name="原0号柴油",
            code="YCY00",
            confirm=True,
            timeout=10.0
        )

        # 修改油品
        result = self.oil_handler.alter_oil_and_verify(
            search_key="原柴油",
            new_short_name="新柴油",
            new_name="新0号柴油",
            new_code="XCY00",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改油品失败: {result.get('error')}"

    @allure.title("删除油品成功")
    def test_delete_oil_success(self):
        """测试删除油品成功场景"""
        # 先添加一个油品
        self.oil_handler.add_oil_and_verify(
            short_name="待删除油品",
            name="待删除油品名称",
            code="DSCY",
            confirm=True,
            timeout=10.0
        )

        # 删除油品
        result = self.oil_handler.delete_oil_and_verify(
            search_key="待删除油品",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"删除油品失败: {result.get('error')}"
        assert result['count'] == 0, "油品未被删除"

    @allure.title("删除油品取消")
    def test_delete_oil_cancel(self):
        """测试删除油品取消场景"""
        # 先添加一个油品
        self.oil_handler.add_oil_and_verify(
            short_name="取消删除油品",
            name="取消删除油品名称",
            code="QXCY",
            confirm=True,
            timeout=10.0
        )

        # 取消删除
        result = self.oil_handler.delete_oil_and_verify(
            search_key="取消删除油品",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"取消删除失败: {result.get('error')}"
        assert result['count'] > 0, "油品被错误删除"

    @allure.title("查询油品")
    def test_query_oil(self):
        """测试查询油品场景"""
        result = self.oil_handler.query_oil(
            search_key="油品",
            timeout=10.0
        )
        assert result['success'], f"查询油品失败: {result.get('error')}"
        assert 'data' in result, "返回数据格式错误"

