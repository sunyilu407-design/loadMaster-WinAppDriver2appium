# WinAppDriver 迁移指南

## 概述
本项目已将自动化测试框架从 pywinauto 迁移到 WinAppDriver，以提供更好的稳定性和兼容性。

## 环境要求

### 1. 系统要求
- Windows 10 或更高版本
- .NET Framework 4.6 或更高版本
- 管理员权限（推荐）

### 2. 安装 WinAppDriver

#### 方法一：通过 GitHub 发布页
1. 访问 [WinAppDriver 发布页](https://github.com/microsoft/WinAppDriver/releases)
2. 下载最新版本的 `Windows Application Driver.msi`
3. 运行安装程序

#### 方法二：通过 PowerShell
```powershell
# 下载 WinAppDriver
Invoke-WebRequest -Uri "https://github.com/microsoft/WinAppDriver/releases/download/v1.2.99/WindowsApplicationDriver_1.2.99_Win32.msi" -OutFile "WinAppDriver.msi"

# 安装 WinAppDriver
Start-Process msiexec.exe -ArgumentList '/i WinAppDriver.msi /quiet' -Wait
```

### 3. 配置环境变量
将 WinAppDriver 安装目录添加到系统 PATH：
- 默认安装路径：`C:\Program Files (x86)\Windows Application Driver\`

## 启动 WinAppDriver

### 方法一：使用启动脚本
运行 `start_winappdriver.bat` 脚本：
```batch
start_winappdriver.bat
```

### 方法二：手动启动
1. 以管理员身份打开命令提示符
2. 运行：
```batch
WinAppDriver.exe 127.0.0.1 4723
```

### 验证服务
打开浏览器访问：http://127.0.0.1:4723/status
如果看到 JSON 响应，说明服务正常运行。

## 配置说明

### 1. 配置文件 (config/env.ini)
```ini
[windows_app]
# Windows应用配置 - WinAppDriver
type = uia
location = C:\Program Files (x86)\微分科技有限公司\微分装车管理系统IP版\Debug\LoadMaster.exe
app_name = 欢迎使用微分科技装车管理系统
# WinAppDriver服务配置
winappdriver_host = 127.0.0.1
winappdriver_port = 4723
# 应用启动超时时间（秒）
app_startup_timeout = 30
# 元素查找超时时间（秒）
element_timeout = 10
# 页面加载等待时间（秒）
page_load_timeout = 15
```

### 2. 页面元素配置 (data/pages/login_page.yaml)
```yaml
elements:
  username_input:
    automation_id: "txtUserName"    # 首选定位方式
    name: "用户名"                   # 备选定位方式
    type: "Edit"
    xpath: "//Edit[@AutomationId='txtUserName']"  # XPath定位
```

## 使用方法

### 1. 运行测试
```batch
# 运行所有测试
run.bat

# 运行特定测试
pytest testCase/test_login.py -v

# 生成详细报告
pytest testCase/test_login.py --alluredir=./report/result
```

### 2. 调试模式
```python
# 在代码中启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 常见问题

### 1. WinAppDriver 无法启动
- **问题**：端口被占用
- **解决**：检查端口 4723 是否被占用，或修改配置文件中的端口

### 2. 元素定位失败
- **问题**：找不到元素
- **解决**：
  - 使用 Inspect.exe 工具检查元素属性
  - 确认 automation_id 是否正确
  - 尝试使用 name 或 xpath 定位

### 3. 权限问题
- **问题**：无法操作应用
- **解决**：以管理员身份运行 WinAppDriver 和测试脚本

### 4. 应用启动失败
- **问题**：应用无法启动
- **解决**：
  - 检查应用路径是否正确
  - 确认应用是否需要特殊权限
  - 检查应用是否已运行

## 调试工具

### 1. Inspect.exe
Windows SDK 提供的 UI 自动化工具，用于检查元素属性。

安装位置（根据 SDK 版本可能不同）：
- `C:\Program Files (x86)\Windows Kits\10\bin\x64\Inspect.exe`
- `C:\Program Files (x86)\Windows Kits\10\bin\x86\Inspect.exe`

### 2. UI Recorder
WinAppDriver 提供的 UI 录制工具，可以自动生成测试代码。

## 最佳实践

### 1. 元素定位策略
1. **优先使用 automation_id**：最稳定可靠的定位方式
2. **次选 name 属性**：用户界面的显示文本
3. **最后使用 xpath**：灵活性高但性能较低

### 2. 等待策略
```python
# 显式等待
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "用户名"))
)

# 隐式等待
driver.implicitly_wait(10)
```

### 3. 错误处理
```python
try:
    element = driver.find_element_by_automation_id("txtUserName")
    element.send_keys("admin")
except NoSuchElementException:
    logging.error("用户名输入框未找到")
    take_screenshot("login_error")
    raise
```

### 4. 性能优化
- 合理设置超时时间
- 使用适当的等待策略
- 避免频繁的元素查找
- 重用已定位的元素

## 迁移注意事项

### 从 pywinauto 迁移的主要变化

1. **元素定位方式**:
   - pywinauto: `app.window(title="窗口标题").child_window(auto_id="元素ID")`
   - WinAppDriver: `driver.find_element_by_automation_id("元素ID")`

2. **元素交互**:
   - pywinauto: `element.click_input()`
   - WinAppDriver: `element.click()`

3. **等待机制**:
   - pywinauto: `element.wait('exists', timeout=10)`
   - WinAppDriver: `WebDriverWait(driver, 10).until(EC.presence_of_element_located(...))`

4. **窗口管理**:
   - pywinauto: `app.window(title="窗口标题")`
   - WinAppDriver: `driver.switch_to.window(window_handle)`

## 支持

如遇到问题，请检查：
1. WinAppDriver 是否正确安装和运行
2. 配置文件是否正确
3. 应用路径和元素定位器是否准确
4. 查看日志文件获取详细错误信息

## 更新日志

### v1.0.0 (2024-01-XX)
- 完成从 pywinauto 到 WinAppDriver 的迁移
- 更新所有核心组件
- 添加完整的配置支持
- 优化错误处理和日志记录