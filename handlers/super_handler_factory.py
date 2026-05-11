"""
超级Handler工厂 - 终极简化版
完全自动化的Handler创建和管理

主要特性：
- 🚀 1行代码创建完整Handler实例
- 🔧 自动创建页面对象和driver
- 📦 智能依赖管理，无需手动配置
- 🛡️ 完善的错误处理和日志记录
"""

import logging
import importlib
import inspect
from typing import Optional, Any, Dict
from utils.driver_factory import DriverFactory
from utils.global_manager import GlobalManager


class SuperHandlerFactory:
    """
    超级Handler工厂 - 终极简化版本

    使用方式：
    # 最简单使用
    handler = SuperHandlerFactory.create('user_profile_page')

    # 高级模式（支持自定义参数）
    handler = SuperHandlerFactory.create(
        'user_profile_page',
        custom_driver=my_driver,
        extra_params={'timeout': 30}
    )
    """

    @classmethod
    def create(cls, page_name: str, **kwargs) -> Any:
        """
        创建Handler实例 - 终极简化版本

        Args:
            page_name: 页面名称，如 'login_page', 'user_profile_page'
            **kwargs: 额外参数

        Returns:
            Handler实例

        示例：
            # 最简单使用
            handler = SuperHandlerFactory.create('user_profile_page')

            # 修改用户名
            result = handler.change_username_and_verify(
                'old_password', 'new_username', 'confirm_username'
            )
        """
        try:
            logger = logging.getLogger(__name__)

            # 1. 获取全局管理器和配置
            global_manager = GlobalManager()
            config_manager = global_manager.get_config_manager()

            # 2. 智能推断Handler类名和模块
            handler_info = cls._infer_handler_info(page_name)
            logger.info(f"推断Handler信息: {handler_info}")

            # 3. 动态导入Handler模块
            handler_module = cls._import_handler_module(handler_info['module_path'])

            # 4. 获取Handler类
            handler_class = getattr(handler_module, handler_info['class_name'])

            # 5. 自动创建依赖对象
            dependencies = cls._create_dependencies(page_name, config_manager, kwargs)

            # 6. 创建Handler实例
            handler_instance = cls._create_handler_instance(handler_class, dependencies, kwargs)

            logger.info(f"✅ 超级Handler工厂成功创建: {handler_info['class_name']}")
            return handler_instance

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"❌ 超级Handler工厂创建失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    @classmethod
    def _infer_handler_info(cls, page_name: str) -> Dict[str, str]:
        """
        智能推断Handler信息

        Args:
            page_name: 页面名称

        Returns:
            dict: 包含class_name和module_path的字典
        """
        # 移除_page后缀
        base_name = page_name.replace('_page', '')

        # 转换为PascalCase
        class_prefix = ''.join(word.title() for word in base_name.split('_'))

        # 统一的Handler后缀
        class_name = f"{class_prefix}Handler"

        # 推断模块路径
        module_path = cls._infer_module_path(base_name)

        return {
            'class_name': class_name,
            'module_path': module_path,
            'base_name': base_name,
            'class_prefix': class_prefix
        }

    @classmethod
    def _infer_module_path(cls, base_name: str) -> str:
        """
        推断Handler模块路径

        Args:
            base_name: 基础名称（如 customer_management）

        Returns:
            str: 模块路径
        """
        # 页面名到Handler模块路径的映射表
        page_handler_map = {
            # 客户管理
            'customer_management': 'handlers.customer.customerManagement.customer_management_handler',
            # 装车开票
            'invoice_management': 'handlers.invoiceManagement.invoice_management_handler',
            # 监控管理
            'monitor_management': 'handlers.monitorManagement.monitor_management_handler',
            # 油品管理
            'oil_management': 'handlers.oil.oilManagement.oil_management_handler',
            # 货位管理
            'station_management': 'handlers.system.stationManagement.station_management_handler',
            # 串口管理
            'port_management': 'handlers.system.portManagement.port_management_handler',
            # 配置设定
            'config_settings': 'handlers.configSettings.config_settings_handler',
            # 用户管理
            'user_management': 'handlers.user.userManagement.user_management_handler',
        }

        # 检查是否是已知页面
        if base_name in page_handler_map:
            return page_handler_map[base_name]

        # 通用推断：下划线转驼峰
        # customer_management -> handlers.customer.customerManagement.customer_management_handler
        parts = base_name.split('_')

        if len(parts) >= 2:
            first_part = parts[0]  # 'customer'
            remaining_parts = parts[1:]  # ['management']
            camel_name = ''.join(p.title() for p in remaining_parts)  # 'Management'

            # 构建路径：handlers.customer.customerManagement.customer_management_handler
            sub_dir = f"{first_part}.{first_part}{camel_name}"
            module_name = f"handlers.{sub_dir}.{base_name}_handler"
        else:
            # 根目录结构
            module_name = f"handlers.{base_name}_handler"

        return module_name

    @classmethod
    def _import_handler_module(cls, module_path: str):
        """
        动态导入Handler模块

        Args:
            module_path: 模块路径

        Returns:
            导入的模块
        """
        try:
            return importlib.import_module(module_path)
        except ImportError as e:
            # 尝试其他可能的路径
            alternatives = cls._generate_alternative_paths(module_path)
            for alt_path in alternatives:
                try:
                    return importlib.import_module(alt_path)
                except ImportError:
                    continue

            raise ImportError(f"无法导入Handler模块: {module_path} 或其替代路径")

    @classmethod
    def _generate_alternative_paths(cls, original_path: str) -> list:
        """
        生成替代的模块路径

        Args:
            original_path: 原始路径

        Returns:
            list: 替代路径列表
        """
        alternatives = []

        # 如果是子目录结构，尝试根目录
        if '.handler' in original_path:
            # handlers.user.userProfile.user_profile_handler -> handlers.user_profile_handler
            parts = original_path.split('.')
            if len(parts) >= 3:
                alt_path = f"{parts[0]}.{parts[-1]}"
                alternatives.append(alt_path)

        return alternatives

    @classmethod
    def _create_dependencies(cls, page_name: str, config_manager, kwargs: Dict) -> Dict:
        """
        自动创建依赖对象

        Args:
            page_name: 页面名称
            config_manager: 配置管理器
            kwargs: 额外参数

        Returns:
            dict: 依赖对象字典
        """
        dependencies = {
            'config_manager': config_manager
        }

        # 获取或创建driver
        custom_driver = kwargs.get('custom_driver')
        if custom_driver:
            dependencies['driver'] = custom_driver
        else:
            dependencies['driver'] = DriverFactory.get_windows_driver()

        # 创建页面对象
        page_class = cls._get_page_class(page_name)
        dependencies['page_instance'] = page_class(dependencies['driver'], config_manager)

        return dependencies

    @classmethod
    def _get_page_class(cls, page_name: str):
        """
        获取页面类

        Args:
            page_name: 页面名称

        Returns:
            页面类
        """
        # 页面名到Page模块路径的映射表
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
            # 用户管理
            'user_management_page': 'pageObject.user.userManagement.user_management_page',
        }

        # 推断页面类路径
        base_name = page_name.replace('_page', '')

        if page_name in page_module_map:
            module_path = page_module_map[page_name]
        else:
            # 通用推断：下划线转驼峰
            parts = base_name.split('_')

            if len(parts) >= 2:
                first_part = parts[0]  # 'customer'
                remaining_parts = parts[1:]  # ['management']
                camel_name = ''.join(p.title() for p in remaining_parts)  # 'Management'

                # 构建路径：pageObject.customer.customerManagement.customer_management_page
                sub_dir = f"{first_part}.{first_part}{camel_name}"
                module_path = f"pageObject.{sub_dir}.{base_name}_page"
            else:
                module_path = f"pageObject.{base_name}_page"

        try:
            page_module = importlib.import_module(module_path)
            class_name = ''.join(word.title() for word in base_name.split('_')) + 'Page'
            return getattr(page_module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"无法找到页面类: {module_path}.{class_name}")

    @classmethod
    def _create_handler_instance(cls, handler_class, dependencies: Dict, kwargs: Dict):
        """
        创建Handler实例

        Args:
            handler_class: Handler类
            dependencies: 依赖对象
            kwargs: 额外参数

        Returns:
            Handler实例
        """
        # 检查构造函数参数
        sig = inspect.signature(handler_class.__init__)
        params = list(sig.parameters.keys())[1:]  # 跳过self

        # 构建初始化参数
        init_kwargs = {}

        # 添加依赖对象
        for param_name, dep_obj in dependencies.items():
            if param_name in params:
                init_kwargs[param_name] = dep_obj

        # 添加额外参数
        for key, value in kwargs.items():
            if key in params and key not in init_kwargs:
                init_kwargs[key] = value

        return handler_class(**init_kwargs)


# 便捷函数
def create_handler(page_name: str, **kwargs):
    """
    便捷函数 - 创建Handler实例

    Args:
        page_name: 页面名称
        **kwargs: 额外参数

    Returns:
        Handler实例

    示例：
        handler = create_handler('user_profile_page')
    """
    return SuperHandlerFactory.create(page_name, **kwargs)
