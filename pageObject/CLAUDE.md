[根目录](../../CLAUDE.md) > **pageObject**

## PageObject 模块文档

### 模块职责

PageObject模块采用页面对象设计模式（Page Object Pattern），封装了Windows桌面应用的UI元素定位和操作逻辑。它将页面元素与业务操作分离，提供稳定的元素定位策略和可复用的操作方法，是自动化测试框架的核心基础层。

### 入口与启动

#### 核心页面类
- **BasePage**: 基础页面类，提供通用元素操作和高级功能
- **LoginPage**: 登录页面，处理用户认证相关UI操作
- **MainPage**: 主页面，处理导航和菜单操作
- **UserManagementPage**: 用户管理页面，处理用户CRUD的UI操作
- **UserProfilePage**: 用户资料页面，处理个人信息管理

#### 页面初始化
```python
# 标准初始化模式
class LoginPage(BasePage):
    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, platform="windows")
        self.config = config_manager.load_page_config('login_page')
        self.elements = self.config.get('elements', {})
```

### 对外接口

#### BasePage 核心接口
```python
class BasePage:
    # 元素定位
    def locate_element(timeout=10, **kwargs) -> WebElement
    def locate_elements(**kwargs) -> List[WebElement]
    def wait_for_element(timeout=10, **kwargs) -> WebElement
    def is_element_present(timeout=5, **kwargs) -> bool

    # 元素操作
    def click_element(**kwargs) -> bool
    def send_keys_to_element(text, **kwargs) -> bool
    def get_element_text(**kwargs) -> str
    def take_screenshot(filename=None) -> str

    # 高级功能
    def get_table_data_as_json(content_table, header_keywords=None) -> List[dict]
    def click_table_row(content_table, search_criteria, **kwargs) -> bool
    def select_combobox_option(option_text, **kwargs) -> bool
    def check_tree_nodes_with_space_key(tree_locator, node_names) -> bool

    # 弹窗处理
    def handle_operation_prompt(**kwargs) -> bool
    def handle_prompt_window(**kwargs) -> bool
```

#### 页面特定接口
```python
class LoginPage(BasePage):
    def clear_input_fields() -> bool
    def login(username, password) -> bool
    def get_error_message() -> str
    def is_login_successful() -> bool

class MainPage(BasePage):
    def navigate_to_menu(menu_path) -> bool
    def get_menu_items() -> List[str]
    def is_menu_visible(menu_name) -> bool

class UserManagementPage(BasePage):
    def search_users(search_criteria) -> List[dict]
    def add_user(user_data) -> bool
    def edit_user(user_id, user_data) -> bool
    def delete_user(user_id) -> bool
```

### 关键依赖与配置

#### WinAppDriver集成
- **定位策略**: 支持AutomationId、Name、XPath、ClassName等多种定位方式
- **元素等待**: 智能等待和超时处理机制
- **平台兼容**: 专门针对Windows桌面应用优化

#### 配置驱动
```yaml
# 示例: login_page.yaml
elements:
  username_input:
    automation_id: "txtUserName"
    name: "用户名输入框"
    type: "Edit"
  password_input:
    automation_id: "txtPassword"
    name: "密码输入框"
    type: "Edit"
  login_button:
    automation_id: "btnLogin"
    name: "登录按钮"
    type: "Button"

test_data:
  valid_login:
    username: "admin"
    password: "123456"
```

#### 依赖模块
- **selenium**: WebDriver API
- **utils.config_manager**: 配置管理
- **utils.driver_factory**: 驱动工厂
- **data.pages**: 页面元素配置

### 数据模型

#### 元素定位模型
```python
element_locator = {
    "automation_id": "txtUserName",      # 优先使用AutomationId
    "name": "用户名",                   # 备用Name属性
    "type": "Edit",                     # 控件类型
    "xpath": "//Edit[@AutomationId='txtUserName']",  # XPath表达式
    "timeout": 10                       # 超时时间
}
```

#### 表格数据模型
```python
table_data = [
    {
        "用户姓名": "张三",
        "用户类型": "操作员",
        "注册时间": "2024-01-01",
        "备注": "测试用户"
    },
    {
        "用户姓名": "李四",
        "用户类型": "管理员",
        "注册时间": "2024-01-02",
        "备注": "管理员用户"
    }
]
```

#### 弹窗配置模型
```yaml
# common_dialogs.yaml
common_dialogs:
  operation_window:
    name: "操作提示"
    child_elements:
      prompt_text:
        automation_id: "lblMessage"
      confirm_button:
        automation_id: "btnConfirm"
      cancel_button:
        automation_id: "btnCancel"
```

### 测试与质量

#### 元素定位策略
1. **优先级顺序**: AutomationId > Name > XPath > ClassName
2. **兼容性处理**: 针对WinAppDriver的特殊优化
3. **重试机制**: 自动重试失败的元素定位
4. **超时管理**: 可配置的等待超时时间

#### 特殊控件处理
```python
# 表格操作
table_data = self.get_table_data_as_json(
    content_table=self.elements['content_table'],
    header_keywords=["用户姓名", "用户类型", "注册时间", "备注"]
)

# 下拉框选择
self.select_combobox_option(
    option_text="管理员",
    automation_id="cmbUserType"
)

# 树节点勾选
self.check_tree_nodes_with_space_key(
    tree_locator=self.elements['system_tree'],
    node_names=["发油系统", "排队系统"]
)
```

#### 错误处理
- 元素未找到自动截图
- 详细的错误日志记录
- 智能重试机制
- 降级策略处理

### 常见问题 (FAQ)

#### Q1: WinAppDriver元素定位失败怎么办？
**A**:
1. 使用Inspect.exe工具检查元素属性
2. 优先使用AutomationId定位
3. 尝试组合定位方式（如AutomationId + Type）
4. 增加等待超时时间

#### Q2: 如何处理动态表格数据？
**A**:
```python
# 使用表格数据获取方法
table_data = self.get_table_data_as_json(
    content_table=table_locator,
    header_keywords=expected_headers
)

# 点击特定行
self.click_table_row(
    content_table=table_locator,
    search_criteria={"用户姓名": "张三"},
    match_mode='exact'
)
```

#### Q3: 如何处理WinForm控件？
**A**:
- 使用专门的WinFormComboBoxHandler处理下拉框
- 对于特殊控件，使用键盘操作模拟
- 考虑使用坐标定位作为最后手段

### 相关文件清单

#### 核心页面文件
- `base_page.py` - 基础页面类，2000+行代码，功能完整
- `login_page.py` - 登录页面实现
- `main_page.py` - 主页面实现

#### 用户管理页面
- `user/userManagement/user_management_page.py` - 用户管理页面
- `user/userProfile/user_profile_page.py` - 用户资料页面

#### 配置文件
- `../data/pages/login_page.yaml` - 登录页面元素配置
- `../data/pages/main_page.yaml` - 主页面元素配置
- `../data/pages/user/user_management_page.yaml` - 用户管理页面配置
- `../data/pages/common_dialogs.yaml` - 通用弹窗配置

#### 工具类
- `../utils/winform_combobox_handler.py` - WinForm下拉框处理器

### 变更记录 (Changelog)

#### 2025-12-29 11:39:10
- ✅ 创建pageObject模块文档
- ✅ 添加导航面包屑链接
- ✅ 完善元素定位策略说明
- ✅ 更新特殊控件处理文档

#### 2024-XX-XX
- 完成从pywinauto到WinAppDriver的迁移
- 增加表格数据获取和操作功能
- 优化元素定位兼容性
- 添加WinForm控件特殊处理
- 完善弹窗处理机制

---

**提示**: 在编写新的页面对象时，请优先使用AutomationId定位方式，并在YAML配置文件中完整定义页面元素，确保代码的可维护性和可读性。