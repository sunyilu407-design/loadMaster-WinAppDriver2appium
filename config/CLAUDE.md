[根目录](../../CLAUDE.md) > **config**

## Config 模块文档

### 模块职责

Config模块是项目的配置管理中心，负责统一管理所有环境配置、应用参数、数据库连接信息、测试参数等。通过结构化的配置文件，实现不同环境的快速切换和参数的集中管理，为整个测试框架提供灵活的配置支持。

### 入口与启动

#### 核心配置文件
- **env.ini**: 主配置文件，包含所有环境参数
- **pytest.ini**: pytest框架配置文件
- **requirements.txt**: Python依赖包声明（需要创建）

#### 配置加载流程
```python
# 1. 环境配置读取
from utils.env import Environment

env = Environment()
app_path = env.get_app_path()
db_config = {
    'host': env.get_db_host(),
    'port': env.get_db_port(),
    'username': env.get_db_username(),
    'password': env.get_db_password(),
    'database': env.get_db_name()
}
```

### 配置结构详解

#### env.ini 主配置文件
```ini
# ==================================
# 通用自动化测试环境配置
# ==================================

[windows_app]
# Windows应用配置 - WinAppDriver
type = uia
location = D:\\Program Files (x86)\\微分科技\\Load Studio\\发油系统\\LoadMaster.exe
app_name = 欢迎使用微分科技装车管理系统
# WinAppDriver服务配置
winappdriver_host = 127.0.0.1
winappdriver_port = 4723
# 超时配置
app_startup_timeout = 30
element_timeout = 10
page_load_timeout = 15

[web]
# Web测试配置（预留）
browser = chrome
headless = False
base_url =
webdriver_timeout = 10
webdriver_implicit_wait = 5

[database]
# 数据库配置
db_type = mysql
host = localhost
port = 3306
username = root
password =
database = test
db_timeout = 30

[allure]
# Allure报告配置
report_url =
info_url =
report_dir = ./reports
screenshot_dir = ./screenshots

[logging]
# 日志配置
log_level = INFO
log_file = ./logs/automation.log
log_format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
max_log_size = 10
backup_count = 5

[retry]
# 重试配置
max_retries = 0
retry_delay = 0

[performance]
# 性能测试配置
response_time_threshold = 30
memory_threshold = 80
cpu_threshold = 90
```

#### pytest.ini 测试框架配置
```ini
[pytest]
norecursedirs = testCase/python-client test_app.txt
python_files = test_*.py *_test.py
```

#### requirements.txt 依赖管理
```txt
# 核心依赖
selenium>=4.0.0
pytest>=7.0.0
allure-pytest>=2.12.0
PyMySQL>=1.0.2
SQLAlchemy>=1.4.0
pyyaml>=6.0
python-dotenv>=0.19.0

# 工具依赖
requests>=2.28.0
colorlog>=6.7.0
```

### 配置使用指南

#### 环境变量获取
```python
from utils.env import Environment

class ConfigUsage:
    def __init__(self):
        self.env = Environment()

    def get_app_config(self):
        return {
            'app_path': self.env.get_app_path(),
            'app_name': self.env.get_app_top_level_window(),
            'host': self.env.get_winappdriver_host(),
            'port': self.env.get_winappdriver_port(),
            'timeout': self.env.get_element_timeout()
        }

    def get_db_config(self):
        return {
            'type': self.env.get_db_type(),
            'host': self.env.get_db_host(),
            'port': self.env.get_db_port(),
            'user': self.env.get_db_username(),
            'password': self.env.get_db_password(),
            'database': self.env.get_db_name()
        }
```

#### 配置验证机制
```python
def validate_config():
    """配置有效性验证"""
    env = Environment()

    # 检查应用路径
    app_path = env.get_app_path()
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"应用路径不存在: {app_path}")

    # 检查WinAppDriver端口
    port = env.get_winappdriver_port()
    if not is_port_available(port):
        raise ConnectionError(f"端口被占用或不可用: {port}")

    # 检查数据库连接
    db_helper = DatabaseHelper()
    if not db_helper.connect():
        raise ConnectionError("数据库连接失败")

    return True
```

### 环境管理

#### 多环境配置策略
```
config/
├── env.ini                 # 默认配置
├── env.dev.ini            # 开发环境配置
├── env.test.ini           # 测试环境配置
└── env.prod.ini           # 生产环境配置
```

#### 环境切换方法
```python
import os
from utils.env import Environment

def load_environment_config(env_name='default'):
    """加载指定环境配置"""
    config_file = f'env.{env_name}.ini' if env_name != 'default' else 'env.ini'
    config_path = os.path.join('config', config_file)

    if os.path.exists(config_path):
        # 重新加载配置
        cf = configparser.ConfigParser()
        cf.read(config_path, encoding='UTF-8')
        return Environment(cf)
    else:
        # 使用默认配置
        return Environment()
```

### 安全考虑

#### 敏感信息管理
```ini
# 数据库密码使用环境变量
[database]
host = localhost
port = 3306
username = root
password = ${DB_PASSWORD}  # 从环境变量读取
database = test
```

#### 配置文件权限
```bash
# 限制配置文件访问权限
chmod 600 config/env.ini
chmod 600 config/credentials.ini
```

### 最佳实践

#### 配置组织原则
1. **分类清晰**: 按功能模块分组配置项
2. **命名规范**: 使用有意义的配置项名称
3. **注释完整**: 每个配置项都有详细说明
4. **版本控制**: 敏感信息不入版本库

#### 配置更新策略
```python
class ConfigUpdater:
    def __init__(self):
        self.config_path = 'config/env.ini'
        self.cf = configparser.ConfigParser()
        self.cf.read(self.config_path, encoding='UTF-8')

    def update_timeout(self, new_timeout):
        """更新超时配置"""
        self.cf.set('windows_app', 'element_timeout', str(new_timeout))
        with open(self.config_path, 'w', encoding='UTF-8') as f:
            self.cf.write(f)

    def backup_config(self):
        """备份当前配置"""
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'config/env_{timestamp}.ini.bak'
        shutil.copy2(self.config_path, backup_path)
        return backup_path
```

### 常见问题 (FAQ)

#### Q1: 如何修改应用路径？
**A**:
1. 编辑 `config/env.ini` 文件
2. 找到 `[windows_app]` 部分
3. 修改 `location` 配置项为新的应用路径
4. 重启测试框架

#### Q2: 如何配置不同的数据库？
**A**:
```ini
[database]
# MySQL配置
db_type = mysql
host = localhost
port = 3306
username = root
password = your_password
database = test_db

# 或 PostgreSQL配置
db_type = postgresql
host = localhost
port = 5432
username = postgres
password = your_password
database = test_db
```

#### Q3: 如何调整日志级别？
**A**:
```ini
[logging]
log_level = DEBUG    # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
log_file = ./logs/automation.log
max_log_size = 10    # MB
backup_count = 5
```

#### Q4: 如何设置WinAppDriver服务地址？
**A**:
```ini
[windows_app]
winappdriver_host = 127.0.0.1
winappdriver_port = 4723
# 确保WinAppDriver服务在此地址运行
```

### 相关文件清单

#### 核心配置文件
- `env.ini` - 主配置文件，包含所有系统参数
- `pytest.ini` - pytest测试框架配置
- `requirements.txt` - Python依赖包声明（需要创建）

#### 环境配置（可选）
- `env.dev.ini` - 开发环境专用配置
- `env.test.ini` - 测试环境专用配置
- `env.prod.ini` - 生产环境专用配置

#### 配置管理代码
- `../utils/env.py` - 环境配置读取类
- `../utils/config_manager.py` - 配置管理器

### 变更记录 (Changelog)

#### 2025-12-29 11:39:10
- ✅ 创建config模块文档
- ✅ 添加导航面包屑链接
- ✅ 完善配置结构说明
- ✅ 添加配置使用指南

#### 2024-XX-XX
- 完成env.ini配置结构设计
- 添加多环境配置支持
- 优化配置读取机制
- 增加配置验证功能

---

**提示**: 在修改配置文件时，请先备份原文件，确保配置格式正确。敏感信息建议使用环境变量，避免直接写入配置文件。