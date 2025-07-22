#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 带登录认证的Web应用
提供完整的用户认证和权限管理

Author: zengzhengtx
"""

import os
import sys
import argparse
import gradio as gr
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging
from src.auth.authentication import UserManager


class AuthenticatedWebApp:
    """带认证的Web应用类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.logger = init_logging()
        self.user_manager = UserManager()
        
        self.logger.info("带认证的Web应用初始化完成")
    
    def create_login_interface(self):
        """创建登录界面"""
        with gr.Column():
            gr.Markdown(
                "# 🤖 AI资讯智能体\n## 用户登录",
                elem_classes="login-title"
            )
            
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
            
            login_status = gr.Markdown("", visible=False)
            
            # 默认账户提示
            gr.Markdown(
                """
                ---
                **默认管理员账户**  
                用户名: `admin`  
                密码: `admin123`
                
                ⚠️ **安全提示**: 首次登录后请立即修改默认密码
                """
            )
        
        return username_input, password_input, login_btn, login_status
    
    def create_main_interface(self):
        """创建主界面内容"""
        with gr.Tabs():
            with gr.TabItem("📝 文章格式化"):
                gr.Markdown("## 自动生成演示文章")
                
                generate_btn = gr.Button("生成演示文章", variant="primary", size="lg")
                article_title = gr.Textbox(label="文章标题", interactive=False)
                article_content = gr.Markdown(label="格式化后的文章内容", height=400)
                
                def generate_demo_article():
                    try:
                        from src.tools.base_tool import NewsItem
                        from src.tools.wechat_formatter import WeChatFormatterTool
                        from src.utils.datetime_utils import get_utc_now
                        
                        news_item = NewsItem(
                            title="OpenAI发布GPT-4 Turbo：性能大幅提升",
                            content="OpenAI在其首届开发者大会上发布了GPT-4 Turbo，这是GPT-4的升级版本...",
                            url="https://openai.com/blog/new-models",
                            source="web_search",
                            published_date=get_utc_now(),
                            tags=['OpenAI', 'GPT-4'],
                            score=0.95
                        )
                        
                        formatter = WeChatFormatterTool()
                        formatted_content = formatter.format_content(
                            content=news_item.content,
                            title=news_item.title,
                            include_images=True,
                            include_source_links=True,
                            add_emojis=True
                        )
                        
                        return news_item.title, formatted_content
                    except Exception as e:
                        return "生成失败", f"错误: {str(e)}"
                
                generate_btn.click(
                    fn=generate_demo_article,
                    outputs=[article_title, article_content]
                )
            
            with gr.TabItem("🧹 内容筛选"):
                gr.Markdown("## 内容筛选与去重")
                
                filter_btn = gr.Button("执行内容筛选", variant="primary", size="lg")
                filter_result = gr.Textbox(label="筛选结果", lines=15, interactive=False)
                
                def filter_demo_content():
                    return "演示内容筛选功能：\n原始资讯数量: 5\n筛选后数量: 3\n\n筛选结果:\n1. OpenAI发布GPT-4 Turbo\n2. Google发布Gemini模型\n3. Meta开源Code Llama"
                
                filter_btn.click(
                    fn=filter_demo_content,
                    outputs=[filter_result]
                )
            
            with gr.TabItem("📊 数据库管理"):
                gr.Markdown("## 数据库管理")
                
                stats_btn = gr.Button("获取统计信息", variant="primary")
                db_result = gr.Textbox(label="统计信息", lines=10, interactive=False)
                
                def get_stats():
                    try:
                        from src.database.database import DatabaseManager
                        db_manager = DatabaseManager(self.config.database_path)
                        stats = db_manager.get_articles_stats()
                        
                        result = "📊 数据库统计信息:\n\n"
                        result += f"总文章数: {stats.get('total', 0)}\n"
                        result += f"草稿数量: {stats.get('status_draft', 0)}\n"
                        result += f"已发布: {stats.get('status_published', 0)}\n"
                        result += f"今日新增: {stats.get('today', 0)}\n"
                        
                        return result
                    except Exception as e:
                        return f"获取统计信息失败: {str(e)}"
                
                stats_btn.click(
                    fn=get_stats,
                    outputs=[db_result]
                )
            
            with gr.TabItem("👥 用户管理"):
                gr.Markdown("## 用户管理")
                
                # 用户列表
                with gr.Row():
                    refresh_users_btn = gr.Button("刷新用户列表")
                    users_display = gr.Dataframe(
                        headers=["用户名", "角色", "创建时间", "最后登录"],
                        label="用户列表"
                    )
                
                # 添加用户
                gr.Markdown("### 添加新用户")
                with gr.Row():
                    new_username = gr.Textbox(label="用户名")
                    new_password = gr.Textbox(label="密码", type="password")
                    new_role = gr.Dropdown(choices=["user", "admin"], value="user", label="角色")
                    add_user_btn = gr.Button("添加用户", variant="primary")
                
                add_result = gr.Markdown("")
                
                def refresh_users():
                    users = self.user_manager.list_users()
                    data = []
                    for user in users:
                        data.append([
                            user['username'],
                            user['role'],
                            user['created_at'],
                            user['last_login'] or "从未登录"
                        ])
                    return data
                
                def add_user(username, password, role):
                    if not username or not password:
                        return "❌ 请填写完整信息"
                    
                    if self.user_manager.add_user(username, password, role):
                        return f"✅ 用户 {username} 添加成功"
                    else:
                        return f"❌ 用户 {username} 已存在"
                
                refresh_users_btn.click(fn=refresh_users, outputs=[users_display])
                add_user_btn.click(
                    fn=add_user,
                    inputs=[new_username, new_password, new_role],
                    outputs=[add_result]
                )
    
    def create_app(self):
        """创建完整应用"""
        with gr.Blocks(
            title="AI资讯智能体 - 登录系统",
            theme=gr.themes.Soft(),
            css="""
            .login-container { max-width: 400px; margin: 50px auto; padding: 30px; }
            .user-info { text-align: right; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
            """
        ) as app:
            
            # 会话状态
            session_state = gr.State(value=None)
            
            # 登录界面
            with gr.Column(visible=True, elem_classes="login-container") as login_section:
                username_input, password_input, login_btn, login_status = self.create_login_interface()
            
            # 主界面
            with gr.Column(visible=False) as main_section:
                # 顶部导航
                with gr.Row():
                    with gr.Column(scale=4):
                        gr.Markdown("# 🤖 AI资讯微信公众号智能体")
                    with gr.Column(scale=1):
                        user_info = gr.Markdown("", elem_classes="user-info")
                        logout_btn = gr.Button("登出", size="sm", variant="secondary")
                
                # 主界面内容
                self.create_main_interface()
            
            # 登录处理
            def handle_login(username, password):
                if not username or not password:
                    return (
                        gr.Column(visible=True),
                        gr.Column(visible=False),
                        None,
                        gr.Markdown("❌ 请输入用户名和密码", visible=True),
                        gr.Markdown("")
                    )
                
                success, session_token = self.user_manager.authenticate(username, password)
                
                if success:
                    session_valid, session_info = self.user_manager.validate_session(session_token)
                    if session_valid:
                        user_display = f"👤 {session_info['username']} ({session_info['role']})"
                        return (
                            gr.Column(visible=False),
                            gr.Column(visible=True),
                            session_token,
                            gr.Markdown("✅ 登录成功！", visible=True),
                            gr.Markdown(user_display)
                        )
                
                return (
                    gr.Column(visible=True),
                    gr.Column(visible=False),
                    None,
                    gr.Markdown("❌ 用户名或密码错误", visible=True),
                    gr.Markdown("")
                )
            
            # 登出处理
            def handle_logout(session_token):
                if session_token:
                    self.user_manager.logout(session_token)
                return (
                    gr.Column(visible=True),
                    gr.Column(visible=False),
                    None,
                    gr.Markdown("", visible=False),
                    gr.Markdown("")
                )
            
            # 绑定事件
            login_btn.click(
                fn=handle_login,
                inputs=[username_input, password_input],
                outputs=[login_section, main_section, session_state, login_status, user_info]
            )
            
            logout_btn.click(
                fn=handle_logout,
                inputs=[session_state],
                outputs=[login_section, main_section, session_state, login_status, user_info]
            )
            
            # 回车键登录
            password_input.submit(
                fn=handle_login,
                inputs=[username_input, password_input],
                outputs=[login_section, main_section, session_state, login_status, user_info]
            )
        
        return app


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI资讯微信公众号智能体 - 带认证版本")
    
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Web界面主机地址")
    parser.add_argument("--port", type=int, default=7862, help="Web界面端口")
    parser.add_argument("--share", action="store_true", help="是否共享Web界面")
    parser.add_argument("--config", type=str, default="config.yaml", help="配置文件路径")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    logger = init_logging()
    logger.info("启动带认证的AI资讯智能体...")
    
    try:
        web_app = AuthenticatedWebApp(args.config)
        app = web_app.create_app()
        
        logger.info(f"启动Web界面: http://{args.host}:{args.port}")
        print(f"\n🌐 带认证的Web界面启动中...")
        print(f"📍 访问地址: http://{args.host}:{args.port}")
        print(f"👤 默认管理员账户: admin / admin123")
        print(f"⚠️  请首次登录后立即修改默认密码")
        
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            inbrowser=True
        )
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        print(f"\n❌ 应用启动失败: {e}")


if __name__ == "__main__":
    main()
