import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(BASE_DIR, "../config/env.ini")
cf = configparser.ConfigParser()
cf.read(configPath, encoding='UTF-8')


class Environment:

    def get_windows_app_type(self):
        return cf.get('windows_app', "type")

    def get_windows_app_location(self):
        return cf.get('windows_app', "location")

    def get_windows_app_name(self):
        return cf.get('windows_app', "app_name")

    def get_app_name(self):
        """获取应用窗口标题（用于查找已有窗口）"""
        return cf.get('windows_app', "app_name")

    def get_app_path(self):
        return cf.get('windows_app', 'location')

    def get_app_top_level_window(self):
        return cf.get('windows_app', 'app_name')

    def get_winappdriver_host(self):
        return cf.get('windows_app', 'winappdriver_host')

    def get_winappdriver_port(self):
        return cf.getint('windows_app', 'winappdriver_port')

    def get_appium_host(self):
        return cf.get('windows_app', 'appium_host')

    def get_appium_port(self):
        return cf.getint('windows_app', 'appium_port')

    def get_app_startup_timeout(self):
        return cf.getint('windows_app', 'app_startup_timeout')

    def get_element_timeout(self):
        return cf.getint('windows_app', 'element_timeout')

    def get_page_load_timeout(self):
        return cf.getint('windows_app', 'page_load_timeout')

    def get_web_browser(self):
        return cf.get('web', 'browser')

    def get_web_headless(self):
        return cf.getboolean('web', 'headless')

    def get_web_base_url(self):
        return cf.get('web', 'base_url')

    def get_webdriver_timeout(self):
        return cf.getint('web', 'webdriver_timeout')

    def get_webdriver_implicit_wait(self):
        return cf.getint('web', 'webdriver_implicit_wait')

    def get_db_type(self):
        return cf.get('database', 'db_type')

    def get_db_host(self):
        return cf.get('database', 'host')

    def get_db_port(self):
        return cf.get('database', 'port')

    def get_db_username(self):
        return cf.get('database', 'username')

    def get_db_password(self):
        return cf.get('database', 'password')

    def get_db_name(self):
        return cf.get('database', 'database')

    def get_db_timeout(self):
        return cf.getint('database', 'db_timeout')

    def get_report_url(self):
        return cf.get('allure', 'report_url')

    def get_info_url(self):
        return cf.get('allure', 'info_url')

    def get_allure_report_dir(self):
        return cf.get('allure', 'report_dir')

    def get_allure_screenshot_dir(self):
        return cf.get('allure', 'screenshot_dir')

    def get_log_level(self):
        return cf.get('logging', 'log_level')

    def get_log_file(self):
        return cf.get('logging', 'log_file')

    def get_log_format(self):
        return cf.get('logging', 'log_format')

    def get_max_log_size(self):
        return cf.getint('logging', 'max_log_size')

    def get_backup_count(self):
        return cf.getint('logging', 'backup_count')

    def get_max_retries(self):
        return cf.getint('retry', 'max_retries')

    def get_retry_delay(self):
        return cf.getint('retry', 'retry_delay')

    def get_response_time_threshold(self):
        return cf.getint('performance', 'response_time_threshold')

    def get_memory_threshold(self):
        return cf.getint('performance', 'memory_threshold')

    def get_cpu_threshold(self):
        return cf.getint('performance', 'cpu_threshold')

    # ==================== Appium性能优化配置 ====================

    def is_element_cache_enabled(self):
        """检查是否启用元素缓存"""
        return cf.getboolean('windows_app', 'element_cache_enabled', fallback=True)

    def get_element_cache_timeout(self):
        """获取元素缓存超时时间（秒）"""
        return cf.getint('windows_app', 'element_cache_timeout', fallback=300)

    def is_smart_wait_enabled(self):
        """检查是否启用智能等待"""
        return cf.getboolean('windows_app', 'smart_wait_enabled', fallback=True)

    def get_smart_wait_poll_interval(self):
        """获取智能等待轮询间隔（秒）"""
        return float(cf.get('windows_app', 'smart_wait_poll_interval', fallback='0.3'))

    def get_smart_wait_timeout(self):
        """获取智能等待超时时间（秒）"""
        return cf.getint('windows_app', 'smart_wait_timeout', fallback=10)

    def get_implicit_wait(self):
        """获取隐式等待时间（秒）"""
        return cf.getint('windows_app', 'implicit_wait', fallback=2)

    def get_appium_session_timeout(self):
        """获取Appium Session超时时间"""
        return cf.getint('windows_app', 'appium_session_timeout', fallback=60)

    def get_appium_command_timeout(self):
        """获取Appium命令执行超时"""
        return cf.getint('windows_app', 'appium_command_timeout', fallback=60)

    # ==================== 并行测试配置 ====================

    def is_parallel_enabled(self):
        """检查是否启用并行测试"""
        return cf.getboolean('parallel', 'enabled', fallback=True)

    def get_max_workers(self):
        """获取最大并行工作线程数"""
        return cf.getint('parallel', 'max_workers', fallback=3)


env = Environment()
if __name__ == "__main__":
    print("环境配置工具类")
