# 测试用例开发规范文档

## 🎯 开发规范要求

基于项目现有架构，我们采用**传统测试用例开发模式**：手动实例化页面对象→传递给Handler→执行业务逻辑。

### 📋 核心开发模式

#### 1. 页面对象实例化模式
```python
# 推荐模式：手动实例化页面对象
driver = DriverFactory.get_windows_driver()
page_instance = LoginPage(driver, config_manager)
handler = LoginHandler(page_instance, config_manager)

# 惰性初始化模式（测试夹具中使用）
page_instance = LoginPage  # 传递类
handler = LoginHandler(page_instance, config_manager)
handler._ensure_pages()  # 首次使用时自动初始化
```

#### 2. 测试类标准结构
```python
class TestLoginPage:
    @pytest.fixture(autouse=True)
    def setup_test_resources(self, page_test_factory):
        """自动设置测试资源"""
        self.resources = page_test_factory
        self.driver = self.resources['driver']
        self.page = self.resources['page']
        self.handler = self.resources['handler']
        self.config_manager = self.resources['config_manager']
        self.page_config = self.resources['page_config']
        self.log = self.resources['log']

    def test_valid_login(self):
        """测试有效凭据登录"""
        result = self.handler.login("admin", "123456")
        assert result is True
        self.log.info("✅ 有效登录测试通过")
```

### 🔧 配置文件使用

#### YAML测试数据配置
```yaml
# test_login_page.yaml
test_data:
  valid_login_scenario:
    _description: "有效用户名和密码登录"
    _method: "login"
    username: "admin"
    password: "123456"
    expected_result: True
    timeout: 10.0

  invalid_credentials_scenario:
    _description: "无效凭据登录"
    _method: "login"
    username: "wrong_user"
    password: "wrong_password"
    expected_result: False
    expected_error: "用户名或密码错误"
    timeout: 10.0
```

#### 测试夹具配置（conftest.py）
```python
# 页面测试夹具 - 为每个页面提供统一资源
@pytest.fixture(scope="class")
def page_test_fixture(request, test_setup):
    # 根据测试类名自动推断页面配置
    class_name = request.cls.__name__  # TestLoginPage -> login_page
    page_name = convert_class_to_page_name(class_name)

    # 手动创建页面对象实例
    driver = test_setup['driver']
    config_manager = test_setup['config_manager']
    page_config = config_manager.load_page_config(page_name)

    # 动态导入页面对象类
    page_module = __import__(f"pageObject.{page_name}")
    page_class_name = convert_class_to_page_class(class_name)
    page_class = getattr(page_module, page_class_name)
    page_instance = page_class(driver, config_manager)

    # 创建Handler实例（传统方式）
    if page_name == 'login_page':
        from handlers.login_handler import LoginHandler
        handler = LoginHandler(page_instance, config_manager)
    # ... 其他页面Handler

    return {
        'driver': driver,
        'page': page_instance,
        'handler': handler,
        'config_manager': config_manager,
        'page_config': page_config,
        'log': logging.getLogger(f"{page_name}_test")
    }
```

### 📝 测试用例编写规范

#### 1. 命名规范
```python
# 文件命名：test_[page_name].py
# 类命名：Test[PageName]  - TestLoginPage, TestMainPage, TestUserManagement
# 方法命名：test_[feature_scenario]  - test_valid_login, test_logout_function, test_switch_user
```

#### 2. 断言规范
```python
def test_login_success(self):
    """测试登录成功场景"""
    result = self.handler.login("admin", "123456")

    # 使用assert进行断言
    assert result is True, "登录应该成功"
    assert self.page.is_login_successful(), "应该显示登录成功状态"

    # 记录测试结果
    self.log.info("✅ 登录成功测试通过")

def test_login_failure(self):
    """测试登录失败场景"""
    result = self.handler.login("wrong", "wrong")

    # 验证失败场景
    assert result is False, "登录应该失败"
    error_msg = self.page.get_error_message()
    assert "用户名或密码错误" in error_msg, "应该显示错误消息"

    self.log.info(f"✅ 登录失败测试通过：{error_msg}")
```

#### 3. 数据驱动测试
```python
@pytest.mark.parametrize("username,password,expected_result", [
    ("admin", "123456", True),
    ("", "", False),
    ("wrong_user", "wrong_pass", False)
])
def test_login_scenarios(self, username, password, expected_result):
    """数据驱动登录测试"""
    result = self.handler.login(username, password)
    assert result == expected_result

    if expected_result:
        self.log.info(f"✅ 登录成功：{username}")
    else:
        self.log.info(f"✅ 登录失败：{username}")
```

### 🔄 与BaseHandler兼容性

虽然我们采用传统模式，但新的BaseHandler架构完全兼容：

1. **传入实例模式**：页面对象已创建，直接使用
```python
# 传统模式（推荐）
driver = DriverFactory.get_windows_driver()
page_instance = LoginPage(driver, config_manager)
handler = LoginHandler(page_instance, config_manager)

# BaseHandler会直接使用传入的page_instance
```

2. **传入类模式**：页面对象未创建，BaseHandler自动初始化
```python
# 惰性初始化模式
handler = LoginHandler(LoginPage, config_manager)
handler._ensure_pages()  # BaseHandler自动创建实例
```

### 🚨 常见问题和解决方案

#### Q1: Handler初始化失败
**问题**: `HandlerFactory.create_handler()` 方法找不到对应的Handler
**解决方案**: 使用直接导入方式
```python
# 不推荐（会报错）
handler = HandlerFactory.create_handler('login_page', page_instance, config_manager)

# 推荐方式
from handlers.login_handler import LoginHandler
handler = LoginHandler(page_instance, config_manager)
```

#### Q2: 页面对象driver为空
**问题**: 页面对象创建失败，driver为None
**解决方案**: 确保WinAppDriver已启动
```python
# 确保在conftest.py中正确初始化driver
driver_instance = DriverFactory.get_windows_driver()
if driver_instance is None:
    raise Exception("WinAppDriver启动失败")
```

#### Q3: 配置文件加载失败
**问题**: YAML配置文件路径错误或格式错误
**解决方案**: 检查文件路径和YAML语法
```python
try:
    page_config = config_manager.load_page_config('login_page')
except Exception as e:
    self.log.error(f"配置加载失败: {e}")
    raise
```

### 📁 推荐测试文件结构

```
testCase/
├── __init__.py
├── conftest.py              # 全局配置和夹具
├── test_login_page.py       # 登录页面测试
├── test_main_page.py        # 主页面测试
├── test_user_management_page.py # 用户管理测试
└── test_user_profile_page.py  # 用户资料测试
```

### ✅ 开发检查清单

#### 代码质量检查
- [ ] 测试方法命名符合规范
- [ ] 使用了正确的断言方式
- [ ] 添加了适当的日志记录
- [ ] 异常处理完整
- [ ] 代码注释充分

#### 测试覆盖检查
- [ ] 正常场景覆盖
- [ ] 异常场景覆盖
- [ ] 边界条件测试
- [ ] 错误处理验证

#### 配置验证检查
- [ ] YAML语法正确
- [ ] 测试数据完整
- [ ] 页面元素配置准确
- [ ] 成功消息配置正确

### 🎉 最佳实践总结

1. **优先使用传统模式**：手动创建页面对象实例，确保可控性
2. **充分利用测试夹具**：使用conftest.py统一管理测试资源
3. **数据驱动测试**：通过YAML配置管理测试数据，提高维护性
4. **详细日志记录**：记录每个测试步骤和结果，便于调试
5. **异常处理完整**：确保测试失败时提供有意义的错误信息
6. **保持代码简洁**：避免重复代码，使用夹具和辅助函数
7. **向后兼容性**：新代码应该不破坏现有测试

---

**注意**: 此规范基于项目现有架构制定，确保与BaseHandler的统一解决方案完全兼容。在编写新测试用例时，请严格遵循此规范！