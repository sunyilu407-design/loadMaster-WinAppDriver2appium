"""装车开票管理页面对象类"""
import time
import allure
from pageObject.base_page import BasePage


class InvoiceManagementPage(BasePage):
    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")
        self.config = self.config_manager.load_page_config('invoice_management_page')
        if self.config is None:
            self.log.error("InvoiceManagementPage: 页面配置加载失败")
            raise Exception("InvoiceManagementPage: 页面配置加载失败")
        self.elements = self.config.get('elements', {})
        self.test_data = self.config.get('test_data', {})
        self.app_config = self.config.get('app_config', {})

    def _get_element_config(self, element_name):
        def find_element(config, name):
            if name in config:
                return config[name]
            for key, value in config.items():
                if isinstance(value, dict):
                    if key == 'child_elements' and name in value:
                        return value[name]
                    result = find_element(value, name)
                    if result:
                        return result
            return None
        element_config = find_element(self.elements, element_name)
        if element_config:
            return element_config
        self.log.error(f"未找到元素配置: {element_name}")
        return None

    def switch_to_invoice_window(self):
        """切换到装车开票窗口"""
        import time
        # 点击菜单后窗口可能还没打开，等待一下
        time.sleep(1)
        # 尝试通过窗口标题切换
        result = self.switch_to_window(title=self.app_config['main_window_name'], timeout=5)
        if not result:
            # 如果找不到精确匹配，尝试模糊匹配 "装车开票"
            self.log.warning("未找到精确匹配的窗口，尝试模糊匹配")
            try:
                window_handles = self.driver.window_handles
                for handle in window_handles:
                    self.driver.switch_to.window(handle)
                    if "装车开票" in self.driver.title:
                        self.log.info(f"模糊匹配到装车开票窗口: {self.driver.title}")
                        return True
            except Exception as e:
                self.log.error(f"模糊匹配失败: {e}")
        return result

    @allure.step("点击添加开票信息按钮")
    def click_add_invoice_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('add_invoice_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击修改开票信息按钮")
    def click_update_invoice_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('update_invoice_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击删除开票信息按钮")
    def click_delete_invoice_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('delete_invoice_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击修改提单状态按钮")
    def click_update_state_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('update_state_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击分单按钮")
    def click_split_bill_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('split_bill_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击异常处理按钮")
    def click_exception_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('exception_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击审核按钮")
    def click_audit_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('audit_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击打印交接单按钮")
    def click_print_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('print_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("点击修改提单货位按钮")
    def click_update_station_button(self):
        self.switch_to_invoice_window()
        element_config = self._get_element_config('update_station_button')
        return self.click_element(**element_config) if element_config else False

    @allure.step("获取装车开票表格数据")
    def get_content_table(self):
        self.switch_to_invoice_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)

    def _get_state_combo_current_text(self):
        """获取状态查询下拉框当前选中的文本"""
        try:
            element_config = self._get_element_config('state_query_combo')
            if not element_config:
                return None
            combobox = self.locate_element(**element_config)
            if not combobox:
                return None
            from selenium.webdriver.common.by import By
            edit = combobox.find_element(By.XPATH, ".//Edit")
            if edit:
                text = (edit.text or "").strip()
                self.log.debug(f"状态查询下拉框当前选中: {text}")
                return text
            return None
        except Exception as e:
            self.log.debug(f"获取状态查询下拉框当前选中文本失败: {e}")
            return None

    @allure.step("选择状态查询条件")
    def select_state_query(self, option_text):
        """选择状态查询条件（用于显示全部开票信息）"""
        element_config = self._get_element_config('state_query_combo')
        if element_config:
            return self.select_combobox_option(option_text, **element_config)
        self.log.warning("未找到状态查询下拉框配置")
        return False

    @allure.step("点击表格中的开票行")
    def click_invoice_table_row(self, search_criteria, match_mode='exact'):
        """点击表格中的开票行（先选择状态为"全部"）"""
        self.switch_to_invoice_window()

        # # 只在不是"全部"时才切换，避免重复操作
        if self._get_state_combo_current_text() != "全部":
            self.select_state_query("全部")

        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)

    # ==================== 添加开票信息窗口方法 ====================
    @allure.step("切换到添加开票信息窗口")
    def switch_to_add_invoice_window(self):
        window_config = self._get_element_config('add_invoice_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("输入ERP物料凭证")
    def set_item_spec_cert(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('item_spec_cert_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入提货单号")
    def set_bill_num(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('bill_num_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入ERP提货单号")
    def set_erp_bill_num(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('erp_bill_num_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入IC卡号")
    def set_ic_card_no(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('ic_card_no_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入车牌号码")
    def set_vehicle_no(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('vehicle_no_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入预装体积")
    def set_volume(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('volume_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入预装重量")
    def set_weight(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入特殊作业体积")
    def set_special_job_volume(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('special_job_volume_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入特殊作业重量")
    def set_special_job_weight(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('special_job_weight_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入备注摘要")
    def set_remark(self, text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('remark_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("选择票据分类")
    def select_sort(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('sort_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择油品名称")
    def select_oil_name(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('oil_name_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择发油货位")
    def select_station(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择发油方式")
    def select_load_mode(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('load_mode_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择客户全称")
    def select_buyer(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('buyer_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择特殊作业方式")
    def select_special_operation(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('special_operation_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("选择仓位")
    def select_erp_cw(self, option_text):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('erp_cw_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("勾选使用IC卡")
    def check_use_ic_card(self):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('use_ic_card_check')
            if child:
                element = self.locate_element(**child)
                if element and not element.is_selected():
                    return self.click_element(**child)
                return True
        return False

    @allure.step("勾选含添加剂")
    def check_additive(self):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('additive_check')
            if child:
                element = self.locate_element(**child)
                if element and not element.is_selected():
                    return self.click_element(**child)
                return True
        return False

    @allure.step("点击添加开票窗口的添加按钮")
    def click_add_invoice_window_add_button(self):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('add_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击添加开票窗口的取消按钮")
    def click_add_invoice_window_cancel_button(self):
        element_config = self._get_element_config('add_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改开票信息窗口方法 ====================
    @allure.step("切换到修改开票信息窗口")
    def switch_to_edit_invoice_window(self):
        window_config = self._get_element_config('edit_invoice_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取修改窗口的提货单号")
    def get_edit_bill_num(self):
        element_config = self._get_element_config('edit_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('bill_num_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击修改开票窗口的保存按钮")
    def click_edit_invoice_window_save_button(self):
        element_config = self._get_element_config('edit_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改开票窗口的取消按钮")
    def click_edit_invoice_window_cancel_button(self):
        element_config = self._get_element_config('edit_invoice_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 分单窗口方法 ====================
    @allure.step("切换到分单窗口")
    def switch_to_split_bill_window(self):
        window_config = self._get_element_config('split_bill_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("输入一仓体积")
    def set_split_volume1(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('volume1_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入一仓重量")
    def set_split_weight1(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight1_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入二仓体积")
    def set_split_volume2(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('volume2_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入二仓重量")
    def set_split_weight2(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight2_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入三仓体积")
    def set_split_volume3(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('volume3_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("输入三仓重量")
    def set_split_weight3(self, text):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('weight3_text')
            if child:
                return self.send_keys_to_element(text, **child)
        return False

    @allure.step("点击分单窗口的保存按钮")
    def click_split_bill_save_button(self):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击分单窗口的取消按钮")
    def click_split_bill_cancel_button(self):
        element_config = self._get_element_config('split_bill_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 异常处理窗口方法 ====================
    @allure.step("切换到异常处理窗口")
    def switch_to_exception_window(self):
        window_config = self._get_element_config('exception_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("点击异常处理窗口的保存按钮")
    def click_exception_save_button(self):
        element_config = self._get_element_config('exception_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击异常处理窗口的取消按钮")
    def click_exception_cancel_button(self):
        element_config = self._get_element_config('exception_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改提单货位窗口方法 ====================
    @allure.step("切换到修改提单货位窗口")
    def switch_to_update_station_window(self):
        window_config = self._get_element_config('update_station_window')
        if window_config:
            return self.switch_to_window(title=window_config.get('name'))
        return False

    @allure.step("获取修改提单货位窗口的提货单号")
    def get_update_station_bill_num(self):
        element_config = self._get_element_config('update_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('bill_num_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("选择新的发油货位")
    def select_new_station(self, option_text):
        element_config = self._get_element_config('update_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('station_combo')
            if child:
                return self.select_combobox_option(option_text, **child)
        return False

    @allure.step("点击���改提单货位窗口的保存按钮")
    def click_update_station_save_button(self):
        element_config = self._get_element_config('update_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('save_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改提单货位窗口的取消按钮")
    def click_update_station_cancel_button(self):
        element_config = self._get_element_config('update_station_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 删除确认窗口方法 ====================
    @allure.step("切换到删除确认窗口")
    def switch_to_delete_confirm_window(self):
        window_config = self._get_element_config('delete_confirm_window')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("获取删除确认窗口的提示文本")
    def get_delete_prompt_text(self):
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击删除确认按钮")
    def click_delete_confirm_button(self):
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击删除取消按钮")
    def click_delete_cancel_button(self):
        element_config = self._get_element_config('delete_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 审核确认窗口方法 ====================
    @allure.step("切换到审核确认窗口")
    def switch_to_audit_confirm_window(self):
        window_config = self._get_element_config('audit_confirm_window')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("点击审核确认按钮")
    def click_audit_confirm_button(self):
        element_config = self._get_element_config('audit_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击审核取消按钮")
    def click_audit_cancel_button(self):
        element_config = self._get_element_config('audit_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    # ==================== 修改提单状态确认窗口方法 ====================
    @allure.step("切换到修改提单状态确认窗口")
    def switch_to_update_state_confirm_window(self):
        window_config = self._get_element_config('update_state_confirm_window')
        if window_config:
            return self.switch_to_window(automation_id=window_config.get('automation_id'))
        return False

    @allure.step("获取修改提单状态确认窗口的提示文本")
    def get_update_state_prompt_text(self):
        element_config = self._get_element_config('update_state_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('prompt_text')
            if child:
                return self.get_element_text(**child)
        return ""

    @allure.step("点击修改提单状态确认按钮")
    def click_update_state_confirm_button(self):
        element_config = self._get_element_config('update_state_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('confirm_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("点击修改提单状态取消按钮")
    def click_update_state_cancel_button(self):
        element_config = self._get_element_config('update_state_confirm_window')
        if element_config and 'child_elements' in element_config:
            child = element_config['child_elements'].get('cancel_button')
            if child:
                return self.click_element(**child)
        return False

    @allure.step("关闭装车开票页面")
    def close_invoice_window(self):
        """关闭装车开票页面"""
        try:
            # 使用 app_config 中的 main_window_name 来关闭
            window_name = self.app_config.get('main_window_name', '装车开票')
            
            # 切换到要关闭的窗口
            if not self.switch_to_window(title=window_name, timeout=2):
                self.log.warning(f"未找到要关闭的窗口: {window_name}")
                return False
            
            # 查找并点击关闭按钮
            close_button = None
            for aid in ['close', 'btnClose', 'button1', 'btnCloseWindow']:
                try:
                    close_button = self.locate_element(timeout=1, automation_id=aid)
                    if close_button:
                        break
                except Exception:
                    continue
            
            if close_button:
                close_button.click()
                self.log.info("通过关闭按钮关闭窗口成功")
            else:
                # 如果没有找到关闭按钮，使用 Alt+F4
                from selenium.webdriver.common.keys import Keys
                self.driver.switch_to.active_element.send_keys(Keys.ALT + Keys.F4)
                self.log.info("通过快捷键关闭窗口成功")
            
            # 关闭窗口后，等待关闭操作完成
            time.sleep(1)
            
            # 切换回主窗口
            main_window_title = "装车管理系统"
            if self.switch_to_window(title=main_window_title, timeout=3):
                self.log.info(f"已切换回主窗口: {main_window_title}")
            else:
                self.log.warning(f"切换回主窗口失败: {main_window_title}")
            
            return True
        except Exception as e:
            self.log.error(f"关闭窗口失败: {e}")
            return False