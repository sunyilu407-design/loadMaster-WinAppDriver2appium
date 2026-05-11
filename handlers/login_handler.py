import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin
from pageObject.login_page import LoginPage
from utils.db_helper import DatabaseHelper
from utils.logger import Logger
from utils.driver_factory import DriverFactory
import time
import allure
import logging

logger = Logger().logger

class LoginHandler(BaseHandler, NavigationMixin):
    def __init__(self, page_instance=None, config_manager=None):
        """初始化登录处理器"""
        super().__init__(page_instance, config_manager)
        # 初始化NavigationMixin
        NavigationMixin.__init__(self)

        # 赋值页面对象（自动创建）
        self.login_page = self.page_instance

        # 保持其他兼容性设置
        self.logger = logger

    def login(self, username, password, max_retries=0):
        """
        执行登录操作
        
        Args:
            username (str): 用户名
            password (str): 密码
            max_retries (int): 最大重试次数，默认为0不重试
            
        Returns:
            bool: 登录是否成功
        """
        logging.warning(f"LoginHandler.login被调用，username: {username}, password: {password}")
        logging.warning(f"self.login_page: {self.login_page}")
        if hasattr(self.login_page, 'driver'):
            logging.warning(f"self.login_page.driver: {self.login_page.driver}")
            logging.warning(f"self.login_page.driver类型: {type(self.login_page.driver)}")
        else:
            logging.warning("self.login_page没有driver属性")
            
        if not self.login_page.driver:
            logging.error("驱动未初始化，无法执行登录操作")
            return False
            
        retry_count = 0
        while retry_count <= max_retries:
            try:
                self.login_page.clear_input_fields()
                with allure.step(f"执行登录操作 (尝试 {retry_count + 1}/{max_retries + 1})"):
                    logging.info(f"开始登录，用户名: {username} (尝试 {retry_count + 1}/{max_retries + 1})")
                    
                    # 执行登录
                    logging.info("开始调用 login_page.login")
                    success = self.login_page.login(username, password)
                    logging.info(f"login_page.login 返回: {success}")
                    
                    if success:
                        logging.info("登录成功")
                        return True
                    else:
                        logging.warning(f"登录失败 (尝试 {retry_count + 1}/{max_retries + 1})")
                        
            except Exception as e:
                logging.error(f"登录过程中发生异常: {e}")
                logging.exception(e)
                if retry_count == max_retries:
                    raise
                    
            retry_count += 1
            if retry_count <= max_retries:
                logging.info(f"等待2秒后进行重试...")
                time.sleep(2)
                
        return False

    def login_with_retry(self, username, password, max_retries=3):
        """
        带重试机制的登录方法
        
        Args:
            username (str): 用户名
            password (str): 密码
            max_retries (int): 最大重试次数
            
        Returns:
            bool: 登录是否成功
        """
        return self.login(username, password, max_retries)

    def login_with_failure(self, username, password, expected_error):
        """
        测试登录失败场景
        
        Args:
            username (str): 用户名
            password (str): 密码
            expected_error (str): 预期的错误信息
            
        Returns:
            bool: 是否登录失败并显示预期错误
        """
        status = self.login_page.login(username, password)
        if status:
            logging.error("登录成功，而预期是失败")
            return False
            
        error_msg = self.login_page.get_error_message()  
        if  error_msg is None   :
            logging.error("登录失败")
            return False
        
        if error_msg != expected_error:
            logging.error(f"登录失败，但错误信息不是预期的 {expected_error}，而是 {error_msg}")
            return False
            
        logging.info("登录失败并显示预期错误")
        return True


    def is_login_successful(self):
        """
        检查是否登录成功
        
        Returns:
            bool: 是否登录成功
        """
        if not self.login_page.driver:
            logging.error("驱动未初始化，无法检查登录状态")
            return False
            
        try:
            return self.login_page.is_login_successful()
        except Exception as e:
            logging.error(f"检查登录状态时发生异常: {e}")
            return False

    def get_error_message(self):
        """
        获取登录错误信息
        
        Returns:
            str: 错误信息，如果获取失败则返回None
        """
        if not self.login_page.driver:
            logging.error("驱动未初始化，无法获取错误信息")
            return None
            
        try:
            return self.login_page.get_error_message()
        except Exception as e:
            logging.error(f"获取错误信息时发生异常: {e}")
            return None

    def validate_login_data(self, username, password):
        """
        验证登录数据
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 数据是否有效
        """
        if not username or not password:
            logging.warning("用户名或密码为空")
            return False
        return True

    def perform_database_operation_example(self, query):
        """
        执行数据库操作示例

        Args:
            query (str): SQL查询语句

        Returns:
            list: 查询结果
        """
        try:
            logging.info(f"执行数据库查询: {query}")
            result = self.db_helper.execute_query(query)
            logging.info(f"查询结果: {result}")
            return result
        except Exception as e:
            logging.error(f"数据库操作失败: {e}")
            return []


    def logout_and_login(self, username: str, password: str, max_retries=0) -> dict:
        """
        退出登录后使用指定用户登录

        Args:
            username (str): 要登录的用户名
            password (str): 要登录的密码
            max_retries (int): 最大重试次数，默认为0不重试

        Returns:
            dict: {
                'success': bool,
                'error': str
            }
        """
        logging.info(f"开始退出登录并使用用户 {username} 重新登录")

        try:
            # 步骤1: 导航到退出登录页面
            from handlers.main_handler import MainHandler
            from pageObject.main_page import MainPage

            main_page = MainPage(self.login_page.driver, self.config_manager)
            main_handler = MainHandler(main_page)

            logging.info("导航到退出登录页面")
            if not main_handler.navigate_to_user_logout():
                return {
                    'success': False,
                    'error': '导航到退出登录页面失败'
                }

            # 等待登录页面出现
            time.sleep(2)

            # 步骤2: 使用指定用户登录
            logging.info(f"使用用户 {username} 登录")
            login_success = self.login(username, password, max_retries)

            if not login_success:
                return {
                    'success': False,
                    'error': f'使用用户 {username} 登录失败'
                }

            logging.info(f"成功退出并重新登录: {username}")
            return {
                'success': True,
                'error': None
            }

        except Exception as e:
            logging.error(f"退出登录过程中发生异常: {e}")
            logging.exception(e)
            return {
                'success': False,
                'error': f'退出登录异常: {str(e)}'
            }