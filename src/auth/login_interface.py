"""
登录界面模块
提供基于Gradio的登录界面

Author: zengzhengtx
"""

import gradio as gr
from typing import Tuple, Optional, Any
import time

from src.auth.authentication import UserManager
from src.utils.logger import get_logger


class LoginInterface:
    """登录界面类"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.logger = get_logger()
        self.current_session = None
        
        # 定期清理过期会话
        self.user_manager.cleanup_expired_sessions()
    
    def create_login_interface(self) -> gr.Blocks:
        """
        创建登录界面
        
        Returns:
            gr.Blocks: Gradio登录界面
        """
        with gr.Blocks(
            title="AI资讯智能体 - 登录",
            theme=gr.themes.Soft(),
            css="""
            .login-container {
                max-width: 400px;
                margin: 50px auto;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .login-title {
                text-align: center;
                margin-bottom: 30px;
                color: #2c3e50;
            }
            .login-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            """
        ) as login_app:
            
            with gr.Column(elem_classes="login-container"):
                gr.Markdown(
                    "# 🤖 AI资讯智能体\n## 用户登录",
                    elem_classes="login-title"
                )
                
                with gr.Column(elem_classes="login-form"):
                    username_input = gr.Textbox(
                        label="用户名",
                        placeholder="请输入用户名",
                        max_lines=1
                    )
                    
                    password_input = gr.Textbox(
                        label="密码",
                        placeholder="请输入密码",
                        type="password",
                        max_lines=1
                    )
                    
                    login_btn = gr.Button(
                        "登录",
                        variant="primary",
                        size="lg"
                    )
                    
                    login_status = gr.Markdown(
                        "",
                        visible=False
                    )
                    
                    # 默认账户提示
                    gr.Markdown(
                        """
                        ---
                        **默认管理员账户**  
                        用户名: `admin`  
                        密码: `admin123`
                        
                        ⚠️ **安全提示**: 首次登录后请立即修改默认密码
                        """,
                        elem_classes="default-account-info"
                    )
            
            # 绑定登录事件
            login_btn.click(
                fn=self._handle_login,
                inputs=[username_input, password_input],
                outputs=[login_status]
            )
            
            # 回车键登录
            username_input.submit(
                fn=self._handle_login,
                inputs=[username_input, password_input],
                outputs=[login_status]
            )
            
            password_input.submit(
                fn=self._handle_login,
                inputs=[username_input, password_input],
                outputs=[login_status]
            )
        
        return login_app
    
    def _handle_login(self, username: str, password: str) -> gr.Markdown:
        """
        处理登录请求
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            gr.Markdown: 登录状态信息
        """
        if not username or not password:
            return gr.Markdown(
                "❌ 请输入用户名和密码",
                visible=True
            )
        
        # 尝试认证
        success, session_token = self.user_manager.authenticate(username, password)
        
        if success:
            self.current_session = session_token
            self.logger.info(f"用户 {username} 登录成功")
            
            return gr.Markdown(
                f"✅ 登录成功！欢迎 {username}",
                visible=True
            )
        else:
            return gr.Markdown(
                "❌ 用户名或密码错误",
                visible=True
            )
    
    def create_protected_interface(self, main_interface_func) -> gr.Blocks:
        """
        创建受保护的界面
        
        Args:
            main_interface_func: 主界面创建函数
            
        Returns:
            gr.Blocks: 受保护的界面
        """
        with gr.Blocks(title="AI资讯智能体") as protected_app:
            
            # 会话状态
            session_state = gr.State(value=None)
            
            with gr.Column() as login_section:
                login_interface = self.create_login_interface()
            
            with gr.Column(visible=False) as main_section:
                # 顶部导航栏
                with gr.Row():
                    with gr.Column(scale=4):
                        gr.Markdown("# 🤖 AI资讯微信公众号智能体")
                    
                    with gr.Column(scale=1):
                        user_info = gr.Markdown("", elem_classes="user-info")
                        logout_btn = gr.Button("登出", size="sm")
                
                # 主界面内容
                main_content = main_interface_func()
            
            # 登录成功后的处理
            def on_login_success(username, password):
                success, session_token = self.user_manager.authenticate(username, password)
                
                if success:
                    # 获取用户信息
                    session_valid, session_info = self.user_manager.validate_session(session_token)
                    
                    if session_valid:
                        user_display = f"👤 {session_info['username']} ({session_info['role']})"
                        
                        return (
                            gr.Column(visible=False),  # 隐藏登录界面
                            gr.Column(visible=True),   # 显示主界面
                            session_token,             # 保存会话
                            gr.Markdown(user_display)  # 显示用户信息
                        )
                
                return (
                    gr.Column(visible=True),   # 显示登录界面
                    gr.Column(visible=False),  # 隐藏主界面
                    None,                      # 清空会话
                    gr.Markdown("")           # 清空用户信息
                )
            
            # 登出处理
            def on_logout(session_token):
                if session_token:
                    self.user_manager.logout(session_token)
                
                return (
                    gr.Column(visible=True),   # 显示登录界面
                    gr.Column(visible=False),  # 隐藏主界面
                    None,                      # 清空会话
                    gr.Markdown("")           # 清空用户信息
                )
            
            # 绑定事件（这里需要在实际使用时根据具体的登录按钮来绑定）
            logout_btn.click(
                fn=on_logout,
                inputs=[session_state],
                outputs=[login_section, main_section, session_state, user_info]
            )
        
        return protected_app
    
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[dict]]:
        """
        验证会话
        
        Args:
            session_token: 会话token
            
        Returns:
            Tuple[bool, Optional[dict]]: (是否有效, 用户信息)
        """
        return self.user_manager.validate_session(session_token)
    
    def require_auth(self, func):
        """
        装饰器：要求认证
        
        Args:
            func: 需要保护的函数
            
        Returns:
            装饰后的函数
        """
        def wrapper(*args, **kwargs):
            # 这里可以添加会话验证逻辑
            # 实际实现需要根据Gradio的状态管理来调整
            return func(*args, **kwargs)
        
        return wrapper


def create_user_management_interface(user_manager: UserManager) -> gr.Blocks:
    """
    创建用户管理界面（仅管理员可用）
    
    Args:
        user_manager: 用户管理器
        
    Returns:
        gr.Blocks: 用户管理界面
    """
    with gr.Blocks(title="用户管理") as user_mgmt_app:
        gr.Markdown("# 👥 用户管理")
        
        with gr.Tabs():
            with gr.TabItem("用户列表"):
                users_display = gr.Dataframe(
                    headers=["用户名", "角色", "创建时间", "最后登录"],
                    label="用户列表"
                )
                
                refresh_btn = gr.Button("刷新列表")
                
                def refresh_users():
                    users = user_manager.list_users()
                    data = []
                    for user in users:
                        data.append([
                            user['username'],
                            user['role'],
                            user['created_at'],
                            user['last_login'] or "从未登录"
                        ])
                    return data
                
                refresh_btn.click(
                    fn=refresh_users,
                    outputs=[users_display]
                )
                
                # 页面加载时自动刷新
                user_mgmt_app.load(
                    fn=refresh_users,
                    outputs=[users_display]
                )
            
            with gr.TabItem("添加用户"):
                with gr.Row():
                    with gr.Column():
                        new_username = gr.Textbox(label="用户名")
                        new_password = gr.Textbox(label="密码", type="password")
                        new_role = gr.Dropdown(
                            choices=["user", "admin"],
                            value="user",
                            label="角色"
                        )
                        add_user_btn = gr.Button("添加用户", variant="primary")
                        add_result = gr.Markdown("")
                
                def add_user(username, password, role):
                    if not username or not password:
                        return "❌ 请填写完整信息"
                    
                    if user_manager.add_user(username, password, role):
                        return f"✅ 用户 {username} 添加成功"
                    else:
                        return f"❌ 用户 {username} 已存在"
                
                add_user_btn.click(
                    fn=add_user,
                    inputs=[new_username, new_password, new_role],
                    outputs=[add_result]
                )
            
            with gr.TabItem("修改密码"):
                with gr.Row():
                    with gr.Column():
                        change_username = gr.Textbox(label="用户名")
                        old_password = gr.Textbox(label="旧密码", type="password")
                        new_password = gr.Textbox(label="新密码", type="password")
                        change_pwd_btn = gr.Button("修改密码", variant="primary")
                        change_result = gr.Markdown("")
                
                def change_password(username, old_pwd, new_pwd):
                    if not all([username, old_pwd, new_pwd]):
                        return "❌ 请填写完整信息"
                    
                    if user_manager.change_password(username, old_pwd, new_pwd):
                        return f"✅ 用户 {username} 密码修改成功"
                    else:
                        return f"❌ 密码修改失败，请检查用户名和旧密码"
                
                change_pwd_btn.click(
                    fn=change_password,
                    inputs=[change_username, old_password, new_password],
                    outputs=[change_result]
                )
    
    return user_mgmt_app
