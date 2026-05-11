"""
用户个人中心Handler - 业务逻辑处理
组合页面操作实现复杂的个人信息修改业务逻辑
"""

import logging
import time
import allure

from handlers.base_handler import BaseHandler
from handlers.navigation_mixin import NavigationMixin
from handlers.login_handler import LoginHandler


class UserProfileHandler(BaseHandler, NavigationMixin):
    """
    用户个人中心Handler - 业务逻辑处理类
    职责：封装用户名修改和密码修改的完整业务流程
    """

    def __init__(self, page_instance=None, config_manager=None):
        """
        初始化用户个人中心处理器

        Args:
            page_instance: 用户资料页面对象（可为None或类）
            config_manager: 配置管理器
        """
        super().__init__(page_instance, config_manager)
        # 初始化NavigationMixin
        NavigationMixin.__init__(self)

        # 赋值页面对象
        self.user_profile_page = self.page_instance

        # 获取成功消息配置
        self.success_messages = self.config_manager.load_page_config('user_profile_page').get('app_config', {}).get(
            'success_messages', {})

        logging.info("用户个人中心处理器初始化完成（集成导航功能）")

    def _create_page_instance(self, config_manager):
        """
        创建用户个人中心页面对象实例

        Args:
            config_manager: 配置管理器

        Returns:
            UserProfilePage: 用户个人中心页面对象实例
        """
        from pageObject.user.userProfile.user_profile_page import UserProfilePage
        from utils.driver_factory import DriverFactory

        # 获取驱动实例
        driver = DriverFactory.get_windows_driver()
        if driver is None:
            raise Exception("无法获取Windows驱动实例")

        # 创建用户个人中心页面对象
        return UserProfilePage(driver, config_manager)

    def _ensure_pages(self):
        """确保页面对象已正确初始化（惰性初始化）"""
        try:
            # 确保页面对象可用
            if self.user_profile_page is None:
                raise Exception("用户资料页面对象未初始化")

            # 确保驱动可用
            if not hasattr(self.user_profile_page, 'driver') or self.user_profile_page.driver is None:
                raise Exception("页面驱动未初始化")

            self.log.info("页面对象初始化检查通过")
        except Exception as e:
            self.log.error(f"页面初始化失败: {e}")
            raise

    def _handle_prompt_window_and_verify(self, expected_message_key: str, timeout: float = 5.0) -> dict:
        """
        处理提示弹窗并验证消息内容

        Args:
            expected_message_key: 期望的消息键名（如'change_username'或'change_password'）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'error': str
            }
        """
        try:
            # 等待提示窗口出现
            time.sleep(1.0)  # 等待弹窗出现

            # 切换到消息提示窗口
            if self.user_profile_page.switch_to_prompt_window():
                # 获取提示文本
                prompt_text = self.user_profile_page.get_prompt_window_text()
                self.log.info(f"获取到提示文本: {prompt_text}")

                # 获取期望的成功消息
                expected_message = self.success_messages.get(expected_message_key, "")
                self.log.info(f"期望的成功消息: {expected_message}")

                # 验证消息是否包含期望内容
                if expected_message and expected_message in prompt_text:
                    self.log.info(f"✅ 操作成功验证通过: {prompt_text}")
                    # 点击确认按钮关闭提示窗口
                    self.user_profile_page.click_prompt_window_confirm_button()
                    return {
                        'success': True,
                        'message': prompt_text,
                        'error': None
                    }
                else:
                    error_msg = f"操作结果不符合预期，期望包含: {expected_message}，实际: {prompt_text}"
                    self.log.error(f"❌ {error_msg}")
                    self.user_profile_page.click_prompt_window_confirm_button()
                    return {
                        'success': False,
                        'message': prompt_text,
                        'error': error_msg
                    }
            else:
                error_msg = "提示窗口未出现或切换失败"
                self.log.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': None,
                    'error': error_msg
                }

        except Exception as e:
            error_msg = f"处理提示弹窗时发生异常: {str(e)}"
            self.log.error(f"❌ {error_msg}")
            return {
                'success': False,
                'message': None,
                'error': error_msg
            }

    def change_username_and_verify(self, old_password: str, new_username: str,
                                   confirm_username: str, confirm: bool = True,
                                   timeout: float = 5.0) -> dict:
        """
        修改用户名并验证结果

        Args:
            old_password: 旧密码（用于验证身份）
            new_username: 新用户名
            confirm_username: 确认新用户名
            confirm: 是否确认修改（True为确认，False为取消）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,              # 是否成功
                'message': str,               # 操作结果消息
                'error': str,                 # 错误信息
                'steps_completed': list        # 完成的操作步骤
            }
        """
        with allure.step(f"修改用户名并验证 (新用户名: {new_username})"):
            steps_completed = []

            try:
                self.log.info(f"开始修改用户名操作")
                self.log.info(
                    f"参数 - 旧密码: {old_password}, 新用户名: {new_username}, 确认用户名: {confirm_username}, 确认操作: {confirm}")

                # 步骤0: 检查是否在主页面
                with allure.step("检查当前页面状态"):
                    if not self.is_main_page_present():
                        return {
                            'success': False,
                            'message': None,
                            'error': '当前不在主页面，无法执行修改用户名操作',
                            'steps_completed': steps_completed
                        }

                # 步骤1: 导航到修改用户名页面
                with allure.step("导航到修改用户名页面"):
                    if self.navigate_to_username_change():
                        steps_completed.append("✓ 成功导航到修改用户名页面")
                        self.log.info("成功导航到修改用户名页面")

                        # 初始化页面对象（如果还没有初始化）
                        self._ensure_pages()

                        # 步骤1: 切换到修改用户名窗口
                        if self.user_profile_page.switch_to_alter_username_window():
                            steps_completed.append("✓ 成功切换到修改用户名窗口")
                            self.log.info("成功切换到修改用户名窗口")
                        else:
                            return {
                                'success': False,
                                'message': None,
                                'error': '切换到修改用户名窗口失败',
                                'steps_completed': steps_completed
                            }

                        # 步骤2: 输入旧密码
                        if self.user_profile_page.set_alter_username_old_password(old_password):
                            steps_completed.append("✓ 成功输入旧密码")
                            self.log.info("成功输入旧密码")
                        else:
                            return {
                                'success': False,
                                'message': None,
                                'error': '输入旧密码失败',
                                'steps_completed': steps_completed
                            }

                        # 步骤3: 输入新用户名
                        if self.user_profile_page.set_alter_username_new_username(new_username):
                            steps_completed.append("✓ 成功输入新用户名")
                            self.log.info("成功输入新用户名")
                        else:
                            return {
                                'success': False,
                                'message': None,
                                'error': '输入新用户名失败',
                                'steps_completed': steps_completed
                            }

                        # 步骤4: 输入确认新用户名
                        if self.user_profile_page.set_alter_username_confirm_username(confirm_username):
                            steps_completed.append("✓ 成功输入确认用户名")
                            self.log.info("成功输入确认用户名")
                        else:
                            return {
                                'success': False,
                                'message': None,
                                'error': '输入确认用户名失败',
                                'steps_completed': steps_completed
                            }

                        # 步骤5: 点击保存按钮
                        if self.user_profile_page.click_alter_username_save_button():
                            steps_completed.append("✓ 成功点击保存按钮")
                            self.log.info("成功点击保存按钮")
                        else:
                            return {
                                'success': False,
                                'message': None,
                                'error': '点击保存按钮失败',
                                'steps_completed': steps_completed
                            }

                        # 步骤6: 处理操作结果
                        if confirm:
                            # 确认操作，等待处理结果
                            time.sleep(2.0)  # 等待系统处理
                            result = self._handle_prompt_window_and_verify('change_username', timeout)
                        else:
                            # 取消操作，点击取消按钮
                            if self.user_profile_page.click_alter_username_cancel_button():
                                steps_completed.append("✓ 成功点击取消按钮")
                                self.log.info("成功取消修改用户名操作")
                                return {
                                    'success': True,
                                    'message': '用户名修改操作已取消',
                                    'error': None,
                                    'steps_completed': steps_completed
                                }
                            else:
                                return {
                                    'success': False,
                                    'message': None,
                                    'error': '点击取消按钮失败',
                                    'steps_completed': steps_completed
                                }

                        # 合并步骤信息
                        if 'steps_completed' not in result:
                            result['steps_completed'] = steps_completed

                        return result
                    else:
                        return {
                            'success': False,
                            'message': None,
                            'error': '导航到修改用户名页面失败',
                            'steps_completed': steps_completed
                        }

            except Exception as e:
                error_msg = f"修改用户名操作异常: {str(e)}"
                self.log.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': None,
                    'error': error_msg,
                    'steps_completed': []
                }

    def change_password_and_verify(self, old_password: str, new_password: str,
                                   confirm_password: str, confirm: bool = True,
                                   timeout: float = 5.0) -> dict:
        """
        修改密码并验证结果

        Args:
            old_password: 旧密码
            new_password: 新密码
            confirm_password: 确认新密码
            confirm: 是否确认修改（True为确认，False为取消）
            timeout: 超时时间

        Returns:
            dict: {
                'success': bool,              # 是否成功
                'message': str,               # 操作结果消息
                'error': str,                 # 错误信息
                'steps_completed': list        # 完成的操作步骤
            }
        """
        with allure.step("修改密码并验证"):
            steps_completed = []

            try:
                self.log.info(f"开始修改密码操作")
                self.log.info(
                    f"参数 - 旧密码: {old_password}, 新密码: {new_password}, 确认密码: {confirm_password}, 确认操作: {confirm}")

                # 步骤1: 导航到修改密码页面
                if self.navigate_to_password_change():
                    steps_completed.append("✓ 成功导航到修改密码页面")
                    self.log.info("成功导航到修改密码页面")

                    # 初始化页面对象（如果还没有初始化）
                    self._ensure_pages()
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '导航到修改密码页面失败',
                        'steps_completed': steps_completed
                    }

                # 步骤1: 切换到修改密码窗口
                if self.user_profile_page.switch_to_alter_password_window():
                    steps_completed.append("✓ 成功切换到修改密码窗口")
                    self.log.info("成功切换到修改密码窗口")
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '切换到修改密码窗口失败',
                        'steps_completed': steps_completed
                    }

                # 步骤2: 输入旧密码
                if self.user_profile_page.set_alter_password_old_password(old_password):
                    steps_completed.append("✓ 成功输入旧密码")
                    self.log.info("成功输入旧密码")
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '输入旧密码失败',
                        'steps_completed': steps_completed
                    }

                # 步骤3: 输入新密码
                if self.user_profile_page.set_alter_password_new_password(new_password):
                    steps_completed.append("✓ 成功输入新密码")
                    self.log.info("成功输入新密码")
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '输入新密码失败',
                        'steps_completed': steps_completed
                    }

                # 步骤4: 输入确认新密码
                if self.user_profile_page.set_alter_password_confirm_password(confirm_password):
                    steps_completed.append("✓ 成功输入确认密码")
                    self.log.info("成功输入确认密码")
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '输入确认密码失败',
                        'steps_completed': steps_completed
                    }

                # 步骤5: 点击保存按钮
                if self.user_profile_page.click_alter_password_save_button():
                    steps_completed.append("✓ 成功点击保存按钮")
                    self.log.info("成功点击保存按钮")
                else:
                    return {
                        'success': False,
                        'message': None,
                        'error': '点击保存按钮失败',
                        'steps_completed': steps_completed
                    }

                # 步骤6: 处理操作结果
                if confirm:
                    # 确认操作，等待处理结果
                    time.sleep(2.0)  # 等待系统处理
                    result = self._handle_prompt_window_and_verify('change_password', timeout)
                else:
                    # 取消操作，点击取消按钮
                    if self.user_profile_page.click_alter_password_cancel_button():
                        steps_completed.append("✓ 成功点击取消按钮")
                        self.log.info("成功取消修改密码操作")
                        return {
                            'success': True,
                            'message': '密码修改操作已取消',
                            'error': None,
                            'steps_completed': steps_completed
                        }
                    else:
                        return {
                            'success': False,
                            'message': None,
                            'error': '点击取消按钮失败',
                            'steps_completed': steps_completed
                        }

                # 合并步骤信息
                if 'steps_completed' not in result:
                    result['steps_completed'] = steps_completed

                return result

            except Exception as e:
                error_msg = f"修改密码操作异常: {str(e)}"
                self.log.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': None,
                    'error': error_msg,
                    'steps_completed': steps_completed
                }


def handle_logout_prompt(self, confirm_logout: bool = True, timeout: float = 5.0) -> dict:
    """
    处理退出登录操作提示弹窗

    Args:
        confirm_logout: 是否确认退出登录（True为确认退出，False为取消退出）
        timeout: 超时时间

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'error': str,
            'logged_out': bool  # 是否真的退出了登录
        }
    """
    try:
        self.log.info(f"开始处理退出登录操作，确认退出: {confirm_logout}")
        # 导航到退出登录页面
        self.navigate_to_user_logout()

        # 等待退出提示窗口出现
        time.sleep(1.0)

        # 切换到提示窗口
        if self.user_profile_page.switch_to_prompt_window():
            prompt_text = self.user_profile_page.get_prompt_window_text()
            self.log.info(f"获取到退出提示文本: {prompt_text}")

            # 根据提示文本判断操作类型
            if "退出登录" in prompt_text:
                # 这是退出登录的确认提示
                if confirm_logout:
                    # 确认退出 - 点击确认按钮
                    if self.user_profile_page.click_prompt_window_confirm_button():
                        self.log.info("✅ 确认退出登录，点击确认按钮")
                        time.sleep(2.0)  # 等待系统处理
                        return {
                            'success': True,
                            'message': f"已确认退出登录: {prompt_text}",
                            'error': None,
                            'logged_out': True  # 真的退出了登录
                        }
                    else:
                        return {
                            'success': False,
                            'message': None,
                            'error': '点击确认按钮失败',
                            'logged_out': False
                        }
                else:
                    # 取消退出 - 点击取消或关闭按钮
                    if self.user_profile_page.click_prompt_window_confirm_button() or self.user_profile_page.click_prompt_window_cancel_button():
                        self.log.info("✅ 取消退出登录")
                        return {
                            'success': True,
                            'message': f"已取消退出登录: {prompt_text}",
                            'error': None,
                            'logged_out': False  # 没有真的退出
                        }
                    else:
                        return {
                            'success': False,
                            'message': None,
                            'error': '无法处理退出提示窗口',
                            'logged_out': False
                        }
            else:
                error_msg = f"未知提示窗口内容: {prompt_text}"
                self.log.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': prompt_text,
                    'error': error_msg,
                    'logged_out': False
                }
        else:
            return {
                'success': False,
                'message': "未知提示窗口内容",
                'error': '未知提示窗口内容',
                'logged_out': False
            }

    except Exception as e:
        error_msg = f"处理退出登录操作异常: {str(e)}"
        self.log.error(f"❌ {error_msg}")
        return {
            'success': False,
            'message': None,
            'error': error_msg,
            'logged_out': False
        }


def handle_switch_user_prompt(self, confirm_switch: bool = True, timeout: float = 5.0) -> dict:
    """
    处理切换用户操作提示弹窗

    切换用户的完整流程：
    1. 导航到退出登录页面
    2. 确认退出登录
    3. 导航到用户登录页面
    4. 复用登录逻辑进行登录（此步骤由调用方处理）

    Args:
        confirm_switch: 是否确认切换用户（True为确认切换，False为取消切换）
        timeout: 超时时间

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'error': str,
            'switched': bool  # 是否真的切换了用户
        }
    """
    try:
        self.log.info(f"开始处理切换用户操作，确认切换: {confirm_switch}")

        # 按照用户要求，切换用户是先导航到退出登录页面进行退出
        # 步骤1: 导航到退出登录页面
        if self.navigate_to_user_logout():
            self.log.info("✓ 成功导航到退出登录页面")
        else:
            return {
                'success': False,
                'message': None,
                'error': '导航到退出登录页面失败',
                'switched': False
            }

        # 步骤2: 处理退出登录确认弹窗
        if confirm_switch:
            # 等待退出提示窗口出现
            time.sleep(1.0)

            # 切换到提示窗口
            if self.user_profile_page.switch_to_prompt_window():
                prompt_text = self.user_profile_page.get_prompt_window_text()
                self.log.info(f"获取到退出提示文本: {prompt_text}")

                if "退出登录" in prompt_text:
                    # 确认退出 - 点击确认按钮
                    if self.user_profile_page.click_prompt_window_confirm_button():
                        self.log.info("✅ 确认退出登录，点击确认按钮")
                        time.sleep(2.0)  # 等待系统处理

                        # 步骤3: 导航到用户登录页面，为登录做准备
                        if self.navigate_to_user_login():
                            self.log.info("✅ 已导航到用户登录页面，可以进行登录")
                            return {
                                'success': True,
                                'message': f"已退出登录并导航到登录页面: {prompt_text}",
                                'error': None,
                                'switched': True  # 可以进行切换登录
                            }
                        else:
                            return {
                                'success': False,
                                'message': f"已退出登录但导航到登录页面失败: {prompt_text}",
                                'error': '导航到用户登录页面失败',
                                'switched': False
                            }
                    else:
                        return {
                            'success': False,
                            'message': None,
                            'error': '点击退出确认按钮失败',
                            'switched': False
                        }
                else:
                    error_msg = f"未知提示窗口内容: {prompt_text}"
                    self.log.error(f"❌ {error_msg}")
                    return {
                        'success': False,
                        'message': prompt_text,
                        'error': error_msg,
                        'switched': False
                    }
            else:
                error_msg = "退出登录提示窗口未出现或切换失败"
                self.log.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': None,
                    'error': error_msg,
                    'switched': False
                }
        else:
            # 取消切换用户 - 直接返回成功，但标记为未切换
            self.log.info("✅ 取消切换用户操作")
            return {
                'success': True,
                'message': '已取消切换用户操作',
                'error': None,
                'switched': False  # 没有真的切换用户
            }

    except Exception as e:
        error_msg = f"处理切换用户操作异常: {str(e)}"
        self.log.error(f"❌ {error_msg}")
        return {
            'success': False,
            'message': None,
            'error': error_msg,
            'switched': False
        }


def navigate_to_user_login_page(self, username=None, password=None) -> dict:
    """
    导航到用户登录页面并执行登录（在退出登录后使用）

    Args:
        username: 用户名（可选，如果不提供则只导航不登录）
        password: 密码（可选，如果不提供则只导航不登录）

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'error': str,
            'logged_in': bool  # 是否成功登录
        }
    """
    try:
        self.log.info("开始导航到用户登录页面")

        # 通过main_handler导航到用户登录子菜单
        if self.navigate_to_user_login():
            self.log.info("✅ 成功导航到用户登录页面")

            # 如果提供了用户名和密码，执行登录操作
            if username and password:
                self.log.info(f"开始执行登录操作，用户名: {username}")
                # 创建LoginHandler实例
                login_handler = LoginHandler(config_manager=self.config_manager)

                # 执行登录
                if login_handler.login(username, password):
                    self.log.info("✅ 登录成功")
                    return {
                        'success': True,
                        'message': f'成功导航到登录页面并登录用户: {username}',
                        'error': None,
                        'logged_in': True
                    }
                else:
                    self.log.error("❌ 登录失败")
                    return {
                        'success': False,
                        'message': '导航成功但登录失败',
                        'error': '用户名或密码错误',
                        'logged_in': False
                    }
            else:
                # 只导航不登录
                return {
                    'success': True,
                    'message': '成功导航到用户登录页面',
                    'error': None,
                    'logged_in': False
                }
        else:
            self.log.error("❌ 导航到用户登录页面失败")
            return {
                'success': False,
                'message': None,
                'error': '导航到用户登录页面失败',
                'logged_in': False
            }

    except Exception as e:
        self.log.error(f"导航到用户登录页面失败: {str(e)}")
        return {
            'success': False,
            'message': None,
            'error': f'导航到用户登录页面异常: {str(e)}',
            'logged_in': False
        }
