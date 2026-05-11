[根目录](../../CLAUDE.md) > **utils**

## Utils 模块文档

### 模块职责

Utils模块是项目的基础设施层，提供各种通用工具类和辅助功能。它负责驱动管理、配置管理、数据库操作、日志记录、环境配置等核心基础设施服务，为整个测试框架提供稳定可靠的技术支撑。

### 入口与启动

#### 核心工具类
- **DriverFactory**: WinAppDriver驱动工厂，管理驱动生命周期
- **ConfigManager**: 配置管理器，统一加载和管理配置文件
- **DatabaseHelper**: 数据库助手，封装数据库操作
- **Logger**: 日志管理器，提供统一的日志记录服务
- **Environment**: 环境配置类，读取环境变量和配置
- **WinFormComboBoxHandler**: WinForm下拉框处理器，专门处理Windows控件

#### 初始化流程
```python
# 1. 环境配置初始化
env = Environment()
app_path = env.get_app_path()
timeout = env.get_element_timeout()

# 2. 配置管理器初始化
config_manager = ConfigManager()
page_config = config_manager.load_page_config('login_page')

# 3. 驱动初始化
driver = DriverFactory.get_windows_driver()

# 4. 数据库连接
db_helper = DatabaseHelper()
db_helper.connect()

# 5. 日志配置
logger = Logger().logger
logger.info("系统初始化完成")
```

### 对外接口

#### DriverFactory 接口
```python
class DriverFactory:
    @staticmethod
    def get_windows_driver() -> RemoteWebDriver
    @staticmethod
    def get_appium_driver() -> RemoteWebDriver
    @staticmethod
    def create_driver_capabilities() -> dict
    @staticmethod
    def quit_driver(driver) -> None
```

#### ConfigManager 接口
```python
class ConfigManager:
    def load_page_config(page_name: str) -> dict
    def get_test_data(page_name: str, data_key: str) -> dict
    def get_common_dialog_config(dialog_name: str) -> dict
    def reload_config() -> None
```

#### DatabaseHelper 接口
```python
class DatabaseHelper:
    def connect() -> bool
    def disconnect() -> None
    def execute_query(sql: str, params=None) -> List[tuple]
    def execute_update(sql: str, params=None) -> int
    def get_table_data(table_name: str, condition=None) -> List[tuple]
```

#### Logger 接口
```python
class Logger:
    def __init__(self, name: str = None, level: str = None)
    def get_logger(self) -> logging.Logger
    def setup_file_handler(self, file_path: str) -> None
    def setup_console_handler(self) -> None
```

#### Environment 接口
```python
class Environment:
    # Windows应用配置
    def get_app_path() -> str
    def get_app_top_level_window() -> str
    def get_winappdriver_host() -> str
    def get_winappdriver_port() -> int
    def get_element_timeout() -> int

    # 数据库配置
    def get_db_type() -> str
    def get_db_host() -> str
    def get_db_port() -> int
    def get_db_username() -> str
    def get_db_password() -> str
    def get_db_name() -> str
```

### 关键依赖与配置

#### 外部依赖
```python
# requirements.txt (建议创建)
selenium>=4.0.0
pytest>=7.0.0
allure-pytest>=2.12.0
PyMySQL>=1.0.2
SQLAlchemy>=1.4.0
pyyaml>=6.0
python-dotenv>=0.19.0
```

#### 配置文件结构
```
config/
└── env.ini              # 主配置文件

data/
├── pages/               # 页面配置目录
│   ├── login_page.yaml   # 登录页面配置
│   ├── main_page.yaml    # 主页面配置
│   └── common_dialogs.yaml  # 通用弹窗配置
└── test_data/           # 测试数据目录
```

#### 环境配置示例
```ini
# env.ini
[windows_app]
type = uia
location = D:\\Program Files (x86)\\微分科技\\Load Studio\\发油系统\\LoadMaster.exe
app_name = 欢迎使用微分科技装车管理系统
winappdriver_host = 127.0.0.1
winappdriver_port = 4723
element_timeout = 10

[database]
db_type = mysql
host = localhost
port = 3306
username = root
password =
database = test
```

### 数据模型

#### 页面配置模型
```python
page_config = {
    "elements": {
        "username_input": {
            "automation_id": "txtUserName",
            "name": "用户名输入框",
            "type": "Edit"
        },
        "login_button": {
            "automation_id": "btnLogin",
            "name": "登录按钮",
            "type": "Button"
        }
    },
    "test_data": {
        "valid_login": {
            "username": "admin",
            "password": "admin123"
        }
    },
    "head_keys": ["用户姓名", "用户类型", "注册时间", "备注"]
}
```

#### 驱动配置模型
```python
driver_capabilities = {
    "app": "D:\\Program Files (x86)\\微分科技\\Load Studio\\发油系统\\LoadMaster.exe",
    "platformName": "Windows",
    "deviceName": "WindowsPC",
    "ms:experimental-webdriver": "true",
    "ms:waitForAppLaunch": "30"
}
```

#### 数据库连接模型
```python
db_config = {
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "test",
        "charset": "utf8mb4"
    }
}
```

### 测试与质量

#### 工具类测试覆盖
- ✅ ConfigManager配置加载测试
- ✅ DatabaseHelper数据库连接测试
- ✅ Environment环境变量读取测试
- 🔄 DriverFactory驱动初始化测试
- 🔄 Logger日志输出测试

#### 错误处理机制
```python
# 统一错误处理模式
try:
    result = self._execute_operation()
    return result
except ConnectionError as e:
    logger.error(f"连接错误: {e}")
    return None
except TimeoutError as e:
    logger.error(f"超时错误: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    logger.exception(e)
    raise
```

#### 性能优化
- **连接池**: 数据库连接复用
- **配置缓存**: 配置文件缓存机制
- **资源管理**: 自动资源清理和释放
- **异步操作**: 支持异步数据库操作

### 常见问题 (FAQ)

#### Q1: 如何初始化WinAppDriver？
**A**:
```python
# 使用DriverFactory
from utils.driver_factory import DriverFactory

driver = DriverFactory.get_windows_driver()
if driver:
    print("WinAppDriver初始化成功")
else:
    print("WinAppDriver初始化失败")
```

#### Q2: 如何加载页面配置？
**A**:
```python
# 使用ConfigManager
from utils.config_manager import ConfigManager

config_manager = ConfigManager()
page_config = config_manager.load_page_config('login_page')

# 获取元素定位信息
username_locator = page_config['elements']['username_input']
print(f"用户名输入框定位: {username_locator}")
```

#### Q3: 如何执行数据库操作？
**A**:
```python
# 使用DatabaseHelper
from utils.db_helper import DatabaseHelper

db_helper = DatabaseHelper()
if db_helper.connect():
    # 查询数据
    result = db_helper.execute_query("SELECT * FROM users WHERE name = %s", ("admin",))

    # 执行更新
    affected_rows = db_helper.execute_update("UPDATE users SET status = %s WHERE id = %s", ("active", 1))

    db_helper.disconnect()
```

#### Q4: 如何配置日志？
**A**:
```python
# 使用Logger
from utils.logger import Logger

logger = Logger("test_module").logger
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

### 相关文件清单

#### 核心工具文件
- `driver_factory.py` - WinAppDriver驱动工厂类
- `config_manager.py` - 配置管理器，统一配置加载
- `db_helper.py` - 数据库操作助手类
- `logger.py` - 日志管理器
- `env.py` - 环境配置类，读取env.ini

#### 特殊处理器
- `winform_combobox_handler.py` - WinForm下拉框专用处理器
- `generate_test_data_template.py` - 测试数据模板生成器

#### 配置文件
- `../config/env.ini` - 主配置文件
- `../data/pages/**/*.yaml` - 页面配置文件

#### 依赖管理
- `../requirements.txt` - Python依赖包（需要创建）

### 变更记录 (Changelog)

#### 2025-12-29 11:39:10
- ✅ 创建utils模块文档
- ✅ 添加导航面包屑链接
- ✅ 完善工具类接口文档
- ✅ 更新依赖关系说明

#### 2024-XX-XX
- 完成DriverFactory WinAppDriver集成
- 优化ConfigManager配置加载机制
- 增加DatabaseHelper数据库连接池
- 完善Logger日志分级输出
- 添加WinForm特殊控件处理

---

**提示**: 在开发新的工具类时，请遵循现有的设计模式和错误处理机制，确保代码的健壮性和可维护性。记得更新requirements.txt文件，声明新增的外部依赖。