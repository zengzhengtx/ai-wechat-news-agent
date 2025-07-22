"""
用户认证模块
提供登录验证和会话管理功能

Author: zengzhengtx
"""

import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

from src.utils.logger import get_logger


class UserManager:
    """用户管理类"""
    
    def __init__(self, users_file: str = "data/users.json"):
        self.users_file = users_file
        self.logger = get_logger()
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = 3600  # 1小时超时
        
        # 确保用户文件存在
        self._ensure_users_file()
        
        # 加载用户数据
        self.users = self._load_users()
    
    def _ensure_users_file(self):
        """确保用户文件存在"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        if not os.path.exists(self.users_file):
            # 创建默认管理员用户
            default_users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                }
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"创建默认用户文件: {self.users_file}")
            self.logger.info("默认管理员账户 - 用户名: admin, 密码: admin123")
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载用户文件失败: {e}")
            return {}
    
    def _save_users(self):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存用户文件失败: {e}")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = "wechat_agent_salt_2025"  # 固定盐值，实际应用中应该为每个用户生成随机盐
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == password_hash
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        用户认证
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 会话token)
        """
        if not username or not password:
            return False, None
        
        user = self.users.get(username)
        if not user:
            self.logger.warning(f"用户不存在: {username}")
            return False, None
        
        if not self._verify_password(password, user['password_hash']):
            self.logger.warning(f"密码错误: {username}")
            return False, None
        
        # 创建会话
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'username': username,
            'role': user.get('role', 'user'),
            'login_time': time.time(),
            'last_activity': time.time()
        }
        
        # 更新最后登录时间
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        self.logger.info(f"用户登录成功: {username}")
        return True, session_token
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证会话
        
        Args:
            session_token: 会话token
            
        Returns:
            Tuple[bool, Optional[Dict]]: (是否有效, 用户信息)
        """
        if not session_token or session_token not in self.sessions:
            return False, None
        
        session = self.sessions[session_token]
        current_time = time.time()
        
        # 检查会话是否超时
        if current_time - session['last_activity'] > self.session_timeout:
            del self.sessions[session_token]
            return False, None
        
        # 更新最后活动时间
        session['last_activity'] = current_time
        
        return True, session
    
    def logout(self, session_token: str) -> bool:
        """
        用户登出
        
        Args:
            session_token: 会话token
            
        Returns:
            bool: 是否成功
        """
        if session_token in self.sessions:
            username = self.sessions[session_token]['username']
            del self.sessions[session_token]
            self.logger.info(f"用户登出: {username}")
            return True
        return False
    
    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        """
        添加用户
        
        Args:
            username: 用户名
            password: 密码
            role: 角色
            
        Returns:
            bool: 是否成功
        """
        if username in self.users:
            return False
        
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users()
        self.logger.info(f"添加用户: {username}, 角色: {role}")
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        修改密码
        
        Args:
            username: 用户名
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 是否成功
        """
        user = self.users.get(username)
        if not user:
            return False
        
        if not self._verify_password(old_password, user['password_hash']):
            return False
        
        user['password_hash'] = self._hash_password(new_password)
        self._save_users()
        
        self.logger.info(f"用户修改密码: {username}")
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Optional[Dict]: 用户信息
        """
        user = self.users.get(username)
        if user:
            # 返回安全的用户信息（不包含密码哈希）
            return {
                'username': username,
                'role': user.get('role', 'user'),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
        return None
    
    def list_users(self) -> list:
        """
        列出所有用户
        
        Returns:
            list: 用户列表
        """
        users = []
        for username, user_data in self.users.items():
            users.append({
                'username': username,
                'role': user_data.get('role', 'user'),
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login')
            })
        return users
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        current_time = time.time()
        expired_tokens = []
        
        for token, session in self.sessions.items():
            if current_time - session['last_activity'] > self.session_timeout:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.sessions[token]
        
        if expired_tokens:
            self.logger.info(f"清理过期会话: {len(expired_tokens)}个")
