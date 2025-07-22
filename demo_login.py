#!/usr/bin/env python3
"""
登录系统演示脚本
展示用户认证功能

Author: zengzhengtx
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.auth.authentication import UserManager
from src.utils.logger import init_logging


def demo_user_management():
    """演示用户管理功能"""
    print("🚀 用户管理系统演示")
    print("=" * 50)
    
    # 初始化日志和用户管理器
    logger = init_logging()
    user_manager = UserManager()
    
    print("\n1. 📋 当前用户列表:")
    users = user_manager.list_users()
    for user in users:
        print(f"   👤 {user['username']} ({user['role']}) - 创建于: {user['created_at']}")
    
    print("\n2. 🔐 测试用户认证:")
    
    # 测试正确的登录
    print("   测试管理员登录...")
    success, token = user_manager.authenticate("admin", "admin123")
    if success:
        print(f"   ✅ 登录成功，会话token: {token[:20]}...")
        
        # 验证会话
        valid, session_info = user_manager.validate_session(token)
        if valid:
            print(f"   ✅ 会话有效，用户: {session_info['username']}")
        
        # 登出
        user_manager.logout(token)
        print("   ✅ 登出成功")
    else:
        print("   ❌ 登录失败")
    
    # 测试错误的登录
    print("   测试错误密码...")
    success, token = user_manager.authenticate("admin", "wrong_password")
    if success:
        print("   ❌ 不应该登录成功")
    else:
        print("   ✅ 正确拒绝了错误密码")
    
    print("\n3. 👥 添加新用户:")
    if user_manager.add_user("testuser", "testpass", "user"):
        print("   ✅ 添加用户 testuser 成功")
        
        # 测试新用户登录
        success, token = user_manager.authenticate("testuser", "testpass")
        if success:
            print("   ✅ 新用户登录成功")
            user_manager.logout(token)
        else:
            print("   ❌ 新用户登录失败")
    else:
        print("   ❌ 添加用户失败（可能已存在）")
    
    print("\n4. 🔑 修改密码:")
    if user_manager.change_password("testuser", "testpass", "newpass123"):
        print("   ✅ 密码修改成功")
        
        # 测试新密码
        success, token = user_manager.authenticate("testuser", "newpass123")
        if success:
            print("   ✅ 新密码登录成功")
            user_manager.logout(token)
        else:
            print("   ❌ 新密码登录失败")
    else:
        print("   ❌ 密码修改失败")
    
    print("\n5. 📊 最终用户列表:")
    users = user_manager.list_users()
    for user in users:
        print(f"   👤 {user['username']} ({user['role']}) - 最后登录: {user['last_login'] or '从未登录'}")
    
    print("\n✅ 用户管理系统演示完成！")


def demo_session_management():
    """演示会话管理功能"""
    print("\n🔄 会话管理演示")
    print("=" * 50)
    
    user_manager = UserManager()
    
    # 创建多个会话
    print("\n1. 创建多个会话:")
    sessions = []
    
    for i in range(3):
        success, token = user_manager.authenticate("admin", "admin123")
        if success:
            sessions.append(token)
            print(f"   ✅ 会话 {i+1} 创建成功: {token[:20]}...")
    
    print(f"\n2. 当前活跃会话数: {len(user_manager.sessions)}")
    
    # 验证所有会话
    print("\n3. 验证会话:")
    for i, token in enumerate(sessions):
        valid, session_info = user_manager.validate_session(token)
        if valid:
            print(f"   ✅ 会话 {i+1} 有效")
        else:
            print(f"   ❌ 会话 {i+1} 无效")
    
    # 登出部分会话
    print("\n4. 登出部分会话:")
    for i in range(2):
        user_manager.logout(sessions[i])
        print(f"   ✅ 会话 {i+1} 已登出")
    
    print(f"\n5. 剩余活跃会话数: {len(user_manager.sessions)}")
    
    # 清理过期会话
    print("\n6. 清理过期会话:")
    user_manager.cleanup_expired_sessions()
    print(f"   清理后活跃会话数: {len(user_manager.sessions)}")


def main():
    """主函数"""
    print("🤖 AI资讯智能体 - 登录系统演示")
    print("Author: zengzhengtx")
    print("=" * 60)
    
    try:
        # 演示用户管理
        demo_user_management()
        
        # 演示会话管理
        demo_session_management()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 提示:")
        print("   - 用户数据保存在 data/users.json")
        print("   - 默认管理员账户: admin / admin123")
        print("   - 可以运行 python app_with_auth.py 启动带登录的Web界面")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
