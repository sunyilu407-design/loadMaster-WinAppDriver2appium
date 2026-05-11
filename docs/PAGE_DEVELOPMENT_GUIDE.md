# 页面开发指南

本指南提供完整的页面开发流程、模板和示例，帮助快速开发新页面的自动化测试代码。

---

## 📋 目录

1. [开发流程](#开发流程)
2. [YAML配置模板](#yaml配置模板)
3. [PageObject类模板](#pageobject类模板)
4. [Handler类模板](#handler类模板)
5. [完整示例](#完整示例)
6. [常见问题](#常见问题)

---

## 🚀 开发流程

### 完整开发流程图

```
1. 用户提供YAML配置
   └─ 包含app_config和elements
   └─ 不需要test_data（由AI生成）

2. AI生成PageObject类
   └─ 基于elements生成操作方法
   └─ 自动继承公共弹窗方法

3. AI生成Handler类
   └─ 实现业务流程方法
   └─ 集成导航和验证逻辑

4. AI生成test_data模板
   └─ 运行工具自动生成
   └─ 用户填写具体测试值

5. 用户编写测试用例
   └─ 调用handler执行测试
   └─ 运行验证功能
```

### 用户操作步骤

```bash
# 步骤1: 创建YAML配置文件
vim data/pages/customer_management_page.yaml

# 步骤2: 告知AI需求
# "我写好了customer_management_page的YAML，需要实现添加、修改、删除客户功能"

# 步骤3: AI自动生成代码
# - pageObject/customer_management_page.py
# - handlers/customer_management_handler.py
# - test_data模板（追加到YAML）

# 步骤4: 填写test_data
vim data/pages/customer_management_page.yaml

# 步骤5: 运行测试
pytest testCase/test_customer_management_page.py -v
```

---

## 📄 YAML配置模板

### 基础模板

```yaml
# {page_name}_page.yaml 配置模板

# 应用配置（必需）
app_config:
  main_window_name: "窗口标题名称"           # 页面主窗口标题
  head_keys: ["列1", "列2", "列3"]         # 表格表头关键词（有表格时必需）

# 元素定位配置（必需）
elements:
  # ========== 按钮元素 ==========
  add_button:
    automation_id: "btnAdd"                 # AutomationId（优先）
    name: "添加"                            # Name属性（备选）
    type: "Button"                          # 控件类型（可选）
  
  edit_button:
    automation_id: "btnEdit"
  
  delete_button:
    automation_id: "btnDelete"
  
  # ========== 输入框元素 ==========
  name_input:
    automation_id: "txtName"
    type: "Edit"
  
  # ========== 下拉框元素 ==========
  type_combo:
    automation_id: "cboType"
    type: "ComboBox"
  
  # ========== 表格元素 ==========
  content_table:
    name: "DataGridView"                    # 表格通常用name定位
    # automation_id: "dgvContent"           # 或使用automation_id
  
  # ========== 子窗口（嵌套结构） ==========
  add_window:
    automation_id: "frmAdd"
    name: "添加窗口"
    type: "Window"
    child_elements:
      name_input:
        automation_id: "txtName"
      save_button:
        automation_id: "btnSave"
      cancel_button:
        automation_id: "btnCancel"

# 测试数据（由AI工具自动生成）
test_data:
  # AI生成后用户填写
```

### 带表格的页面示例

```yaml
app_config:
  main_window_name: "客户管理"
  head_keys: ["客户名称", "联系人", "联系电话", "地址"]

elements:
  # 主窗口按钮
  add_button:
    automation_id: "btnAdd"
  
  edit_button:
    automation_id: "btnEdit"
  
  delete_button:
    automation_id: "btnDelete"
  
  refresh_button:
    automation_id: "btnRefresh"
  
  # 表格
  content_table:
    name: "DataGridView"
  
  # 添加/编辑窗口
  edit_window:
    automation_id: "frmCustomerEdit"
    name: "客户信息"
    type: "Window"
    child_elements:
      customer_name_input:
        automation_id: "txtCustomerName"
      contact_person_input:
        automation_id: "txtContactPerson"
      phone_input:
        automation_id: "txtPhone"
      address_input:
        automation_id: "txtAddress"
      save_button:
        automation_id: "btnSave"
      cancel_button:
        automation_id: "btnCancel"
```

---

## 🔧 PageObject类模板

### 基础模板

```python
"""
{PageName} - 页面元素操作
只包含元素定位和基础交互，不含业务逻辑
"""

from pageObject.base_page import BasePage


class {PageName}Page(BasePage):
    """
    {页面描述} - 页面元素操作类
    """
    
    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")
        
        # 加载页面配置（自动合并公共弹窗）
        self.config = self.config_manager.load_page_config('{page_name}_page')
        
        # 检查配置
        if self.config is None:
            self.log.error("{PageName}Page: 配置加载失败")
            raise Exception("{PageName}Page: 配置加载失败")
        
        # 初始化配置项
        self.elements = self.config.get('elements', {})
        self.test_data = self.config.get('test_data', {})
        self.app_config = self.config.get('app_config', {})
    
    def _get_element_config(self, element_name):
        """获取元素配置（支持嵌套child_elements）"""
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
    
    # ========== 窗口切换方法 ==========
    def switch_to_{page_name}_window(self):
        """切换到{页面名称}窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])
    
    # ========== 按钮点击方法 ==========
    def click_add_button(self):
        """点击添加按钮"""
        self.switch_to_{page_name}_window()
        element_config = self._get_element_config('add_button')
        return self.click_element(**element_config)
    
    def click_edit_button(self):
        """点击修改按钮"""
        self.switch_to_{page_name}_window()
        element_config = self._get_element_config('edit_button')
        return self.click_element(**element_config)
    
    def click_delete_button(self):
        """点击删除按钮"""
        self.switch_to_{page_name}_window()
        element_config = self._get_element_config('delete_button')
        return self.click_element(**element_config)
    
    # ========== 输入方法 ==========
    def set_name_input(self, text):
        """输入名称"""
        element_config = self._get_element_config('name_input')
        return self.send_keys_to_element(text, **element_config)
    
    # ========== 下拉框操作 ==========
    def select_type_option(self, option_text):
        """选择类型下拉框选项"""
        element_config = self._get_element_config('type_combo')
        return self.select_combobox_option(option_text, **element_config)
    
    # ========== 表格操作方法 ==========
    def get_content_table(self):
        """获取内容表格数据"""
        self.switch_to_{page_name}_window()
        content_table = self._get_element_config('content_table')
        head_keys = self.app_config.get('head_keys')
        return self.get_table_data_as_json(content_table, head_keys)
    
    def click_table_one_row(self, search_criteria, match_mode='exact'):
        """点击表格指定行"""
        self.switch_to_{page_name}_window()
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config.get('head_keys')
        return self.click_table_row(content_table, search_criteria, header_keywords, match_mode)
    
    # ========== 公共弹窗操作（自动继承） ==========
    def switch_to_operation_window(self):
        """切换到操作提示窗口"""
        window_config = self._get_element_config('operation_window')
        return self.switch_to_window(title=window_config['name'])
    
    def click_operation_confirm_button(self):
        """点击操作窗口确认按钮"""
        self.switch_to_operation_window()
        window_config = self._get_element_config('operation_window')
        btn_config = window_config['child_elements']['confirm_button']
        return self.click_element(**btn_config)
    
    def click_operation_cancel_button(self):
        """点击操作窗口取消按钮"""
        self.switch_to_operation_window()
        window_config = self._get_element_config('operation_window')
        btn_config = window_config['child_elements']['cancel_button']
        return self.click_element(**btn_config)
```

---

## 🎯 Handler类模板

### 基础模板

```python
"""
{PageName}Handler - 业务逻辑处理
组合PageObject方法实现复杂业务流程
"""

import logging
import allure
from handlers.main_handler import MainHandler
from pageObject.{page_name}_page import {PageName}Page


class {PageName}Handler:
    """
    {页面名称}Handler - 业务逻辑处理类
    """
    
    def __init__(self, page_instance=None, config_manager=None):
        """初始化Handler"""
        if page_instance:
            self.page = page_instance
        else:
            from utils.driver_factory import DriverFactory
            driver = DriverFactory.get_windows_driver()
            self.page = {PageName}Page(driver, config_manager)
        
        self.config_manager = config_manager
        self.log = logging.getLogger(__name__)
        
        # 初始化main_handler用于导航
        from pageObject.main_page import MainPage
        self.main_page = MainPage(self.page.driver, config_manager)
        self.main_handler = MainHandler(self.main_page)
    
    # ========== 业务流程方法 ==========
    def add_and_verify(self, name, type_option, confirm=True, timeout=5.0):
        """
        添加数据并验证

        参数：
            name: 名称
            type_option: 类型选项
            confirm: 是否确认操作
            timeout: 超时时间

        返回：
            dict: {'success': bool, 'error': str, ...}
        """
        with allure.step(f"添加数据并验证 (名称: {name})"):
            # 1. 导航到页面（如需要）
            # if not self.main_handler.navigate_to_xxx():
            #     return {'success': False, 'error': '导航失败'}

            # 2. 执行添加操作
            with allure.step("填写数据表单"):
                self.page.click_add_button()
                self.page.set_name_input(name)
                self.page.select_type_option(type_option)
                self.page.click_save_button()

            # 3. 处理弹窗
            action = 'confirm' if confirm else 'cancel'
            with allure.step(f"处理操作提示 ({action})"):
                if not self.handle_operation_prompt(action=action, timeout=timeout):
                    return {'success': False, 'error': '弹窗处理失败'}

            # 4. 验证结果
            with allure.step("验证数据添加结果"):
                return self.verify_in_table({'名称': name}, expected_presence='present')
    
    def delete_and_verify(self, name, confirm=True, timeout=5.0):
        """
        删除数据并验证
        
        参数：
            name: 要删除的数据名称
            confirm: 是否确认删除
            timeout: 超时时间
        
        返回：
            dict: {'success': bool, 'error': str, ...}
        """
        # 1. 点击表格行选中数据
        if not self.page.click_table_one_row({'名称': name}):
            return {'success': False, 'error': f'未找到数据: {name}'}
        
        # 2. 点击删除按钮
        if not self.page.click_delete_button():
            return {'success': False, 'error': '点击删除按钮失败'}
        
        # 3. 处理确认弹窗
        action = 'confirm' if confirm else 'cancel'
        if not self.handle_operation_prompt(action=action, timeout=timeout):
            return {'success': False, 'error': '弹窗处理失败'}
        
        # 4. 验证结果
        expected = 'absent' if confirm else 'present'
        return self.verify_in_table({'名称': name}, expected_presence=expected)
    
    # ========== 弹窗处理方法 ==========
    def wait_for_operation_window(self, timeout=5.0, poll_interval=0.5):
        """轮询等待操作提示窗口出现"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.page.switch_to_operation_window():
                return True
            time.sleep(poll_interval)
        self.log.error("等待操作提示窗口超时")
        return False
    
    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        """
        通用弹窗处理方法
        
        参数：
            action: 'confirm'(确认) / 'cancel'(取消) / 'quit'(退出)
            timeout: 超时时间
        """
        if not self.wait_for_operation_window(timeout):
            return False
        
        if action == 'confirm':
            return self.page.click_operation_confirm_button()
        elif action == 'cancel':
            return self.page.click_operation_cancel_button()
        elif action == 'quit':
            return self.page.click_operation_quit_button()
        
        self.log.error(f"未知动作: {action}")
        return False
    
    # ========== 表格验证方法 ==========
    def verify_in_table(self, search_criteria, expected_presence='present', 
                       match_mode='exact', timeout=5.0):
        """
        验证数据是否在表格中
        
        参数：
            search_criteria: 搜索条件，如 {"名称": "测试"}
            expected_presence: 'present'(应存在) 或 'absent'(应不存在)
            match_mode: 'exact'(精确匹配) 或 'partial'(包含匹配)
            timeout: 超时时间
        
        返回：
            dict: {
                'success': bool,
                'matched_rows': list,
                'total_rows': int,
                'count': int
            }
        """
        self.page.switch_to_{page_name}_window()
        
        content_table = self.page._get_element_config('content_table')
        header_keywords = self.page.app_config.get('head_keys')
        
        return self.page.query_table_after_operation(
            content_table=content_table,
            search_criteria=search_criteria,
            header_keywords=header_keywords,
            match_mode=match_mode,
            expected_presence=expected_presence,
            timeout=timeout
        )
```

---

## 💡 完整示例

### 示例：客户管理页面

#### 1. YAML配置

```yaml
# data/pages/customer_management_page.yaml

app_config:
  main_window_name: "客户管理"
  head_keys: ["客户名称", "联系人", "联系电话", "地址"]

elements:
  # 主窗口按钮
  add_button:
    automation_id: "btnAdd"
  
  edit_button:
    automation_id: "btnEdit"
  
  delete_button:
    automation_id: "btnDelete"
  
  # 表格
  content_table:
    name: "DataGridView"
  
  # 编辑窗口
  edit_window:
    automation_id: "frmCustomerEdit"
    name: "客户编辑"
    child_elements:
      customer_name_input:
        automation_id: "txtCustomerName"
      contact_input:
        automation_id: "txtContact"
      phone_input:
        automation_id: "txtPhone"
      address_input:
        automation_id: "txtAddress"
      save_button:
        automation_id: "btnSave"
      cancel_button:
        automation_id: "btnCancel"

test_data:
  add_customer_scenario:
    _description: "添加客户并验证"
    _method: "add_customer_and_verify"
    customer_name: "测试公司"
    contact_person: "张三"
    phone: "13800138000"
    address: "测试地址"
    confirm: true
  
  delete_customer_scenario:
    _description: "删除客户并验证"
    _method: "delete_customer_and_verify"
    customer_name: "测试公司"
    confirm: true
```

#### 2. PageObject类

```python
"""
客户管理页面 - 页面元素操作
"""

from pageObject.base_page import BasePage


class CustomerManagementPage(BasePage):
    """客户管理页面 - 页面元素操作类"""
    
    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")
        self.config = self.config_manager.load_page_config('customer_management_page')
        
        if self.config is None:
            self.log.error("CustomerManagementPage: 配置加载失败")
            raise Exception("CustomerManagementPage: 配置加载失败")
        
        self.elements = self.config.get('elements', {})
        self.test_data = self.config.get('test_data', {})
        self.app_config = self.config.get('app_config', {})
    
    def _get_element_config(self, element_name):
        """获取元素配置"""
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
        
        return find_element(self.elements, element_name)
    
    # 窗口切换
    def switch_to_customer_window(self):
        """切换到客户管理窗口"""
        return self.switch_to_window(title=self.app_config['main_window_name'])
    
    # 按钮操作
    def click_add_button(self):
        """点击添加按钮"""
        self.switch_to_customer_window()
        return self.click_element(**self._get_element_config('add_button'))
    
    def click_delete_button(self):
        """点击删除按钮"""
        self.switch_to_customer_window()
        return self.click_element(**self._get_element_config('delete_button'))
    
    # 输入操作
    def set_customer_name(self, text):
        """输入客户名称"""
        return self.send_keys_to_element(text, **self._get_element_config('customer_name_input'))
    
    # 表格操作
    def click_table_row_by_name(self, customer_name):
        """根据客户名称点击表格行"""
        self.switch_to_customer_window()
        content_table = self._get_element_config('content_table')
        return self.click_table_row(
            content_table, 
            {'客户名称': customer_name}, 
            self.app_config['head_keys']
        )
```

#### 3. Handler类

```python
"""
客户管理Handler - 业务逻辑处理
"""

import logging
from handlers.main_handler import MainHandler
from pageObject.customer_management_page import CustomerManagementPage


class CustomerManagementHandler:
    """客户管理Handler"""
    
    def __init__(self, page_instance=None, config_manager=None):
        if page_instance:
            self.page = page_instance
        else:
            from utils.driver_factory import DriverFactory
            driver = DriverFactory.get_windows_driver()
            self.page = CustomerManagementPage(driver, config_manager)
        
        self.config_manager = config_manager
        self.log = logging.getLogger(__name__)
        
        from pageObject.main_page import MainPage
        self.main_page = MainPage(self.page.driver, config_manager)
        self.main_handler = MainHandler(self.main_page)
    
    def add_customer_and_verify(self, customer_name, contact_person, phone, address, confirm=True):
        """添加客户并验证"""
        # 执行添加
        self.page.click_add_button()
        self.page.set_customer_name(customer_name)
        # ... 其他输入
        
        # 处理弹窗
        if not self.handle_operation_prompt('confirm' if confirm else 'cancel'):
            return {'success': False, 'error': '弹窗处理失败'}
        
        # 验证
        return self.verify_customer_in_table(customer_name, 'present')
    
    def handle_operation_prompt(self, action='confirm', timeout=5.0):
        """处理操作弹窗"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.page.switch_to_operation_window():
                if action == 'confirm':
                    return self.page.click_operation_confirm_button()
                return self.page.click_operation_cancel_button()
            time.sleep(0.5)
        return False
    
    def verify_customer_in_table(self, customer_name, expected_presence='present'):
        """验证客户是否在表格中"""
        result = self.page.query_table_after_operation(
            content_table=self.page._get_element_config('content_table'),
            search_criteria={'客户名称': customer_name},
            header_keywords=self.page.app_config['head_keys'],
            expected_presence=expected_presence
        )
        return result
```

---

## ❓ 常见问题

### Q1: 如何处理多层嵌套窗口？

**答**：在PageObject中为每个窗口创建切换方法：

```python
def switch_to_main_window(self):
    return self.switch_to_window(title="主窗口")

def switch_to_add_window(self):
    return self.switch_to_window(title="添加窗口")

def switch_to_confirm_window(self):
    return self.switch_to_window(title="确认窗口")
```

### Q2: 表格数据获取不正确怎么办？

**答**：检查以下几点：
1. `head_keys`是否准确匹配表头
2. 操作前是否切换到正确窗口
3. 是否等待表格加载完成

### Q3: 如何处理动态加载的元素？

**答**：使用`wait_for_element`方法：

```python
def click_dynamic_button(self):
    element_config = self._get_element_config('dynamic_button')
    element = self.wait_for_element(timeout=10, **element_config)
    if element:
        return element.click()
    return False
```

### Q4: Handler中如何实现复杂的业务流程？

**答**：将复杂流程拆分为多个步骤方法：

```python
def complex_workflow(self, data):
    # 步骤1: 导航
    if not self._navigate_to_page():
        return self._error_result('导航失败')
    
    # 步骤2: 填写表单
    if not self._fill_form(data):
        return self._error_result('表单填写失败')
    
    # 步骤3: 提交并处理弹窗
    if not self._submit_and_confirm():
        return self._error_result('提交失败')
    
    # 步骤4: 验证结果
    return self._verify_result(data)
```

### Q5: 如何生成test_data模板？

**答**：使用自动生成工具：

```bash
# 生成test_data模板
python utils/generate_test_data_template.py handlers.customer_management_handler CustomerManagementHandler

# 生成并保存到YAML文件
python utils/generate_test_data_template.py handlers.customer_management_handler CustomerManagementHandler data/pages/customer_test_data.yaml
```

---

## 📚 参考资源

- [.cursorrules](.cursorrules) - 完整开发规则
- [common_dialogs.yaml](../data/pages/common_dialogs.yaml) - 公共弹窗配置
- [base_page.py](../pageObject/base_page.py) - 基础页面类
- [handler_factory.py](../handlers/handler_factory.py) - Handler工厂

---

**版本**: v1.0  
**最后更新**: 2024-11  
**维护者**: AI Assistant

