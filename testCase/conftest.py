#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置文件，包含所有测试夹具（fixtures）
"""

import os
import sys
import logging
import time
import pytest
from selenium.common.exceptions import WebDriverException

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.driver_factory import DriverFactory
from utils.config_manager import ConfigManager
from utils.super_handler_factory import SuperHandlerFactory
import configparser # 导入 configparser 模块

# 全局变量存储驱动实例和配置管理器
driver_instance = None
config_manager = None


def _infer_page_module_path(page_name: str) -> str:
    """
    智能推断页面模块路径

    Args:
        page_name: 页面名称（如 'customer_management_page'）

    Returns:
        str: 模块路径（如 'pageObject.customer.customerManagement.customer_management_page'）
    """
    # 页面名到模块路径的映射表
    page_module_map = {
        # 客户管理
        'customer_management_page': 'pageObject.customer.customerManagement.customer_management_page',
        # 装车开票
        'invoice_management_page': 'pageObject.invoiceManagement.invoice_management_page',
        # 监控管理
        'monitor_management_page': 'pageObject.monitorManagement.monitor_management_page',
        # 油品管理
        'oil_management_page': 'pageObject.oil.oilManagement.oil_management_page',
        # 货位管理
        'station_management_page': 'pageObject.system.stationManagement.station_management_page',
        # 串口管理
        'port_management_page': 'pageObject.system.portManagement.port_management_page',
        # 配置设定
        'config_settings_page': 'pageObject.configSettings.config_settings_page',
        # 登录页面
        'login_page': 'pageObject.login_page',
        # 主页面
        'main_page': 'pageObject.main_page',
    }

    # 检查是否是已知页面
    if page_name in page_module_map:
        return page_module_map[page_name]

    # 通用推断：下划线转驼峰
    # customer_management_page -> pageObject.customer.customerManagement.customer_management_page
    base_name = page_name.replace('_page', '')
    parts = base_name.split('_')

    if len(parts) >= 2:
        # 第一个单词作为子目录，后面单词组合成驼峰类名
        first_part = parts[0]  # 'customer'
        remaining_parts = parts[1:]  # ['management']
        camel_name = ''.join(p.title() for p in remaining_parts)  # 'Management'

        # 构建路径：pageObject.customer.customerManagement.customer_management_page
        sub_dir = f"{first_part}.{first_part}{camel_name}"
        module_path = f"pageObject.{sub_dir}.{base_name}_page"
    else:
        # 根目录结构
        module_path = f"pageObject.{base_name}_page"

    return module_path


def pytest_configure(config):
    """
    pytest配置函数，在测试开始前执行
    """
    global driver_instance, config_manager
    
    print("=== 初始化测试环境 (Appium版本) ===")
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 从 env.ini 读取配置
    config_parser = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    config_parser.read(os.path.join(project_root, 'config', 'env.ini'), encoding='utf-8')
 
    
    # 初始化日志
    # 确保log目录存在并使用绝对路径
    log_dir = os.path.join(project_root, 'log')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'test.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 连接Appium服务（自动管理服务器启动）
    print("连接Appium服务...")
    driver_instance = DriverFactory.get_windows_driver()

    if driver_instance:
        print("✓ Appium连接成功")
        print("✓ 应用已准备就绪")
        
        # 启用元素缓存（性能优化）
        cache_enabled = config_parser.getboolean('windows_app', 'element_cache_enabled', fallback=True)
        cache_timeout = config_parser.getint('windows_app', 'element_cache_timeout', fallback=300)
        if cache_enabled:
            DriverFactory.enable_cache(True, cache_timeout)
            print(f"✓ 元素缓存已启用，超时: {cache_timeout}秒")
    else:
        print("✗ Appium连接失败")
        print("可能的原因:")
        print("1. Appium服务未启动 - 请运行 start_appium.bat")
        print("2. 应用未启动 - 请手动启动应用")
        print("3. 应用窗口标题不匹配 - 请检查config/env.ini中的app_name配置")
        print("4. 端口被占用 - 请检查端口4723是否被其他程序使用")
        pytest.exit("Appium连接失败，退出测试")
    
    print("=== 测试环境初始化完成 ===")

#测试设置夹具,主要是配置驱动实例和页面配置类
@pytest.fixture(scope="session")
def test_setup():
    """
    测试设置夹具，在整个测试会话期间运行一次
    初始化驱动和配置管理器
    """
    global driver_instance, config_manager
    
    try:
        print("=== 测试设置开始 ===")
        # 初始化配置管理器
        config_manager = ConfigManager()
        
        # 添加调试信息
        print("=== test_setup夹具开始执行 ===")
        
        # 如果driver_instance为None，初始化WinAppDriver驱动
        if driver_instance is None:
            logging.info("启动WinAppDriver...")
            driver_instance = DriverFactory.get_windows_driver()
        
        # 添加调试信息
        print(f"Driver instance: {driver_instance}")
        
        # 返回测试资源字典
        resources = {
            'driver': driver_instance,
            'config_manager': config_manager
        }
        
        print("=== test_setup夹具执行完成 ===")
        yield resources
        
    except Exception as e:
        print(f"测试设置失败: {e}")
        raise
    finally:
        # 测试会话结束后清理资源
        print("=== 测试清理执行 ===")
        # 使用新的DriverFactory.quit_driver方法（会自动清理缓存）
        DriverFactory.quit_driver(driver_instance)
        driver_instance = None
        print("=== 测试清理执行完成 ===")

#根据传入页面的不同生成对应的页面实例并加载所有页面要用到的资源
def page_test_fixture(test_setup, page_name, page_class_name):
    """
    通用页面测试夹具，为任意页面提供测试资源和数据
    
    Args:
        test_setup: 基础测试设置夹具
        page_name: 页面名称，用于获取配置（如 'login_page'）
        page_class_name: 页面类名（如 'LoginPage'）
    """
    # 获取测试资源
    driver = test_setup['driver']
    config_manager = test_setup['config_manager']
    

    # 获取页面配置
    page_config = config_manager.load_page_config(page_name)

    # 智能推断页面模块路径（支持子目录结构）
    page_module_path = _infer_page_module_path(page_name)
    page_module = __import__(page_module_path, fromlist=[page_class_name])
    page_class = getattr(page_module, page_class_name)

    page_instance = page_class(driver, config_manager) # 传递 driver 和 config_manager
    

    
    # 使用超级工厂创建处理器实例（终极简化！）
    # 注意：超级工厂自动管理所有依赖，无需手动创建页面对象
    # 传递现有的driver实例，避免重复创建
    from utils.super_handler_factory import SuperHandlerFactory
    handler_instance = SuperHandlerFactory.create(page_name, driver=driver)
    
    # 创建日志记录器
    log = logging.getLogger(f"{page_name}_test")
    log.setLevel(logging.INFO)
    
    # 检查是否已经添加了处理器，避免重复添加
    if not log.handlers:
        # 创建文件处理器，使用项目根目录的绝对路径
        log_dir = os.path.join(project_root, 'log')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'test.log')
        
        # 添加文件处理器和控制台处理器
        handlers = [
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        for h in handlers:
            h.setFormatter(formatter)
            log.addHandler(h)
    
    log.info(f"=== {page_class_name} 测试类开始 ===")
    
    # 返回测试资源字典
    yield {
        'driver': driver,
        'page': page_instance,
        'handler': handler_instance,
        'config_manager': config_manager,
        'page_config': page_config,
        'log': log,
    }
    
    log.info(f"=== {page_class_name} 测试类结束 ===")
    
    # 清理处理器
    for h in log.handlers[:]:
        h.close()
        log.removeHandler(h)

#页面测试夹具工厂，根据页面的名称生成相应的资源
@pytest.fixture(scope="class")
def page_test_factory(request):
    """
    通用页面测试工厂夹具，根据测试类名自动推断页面名称和类名
    
    自动推断规则：
    - TestLoginPage -> login_page, LoginPage
    - TestMainPage -> main_page, MainPage
    """
    # 初始化驱动和配置管理器
    # config_manager = ConfigManager() # 已经在pytest_configure中初始化，这里不需要重复初始化
    # driver_instance = DriverFactory.get_windows_driver() # 已经在pytest_configure中初始化，这里不需要重复初始化
    
    # 添加调试信息
    import logging
    log_instance = logging.getLogger("log")
    log_instance.warning(f"Driver instance in page_test_factory: {driver_instance}")
    log_instance.warning(f"Driver instance type: {type(driver_instance)}")
    
    # 获取测试类名
    class_name = request.cls.__name__  # 如 'TestLogin'
    
    # 转换类名到页面配置（TestLogin -> login_page, LoginPage）
    if class_name.startswith('Test'):
        # 正确的转换逻辑：TestLoginPage -> login_page, LoginPage
        page_type = class_name[4:]  # 'LoginPage'
        # 使用正则表达式在大写字母前添加下划线，并转换为小写
        import re
        page_name = re.sub(r'(?<!^)(?=[A-Z])', '_', page_type).lower()  # 'login_page'
        page_class_name = page_type  # 'LoginPage'
    else:
        # 默认规则,文件名main_page,类名MainPage
        page_name = 'main_page'
        page_class_name = 'MainPage'
        
    # 创建测试资源字典
    test_setup = {
        'driver': driver_instance,
        'config_manager': config_manager
    }
    
    # 使用yield from调用page_test_fixture
    yield from page_test_fixture(test_setup, page_name, page_class_name)
    
    # 测试类结束后不再清理资源，由test_setup fixture统一处理
    # 避免驱动被过早关闭

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    pytest钩子，用于生成测试报告
    """
    # 执行测试
    outcome = yield
    rep = outcome.get_result()

    # 设置测试结果属性，供screenshot_on_failure使用
    setattr(item, "rep_" + rep.when, rep)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    测试结束后收集结果并生成报告
    """
    # 收集测试结果
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))

    # 计算成功率
    success_rate = (passed / total * 100) if total > 0 else 0

    # 计算执行时间
    duration = time.time() - getattr(terminalreporter, '_sessionstarttime', getattr(terminalreporter, '_session_start', time.time()))

    # 准备结果信息
    result_info = f"""
    ================================== 测试结果 ==================================
    用例总数: {total}
    通过: {passed}
    失败: {failed}
    错误: {error}
    跳过: {skipped}
    成功率: {success_rate:.2f}%
    执行时间: {duration:.2f}秒
    ==============================================================================
    """

    # 输出到控制台
    print(result_info)

    # 写入结果文件
    result_file = os.path.join(os.getcwd(), "test_result.txt")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result_info)

    # 生成Allure HTML报告
    allure_results_dir = os.path.join(os.getcwd(), "report", "result")
    allure_html_dir = os.path.join(os.getcwd(), "reports", "allure-html")
    
    # 确保reports目录存在
    os.makedirs(os.path.dirname(allure_html_dir), exist_ok=True)
    
    # 检查是否有allure结果文件
    if os.path.exists(allure_results_dir) and os.listdir(allure_results_dir):
        print(f"正在生成Allure HTML报告...")
        try:
            # 使用allure generate命令生成HTML报告
            import subprocess
            cmd = f"allure generate {allure_results_dir} -o {allure_html_dir} --clean"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Allure HTML报告已生成，位于: {allure_html_dir}")
                print(f"可通过以下命令查看报告:")
                print(f"allure serve {allure_results_dir}")
                print(f"或直接打开: {os.path.join(allure_html_dir, 'index.html')}")
            else:
                print(f"生成Allure HTML报告失败: {result.stderr}")
        except Exception as e:
            print(f"生成Allure HTML报告时出错: {e}")
    else:
        print("未找到Allure测试结果文件，跳过HTML报告生成")