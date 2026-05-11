"""
用户个人中心功能测试用例示例
演示如何使用超级工厂进行各种用户操作
"""

import sys
import os
# 添加项目根目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.super_handler_factory import create_handler
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_user_profile_operations():
    """测试用户个人中心各种操作"""

    # 使用超级工厂创建Handler（1行代码！）
    user_profile_handler = create_handler('user_profile_page')

    print("=" * 60)
    print("用户个人中心功能测试")
    print("=" * 60)

    # 测试1: 修改用户名
    print("\n1. 测试修改用户名功能")
    result = user_profile_handler.change_username_and_verify(
        old_password="123456",
        new_username="test_user_001",
        confirm_username="test_user_001",
        confirm=True
    )
    print(f"修改用户名结果: {result['success']}")
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ 错误: {result['error']}")

    # 测试2: 修改密码
    print("\n2. 测试修改密码功能")
    result = user_profile_handler.change_password_and_verify(
        old_password="123456",
        new_password="newpassword123",
        confirm_password="newpassword123",
        confirm=True
    )
    print(f"修改密码结果: {result['success']}")
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ 错误: {result['error']}")

    # 测试3: 退出登录
    print("\n3. 测试退出登录功能")
    result = user_profile_handler.handle_logout_prompt(
        confirm_logout=True
    )
    print(f"退出登录结果: {result['success']}")
    if result['success']:
        if result['logged_out']:
            print(f"✅ {result['message']}")
        else:
            print(f"ℹ️ {result['message']}")
    else:
        print(f"❌ 错误: {result['error']}")

    # 测试4: 切换用户
    print("\n4. 测试切换用户功能")
    result = user_profile_handler.handle_switch_user_prompt(
        confirm_switch=True
    )
    print(f"切换用户结果: {result['success']}")
    if result['success']:
        if result['switched']:
            print(f"✅ {result['message']}")
            print("ℹ️ 可以继续进行新用户登录操作")

            # 测试5: 重新登录（在切换用户后）
            print("\n5. 测试重新登录功能")
            result = user_profile_handler.navigate_to_user_login_page(
                username="test_user_002",
                password="123456"
            )
            print(f"重新登录结果: {result['success']}")
            if result['success']:
                if result['logged_in']:
                    print(f"✅ {result['message']}")
                else:
                    print(f"ℹ️ {result['message']}")
            else:
                print(f"❌ 错误: {result['error']}")
        else:
            print(f"ℹ️ {result['message']}")
    else:
        print(f"❌ 错误: {result['error']}")

def test_data_driven_scenarios():
    """数据驱动的测试场景"""
    print("\n" + "=" * 60)
    print("数据驱动测试场景")
    print("=" * 60)

    config_manager = ConfigManager()

    # 从配置文件加载测试数据
    user_profile_config = config_manager.load_page_config('user_profile_page')
    test_data = user_profile_config.get('test_data', {})

    # 执行修改用户名测试场景
    print("\n执行修改用户名测试场景:")
    for scenario_name, scenario_data in test_data.items():
        if scenario_name.startswith('change_username') and 'scenario' in scenario_name:
            print(f"\n场景: {scenario_data.get('_description')}")
            print(f"参数: 旧密码={scenario_data.get('old_password')}, 新用户名={scenario_data.get('new_username')}")

            # 这里可以调用UserProfileHandler进行实际测试
            # 为演示目的，只打印参数
            confirm_text = "确认" if scenario_data.get('confirm') else "取消"
            print(f"操作: {confirm_text}修改")

    # 执行切换用户测试场景
    print("\n执行切换用户测试场景:")
    for scenario_name, scenario_data in test_data.items():
        if scenario_name.startswith('switch_user'):
            print(f"\n场景: {scenario_data.get('_description')}")

            confirm_text = "确认" if scenario_data.get('confirm_switch') else "取消"
            print(f"操作: {confirm_text}切换用户")

if __name__ == "__main__":
    try:
        # 执行基本功能测试
        test_user_profile_operations()

        # 执行数据驱动测试场景
        test_data_driven_scenarios()

    except Exception as e:
        print(f"❌ 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)