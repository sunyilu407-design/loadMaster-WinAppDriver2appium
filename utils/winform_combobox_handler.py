"""
WinForm ComboBox 专用处理工具
解决WinForm应用中ComboBox选项获取和选择的问题
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging


class WinFormComboBoxHandler:
    """WinForm ComboBox专用处理器"""
    
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.log = logger or logging.getLogger(__name__)
    
    def select_option(self, combobox_element, option_text, timeout=10):
        """
        选择ComboBox选项的主入口方法
        使用多种策略确保选择成功
        """
        self.log.info(f"开始选择WinForm ComboBox选项: {option_text}")
        
        # 策略1: 键盘导航选择（最可靠的WinForm方式）
        if self._select_by_keyboard_navigation(combobox_element, option_text):
            return True
        
        # 策略2: 点击展开 + 精确定位选择
        if self._select_by_click_and_locate(combobox_element, option_text, timeout):
            return True
        
        # # 策略3: SendKeys直接输入（适用于可编辑ComboBox）
        # if self._select_by_send_keys(combobox_element, option_text):
        #     return True
        
        # 策略4: 模拟用户操作序列
        if self._select_by_user_simulation(combobox_element, option_text):
            return True
        
        self.log.error(f"所有策略均失败，无法选择选项: {option_text}")
        return False
    
    def _select_by_keyboard_navigation(self, combobox_element, option_text):
        """
        策略1: 键盘导航选择
        这是WinForm ComboBox最可靠的选择方式
        """
        try:
            self.log.debug("尝试策略1: 键盘导航选择")

            # 1. 先点击展开下拉列表
            combobox_element.click()
            time.sleep(0.3)

            # 2. 尝试多种方式展开下拉列表
            expanded = False

            # 方式A: 再次点击
            combobox_element.click()
            time.sleep(0.5)

            # 方式B: Alt+Down
            try:
                combobox_element.send_keys(Keys.ALT + Keys.DOWN)
                time.sleep(0.3)
            except Exception:
                pass

            # 方式C: F4
            try:
                combobox_element.send_keys(Keys.F4)
                time.sleep(0.3)
            except Exception:
                pass

            # 3. 使用方向键遍历选项
            max_attempts = 30  # 最多尝试30个选项
            for i in range(max_attempts):
                # 获取当前选中的选项文本
                current_text = self._get_current_selected_text(combobox_element)
                self.log.debug(f"当前选项 {i+1}: {current_text}")

                # 检查是否匹配目标选项
                if current_text and option_text in current_text:
                    self.log.info(f"找到匹配选项: {current_text}")
                    # 按Enter确认选择
                    combobox_element.send_keys(Keys.ENTER)
                    time.sleep(0.3)
                    # 验证是否选择成功
                    final_text = self._get_current_selected_text(combobox_element)
                    if option_text in final_text:
                        self.log.info(f"键盘导航选择成功: {final_text}")
                        return True

                # 按下箭头键移动到下一个选项
                combobox_element.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.15)

            self.log.debug("键盘导航未找到匹配选项")
            return False

        except Exception as e:
            self.log.debug(f"键盘导航策略失败: {e}")
            return False
    
    def _select_by_click_and_locate(self, combobox_element, option_text, timeout):
        """
        策略2: 点击展开 + 精确定位选择
        改进的点击定位策略，针对WinForm特性优化
        """
        try:
            self.log.debug("尝试策略2: 点击展开 + 精确定位选择")
            
            # 1. 强制展开下拉框
            self._force_expand_dropdown(combobox_element)
            
            # 2. 获取ComboBox位置信息
            cb_rect = self._get_element_rect(combobox_element)
            
            # 3. 使用多种定位策略查找选项
            options = self._find_dropdown_options(option_text, cb_rect, timeout)
            
            # 4. 点击匹配的选项
            if options:
                for option in options:
                    try:
                        if option.is_displayed() and option.is_enabled():
                            option.click()
                            self.log.info(f"成功点击选项: {option_text}")
                            time.sleep(0.3)
                            return True
                    except Exception as e:
                        self.log.debug(f"点击选项失败: {e}")
                        continue
            
            return False
            
        except Exception as e:
            self.log.debug(f"点击定位策略失败: {e}")
            return False
    
    def _select_by_send_keys(self, combobox_element, option_text):
        """
        策略3: SendKeys直接输入
        适用于可编辑的ComboBox
        """
        try:
            self.log.debug("尝试策略3: SendKeys直接输入")
            
            # 1. 清空并输入选项文本
            combobox_element.click()
            time.sleep(0.2)
            combobox_element.send_keys(Keys.CONTROL + "a")  # 全选
            time.sleep(0.1)
            combobox_element.send_keys(option_text)
            time.sleep(0.3)
            
            # 2. 按Tab或Enter确认
            combobox_element.send_keys(Keys.TAB)
            time.sleep(0.3)
            
            # 3. 验证是否成功
            current_text = self._get_current_selected_text(combobox_element)
            if current_text and option_text in current_text:
                self.log.info(f"SendKeys策略成功: {current_text}")
                return True
            
            return False
            
        except Exception as e:
            self.log.debug(f"SendKeys策略失败: {e}")
            return False
    
    def _select_by_user_simulation(self, combobox_element, option_text):
        """
        策略4: 模拟用户操作序列（改进版）
        模拟真实用户的操作步骤：先展开下拉列表，再点击选择
        """
        try:
            self.log.debug("尝试策略4: 模拟用户操作序列（展开下拉列表方式）")

            # 1. 点击 ComboBox 展开下拉列表
            combobox_element.click()
            time.sleep(0.3)

            # 2. 尝试多种方式展开下拉列表
            expanded = False

            # 方式A: 再次点击（双击）
            combobox_element.click()
            time.sleep(0.5)

            # 检查是否已展开
            if self._is_dropdown_expanded(combobox_element):
                expanded = True
                self.log.debug("通过双击展开下拉列表")
            else:
                # 方式B: 发送 Alt+Down 键
                try:
                    combobox_element.send_keys(Keys.ALT + Keys.DOWN)
                    time.sleep(0.5)
                    if self._is_dropdown_expanded(combobox_element):
                        expanded = True
                        self.log.debug("通过 Alt+Down 展开下拉列表")
                except Exception as e:
                    self.log.debug(f"Alt+Down 失败: {e}")

            if not expanded:
                # 方式C: F4 键（WinForms 标准）
                try:
                    combobox_element.send_keys(Keys.F4)
                    time.sleep(0.5)
                    if self._is_dropdown_expanded(combobox_element):
                        expanded = True
                        self.log.debug("通过 F4 展开下拉列表")
                except Exception as e:
                    self.log.debug(f"F4 失败: {e}")

            if not expanded:
                # 方式D: 发送下拉箭头键
                try:
                    combobox_element.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.5)
                    if self._is_dropdown_expanded(combobox_element):
                        expanded = True
                        self.log.debug("通过 ARROW_DOWN 展开下拉列表")
                except Exception as e:
                    self.log.debug(f"ARROW_DOWN 失败: {e}")

            if not expanded:
                self.log.debug("无法展开下拉列表")
                return False

            # 3. 在展开的下拉列表中查找并点击选项
            self.log.debug(f"在下拉列表中查找选项: {option_text}")
            options = self._find_visible_options(option_text)

            if options:
                for option in options:
                    try:
                        option_text_attr = option.get_attribute("Name") or ""
                        self.log.debug(f"找到选项: {option_text_attr}")
                        if option_text in option_text_attr:
                            option.click()
                            time.sleep(0.3)
                            self.log.info(f"成功点击选项: {option_text}")
                            return True
                    except Exception as e:
                        self.log.debug(f"点击选项失败: {e}")
                        continue

            # 4. 如果点击方式失败，尝试键盘导航
            self.log.debug("尝试键盘导航方式")

            # 按HOME键回到第一个选项
            combobox_element.send_keys(Keys.HOME)
            time.sleep(0.3)

            for i in range(30):  # 最多遍历30个选项
                current_text = self._get_current_selected_text(combobox_element)
                self.log.debug(f"键盘导航当前选项 {i+1}: {current_text}")

                if current_text and option_text in current_text:
                    self.log.info(f"键盘导航找到匹配选项: {current_text}")
                    combobox_element.send_keys(Keys.ENTER)
                    time.sleep(0.5)
                    # 验证是否选择成功
                    final_text = self._get_current_selected_text(combobox_element)
                    self.log.debug(f"验证选择结果: {final_text}")
                    if option_text in final_text:
                        self.log.info(f"键盘导航选择成功: {final_text}")
                        return True

                combobox_element.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.2)

            # 如果还是找不到，尝试按End确认当前选择
            combobox_element.send_keys(Keys.ENTER)
            time.sleep(0.3)

            return False

        except Exception as e:
            self.log.debug(f"用户模拟策略失败: {e}")
            return False

    def _is_dropdown_expanded(self, combobox_element):
        """检查下拉列表是否已展开"""
        try:
            # 检查是否有可见的 ListBox 或 ComboBox 下拉部分
            # 通常展开后会有新的窗口/元素出现
            rect = combobox_element.get_attribute("BoundingRectangle")
            if rect:
                return True
            # 检查是否有弹出窗口
            expanded_state = combobox_element.get_attribute("ExpandCollapse.ExpandCollapseState")
            if expanded_state and "Expanded" in str(expanded_state):
                return True
        except Exception:
            pass
        return False

    def _find_visible_options(self, option_text):
        """查找可见的下拉选项"""
        options = []
        try:
            # 查找常见的下拉列表容器
            list_xpaths = [
                "//*[contains(@ClassName, 'ComboLBox')]",
                "//*[contains(@ClassName, 'WindowsForms10.LISTBOX')]",
                "//*[contains(@ClassName, 'DropDown')]",
            ]

            for xpath in list_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        if elem.is_displayed():
                            # 查找该列表中的选项
                            items = elem.find_elements(By.XPATH, ".//*")
                            for item in items:
                                try:
                                    if item.is_displayed():
                                        item_text = item.get_attribute("Name") or ""
                                        if item_text:
                                            options.append(item)
                                except Exception:
                                    continue
                except Exception:
                    continue

            # 备选方案：直接搜索包含目标文本的元素
            if not options:
                search_xpath = f"//*[(contains(@Name, '{option_text}') or contains(@LegacyIAccessible.Value, '{option_text}')) and @IsOffscreen='false']"
                try:
                    elements = self.driver.find_elements(By.XPATH, search_xpath)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            options.append(elem)
                except Exception:
                    pass

        except Exception as e:
            self.log.debug(f"查找选项失败: {e}")

        return options
    
    def _force_expand_dropdown(self, combobox_element):
        """强制展开下拉框"""
        try:
            # 方法1: 点击ComboBox
            combobox_element.click()
            time.sleep(0.3)
            
            # 方法2: 发送向下箭头键
            combobox_element.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            
            # 方法3: 发送Alt+向下箭头（标准展开快捷键）
            combobox_element.send_keys(Keys.ALT + Keys.ARROW_DOWN)
            time.sleep(0.5)
            
        except Exception as e:
            self.log.debug(f"强制展开下拉框失败: {e}")
    
    def _get_element_rect(self, element):
        """获取元素的位置信息"""
        try:
            rect_str = element.get_attribute("BoundingRectangle")
            if rect_str:
                return eval(rect_str)
        except Exception as e:
            self.log.debug(f"获取元素位置失败: {e}")
        return {"l": 0, "t": 0, "r": 1000, "b": 1000}
    
    def _find_dropdown_options(self, option_text, cb_rect, timeout):
        """使用多种策略查找下拉选项"""
        options = []
        
        # 策略A: WinForm特有的LISTBOX容器
        try:
            wait = WebDriverWait(self.driver, timeout)
            listbox_xpath = "//*[contains(@ClassName, 'WindowsForms10.LISTBOX') or contains(@ClassName, 'ComboLBox')]"
            listboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, listbox_xpath)))
            
            for listbox in listboxes:
                if listbox.is_displayed():
                    # 查找listbox内的选项
                    list_options = listbox.find_elements(By.XPATH, ".//*")
                    for opt in list_options:
                        opt_text = opt.get_attribute("Name") or opt.get_attribute("LegacyIAccessible.Value") or ""
                        if option_text in opt_text:
                            options.append(opt)
                            
        except Exception as e:
            self.log.debug(f"LISTBOX策略失败: {e}")
        
        # 策略B: 直接搜索包含目标文本的元素
        try:
            text_xpath = f"//*[(contains(@Name, '{option_text}') or contains(@LegacyIAccessible.Value, '{option_text}')) and @IsOffscreen='false']"
            text_options = self.driver.find_elements(By.XPATH, text_xpath)
            options.extend([opt for opt in text_options if opt.is_enabled()])
        except Exception as e:
            self.log.debug(f"文本搜索策略失败: {e}")
        
        # 策略C: 查找位置相关的选项（在ComboBox下方）
        try:
            all_elements = self.driver.find_elements(By.XPATH, "//*[@IsOffscreen='false']")
            for elem in all_elements:
                try:
                    elem_rect = self._get_element_rect(elem)
                    # 检查元素是否在ComboBox下方
                    if (elem_rect["t"] > cb_rect["b"] and 
                        elem_rect["l"] >= cb_rect["l"] - 50 and 
                        elem_rect["r"] <= cb_rect["r"] + 50):
                        
                        elem_text = elem.get_attribute("Name") or elem.get_attribute("LegacyIAccessible.Value") or ""
                        if option_text in elem_text:
                            options.append(elem)
                except:
                    continue
        except Exception as e:
            self.log.debug(f"位置相关策略失败: {e}")
        
        return options
    
    def _get_current_selected_text(self, combobox_element):
        """获取当前选中的选项文本 - 从ComboBox内部Edit控件获取"""
        try:
            # 方式1: 从ComboBox内部的Edit控件获取（最准确）
            try:
                edit_element = combobox_element.find_element(By.XPATH, ".//Edit")
                if edit_element:
                    text = edit_element.text or ""
                    if text:
                        return text.strip()
            except Exception:
                pass

            # 方式2: 从LegacyIAccessible获取
            text = combobox_element.get_attribute("LegacyIAccessible.Value") or ""
            if text:
                return text.strip()

            # 方式3: 从Value.Value获取
            text = combobox_element.get_attribute("Value.Value") or ""
            if text:
                return text.strip()

            # 方式4: 从Current.VALUE获取
            text = combobox_element.get_attribute("Current.VALUE") or ""
            if text:
                return text.strip()

            # 方式5: 从Name获取（这是ComboBox的标签，不是选中项）
            text = combobox_element.get_attribute("Name") or ""
            return text.strip()
        except Exception as e:
            self.log.debug(f"获取当前选中文本失败: {e}")
            return ""

    def _get_text_from_combo_edit(self, combobox_element):
        """从ComboBox的编辑部分获取文本（WinForms可编辑ComboBox）"""
        try:
            edit_element = combobox_element.find_element(By.XPATH, ".//Edit")
            if edit_element:
                return edit_element.text
        except Exception:
            pass
        return ""
    
    def verify_selection(self, combobox_element, expected_text):
        """验证选择结果"""
        try:
            time.sleep(0.3)  # 等待选择生效
            current_text = self._get_current_selected_text(combobox_element)
            is_match = expected_text in current_text if current_text else False
            self.log.debug(f"验证选择结果: 期望='{expected_text}', 实际='{current_text}', 匹配={is_match}")
            return is_match
        except Exception as e:
            self.log.debug(f"验证选择结果失败: {e}")
            return False