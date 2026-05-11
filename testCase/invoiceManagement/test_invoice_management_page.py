"""装车开票管理测试用例"""
import pytest
import allure
from utils.super_handler_factory import create_handler


@allure.epic("装车开票管理")
@allure.feature("开票信息管理")
class TestInvoiceManagementPage:
    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        self.invoice_handler = create_handler('invoice_management_page')
        yield

    # ==================== 查询测试 ====================
    @allure.story("查询开票信息")
    @allure.title("测试查询所有开票信息")
    def test_query_invoice(self):
        result = self.invoice_handler.query_invoice(timeout=10.0)
        assert result['success'], f"查询开票信息失败: {result.get('error', '未知错误')}"
        assert 'data' in result, "查询结果应包含 data 字段"

    # ==================== 添加开票信息测试 ====================
    @allure.story("添加开票信息")
    @allure.title("测试添加开票信息成功")
    def test_add_invoice_success(self):
        result = self.invoice_handler.add_invoice_and_verify(
            bill_num="BILL20260001",
            vehicle_no="京A12345",
            oil_name="汽油",
            station="01",
            volume="10000",
            weight="8500",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"添加开票信息失败: {result.get('error', '未知错误')}"

    @allure.story("添加开票信息")
    @allure.title("测试添加开票信息取消")
    def test_add_invoice_cancel(self):
        result = self.invoice_handler.add_invoice_and_verify(
            bill_num="BILL20260002",
            vehicle_no="京B67890",
            oil_name="柴油",
            station="02",
            volume="8000",
            weight="7000",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"添加开票信息取消失败: {result.get('error', '未知错误')}"

    # ==================== 修改开票信息测试 ====================
    @allure.story("修改开票信息")
    @allure.title("测试修改开票信息成功")
    def test_update_invoice_success(self):
        result = self.invoice_handler.update_invoice_and_verify(
            search_key="BILL20260001",
            volume="12000",
            weight="10200",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改开票信息失败: {result.get('error', '未知错误')}"

    @allure.story("修改开票信息")
    @allure.title("测试修改开票信息取消")
    def test_update_invoice_cancel(self):
        result = self.invoice_handler.update_invoice_and_verify(
            search_key="BILL20260001",
            remark="不应存在的修改",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改开票信息取消失败: {result.get('error', '未知错误')}"

    # ==================== 删除开票信息测试 ====================
    @allure.story("删除开票信息")
    @allure.title("测试删除开票信息成功")
    def test_delete_invoice_success(self):
        self.invoice_handler.add_invoice_and_verify(
            bill_num="BILL20260003",
            vehicle_no="京C11111",
            oil_name="汽油",
            station="01",
            volume="9000",
            weight="7650",
            confirm=True,
            timeout=10.0
        )
        result = self.invoice_handler.delete_invoice_and_verify(
            search_key="BILL20260003",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"删除开票信息失败: {result.get('error', '未知错误')}"

    @allure.story("删除开票信息")
    @allure.title("测试删除开票信息取消")
    def test_delete_invoice_cancel(self):
        result = self.invoice_handler.delete_invoice_and_verify(
            search_key="BILL20260001",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"删除开票信息取消失败: {result.get('error', '未知错误')}"

    # ==================== 分单测试 ====================
    @allure.story("分单")
    @allure.title("测试分单成功")
    def test_split_bill_success(self):
        result = self.invoice_handler.split_bill_and_verify(
            search_key="BILL20260001",
            volume1="6000",
            weight1="5100",
            volume2="6000",
            weight2="5100",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"分单失败: {result.get('error', '未知错误')}"

    @allure.story("分单")
    @allure.title("测试分单取消")
    def test_split_bill_cancel(self):
        result = self.invoice_handler.split_bill_and_verify(
            search_key="BILL20260001",
            volume1="3000",
            weight1="2550",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"分单取消失败: {result.get('error', '未知错误')}"

    # ==================== 修改提单货位测试 ====================
    @allure.story("修改提单货位")
    @allure.title("测试修改提单货位成功")
    def test_update_station_success(self):
        result = self.invoice_handler.update_station_and_verify(
            search_key="BILL20260001",
            new_station="03",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"修改提单货位失败: {result.get('error', '未知错误')}"

    @allure.story("修改提单货位")
    @allure.title("测试修改提单货位取消")
    def test_update_station_cancel(self):
        result = self.invoice_handler.update_station_and_verify(
            search_key="BILL20260001",
            new_station="04",
            confirm=False,
            timeout=10.0
        )
        assert result['success'], f"修改提单货位取消失败: {result.get('error', '未知错误')}"

    # ==================== 审核测试 ====================
    @allure.story("审核")
    @allure.title("测试审核开票信息")
    def test_audit_invoice(self):
        result = self.invoice_handler.audit_invoice(
            search_key="BILL20260001",
            confirm=True,
            timeout=10.0
        )
        assert result['success'], f"审核开票信息失败: {result.get('error', '未知错误')}"