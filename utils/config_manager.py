import os
import yaml
from utils.logger import Logger
from copy import deepcopy


class ConfigManager:
    """
    配置管理工具类，用于加载和管理多页面的YAML配置文件
    
    优化功能：
    - 自动加载公共弹窗配置（common_dialogs.yaml）
    - 将公共配置合并到页面配置的elements中
    - 支持页面配置覆盖公共配置
    """
    _instance = None
    _config_cache = {}
    _data_dir = None
    _common_dialogs_cache = None  # 公共弹窗配置缓存
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            # 初始化数据目录路径
            if cls._data_dir is None:
                root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                cls._data_dir = os.path.join(root_path, "data", "pages")
            # 使用Logger单例
            cls._instance.log = Logger().logger
        return cls._instance
    
    def __init__(self):
        # 确保只初始化一次
        pass
    
    def _load_common_dialogs(self):
        """
        加载公共弹窗配置（懒加载）
        :return: 公共弹窗配置数据
        """
        if self._common_dialogs_cache is not None:
            return self._common_dialogs_cache
        
        try:
            common_dialogs_file = os.path.join(self._data_dir, "common_dialogs.yaml")
            
            if not os.path.exists(common_dialogs_file):
                self.log.warning(f"公共弹窗配置文件不存在: {common_dialogs_file}")
                self._common_dialogs_cache = {}
                return {}
            
            with open(common_dialogs_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 提取common_dialogs部分
            common_dialogs = config_data.get('common_dialogs', {})
            self._common_dialogs_cache = common_dialogs
            
            self.log.info(f"✅ 成功加载公共弹窗配置，共 {len(common_dialogs)} 个弹窗")
            return common_dialogs
            
        except Exception as e:
            self.log.error(f"❌ 加载公共弹窗配置失败: {str(e)}")
            self._common_dialogs_cache = {}
            return {}
    
    def _merge_common_dialogs(self, page_config):
        """
        将公共弹窗配置合并到页面配置中
        页面配置优先级更高（可覆盖公共配置）
        
        :param page_config: 页面配置数据
        :return: 合并后的配置数据
        """
        try:
            # 加载公共弹窗配置
            common_dialogs = self._load_common_dialogs()
            
            if not common_dialogs:
                return page_config
            
            # 深拷贝避免修改原始数据
            merged_config = deepcopy(page_config)
            
            # 确保elements字段存在
            if 'elements' not in merged_config:
                merged_config['elements'] = {}
            
            # 合并公共弹窗到elements中（页面配置优先）
            for dialog_name, dialog_config in common_dialogs.items():
                if dialog_name not in merged_config['elements']:
                    # 页面未定义，使用公共配置
                    merged_config['elements'][dialog_name] = deepcopy(dialog_config)
                    self.log.debug(f"  - 合并公共弹窗: {dialog_name}")
                else:
                    # 页面已定义，保留页面配置（覆盖公共配置）
                    self.log.debug(f"  - 页面已自定义弹窗，跳过: {dialog_name}")
            
            return merged_config
            
        except Exception as e:
            self.log.error(f"合并公共弹窗配置失败: {str(e)}")
            return page_config
    
    def load_page_config(self, page_name):
        """
        加载指定页面的配置文件（自动合并公共弹窗配置）
        
        :param page_name: 页面名称，如 'login_page', 'main_page'
        :return: 页面配置数据（已合并公共配置）
        """
        # 添加调试信息
        self.log.info(f"尝试加载页面配置: {page_name}")
        self.log.info(f"配置文件目录: {self._data_dir}")
        
        # 检查缓存
        if page_name in self._config_cache:
            self.log.info(f"从缓存中获取配置: {page_name}")
            return self._config_cache[page_name]
        
        try:
            # 1. 加载页面配置文件
            config_file = os.path.join(self._data_dir, f"{page_name}.yaml")
            
            self.log.info(f"配置文件路径: {config_file}")
            self.log.info(f"配置文件是否存在: {os.path.exists(config_file)}")
            
            if not os.path.exists(config_file):
                self.log.error(f"配置文件不存在: {config_file}")
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                page_config = yaml.safe_load(f)
            
            # 2. 合并公共弹窗配置
            merged_config = self._merge_common_dialogs(page_config)
            
            # 3. 缓存合并后的配置
            self._config_cache[page_name] = merged_config
            
            self.log.info(f"✅ 成功加载页面配置: {page_name}")
            return merged_config
            
        except Exception as e:
            self.log.error(f"❌ 加载页面配置失败 ({page_name}): {str(e)}")
            import traceback
            self.log.error(traceback.format_exc())
            return None
    
    def get_element_locator(self, page_name, element_name, locator_type='automation_id'):
        """
        获取指定页面指定元素的定位器
        :param page_name: 页面名称
        :param element_name: 元素名称
        :param locator_type: 定位器类型，默认为 'automation_id'
        :return: 定位器值
        """
        config_data = self.load_page_config(page_name)
        
        if config_data and 'elements' in config_data:
            elements = config_data['elements']
            if element_name in elements:
                element = elements[element_name]
                if locator_type in element:
                    return element[locator_type]
                else:
                    self.log.error(f"元素 '{element_name}' 中未找到定位器类型 '{locator_type}'")
            else:
                self.log.error(f"页面 '{page_name}' 中未找到元素 '{element_name}'")
        
        return None
    
    def get_test_data(self, page_name, test_case_name=None):
        """
        获取指定页面的测试数据
        :param page_name: 页面名称
        :param test_case_name: 测试用例名称，如果为None则返回所有测试数据
        :return: 测试数据
        """
        config_data = self.load_page_config(page_name)
        
        if config_data and 'test_data' in config_data:
            test_data = config_data['test_data']
            
            if test_case_name:
                if test_case_name in test_data:
                    return test_data[test_case_name]
                else:
                    self.log.error(f"页面 '{page_name}' 中未找到测试用例 '{test_case_name}'")
                    return None
            else:
                return test_data
        
        return None
    
    def get_app_config(self, page_name):
        """
        获取应用程序配置（主要用于登录页面）
        :param page_name: 页面名称
        :return: 应用程序配置
        """
        config_data = self.load_page_config(page_name)
        
        if config_data and 'app_config' in config_data:
            return config_data['app_config']
        
        return None
    
    def clear_cache(self):
        """清空配置缓存"""
        self._config_cache.clear()
        self.log.info("配置缓存已清空")
    
    def list_all_pages(self):
        """
        列出所有可用的页面配置文件
        :return: 页面名称列表
        """
        pages = []
        
        try:
            if os.path.exists(self._data_dir):
                for file_name in os.listdir(self._data_dir):
                    if file_name.endswith('.yaml'):
                        page_name = os.path.splitext(file_name)[0]
                        pages.append(page_name)
        except Exception as e:
            self.log.error(f"列出页面配置文件失败: {str(e)}")
        
        return pages


if __name__ == '__main__':
    # 测试配置管理器
    config_manager = ConfigManager()
    print("可用页面配置:", config_manager.list_all_pages())
    
    # 示例: 加载登录页面配置
    login_config = config_manager.load_page_config('login_page')
    print("登录页面配置:", login_config)
    
    # 示例: 获取登录按钮的定位器
    login_button_locator = config_manager.get_element_locator('login_page', 'login_button', 'automation_id')
    print("登录按钮定位器:", login_button_locator)
    
    # 示例: 获取登录成功的测试数据
    valid_login_data = config_manager.get_test_data('login_page', 'valid_login')
    print("有效登录测试数据:", valid_login_data)