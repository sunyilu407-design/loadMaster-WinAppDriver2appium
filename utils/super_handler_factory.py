"""
超级Handler工厂 - 终极简化版
完全自动化的Handler创建和管理

主要特性：
- 🚀 1行代码创建完整Handler实例
- 🔧 自动创建页面对象和driver
- 🎯 支持传统和全局化两种Handler模式
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
    # 简单模式（推荐）
    handler = SuperHandlerFactory.create('user_profile_page')

    # 高级模式（支持自定义参数）
    handler = SuperHandlerFactory.create(
        'user_profile_page',
        mode='global',  # 'global' 或 'traditional'
        custom_driver=my_driver,
        extra_params={'timeout': 30}
    )
    """

    # Handler类型映射
    # 注意：当前我们主要使用传统Handler，全局化模式预留给未来扩展
    HANDLER_TYPE_MAP = {
        'global': 'GlobalHandler',      # 全局化Handler（预留）
        'traditional': 'Handler'        # 传统Handler（当前推荐）
    }

    @classmethod
    def create(cls, page_name: str, mode: str = 'traditional', **kwargs) -> Any:
        """
        创建Handler实例 - 终极简化版本

        Args:
            page_name: 页面名称，如 'login_page', 'user_profile_page'
            mode: Handler模式 ('global' 或 'traditional')
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
            handler_info = cls._infer_handler_info(page_name, mode)
            logger.info(f"推断Handler信息: {handler_info}")

            # 3. 动态导入Handler模块
            handler_module = cls._import_handler_module(handler_info['module_path'])

            # 4. 获取Handler类
            handler_class = getattr(handler_module, handler_info['class_name'])

            # 5. 自动创建依赖对象
            dependencies = cls._create_dependencies(page_name, handler_info, config_manager, kwargs)

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
    def _infer_handler_info(cls, page_name: str, mode: str) -> Dict[str, str]:
        """
        智能推断Handler信息

        Args:
            page_name: 页面名称
            mode: Handler模式

        Returns:
            dict: 包含class_name和module_path的字典
        """
        # 移除_page后缀
        base_name = page_name.replace('_page', '')

        # 转换为PascalCase
        class_prefix = ''.join(word.title() for word in base_name.split('_'))

        # 根据模式确定类名后缀
        type_suffix = cls.HANDLER_TYPE_MAP.get(mode, 'Handler')
        class_name = f"{class_prefix}{type_suffix}"

        # 推断模块路径（支持子目录结构）
        module_path = cls._infer_module_path(base_name, mode)

        return {
            'class_name': class_name,
            'module_path': module_path,
            'base_name': base_name,
            'class_prefix': class_prefix
        }

    @classmethod
    def _infer_module_path(cls, base_name: str, mode: str) -> str:
        """
        推断模块路径（支持顶级目录和子目录结构）

        Args:
            base_name: 基础名称（如 user_profile）
            mode: Handler模式

        Returns:
            str: 模块路径
        """
        # 完整页面名
        page_name = f"{base_name}_page"

        # 顶级目录映射表
        top_level_handlers = {
            'invoice_management_page': 'handlers.invoiceManagement.invoice_management_handler',
            'config_settings_page': 'handlers.configSettings.config_settings_handler',
            'monitor_management_page': 'handlers.monitorManagement.monitor_management_handler',
            'port_management_page': 'handlers.system.portManagement.port_management_handler',
            'station_management_page': 'handlers.system.stationManagement.station_management_handler',
        }

        # 检查是否是顶级目录页面
        if page_name in top_level_handlers:
            module_name = top_level_handlers[page_name]
            if mode == 'global':
                module_name = module_name.replace('_handler', '_global_handler')
            return module_name

        # 检查是否是子目录结构（如 user.profile -> handlers.user.userProfile）
        parts = base_name.split('_')

        if len(parts) >= 2:
            # 子目录结构: handlers.user.userManagement.user_management_handler
            first_part = parts[0]  # 'user'
            last_part = parts[-1]  # 'management'

            # 构建目录路径：user.userManagement
            sub_dir = f"{first_part}.{first_part}{last_part.title()}"
            module_name = f"handlers.{sub_dir}.{base_name}_{'global_' if mode == 'global' else ''}handler"
        else:
            # 根目录结构: handlers.user_profile_handler
            module_name = f"handlers.{base_name}_{'global_' if mode == 'global' else ''}handler"

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
        if '.global_handler' in original_path:
            # handlers.user.userProfile.user_profile_global_handler -> handlers.user_profile_global_handler
            parts = original_path.split('.')
            if len(parts) >= 3:
                alt_path = f"{parts[0]}.{parts[-1]}"
                alternatives.append(alt_path)

        elif '.handler' in original_path:
            # handlers.user.userProfile.user_profile_handler -> handlers.user_profile_handler
            parts = original_path.split('.')
            if len(parts) >= 3:
                # 子目录 -> 根目录: handlers.user.userProfile.user_profile_handler -> handlers.user_profile_handler
                alt_path = f"{parts[0]}.{parts[-1]}"
                alternatives.append(alt_path)

                # 对于多级子目录，还可以尝试中间层级
                if len(parts) >= 4:
                    # handlers.user.userProfile.user_profile_handler -> handlers.user.user_profile_handler
                    alt_path2 = f"{parts[0]}.{'.'.join(parts[1:-1])}.{parts[-1]}"
                    alternatives.append(alt_path2)

        return alternatives

    @classmethod
    def _create_dependencies(cls, page_name: str, handler_info: Dict, config_manager, kwargs: Dict) -> Dict:
        """
        自动创建依赖对象

        Args:
            page_name: 页面名称
            handler_info: Handler信息
            config_manager: 配置管理器
            kwargs: 额外参数

        Returns:
            dict: 依赖对象字典
        """
        dependencies = {
            'config_manager': config_manager
        }

        # 获取或创建driver
        custom_driver = kwargs.get('custom_driver') or kwargs.get('driver')
        if custom_driver:
            dependencies['driver'] = custom_driver
        else:
            dependencies['driver'] = DriverFactory.get_windows_driver()

        # 获取或创建页面对象（仅对传统Handler需要）
        if handler_info['class_name'].endswith('Handler'):  # 传统Handler
            page_class = cls._get_page_class(page_name)
            dependencies['page_instance'] = page_class(dependencies['driver'], config_manager)

        return dependencies

    @classmethod
    def _get_page_class(cls, page_name: str):
        """
        获取页面类（支持顶级目录和子目录结构）

        Args:
            page_name: 页面名称

        Returns:
            页面类
        """
        # 顶级目录映射表
        top_level_pages = {
            'invoice_management_page': 'pageObject.invoiceManagement.invoice_management_page',
            'config_settings_page': 'pageObject.configSettings.config_settings_page',
            'monitor_management_page': 'pageObject.monitorManagement.monitor_management_page',
            'port_management_page': 'pageObject.system.portManagement.port_management_page',
            'station_management_page': 'pageObject.system.stationManagement.station_management_page',
        }

        # 检查是否是顶级目录页面
        if page_name in top_level_pages:
            module_path = top_level_pages[page_name]
            base_name = page_name.replace('_page', '')
            class_name = ''.join(word.title() for word in base_name.split('_')) + 'Page'
            page_module = importlib.import_module(module_path)
            return getattr(page_module, class_name)

        # 推断页面类路径
        base_name = page_name.replace('_page', '')
        parts = base_name.split('_')

        if len(parts) >= 2:
            # 子目录结构: pageObject.user.userManagement.user_management_page
            first_part = parts[0]  # 'user'
            last_part = parts[-1]  # 'management'

            # 构建目录路径：user.userManagement
            sub_dir = f"{first_part}.{first_part}{last_part.title()}"
            module_path = f"pageObject.{sub_dir}.{base_name}_page"
        else:
            module_path = f"pageObject.{base_name}_page"

        class_name = ''.join(word.title() for word in base_name.split('_')) + 'Page'
        try:
            page_module = importlib.import_module(module_path)
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
def create_handler(page_name: str, mode: str = 'traditional', **kwargs):
    """
    便捷函数 - 创建Handler实例

    Args:
        page_name: 页面名称
        mode: Handler模式 ('global' 或 'traditional')
        **kwargs: 额外参数

    Returns:
        Handler实例

    示例：
        handler = create_handler('user_profile_page')
    """
    return SuperHandlerFactory.create(page_name, mode, **kwargs)
