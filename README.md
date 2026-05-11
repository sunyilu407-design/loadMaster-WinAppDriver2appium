# 通用自动化测试框架

## 项目简介

这是一个通用的自动化测试框架，支持Windows桌面应用和Web应用的自动化测试，并集成了数据库交互功能。该框架基于Page Object设计模式，采用模块化结构，易于扩展和维护。

## 核心特性

- **多平台支持**：同时支持Windows桌面应用和Web应用自动化测试
- **数据库集成**：内置数据库操作功能，支持数据断言
- **配置灵活**：统一的环境配置管理
- **报告生成**：集成Allure测试报告
- **易于扩展**：模块化设计，便于添加新功能

## 技术栈

- **UI自动化**：WinAppDriver (Windows), Selenium (Web)
- **测试框架**：pytest
- **报告工具**：Allure
- **数据库**：SQLAlchemy, PyMySQL, psycopg2
- **配置管理**：configparser, PyYAML
- **移动测试**：Appium-Python-Client

## 目录结构

```
├── config/              # 配置文件目录
├── data/                # 测试数据文件目录
├── handlers/            # 业务处理逻辑目录
├── pageObject/          # 页面对象目录
├── testCase/            # 测试用例目录
├── utils/               # 工具类目录
├── report/              # 测试报告目录
├── requirements.txt     # 项目依赖文件
├── run.bat              # Windows运行脚本
├── clean_cache.bat      # 清理缓存文件脚本
└── README.md            # 项目说明文件
```

## 快速开始

### 1. 环境准备

#### 安装 WinAppDriver (Windows自动化必需)
1. 下载 [WinAppDriver](https://github.com/microsoft/WinAppDriver/releases)
2. 运行安装程序
3. 启动 WinAppDriver 服务：
   ```batch
   # 使用启动脚本
   start_winappdriver.bat
   
   # 或手动启动
   WinAppDriver.exe 127.0.0.1 4723
   ```

#### 安装 Python 依赖
确保已安装Python 3.0+，然后安装依赖包：

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/env.ini` 文件，配置应用路径、数据库连接等信息。

详细配置说明请参考 [WINAPPDRIVER_MIGRATION_GUIDE.md](WINAPPDRIVER_MIGRATION_GUIDE.md)

### 3. 运行测试

#### Windows系统：
双击运行 `run.bat` 脚本

#### 命令行运行：
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest testCase/test_loadmaster.py

# 运行特定测试类或方法
python -m pytest testCase/test_loadmaster.py::TestLoadMaster::test_login_success
```

## 使用文档

详细使用说明请查看 [USAGE.md](USAGE.md) 文件。

### 新增功能

#### 窗口定位功能

框架新增了`locate_window`方法，用于定位新弹出的窗口。该方法支持通过窗口标题或标题正则表达式来定位窗口。

使用示例：
```python
# 通过窗口标题定位
window = base_page.locate_window(title="记事本")

# 通过标题正则表达式定位
window = base_page.locate_window(title_re=".*记事本.*")

# 设置自定义超时时间
window = base_page.locate_window(timeout=5, title="计算器")
```

更多使用示例请查看 [examples/window_locator_example.py](examples/window_locator_example.py) 文件。

## 项目总结

详细项目总结请查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 文件。

## 许可证

本项目采用MIT许可证，详情请查看 [LICENSE](LICENSE) 文件。

### 🚀 超级Handler工厂 - 终极简化（强烈推荐）

```python
# 传统方式（已淘汰 - 繁琐且易错）
driver = DriverFactory.get_windows_driver()
page = CustomerManagementPage(driver, config_manager)
handler = CustomerManagementHandler(page, config_manager)

# 新方式（1行代码搞定所有！）
from handlers.super_handler_factory import create_handler

# 创建任意Handler
login_handler = create_handler('login_page')
main_handler = create_handler('main_page')
user_handler = create_handler('user_profile_page')

# 直接使用业务方法
result = user_handler.change_username_and_verify(
    old_password="123456",
    new_username="new_admin",
    confirm_username="new_admin"
)
```

### 用户操作步骤

#### 方案A：使用超级Handler工厂（推荐）
```bash
# 步骤1: 创建YAML配置文件
vim data/pages/customer_management_page.yaml

# 步骤2: 1行代码创建Handler并使用
python -c "
from handlers.super_handler_factory import create_handler
handler = create_handler('customer_management_page')
result = handler.add_customer_and_verify({
    'name': '测试客户',
    'phone': '13800138000',
    'address': '测试地址'
})
print('操作结果:', result)
"
```

#### 方案B：传统开发流程
```bash
# 步骤1: 创建YAML配置文件
vim data/pages/customer_management_page.yaml

# 步骤2: 告知AI需求
# "我写好了customer_management_page的YAML，需要实现添加、修改、删除客户功能，@PAGE_DEVELOPMENT_GUIDE.md"

# 步骤3: AI自动生成代码
# - pageObject/customer_management_page.py
# - handlers/customer_management_handler.py
# - test_data模板（追加到YAML）

# 步骤4: 填写test_data
vim data/pages/customer_management_page.yaml

# 步骤5: 运行测试
pytest testCase/test_customer_management_page.py -v
```

### 📖 Handler简化指南

查看 **[handlers/HANDLER_SIMPLIFICATION_GUIDE.md](handlers/HANDLER_SIMPLIFICATION_GUIDE.md)** 了解完整的使用简化方案。

运行示例：`python handlers/handler_usage_examples.py`# loadMaster-WinAppDriver2appium
