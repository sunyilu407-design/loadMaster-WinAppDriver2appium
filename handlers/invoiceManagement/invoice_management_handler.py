"""装车开票管理业务逻辑处理类"""
import logging
import time
import allure
from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin


class InvoiceManagementHandler(BaseHandler, NavigationMixin):
    def __init__(self, page_instance=None, config_manager=None):
        super().__init__(page_instance, config_manager)
        NavigationMixin.__init__(self)
        self.invoice_page = self.page_instance
        logging.info("InvoiceManagementHandler 已通过 SuperHandlerFactory 初始化")

    # ==================== 通用辅助方法 ====================
    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        if not self.invoice_page.wait_for_operation_window(timeout):
            return False
        if action == 'confirm':
            return self.invoice_page.click_operation_window_confirm_button()
        elif action == 'cancel':
            return self.invoice_page.click_operation_window_cancel_button()
        return False

    def handle_prompt_window(self, timeout=5.0):
        if not self.invoice_page.wait_for_prompt_window(timeout):
            return {'success': False, 'error': '等待消息提示窗口超时'}
        result = self.invoice_page.click_prompt_window_confirm_button()
        if result:
            return {'success': True, 'message': '已点击确定按钮'}
        return {'success': False, 'error': '点击消息提示窗口确定按钮失败'}

    # ==================== 业务流方法：查询开票信息 ====================
    @allure.step("查询装车开票信息")
    def query_invoice(self, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            table_data = self.invoice_page.get_content_table()
            return {'success': True, 'data': table_data, 'count': len(table_data)}
        except Exception as e:
            self.log.error(f"查询开票信息异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：添加开票信息 ====================
    @allure.step("添加开票信息并验证")
    def add_invoice_and_verify(self, bill_num=None, erp_bill_num=None, vehicle_no=None,
                               oil_name=None, station=None, load_mode=None, buyer=None,
                               volume=None, weight=None, remark=None,
                               sort=None, special_operation=None, erp_cw=None,
                               use_ic_card=False, additive=False,
                               confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_add_invoice_button():
                return {'success': False, 'error': '点击添加开票信息按钮失败'}
            if not self.invoice_page.switch_to_add_invoice_window():
                return {'success': False, 'error': '切换到添加开票信息窗口失败'}
            if bill_num:
                self.invoice_page.set_bill_num(bill_num)
            if erp_bill_num:
                self.invoice_page.set_erp_bill_num(erp_bill_num)
            if vehicle_no:
                self.invoice_page.set_vehicle_no(vehicle_no)
            if oil_name:
                self.invoice_page.select_oil_name(oil_name)
            if station:
                self.invoice_page.select_station(station)
            if load_mode:
                self.invoice_page.select_load_mode(load_mode)
            if buyer:
                self.invoice_page.select_buyer(buyer)
            if volume:
                self.invoice_page.set_volume(volume)
            if weight:
                self.invoice_page.set_weight(weight)
            if remark:
                self.invoice_page.set_remark(remark)
            if sort:
                self.invoice_page.select_sort(sort)
            if special_operation:
                self.invoice_page.select_special_operation(special_operation)
            if erp_cw:
                self.invoice_page.select_erp_cw(erp_cw)
            if use_ic_card:
                self.invoice_page.check_use_ic_card()
            if additive:
                self.invoice_page.check_additive()
            if not self.invoice_page.click_add_invoice_window_add_button():
                return {'success': False, 'error': '点击添加按钮失败'}
            if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                return {'success': False, 'error': '处理操作确认弹窗失败'}
            if confirm:
                return self.verify_invoice_in_table({'提货单号': bill_num} if bill_num else {}, expected_presence='present', timeout=timeout)
            else:
                return {'success': True, 'message': '已取消添加'}
        except Exception as e:
            self.log.error(f"添加开票信息异常: {e}")
            return {'success': False, 'error': str(e)}

    def verify_invoice_in_table(self, search_criteria, expected_presence='present', match_mode='exact', timeout=5.0):
        self.invoice_page.switch_to_invoice_window()
        # 先选择状态为"全部"，确保能看到所有开票信息
        self.invoice_page.select_state_query("全部")
        content_table = self.invoice_page._get_element_config('content_table')
        header_keywords = self.invoice_page.app_config.get('head_keys')
        return self.invoice_page.query_table_after_operation(content_table, search_criteria, header_keywords, match_mode, expected_presence, timeout=timeout)

    def select_state_all(self):
        """选择状态为"全部"，用于显示所有开票信息"""
        return self.invoice_page.select_state_query("全部")

    # ==================== 业务流方法：修改开票信息 ====================
    @allure.step("修改开票信息并验证")
    def update_invoice_and_verify(self, search_key, vehicle_no=None, volume=None, weight=None,
                                  remark=None, confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_update_invoice_button():
                return {'success': False, 'error': '点击修改开票信息按钮失败'}
            if not self.invoice_page.switch_to_edit_invoice_window():
                return {'success': False, 'error': '切换到修改开票信息窗口失败'}
            if vehicle_no:
                self.invoice_page.set_vehicle_no(vehicle_no)
            if volume:
                self.invoice_page.set_volume(volume)
            if weight:
                self.invoice_page.set_weight(weight)
            if remark:
                self.invoice_page.set_remark(remark)
            if not self.invoice_page.click_edit_invoice_window_save_button():
                return {'success': False, 'error': '点击保存按钮失败'}
            if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                return {'success': False, 'error': '处理操作确认弹窗失败'}
            return {'success': True, 'message': '修改开票信息完成' if confirm else '已取消修改'}
        except Exception as e:
            self.log.error(f"修改开票信息异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：删除开票信息 ====================
    @allure.step("删除开票信息并验证")
    def delete_invoice_and_verify(self, search_key, confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_delete_invoice_button():
                return {'success': False, 'error': '点击删除开票信息按钮失败'}
            if not self.invoice_page.switch_to_delete_confirm_window():
                return {'success': False, 'error': '切换到删除确认窗口失败'}
            if confirm:
                if not self.invoice_page.click_delete_confirm_button():
                    return {'success': False, 'error': '点击确认删除按钮失败'}
                return self.verify_invoice_in_table({'提货单号': search_key}, expected_presence='absent', timeout=timeout)
            else:
                if not self.invoice_page.click_delete_cancel_button():
                    return {'success': False, 'error': '点击取消按钮失败'}
                return self.verify_invoice_in_table({'提货单号': search_key}, expected_presence='present', timeout=timeout)
        except Exception as e:
            self.log.error(f"删除开票信息异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：分单 ====================
    @allure.step("分单并验证")
    def split_bill_and_verify(self, search_key, volume1=None, weight1=None,
                               volume2=None, weight2=None, volume3=None, weight3=None,
                               confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_split_bill_button():
                return {'success': False, 'error': '点击分单按钮失败'}
            if not self.invoice_page.switch_to_split_bill_window():
                return {'success': False, 'error': '切换到分单窗口失败'}
            if volume1:
                self.invoice_page.set_split_volume1(volume1)
            if weight1:
                self.invoice_page.set_split_weight1(weight1)
            if volume2:
                self.invoice_page.set_split_volume2(volume2)
            if weight2:
                self.invoice_page.set_split_weight2(weight2)
            if volume3:
                self.invoice_page.set_split_volume3(volume3)
            if weight3:
                self.invoice_page.set_split_weight3(weight3)
            if not self.invoice_page.click_split_bill_save_button():
                return {'success': False, 'error': '点击保存按钮失败'}
            if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                return {'success': False, 'error': '处理操作确认弹窗失败'}
            return {'success': True, 'message': '分单完成' if confirm else '已取消分单'}
        except Exception as e:
            self.log.error(f"分单异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改提单货位 ====================
    @allure.step("修改提单货位并验证")
    def update_station_and_verify(self, search_key, new_station, confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_update_station_button():
                return {'success': False, 'error': '点击修改提单货位按钮失败'}
            if not self.invoice_page.switch_to_update_station_window():
                return {'success': False, 'error': '切换到修改提单货位窗口失败'}
            if not self.invoice_page.select_new_station(new_station):
                return {'success': False, 'error': f'选择新货位失败: {new_station}'}
            if not self.invoice_page.click_update_station_save_button():
                return {'success': False, 'error': '点击保存按钮失败'}
            if not self.handle_operation_prompt(action='confirm' if confirm else 'cancel', timeout=timeout):
                return {'success': False, 'error': '处理操作确认弹窗失败'}
            return {'success': True, 'message': '修改提单货位完成' if confirm else '已取消修改'}
        except Exception as e:
            self.log.error(f"修改提单货位异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：审核 ====================
    @allure.step("审核开票信息并验证")
    def audit_invoice_and_verify(self, search_key, confirm=True, timeout=10.0):
        """审核开票信息并验证"""
        result = self.audit_invoice(search_key, confirm, timeout)
        if result.get('success') and confirm:
            # 审核成功后，关闭装车开票页面
            self.log.info("审核成功，关闭装车开票页面")
            self.invoice_page.close_invoice_window()
            return self.verify_invoice_in_table({'提货单号': search_key}, expected_presence='present', timeout=timeout)
        return result

    @allure.step("审核开票信息")
    def audit_invoice(self, search_key, confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_audit_button():
                return {'success': False, 'error': '点击审核按钮失败'}
            if not self.invoice_page.switch_to_audit_confirm_window():
                return {'success': False, 'error': '切换到审核确认窗口失败'}
            if confirm:
                if not self.invoice_page.click_audit_confirm_button():
                    return {'success': False, 'error': '点击审核确认按钮失败'}
                # 等待审核确认窗口关闭，再等待操作提示窗口出现
                time.sleep(1.0)
                return self.handle_prompt_window(timeout=timeout)
            else:
                return self.invoice_page.click_audit_cancel_button()
        except Exception as e:
            self.log.error(f"审核开票信息异常: {e}")
            return {'success': False, 'error': str(e)}

    # ==================== 业务流方法：修改提单状态 ====================
    @allure.step("修改提单状态")
    def update_state(self, search_key, confirm=True, timeout=10.0):
        try:
            if not self.navigate_to_invoice_management():
                return {'success': False, 'error': '导航到装车开票页面失败'}
            if not self.invoice_page.click_invoice_table_row({'提货单号': search_key}):
                return {'success': False, 'error': f'选择开票行失败: {search_key}'}
            if not self.invoice_page.click_update_state_button():
                return {'success': False, 'error': '点击修改提单状态按钮失败'}
            if not self.invoice_page.switch_to_update_state_confirm_window():
                return {'success': False, 'error': '切换到修改提单状态确认窗口失败'}
            if confirm:
                return self.invoice_page.click_update_state_confirm_button()
            else:
                return self.invoice_page.click_update_state_cancel_button()
        except Exception as e:
            self.log.error(f"修改提单状态异常: {e}")
            return {'success': False, 'error': str(e)}