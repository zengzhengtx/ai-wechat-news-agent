# 登录系统使用指南

## 概述

AI资讯微信公众号智能体现在支持完整的用户认证和权限管理系统，确保只有授权用户才能访问系统功能。

**作者**: zengzhengtx

## 功能特性

### 🔐 用户认证
- 用户名/密码登录
- 安全的密码哈希存储
- 会话管理和超时控制
- 自动登出功能

### 👥 用户管理
- 多用户支持
- 角色权限管理（admin/user）
- 用户添加和删除
- 密码修改功能

### 🛡️安全特性
- 密码哈希加密存储
- 会话token安全管理
- 自动清理过期会话
- 登录失败日志记录

## 快速开始

### 1. 启动带认证的Web界面

```bash
python app_with_auth.py
```

默认访问地址：http://127.0.0.1:7862

### 2. 默认管理员账户

- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **重要**: 首次登录后请立即修改默认密码！

### 3. 登录流程

1. 打开Web界面
2. 输入用户名和密码
3. 点击"登录"按钮
4. 成功后自动跳转到主界面

## 用户管理

### 添加新用户

1. 以管理员身份登录
2. 进入"用户管理"标签页
3. 填写新用户信息：
   - 用户名
   - 密码
   - 角色（user/admin）
4. 点击"添加用户"

### 修改密码

#### 方法1：通过Web界面
1. 登录系统
2. 进入"用户管理"标签页
3. 在"修改密码"部分填写信息
4. 点击"修改密码"

#### 方法2：通过代码
```python
from src.auth.authentication import UserManager

user_manager = UserManager()
success = user_manager.change_password("username", "old_password", "new_password")
```

### 查看用户列表

1. 进入"用户管理"标签页
2. 点击"刷新用户列表"
3. 查看所有用户的信息：
   - 用户名
   - 角色
   - 创建时间
   - 最后登录时间

## 权限管理

### 角色说明

#### Admin（管理员）
- 访问所有功能
- 用户管理权限
- 系统配置权限
- 数据库管理权限

#### User（普通用户）
- 访问基本功能
- 文章格式化
- 内容筛选
- 查看统计信息

### 权限控制

系统通过会话验证实现权限控制：

```python
# 验证用户会话
valid, session_info = user_manager.validate_session(session_token)
if valid:
    user_role = session_info['role']
    # 根据角色控制访问权限
```

## 安全配置

### 会话超时

默认会话超时时间：1小时（3600秒）

可以在 `UserManager` 初始化时修改：

```python
user_manager = UserManager()
user_manager.session_timeout = 7200  # 2小时
```

### 密码安全

- 使用SHA-256哈希算法
- 添加固定盐值防止彩虹表攻击
- 建议使用强密码（8位以上，包含字母数字特殊字符）

### 数据存储

用户数据存储在 `data/users.json` 文件中：

```json
{
  "admin": {
    "password_hash": "hashed_password",
    "role": "admin",
    "created_at": "2025-01-16T10:30:00",
    "last_login": "2025-01-16T11:00:00"
  }
}
```

## 命令行工具

### 演示登录系统

```bash
python demo_login.py
```

这个脚本会演示：
- 用户认证功能
- 会话管理
- 用户添加
- 密码修改

### 启动不同版本的应用

```bash
# 带认证的完整版本
python app_with_auth.py

# 简化版本（无认证）
python simple_web_fixed.py

# 稳定演示版本
python stable_demo.py
```

## 故障排除

### 常见问题

**Q: 忘记管理员密码怎么办？**
A: 删除 `data/users.json` 文件，重启应用会自动创建默认管理员账户。

**Q: 登录后页面没有跳转？**
A: 检查浏览器控制台是否有JavaScript错误，尝试刷新页面。

**Q: 会话经常超时？**
A: 可以增加 `session_timeout` 值，或者实现自动续期功能。

**Q: 如何备份用户数据？**
A: 备份 `data/users.json` 文件即可。

### 日志查看

系统日志保存在 `logs/app.log`，包含：
- 用户登录/登出记录
- 认证失败记录
- 会话管理操作
- 错误信息

```bash
# 查看最新日志
tail -f logs/app.log

# 搜索登录相关日志
grep "登录" logs/app.log
```

## 开发扩展

### 添加新的认证方式

可以扩展 `UserManager` 类支持其他认证方式：

```python
class UserManager:
    def authenticate_with_token(self, api_token):
        # 实现API token认证
        pass
    
    def authenticate_with_oauth(self, oauth_token):
        # 实现OAuth认证
        pass
```

### 自定义权限检查

```python
def require_admin(func):
    """装饰器：要求管理员权限"""
    def wrapper(session_token, *args, **kwargs):
        valid, session_info = user_manager.validate_session(session_token)
        if not valid or session_info['role'] != 'admin':
            raise PermissionError("需要管理员权限")
        return func(*args, **kwargs)
    return wrapper
```

### 集成外部认证系统

可以修改 `authenticate` 方法集成LDAP、OAuth等外部认证：

```python
def authenticate(self, username, password):
    # 先尝试本地认证
    if self._local_authenticate(username, password):
        return True, self._create_session(username)
    
    # 再尝试LDAP认证
    if self._ldap_authenticate(username, password):
        return True, self._create_session(username)
    
    return False, None
```

## 最佳实践

1. **定期更改密码**：建议每3个月更换一次密码
2. **使用强密码**：至少8位，包含大小写字母、数字和特殊字符
3. **及时登出**：使用完毕后及时登出系统
4. **监控日志**：定期检查登录日志，发现异常及时处理
5. **备份数据**：定期备份用户数据和配置文件

## 联系支持

如有问题或建议，请联系：
- GitHub: [@zengzhengtx](https://github.com/zengzhengtx)
- 项目地址: [https://github.com/zengzhengtx/wechatAgent](https://github.com/zengzhengtx/wechatAgent)
