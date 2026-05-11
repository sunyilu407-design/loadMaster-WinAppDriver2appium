# WinAppDriver环境配置指南

## 问题排查

如果测试运行时出现以下错误：
```
ERROR:utils.driver_factory:WinAppDriver驱动初始化失败: Message: 未能找到任何可识别的数字。
```

这通常是由于以下原因之一导致的：

## 解决方案

### 1. 检查WinAppDriver服务

首先确保WinAppDriver服务正在运行：

```bash
# 检查端口4723是否被占用
netstat -ano | findstr 4723

# 如果没有，启动WinAppDriver服务
start_winappdriver.bat
```

### 2. 检查应用配置

更新 `config/env.ini` 文件中的应用配置：

```ini
[windows_app]
# 应用可执行文件路径 (如果不需要自动启动，可以留空)
location = C:\Path\To\Your\Application.exe

# 应用主窗口标题 (用于WinAppDriver连接已运行的应用)
app_name = 你的应用窗口标题
```

### 3. 手动启动应用

如果应用路径配置不正确，请手动启动应用，然后运行测试。

### 4. 使用环境检查工具

运行环境检查脚本：

```bash
python check_environment.py
```

此脚本会检查：
- WinAppDriver服务状态
- 应用运行状态
- 配置文件正确性

### 5. 一键启动环境

使用一键启动脚本：

```bash
start_test_environment.bat
```

此脚本会：
1. 检查并启动WinAppDriver服务
2. 运行环境检查
3. 提供详细的状态报告

## 配置示例

### 场景1: 连接已运行的应用

```ini
[windows_app]
location =
app_name = 欢迎使用微分科技装车管理系统
```

### 场景2: 自动启动应用

```ini
[windows_app]
location = C:\Program Files\YourApp\YourApp.exe
app_name = Your Application Title
```

## 故障排除

### 问题: 应用路径不存在
**解决方案**: 更新 `config/env.ini` 中的 `location` 配置，或留空使用手动启动模式

### 问题: 窗口标题不匹配
**解决方案**:
1. 使用任务管理器查看应用窗口标题
2. 更新 `config/env.ini` 中的 `app_name` 配置
3. 确保标题完全匹配（包括特殊字符）

### 问题: 端口被占用
**解决方案**:
1. 检查是否有其他WinAppDriver实例在运行
2. 修改端口配置：`winappdriver_port = 4724`
3. 重启WinAppDriver服务

### 问题: 权限不足
**解决方案**: 以管理员身份运行命令提示符和测试

## 验证配置

运行以下命令验证配置是否正确：

```bash
# 1. 检查WinAppDriver
python -c "from utils.driver_factory import DriverFactory; print('WinAppDriver:', DriverFactory._check_winappdriver_service())"

# 2. 检查应用路径
python check_environment.py

# 3. 运行单个测试
pytest testCase/test_login_page.py::TestLoginPage::test_valid_login -v -s
```
