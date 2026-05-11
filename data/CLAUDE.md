[根目录](../../CLAUDE.md) > **data**

## Data 模块文档

### 模块职责

Data模块是项目的数据管理中心，负责管理所有测试数据、页面元素配置、通用控件配置等。通过YAML格式的配置文件，实现数据与代码的分离，提供灵活的数据驱动测试支持。

### 入口与启动

#### 数据结构概览
```
data/
├── pages/                   # 页面配置目录
│   ├── login_page.yaml      # 登录页面配置
│   ├── main_page.yaml       # 主页面配置
│   ├── common_dialogs.yaml  # 通用弹窗配置
│   └── user/              # 用户管理相关页面配置
│       ├── user_management_page.yaml
│       └── user_profile_page.yaml
├── test_data/              # 测试数据目录（预留）
└── fixtures/              # 测试夹具数据目录（预留）
```

#### 配置加载方式
```python
# 通过ConfigManager加载页面配置
from utils.config_manager import ConfigManager

config_manager = ConfigManager()
page_config = config_manager.load_page_config('login_page')

# 获取页面元素配置
elements = page_config.get('elements', {})
test_data = page_config.get('test_data', {})
```

### 配置文件详解

#### 登录页面配置 (login_page.yaml)
```yaml
# 登录页面配置文件
page_info:
  name: "登录页面"
  description: "发油系统用户登录页面"
  url: ""  # WinAppDriver不使用URL

elements:
  # 用户名输入框
  username_input:
    automation_id: "txtUserName"
    name: "用户名"
    type: "Edit"
    description: "用户名输入框控件"
    timeout: 10

  # 密码输入框
  password_input:
    automation_id: "txtPassword"
    name: "密码"
    type: "Edit"
    description: "密码输入框控件"
    timeout: 10

  # 登录按钮
  login_button:
    automation_id: "btnLogin"
    name: "登录"
    type: "Button"
    description: "登录按钮"
    timeout: 10

  # 错误提示标签
  error_message:
    automation_id: "lblError"
    name: "错误提示"
    type: "Text"
    description: "登录错误提示信息"
    timeout: 5

test_data:
  # 有效登录凭据
  valid_login:
    username: "admin"
    password: "admin123"
    description: "有效的管理员账户"

  # 无效登录凭据
  invalid_credentials:
    description: "无效登录测试用例"
    test_cases:
      - username: ""
        password: ""
        expected_error: "用户名不能为空"
        description: "用户名和密码都为空"

      - username: "wrong_user"
        password: "wrong_pass"
        expected_error: "用户名或密码错误"
        description: "用户名或密码错误"

      - username: "admin"
        password: "wrong_pass"
        expected_error: "用户名或密码错误"
        description: "密码错误"
```

#### 主页面配置 (main_page.yaml)
```yaml
# 主页面配置文件
page_info:
  name: "主页面"
  description: "发油系统主操作界面"

elements:
  # 主菜单树控件
  main_menu_tree:
    automation_id: "treeMain"
    name: "功能菜单"
    type: "Tree"
    description: "系统主要功能菜单树"
    timeout: 10

  # 用户信息管理菜单项
  user_info_menu:
    name: "用户信息管理"
    control_type: "TreeItem"
    description: "用户信息管理菜单项"
    xpath: "//TreeItem[@Name='用户信息管理']"

  # 状态栏
  status_bar:
    automation_id: "statusBar"
    name: "状态栏"
    type: "StatusBar"
    description: "底部状态栏信息"
    timeout: 5

head_keys:
  - "用户姓名"
  - "用户类型"
  - "注册时间"
  - "备注"

navigation_paths:
  user_management:
    - "基础管理"
    - "用户信息管理"

  oil_dispatch:
    - "发油管理"
    - "发油操作"
```

#### 通用弹窗配置 (common_dialogs.yaml)
```yaml
# 通用弹窗配置文件
common_dialogs:
  # 操作提示窗口
  operation_window:
    name: "操作提示"
    description: "确认操作的提示窗口"
    window_type: "confirmation"

    child_elements:
      # 提示文本
      prompt_text:
        automation_id: "lblMessage"
        name: "提示信息"
        type: "Text"
        description: "操作提示文本内容"
        timeout: 5

      # 确认按钮
      confirm_button:
        automation_id: "btnConfirm"
        name: "确认"
        type: "Button"
        description: "确认操作按钮"
        timeout: 5

      # 取消按钮
      cancel_button:
        automation_id: "btnCancel"
        name: "取消"
        type: "Button"
        description: "取消操作按钮"
        timeout: 5

      # 退出按钮
      quit_button:
        automation_id: "btnQuit"
        name: "退出"
        type: "Button"
        description: "退出操作按钮"
        timeout: 5

  # 消息提示窗口
  prompt_window:
    name: "提示"
    description: "信息提示窗口"
    window_type: "information"

    child_elements:
      # 提示文本
      prompt_text:
        automation_id: "lblMessage"
        name: "提示信息"
        type: "Text"
        description: "信息提示文本内容"
        timeout: 5

      # 确认按钮
      confirm_button:
        automation_id: "btnOK"
        name: "确定"
        type: "Button"
        description: "确定按钮"
        timeout: 5
```

#### 用户管理页面配置 (user/user_management_page.yaml)
```yaml
# 用户管理页面配置
page_info:
  name: "用户管理页面"
  description: "用户信息管理操作界面"

elements:
  # 查询输入框
  search_input:
    automation_id: "txtSearch"
    name: "查询"
    type: "Edit"
    description: "用户查询输入框"
    timeout: 10

  # 查询按钮
  search_button:
    automation_id: "btnSearch"
    name: "查询"
    type: "Button"
    description: "执行查询按钮"
    timeout: 10

  # 新增按钮
  add_button:
    automation_id: "btnAdd"
    name: "新增"
    type: "Button"
    description: "新增用户按钮"
    timeout: 10

  # 编辑按钮
  edit_button:
    automation_id: "btnEdit"
    name: "编辑"
    type: "Button"
    description: "编辑用户按钮"
    timeout: 10

  # 删除按钮
  delete_button:
    automation_id: "btnDelete"
    name: "删除"
    type: "Button"
    description: "删除用户按钮"
    timeout: 10

  # 用户数据表格
  user_table:
    automation_id: "gridUser"
    name: "用户列表"
    type: "DataGrid"
    description: "用户信息数据表格"
    timeout: 10

# 表格表头关键字，用于数据获取
head_keys:
  - "用户姓名"
  - "用户类型"
  - "注册时间"
  - "备注"

test_data:
  # 测试用户数据
  sample_users:
    - name: "测试用户01"
      type: "操作员"
      description: "测试添加的操作员用户"

    - name: "测试用户02"
      type: "管理员"
      description: "测试添加的管理员用户"

  # 查询测试数据
  search_cases:
    - keyword: "admin"
      expected_count: 1
      description: "查询admin用户"

    - keyword: "测试"
      expected_count: 2
      description: "查询测试用户"
```

### 数据模型规范

#### 元素定位模型
```yaml
element_locator:
  # 优先使用AutomationId（最稳定）
  automation_id: "element_id"

  # 备用定位方式
  name: "元素显示名称"
  control_type: "控件类型"    # TreeItem, Button, Edit, DataGrid等
  type: "控件类名"          # WinForm控件类名

  # XPath定位（最后选择）
  xpath: "//Control[@AutomationId='element_id']"

  # 其他属性
  description: "元素描述"
  timeout: 10               # 超时时间（秒）
  index: 0                  # 索引（多个同名元素时使用）
```

#### 测试数据模型
```yaml
test_data_structure:
  test_suite_name:
    description: "测试套件描述"

    # 单个测试用例
    test_case_name:
      # 输入数据
      input_data:
        field1: "value1"
        field2: "value2"

      # 预期结果
      expected_result:
        success: true
        message: "操作成功"

      # 用例描述
      description: "测试用例描述"

    # 批量测试数据
    test_cases:
      - input_data:
          field1: "value1"
        expected_result:
          success: true
        description: "用例1描述"

      - input_data:
          field1: "value2"
        expected_result:
          success: false
        description: "用例2描述"
```

### 配置管理

#### 配置文件命名规范
- **页面配置**: `{page_name}_page.yaml`
- **业务模块配置**: `{module_name}.yaml`
- **通用配置**: `common_{functionality}.yaml`
- **测试数据**: `test_{scenario}.yaml`

#### 配置版本管理
```yaml
# 配置文件版本信息
config_metadata:
  version: "1.0.0"
  last_updated: "2025-12-29"
  updated_by: "自动化测试团队"
  changelog:
    - version: "1.0.0"
      date: "2025-12-29"
      changes: ["初始版本创建"]
```

### 数据验证

#### 配置文件验证
```python
def validate_yaml_config(file_path):
    """验证YAML配置文件格式"""
    try:
        import yaml
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 检查必需字段
        if 'elements' not in config_data:
            raise ValueError("缺少elements配置")

        # 验证元素配置格式
        for element_name, element_config in config_data['elements'].items():
            if not any(key in element_config for key in ['automation_id', 'name', 'xpath']):
                raise ValueError(f"元素{element_name}缺少定位信息")

        return True
    except Exception as e:
        print(f"配置验证失败: {e}")
        return False
```

#### 数据完整性检查
```python
def check_data_integrity(page_config):
    """检查配置数据完整性"""
    elements = page_config.get('elements', {})

    # 检查关键元素
    required_elements = ['login_button', 'username_input', 'password_input']
    missing_elements = [elem for elem in required_elements if elem not in elements]

    if missing_elements:
        print(f"缺少关键元素配置: {missing_elements}")
        return False

    return True
```

### 常见问题 (FAQ)

#### Q1: 如何添加新的页面配置？
**A**:
1. 在`data/pages/`目录下创建新的YAML文件
2. 按照标准模板编写配置
3. 在`ConfigManager`中添加对应的加载方法
4. 创建对应的页面对象类

#### Q2: 如何处理动态元素？
**A**:
```yaml
# 使用索引定位动态元素
dynamic_elements:
  table_row:
    xpath: "//DataGridRow[@Index='{index}']"
    description: "动态表格行，使用索引"
    index_variable: "index"

  list_item:
    xpath: "//ListItem[contains(@Name, '{text}')]"
    description: "动态列表项，使用文本匹配"
    text_variable: "text"
```

#### Q3: 如何配置多语言元素？
**A**:
```yaml
# 多语言元素配置
multilingual_elements:
  login_button:
    zh_cn: "登录"
    en_us: "Login"
    automation_id: "btnLogin"  # 优先使用ID，不依赖语言

  username_label:
    zh_cn: "用户名"
    en_us: "Username"
    automation_id: "lblUsername"
```

#### Q4: 如何优化元素定位？
**A**:
1. **优先级顺序**: AutomationId > Name > XPath
2. **组合定位**: 使用多个属性组合提高准确性
3. **相对定位**: 基于稳定元素的相对位置定位
4. **超时设置**: 根据元素加载时间合理设置超时

### 相关文件清单

#### 页面配置文件
- `pages/login_page.yaml` - 登录页面配置
- `pages/main_page.yaml` - 主页面配置
- `pages/common_dialogs.yaml` - 通用弹窗配置
- `pages/user/user_management_page.yaml` - 用户管理页面配置
- `pages/user/user_profile_page.yaml` - 用户资料页面配置

#### 配置管理代码
- `../utils/config_manager.py` - 配置管理器
- `../utils/env.py` - 环境配置读取

#### 验证工具
- `validate_config.py` - 配置文件验证工具（可创建）

### 变更记录 (Changelog)

#### 2025-12-29 11:39:10
- ✅ 创建data模块文档
- ✅ 添加导航面包屑链接
- ✅ 完善配置文件结构说明
- ✅ 添加数据模型规范

#### 2024-XX-XX
- 完成页面配置文件创建
- 添加通用弹窗配置
- 优化配置文件格式
- 增加多语言支持

---

**提示**: 在编辑YAML配置文件时，请注意缩进和语法正确性。建议使用YAML编辑器插件进行语法检查，确保文件格式正确。