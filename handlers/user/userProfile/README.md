# 用户个人中心Handler开发文档

## 🆕 重大更新：Handler简化方案

### 🚀 新一代Handler使用方式（推荐）

现在支持**1行代码**创建完整Handler实例：

```python
# 传统方式（需要手动创建页面对象）
driver = DriverFactory.get_windows_driver()
page = UserProfilePage(driver, config_manager)
handler = UserProfileHandler(page, config_manager)

# 新方式（超级简化）
from handlers.super_handler_factory import create_handler

# 全局化Handler（推荐）
handler = create_handler('user_profile_page')  # 1行代码搞定！

# 修改用户名
result = handler.change_username_and_verify(
    'old_password', 'new_username', 'confirm_username'
)
```

### 🎯 使用方式

```python
from utils.super_handler_factory import create_handler

# 创建Handler（最简单的方式）
handler = create_handler('user_profile_page')
```

## 模块概述

用户个人中心Handler (`user_profile_handler.py`) 是业务逻辑处理层，专门负责用户个人信息修改相关的业务流程封装。它采用Handler设计模式，将复杂的页面操作组合成完整的业务流程，为测试用例提供简洁的调用接口。

## 核心功能

### 1. 修改用户名 (`change_username_and_verify`)

完整的用户名修改流程，包含：
- 导航到修改用户名页面
- 输入旧密码验证身份
- 输入新用户名
- 输入确认新用户名
- 点击保存按钮
- 处理操作结果弹窗
- 验证成功消息

**调用方式**:
```python
result = user_profile_handler.change_username_and_verify(
    old_password="123456",
    new_username="new_admin",
    confirm_username="new_admin",
    confirm=True  # True=确认, False=取消
)
```

### 2. 修改密码 (`change_password_and_verify`)

完整的密码修改流程，包含：
- 导航到修改密码页面
- 输入旧密码验证身份
- 输入新密码
- 输入确认新密码
- 点击保存按钮
- 处理操作结果弹窗
- 验证成功消息

**调用方式**:
```python
result = user_profile_handler.change_password_and_verify(
    old_password="123456",
    new_password="newpassword123",
    confirm_password="newpassword123",
    confirm=True  # True=确认, False=取消
)
```

### 3. 用户管理功能

#### `handle_logout_prompt`
处理退出登录操作，包含：
- 导航到退出登录页面
- 处理退出确认弹窗
- 根据用户选择确认或取消退出

**调用方式**:
```python
result = user_profile_handler.handle_logout_prompt(
    confirm_logout=True  # True=确认退出, False=取消退出
)
```

#### `handle_switch_user_prompt`
处理切换用户操作，包含完整的切换流程：
- 导航到退出登录页面
- 确认退出当前用户
- 导航到用户登录页面
- 为登录新用户做准备（登录步骤由调用方处理）

**调用方式**:
```python
result = user_profile_handler.handle_switch_user_prompt(
    confirm_switch=True  # True=确认切换, False=取消切换
)
```

#### `navigate_to_user_login_page`
导航到用户登录页面并执行登录（在退出登录后使用），包含：
- 通过主页面菜单导航到用户登录子菜单
- 可选执行登录操作（如果提供了用户名和密码）
- 复用login_handler中的登录逻辑

**调用方式**:
```python
# 只导航不登录
result = user_profile_handler.navigate_to_user_login_page()

# 导航并登录
result = user_profile_handler.navigate_to_user_login_page(
    username="test_user",
    password="123456"
)
```

## 开发规范

### 📋 标准开发流程

#### 1. 导航先行原则
**任何修改操作之前必须先导航到对应页面**：
```python
# 标准流程模板
def any_modify_operation():
    # 步骤0: 导航到目标页面
    if not handler.navigate_to_target_page():
        return {'success': False, 'error': '导航失败'}

    # 步骤1: 初始化页面对象
    handler._ensure_pages()

    # 步骤2-N: 执行具体页面操作
    # ... 页面操作代码 ...

    # 步骤N+1: 处理操作结果
    # ... 结果处理代码 ...
```

#### 2. 页面操作标准
**所有页面操作必须包含错误处理**：
```python
def safe_page_operation():
    try:
        result = self.user_profile_page.some_operation()
        if result:
            steps_completed.append("✓ 操作成功")
        else:
            return {'success': False, 'error': '页面操作失败'}
    except Exception as e:
        return {'success': False, 'error': f'页面操作异常: {str(e)}'}
```

#### 3. 验证机制标准
**基于配置文件的成功消息验证**：
```python
def verify_operation_result():
    expected_message = self.success_messages.get('operation_key', '')
    actual_message = get_prompt_message()

    if expected_message in actual_message:
        return {'success': True, 'message': actual_message}
    else:
        return {'success': False, 'error': f'验证失败: 期望{expected_message}'}
```

#### 4. 返回值标准
**统一的返回格式**：
```python
return {
    'success': bool,              # 操作是否成功
    'message': str,               # 操作结果消息或提示
    'error': str,                 # 错误信息（失败时）
    'steps_completed': list        # 完成的操作步骤列表
}
```

### 🔍 配置文件依赖

#### 页面配置
- **主配置文件**: `data/pages/main_page.yaml`
- **用户配置文件**: `data/pages/user/user_profile_page.yaml`
- **公共弹窗**: `data/pages/common_dialogs.yaml`

#### 成功消息配置
```yaml
app_config:
  success_messages:
    change_username: "用户名修改成功！"
    change_password: "密码修改成功！"
```

### 📝 测试用例开发

#### 标准测试用例模板
```python
def test_change_username_success():
    """测试修改用户名成功场景"""
    # 1. 初始化Handler
    user_profile_handler = UserProfileHandler(config_manager=config_manager)

    # 2. 导航到修改用户名页面
    assert user_profile_handler.navigate_to_alter_username_page(), "导航失败"

    # 3. 执行修改操作
    result = user_profile_handler.change_username_and_verify(
        old_password="123456",
        new_username="test_user_001",
        confirm_username="test_user_001",
        confirm=True
    )

    # 4. 验证结果
    assert result['success'], f"修改失败: {result['error']}"
    assert "用户名修改成功！" in result['message'], "成功消息不匹配"

def test_change_password_cancel():
    """测试修改密码取消场景"""
    user_profile_handler = UserProfileHandler(config_manager=config_manager, main_handler=main_handler)

    # 导航到修改密码页面
    assert user_profile_handler.main_handler.navigate_to_password_change(), "导航失败"

    # 执行修改操作（取消）
    result = user_profile_handler.change_password_and_verify(
        old_password="123456",
        new_password="newpassword123",
        confirm_password="newpassword123",
        confirm=False  # 取消操作
    )

    # 验证取消结果
    assert result['success'], "取消操作应该成功"
    assert "修改密码操作已取消" in result['message']
```

### 🚨 错误处理规范

#### 分层错误处理
```python
# 1. 页面级错误（页面元素找不到、操作失败）
try:
    element_result = page.click_element()
except ElementNotFoundError as e:
    return {'success': False, 'error': f'页面元素错误: {e}'}

# 2. 业务级错误（流程失败、验证失败）
try:
    business_result = handler.change_username_and_verify()
except BusinessLogicError as e:
    return {'success': False, 'error': f'业务逻辑错误: {e}'}

# 3. 系统级错误（导航失败、系统异常）
try:
    system_result = handler.navigate_to_page()
except SystemError as e:
    return {'success': False, 'error': f'系统错误: {e}'}
```

### 📊 日志记录规范

#### 分级日志记录
```python
# 信息级别 - 正常流程信息
self.log.info("开始修改用户名操作")
self.log.info(f"参数: 新用户名={new_username}")

# 警告级别 - 非致命错误
self.log.warning("页面元素加载较慢，操作可能超时")
self.log.warning(f"未预期的提示消息: {message}")

# 错误级别 - 操作失败
self.log.error(f"修改用户名失败: {error_msg}")
self.log.error(f"页面切换失败: {str(e)}")

# 调试级别 - 详细调试信息
self.log.debug(f"元素定位信息: {element_config}")
self.log.debug(f"窗口句柄: {window_handle}")
```

### 🔄 扩展开发指南

#### 添加新功能的标准流程
1. **页面配置更新** - 在YAML中添加新的元素配置
2. **页面对象扩展** - 在UserProfilePage中添加新的操作方法
3. **Handler业务逻辑** - 在UserProfileHandler中添加新的业务方法
4. **导航方法扩展** - 在MainPage中添加新的导航方法（如需要）
5. **测试用例补充** - 在testCase中添加对应的测试用例

#### 🔧 MainHandler导航方法说明
根据分析，main_handler.py提供了完整的导航方法：
- **`navigate_to_username_change()`** - 导航到修改用户名页面
- **`navigate_to_password_change()`** - 导航到修改密码页面
- **`navigate_to_user_logout()`** - 导航到退出登录子菜单
- **`logout_and_login()`** - 退出当前用户并使用新用户重新登录
- **其他系统导航方法** - 桹据系统菜单结构实现

#### 正确的调用方式
```python
# 在UserProfileHandler中使用main_handler的导航方法
def change_username_and_verify(self, ...):
    # 先导航到修改用户名页面
    if self.main_handler.navigate_to_username_change():
        steps_completed.append("✓ 成功导航到修改用户名页面")
        # 继续执行页面操作...
    else:
        return {'success': False, 'error': '导航失败'}

# 退出用户的简化逻辑
def test_logout_success():
    user_profile_handler = UserProfileHandler(config_manager=config_manager, main_handler=main_handler)
    result = user_profile_handler.handle_logout_prompt(confirm_logout=True)

    # 验证结果
    assert result['success'] and result['logged_out']
    print("✅ 用户退出登录成功")
```

#### 🔍 切换用户优化实现
基于您的需求调整，切换用户的逻辑更加清晰：
- **完整流程**: 先导航到退出登录页面进行退出，然后导航到用户登录页面准备新用户登录
- **复用现有逻辑**: 充分利用main_handler中的导航方法和login_handler中的登录功能
- **统一处理**: 所有结果都通过统一的方法处理

#### 📝 业务流程完善
现在切换用户的完整操作流程：
1. `导航到退出登录页面` → main_handler.navigate_to_user_logout()
2. `处理退出确认弹窗` → user_profile_page.switch_to_prompt_window() → 点击确认按钮
3. `导航到用户登录页面` → main_handler.navigate_to_user_login()
4. `执行新用户登录` → 复用login_handler中的登录逻辑（由调用方处理）
5. **返回结果** → 包含switched字段标识切换状态，便于后续判断

### 🚀 重要改进点
- **简化切换流程**: 去除了繁琐的页面导航，直接调用核心功能
- **提升用户体验**: 减少不必要的操作步骤，提高效率
- **保持一致性**: 所有用户相关操作都使用相同的业务模式
1. **页面配置更新** - 在YAML中添加新的元素配置
2. **页面对象扩展** - 在UserProfilePage中添加新的操作方法
3. **Handler业务逻辑** - 在UserProfileHandler中添加新的业务方法
4. **使用MainHandler导航方法** - 充分利用main_handler中已有的导航方法

#### MainHandler导航方法说明
- **`navigate_to_username_change()`** - 导航到修改用户名页面
- **`navigate_to_password_change()`** - 导航到修改密码页面
- **`navigate_to_user_info_management()`** - 导航到用户信息管理
- **其他系统导航方法** - 根据main_handler中的实现调用对应的菜单导航

#### 正确的调用方式
```python
# 在UserProfileHandler中使用main_handler的导航方法
def change_username_and_verify(self, ...):
    # 先导航到修改用户名页面
    if self.main_handler.navigate_to_username_change():
        steps_completed.append("✓ 成功导航到修改用户名页面")
        # 继续执行页面操作...
    else:
        return {'success': False, 'error': '导航失败'}

def change_password_and_verify(self, ...):
    # 先导航到修改密码页面
    if self.main_handler.navigate_to_password_change():
        steps_completed.append("✓ 成功导航到修改密码页面")
        # 继续执行页面操作...
    else:
        return {'success': False, 'error': '导航失败'}
```

#### 代码复用原则
- **公共逻辑抽取** - 将重复的导航、验证逻辑抽取为公共方法
- **配置驱动** - 所有可变参数通过配置文件管理
- **接口统一** - 相同类型的方法保持一致的接口设计
5. **测试用例补充** - 在testCase中添加对应的测试用例

#### 代码复用原则
- **公共逻辑抽取** - 将重复的导航、验证逻辑抽取为公共方法
- **配置驱动** - 所有可变参数通过配置文件管理
- **接口统一** - 相同类型的方法保持一致的接口设计

---

## 📋 文件说明

- **Handler**: `user_profile_handler.py` - 业务逻辑处理（当前文件）
- **Page Object**: `../pageObject/user/userProfile/user_profile_page.py` - 页面元素操作
- **Configuration**: `../../data/pages/user/user_profile_page.yaml` - 页面配置文件
- **Main Page**: `../../pageObject/main_page.py` - 主页面导航（新增导航方法）

## 🎯 开发最佳实践

1. **导航优先**: 任何页面操作前先导航到目标页面
2. **配置驱动**: 页面元素和成功消息从配置文件读取
3. **错误完整**: 每个步骤都有独立的成功/失败判断
4. **日志详细**: 记录每个关键步骤和错误信息
5. **返回统一**: 使用统一的返回格式便于测试验证
6. **步骤跟踪**: 记录所有完成步骤便于问题排查

---

**重要提醒**: 后续开发其他功能模块时，请严格按照此文档的规范执行，确保代码质量和可维护性！