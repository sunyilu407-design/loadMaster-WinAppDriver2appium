"""
用户信息管理页面 - 页面元素操作
只包含页面元素定位和基础交互，不包含业务逻辑
"""

import allure
from pageObject.base_page import BasePage


class UserManagementPage(BasePage):
    """
    用户信息管理页面 - 页面元素操作类
    """

    def __init__(self, driver, config_manager):
        super().__init__(driver, config_manager, "windows")

        # 加载页面配置,user_management_page.yaml
        self.config = self.config_manager.load_page_config('user_management_page')

        # 检查配置加载是否成功
        if self.config is None:
            self.log.error("user_management_page: 配置加载失败")
            raise Exception("user_management_page: 配置加载失败")

        # 检查驱动是否初始化成功
        if self.driver is None:
            self.log.error("user_management_page: 驱动未初始化")
            raise Exception("user_management_page: 驱动未初始化")
        else:
            self.log.info("user_management_page: 驱动初始化成功")
            self.elements = self.config.get('elements', {})
            self.test_data = self.config.get('test_data', [])
            self.app_config = self.config.get('app_config', [])


    def _get_element_config(self, element_name):
        """
        获取元素配置
        :param element_name: 元素名称
        :return: 元素配置字典
        """
        # 递归查找元素配置
        def find_element(config, name):
            if name in config:
                return config[name]
            for key, value in config.items():
                if isinstance(value, dict):
                    if key == 'child_elements' and name in value:
                        return value[name]
                    result = find_element(value, name)
                    if result:
                        return result
            return None

        element_config = find_element(self.elements, element_name)
        if element_config:
            return element_config
        self.log.error(f"未找到元素配置: {element_name}")
        return None

    # 按钮元素点击方法
    def click_add_user_button(self):
        """
        点击添加用户按钮
        """
        with allure.step("点击添加用户按钮"):
            status =  self.switch_to_user_info_management_window()
            if status:
                self.log.info("已切换到用户信息管理窗口")
            else:
                self.log.error("切换用户信息管理窗口失败")
                return False
            element_config = self._get_element_config('add_user_button')
            if element_config:
                return self.click_element(**element_config)
            return False

    def click_alter_user_button(self):
        """
        点击修改用户按钮
        """
        status = self.switch_to_user_info_management_window()
        if status:
            self.log.info("已切换到用户信息管理窗口")
        else:
            self.log.error("切换用户信息管理窗口失败")
            return False
        element_config = self._get_element_config('alter_user_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_delete_user_button(self):
        """
        点击删除用户按钮
        """
        status = self.switch_to_user_info_management_window()
        if status:
            self.log.info("已切换到用户信息管理窗口")
        else:
            self.log.error("切换用户信息管理窗口失败")
            return False
        element_config = self._get_element_config('delete_user_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_set_permission_button(self):
        """
        点击设置权限按钮
        """
        status = self.switch_to_user_info_management_window()
        if status:
            self.log.info("已切换到用户信息管理窗口")
        else:
            self.log.error("切换用户信息管理窗口失败")
            return False
        element_config = self._get_element_config('set_permission_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_reset_password_button(self):
        """
        点击重置密码按钮
        """
        status = self.switch_to_user_info_management_window()
        if status:
            self.log.info("已切换到用户信息管理窗口")
        else:
            self.log.error("切换用户信息管理窗口失败")
            return False
        element_config = self._get_element_config('reset_password_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    # 添加用户窗口相关方法
    def switch_to_add_user_window(self):
        """
        切换到添加用户信息窗口
        """
        window_config = self._get_element_config('add_user_window')
        if not window_config:
            self.log.error("add_user_window: 未找到窗口配置")
            return False

        # 同时使用 title 和 automation_id 进行匹配
        title = window_config.get('name', '添加用户信息')
        automation_id = window_config.get('automation_id')

        return self.switch_to_window(title=title, automation_id=automation_id)

    def set_user_name_edit(self, text):
        """
        在添加/修改用户窗口中输入用户名
        """
        element_config = self._get_element_config('user_name_edit')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def set_remark_edit(self, text):
        """
        在添加/修改用户窗口中输入备注
        """
        element_config = self._get_element_config('remark_edit')
        if element_config:
            return self.send_keys_to_element(text, **element_config)
        return False

    def click_add_window_add_button(self):
        """
        点击添加用户窗口中的添加按钮
        """
        element_config = self._get_element_config('add_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_add_window_cancel_button(self):
        """
        点击添加用户窗口中的取消按钮
        """
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_add_window_quit_button(self):
        """
        点击添加用户窗口中的退出按钮
        """
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    # 修改用户窗口相关方法
    def switch_to_alter_user_window(self):
        """
        切换到修改用户信息窗口
        """
        window_config = self._get_element_config('alter_user_window')
        if not window_config:
            self.log.error("alter_user_window: 未找到窗口配置")
            return False

        # 同时使用 title 和 automation_id 进行匹配
        title = window_config.get('name', '修改用户信息')
        automation_id = window_config.get('automation_id')

        return self.switch_to_window(title=title, automation_id=automation_id)

    def click_alter_window_alter_button(self):
        """
        点击修改用户窗口中的修改按钮
        """
        element_config = self._get_element_config('alter_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_window_cancel_button(self):
        """
        点击修改用户窗口中的取消按钮
        """
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_alter_window_quit_button(self):
        """
        点击修改用户窗口中的退出按钮
        """
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    # 确认窗口相关方法
    def switch_to_confirm_window(self):
        """
        切换到确认窗口（删除用户确认）
        """
        window_config = self._get_element_config('delete_user_window')
        if not window_config:
            self.log.error("delete_user_window: 未找到窗口配置")
            return False

        # 同时使用 title 和 automation_id 进行匹配
        title = window_config.get('name', '确认删除')
        automation_id = window_config.get('automation_id')

        return self.switch_to_window(title=title, automation_id=automation_id)

    def get_confirm_window_prompt_text(self):
        """
        获取确认窗口中的提示文本
        """
        element_config = self._get_element_config('prompt_text')
        if element_config:
            return self.get_element_text(**element_config)
        return None

    def click_confirm_window_confirm_button(self):
        """
        点击确认窗口中的确认按钮
        """
        element_config = self._get_element_config('confirm_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_confirm_window_cancel_button(self):
        """
        点击确认窗口中的取消按钮
        """
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_confirm_window_quit_button(self):
        """
        点击确认窗口中的退出按钮
        """
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    # 操作提示窗口相关方法（operation_window）
    # 注意：这些方法已移至 base_page.py 中，作为公共弹窗处理方法
    # 如需使用，直接调用继承自 base_page 的方法即可

    # 设置权限窗口相关方法
    def switch_to_set_permission_window(self):
        """
        切换到设置权限窗口
        """
        window_config = self._get_element_config('set_permission_window')
        if not window_config:
            self.log.error("set_permission_window: 未找到窗口配置")
            return False

        # 同时使用 title 和 automation_id 进行匹配
        title = window_config.get('name', '设置权限')
        automation_id = window_config.get('automation_id')

        return self.switch_to_window(title=title, automation_id=automation_id)

    def click_save_permission_button(self):
        """
        点击设置权限窗口中的保存按钮
        """
        element_config = self._get_element_config('save_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_set_permission_window_cancel_button(self):
        """
        点击设置权限窗口中的取消按钮
        """
        element_config = self._get_element_config('cancel_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def click_set_permission_window_quit_button(self):
        """
        点击设置权限窗口中的退出按钮
        """
        element_config = self._get_element_config('quit_button')
        if element_config:
            return self.click_element(**element_config)
        return False

    def check_permission_tree_with_space_key(self, node_names):
        """
        勾选设置权限窗口中的权限树节点（使用空格键方式）
        :param node_names: 想要勾选的节点名称列表
        :return: 勾选是否成功
        """
        # 切换到设置权限窗口
        if self.switch_to_set_permission_window():
            self.log.info("切换到设置权限窗体成功")
        else:
            self.log.error("切换到设置权限窗体失败")
            return False
        
        # 首先分析树控件结构，帮助诊断问题
        self.log.info("开始分析权限树控件结构...")
        tree_analysis = self.analyze_tree_structure(self._get_element_config('permission_tree'))
        
        if tree_analysis:
            self.log.info(f"权限树控件分析完成: {tree_analysis['tree_info']}")
            self.log.info(f"找到{tree_analysis['total_children']}个子元素")
        else:
            self.log.warning("权限树控件分析失败，继续尝试勾选操作")
        
        # 使用空格键方式勾选节点
        self.log.info(f"使用空格键方式勾选权限节点: {node_names}")
        return self.check_tree_nodes_with_space_key(self._get_element_config('permission_tree'), node_names)

    # 重置密码窗口相关方法
    # 注意：重置密码确认弹窗与公共的 operation_window 是同一个弹窗，直接使用公共方法
    def switch_to_reset_password_window(self):
        """
        切换到重置密码窗口（与 operation_window 同一弹窗）
        """
        return self.switch_to_operation_window()

    def get_reset_password_prompt_text(self):
        """
        获取重置密码窗口中的提示文本
        """
        return self.get_operation_window_prompt_text()

    def click_reset_password_confirm_button(self):
        """
        点击重置密码窗口中的确认按钮（是）
        """
        return self.click_operation_window_confirm_button()

    def click_reset_password_cancel_button(self):
        """
        点击重置密码窗口中的取消按钮（否）
        """
        return self.click_operation_window_cancel_button()

    def click_reset_password_quit_button(self):
        """
        点击重置密码窗口中的退出按钮
        """
        return self.click_operation_window_quit_button()

    # 消息提示窗口相关方法
    # 注意：直接使用 base_page.py 中的公共方法，无需重复定义
    # - switch_to_prompt_window() 继承自 base_page.py
    # - get_prompt_window_text() 继承自 base_page.py
    # - click_prompt_window_confirm_button() 继承自 base_page.py

    def switch_to_user_info_management_window(self):
        """
        切换到用户信息管理页面
        """
        # 切换到用户信息管理窗体
        self.log.info("切换到用户信息管理窗体")
        return self.switch_to_window(title=self.app_config['main_window_name'])
    # 表格操作方法
    def get_content_table(self):
        """
        获取用户信息管理页面内容表格
        """
        status = self.switch_to_user_info_management_window()
        if status:
            self.log.info("切换到用户信息管理窗体成功")
        else:
            self.log.error("切换到用户信息管理窗体失败")
            return None
        content_table = self._get_element_config('content_table')
        if content_table:
            self.log.info("获取用户信息管理窗口中的表格数据")
            #传入表头信息帮助定位
            head_keys = self.app_config['head_keys']
            return self.get_table_data_as_json(content_table,head_keys)
        return None

    def check_add_user_affiliated_system_tree_with_space_key(self, node_names):
        """
        使用空格键方式勾选树控件的节点（更可靠的方法）
        :param node_names: 想要勾选的节点名称列表
        :return: 勾选是否成功
        """
        # 切换到添加用户窗体
        if self.switch_to_add_user_window():
            self.log.info("切换到添加用户窗体成功")
        else:
            self.log.error("切换到添加用户窗体失败")
            return False
        
        # 首先分析树控件结构，帮助诊断问题
        self.log.info("开始分析树控件结构...")
        tree_analysis = self.analyze_tree_structure(self._get_element_config('affiliated_system_tree'))
        
        if tree_analysis:
            self.log.info(f"树控件分析完成: {tree_analysis['tree_info']}")
            self.log.info(f"找到{tree_analysis['total_children']}个子元素")
        else:
            self.log.warning("树控件分析失败，继续尝试勾选操作")
        
        # 使用空格键方式勾选节点
        self.log.info(f"使用空格键方式勾选节点: {node_names}")
        return self.check_tree_nodes_with_space_key(self._get_element_config('affiliated_system_tree'), node_names)

    def select_user_type(self, user_type):
        """
        选择用户类型下拉框中的选项（添加用户窗口）
        :param user_type: 要选择的用户类型（如"管理员"、"操作员"等）
        :return: 是否成功选择
        """
        # 注意：此处不重复切换窗口！
        # 调用方（Handler）已切换到添加用户窗口并填写了用户名，
        # 若这里再次调用 switch_to_add_user_window()，
        # Appium 遍历 window handles 的过程会触发文本框 LostFocus 事件，
        # 导致已输入的用户名被 WinForms 清空。
        self.log.info(f"开始选择用户类型: {user_type}")
        
        # 获取用户类型ComboBox的配置
        combobox_config = self._get_element_config('user_type_combo')
        if not combobox_config:
            self.log.error("未找到用户类型ComboBox的配置")
            return False
        
        # 使用基类的select_combobox_option方法
        success = self.select_combobox_option(user_type, **combobox_config)
        
        if success:
            self.log.info(f"成功选择用户类型: {user_type}")
        else:
            self.log.error(f"选择用户类型失败: {user_type}")
        
        return success

    def select_alter_user_type(self, user_type):
        """
        选择用户类型下拉框中的选项（修改用户窗口）
        :param user_type: 要选择的用户类型（如"管理员"、"普通用户"等）
        :return: 是否成功选择
        """
        #切换到修改用户窗口
        self.switch_to_alter_user_window()

        self.log.info(f"开始选择用户类型（修改窗口）: {user_type}")
        
        # 获取用户类型ComboBox的配置
        combobox_config = self._get_element_config('user_type_combo')
        if not combobox_config:
            self.log.error("未找到用户类型ComboBox的配置")
            return False
        
        # 使用基类的select_combobox_option方法
        success = self.select_combobox_option(user_type, **combobox_config)
        
        if success:
            self.log.info(f"成功选择用户类型（修改窗口）: {user_type}")
        else:
            self.log.error(f"选择用户类型失败（修改窗口）: {user_type}")
        
        return success

    #勾选tree控件方法
    def check_alter_user_affiliated_system_tree_with_space_key(self,node_names):
        """
        勾选tree控件的节点
        :param node_names: 想要勾选的节点名称列表
        :return:勾选是否成功
        """
        #切换到修改用户窗体
        if self.switch_to_alter_user_window():
            self.log.info("切换到修改用户窗体成功")
        else:
            self.log.error("切换到修改用户窗体失败")
            return False

        # 首先分析树控件结构，帮助诊断问题
        self.log.info("开始分析树控件结构...")
        tree_analysis = self.analyze_tree_structure(self._get_element_config('affiliated_system_tree'))

        if tree_analysis:
            self.log.info(f"树控件分析完成: {tree_analysis['tree_info']}")
            self.log.info(f"找到{tree_analysis['total_children']}个子元素")
        else:
            self.log.warning("树控件分析失败，继续尝试勾选操作")

        # 使用空格键方式勾选节点
        self.log.info(f"使用空格键方式勾选节点: {node_names}")
        return self.check_tree_nodes_with_space_key(self._get_element_config('affiliated_system_tree'), node_names)

    def click_table_one_row(self, search_criteria,match_mode="exact" ):
        """
        点击表格中的行
        :param search_criteria: 查询条件 {"用户名":"张三"}键值对格式
        :param match_mode: 匹配模式，可选值有"exact"（精确匹配）和"contains"（包含匹配）
        :return: 点击是否成功
        """
        content_table = self._get_element_config('content_table')
        header_keywords = self.app_config['head_keys']
        #一定要切换到对应的窗口，因为程序太多的table标签，否则会点击到其他窗口的table标签，并且获取到的数据有问题
        self.switch_to_user_info_management_window()
        return self.click_table_row(content_table, search_criteria, header_keywords,match_mode)

