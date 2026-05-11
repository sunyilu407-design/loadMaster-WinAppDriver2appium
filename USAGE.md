# 通用自动化测试框架使用说明

## 项目概述

这是一个通用的自动化测试框架，支持Windows桌面应用和Web应用的自动化测试，并集成了数据库交互功能。

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

确保已安装Python 3.7+，然后安装依赖包：

```bash
pip install -r requirements.txt
```

### 2. 配置环境

编辑 `config/env.ini` 文件，配置应用路径、数据库连接等信息。

### 3. 编写测试

参考 `demo_page.py`、`demo_handler.py` 和 `test_demo.py` 文件创建自己的页面对象、处理程序和测试用例。

### 4. 运行测试

#### Windows系统：
双击运行 `run.bat` 脚本

#### 命令行运行：
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest testCase/test_loadmaster.py

# 运行特定测试类或方法
pytest testCase/test_loadmaster.py::TestLoadMaster::test_login_success
```

### 5. 清理缓存文件

#### Windows系统：
双击运行 `clean_cache.bat` 脚本

#### 命令行运行：
```bash
# 手动清理缓存文件
python -c "import os; [os.remove(os.path.join(dp, f)) for dp, dn, fn in os.walk('.') for f in fn if f.endswith('.pyc')]"
```

## 核心组件说明

### 1. 页面对象 (Page Object)

页面对象封装了界面元素的定位和操作方法。

### 2. 处理程序 (Handler)

处理程序封装了业务逻辑，可以调用页面对象的方法，并可与数据库交互。

### 3. 数据库交互

通过 `DatabaseHelper` 类可以方便地进行数据库操作：

```python
from utils.db_helper import DatabaseHelper

# 创建数据库助手实例
db_helper = DatabaseHelper()

# 连接数据库
if db_helper.connect():
    # 查询数据
    result = db_helper.get_table_data("users")
    
    # 执行更新语句
    db_helper.execute_update("INSERT INTO users (name, email) VALUES (%s, %s)", ("张三", "zhangsan@example.com"))
    
    # 断开连接
    db_helper.disconnect()
```

### 4. 测试数据

测试数据建议存放在 `data/` 目录下，支持YAML格式。

### 5. 窗口定位

对于Windows桌面应用，框架提供了`locate_window`方法来定位新弹出的窗口。该方法支持通过窗口标题或标题正则表达式来定位窗口。

使用示例：
```python
# 通过窗口标题定位
window = base_page.locate_window(title="记事本")

# 通过标题正则表达式定位
window = base_page.locate_window(title_re=".*记事本.*")

# 设置自定义超时时间（默认10秒）
window = base_page.locate_window(timeout=5, title="计算器")
```

该方法会返回一个pywinauto窗口对象，可以对该对象进行进一步的操作。

## 开发建议

1. 遵循Page Object设计模式，将页面元素和操作分离
2. 在handlers中封装业务逻辑
3. 使用YAML文件管理测试数据
4. 合理使用allure注解提高报告可读性
5. 利用数据库交互功能实现数据断言

## 常见问题

1. **如何添加新的测试用例？**
   在 `testCase/` 目录下创建新的测试文件，参考 `test_demo.py` 的结构。

2. **如何配置数据库连接？**
   修改 `config/env.ini` 中的 `[database]` 配置节。

3. **如何支持新的定位方式？**
   在 `pageObject/base_page.py` 的 `locate_element` 方法中添加新的定位策略。

4. **如何添加新的依赖包？**
   在 `requirements.txt` 中添加新的依赖包，然后运行 `pip install -r requirements.txt`。

5. **如何清理缓存文件？**
   运行 `clean_cache.bat` 脚本或手动删除 `__pycache__` 目录和 `.pyc` 文件。