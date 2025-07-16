# AI资讯微信公众号智能体

基于smolagents框架开发的AI智能体，能够自动获取最新AI资讯并将其改写为适合微信公众号发布的文章格式。

## 功能特点

- 🔍 **多源资讯获取**：从arXiv、Hugging Face、GitHub和网络搜索等多个渠道获取最新AI资讯
- 🤖 **智能内容改写**：使用OpenAI GPT-4o将技术内容转换为通俗易懂的语言
- 📱 **微信公众号格式**：自动生成符合微信公众号排版规范的文章
- 🌐 **Web界面**：基于Gradio的友好用户界面，方便操作和管理
- 📊 **内容管理**：文章存储、预览和编辑功能
- ⏱️ **定时任务**：支持定时自动获取和生成内容

## 快速开始

### 环境要求

- Python 3.10+ （推荐使用Python 3.11）
- OpenAI API密钥

### 安装

1. 克隆仓库
```bash
git clone https://github.com/zengzheng/wechatAgent.git
cd wechatAgent
```

2. 创建虚拟环境（推荐）
```bash
# 使用conda
conda create -n wechat-agent python=3.11 -y
conda activate wechat-agent

# 或使用venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的OpenAI API密钥
```

### 运行演示

我们提供了几种不同的演示方式，方便您快速体验系统功能：

1. **Web界面演示**（推荐）：
```bash
python demo_web.py
```

2. **文章格式化演示**：
```bash
python demo.py --mode format
```

3. **内容筛选演示**：
```bash
python demo.py --mode filter
```

4. **数据库操作演示**：
```bash
python demo.py --mode save
```

### 运行完整系统

启动Web界面：
```bash
python app.py
```

或者直接运行智能体：
```bash
python main.py
```

## 配置

编辑`config.yaml`文件可以自定义智能体的行为：

- 资讯源设置
- 内容筛选参数
- 输出格式选项
- Web界面配置

## 项目结构

```
wechatAgent/
├── src/
│   ├── agent/       # 智能体核心逻辑
│   ├── tools/       # 工具集合
│   ├── database/    # 数据存储
│   ├── utils/       # 工具函数
│   └── web/         # Web界面
├── data/            # 数据文件
├── logs/            # 日志文件
└── tests/           # 测试代码
```

## 主要文件说明

- `app.py` - Web界面入口
- `main.py` - 命令行入口
- `demo.py` - 演示脚本
- `demo_web.py` - Web演示界面
- `config.yaml` - 配置文件
- `.env` - 环境变量配置

## 技术栈

- [smolagents](https://huggingface.co/docs/smolagents/index) - 智能体框架
- [OpenAI API](https://openai.com/blog/openai-api) - GPT-4o模型
- [Gradio](https://gradio.app/) - Web界面
- [SQLite](https://www.sqlite.org/) - 数据存储

## 常见问题

**Q: 如何更改OpenAI API密钥？**
A: 编辑`.env`文件，修改`OPENAI_API_KEY`值。

**Q: 如何添加新的资讯源？**
A: 在`src/tools/`目录下创建新的工具类，然后在`src/agent/ai_news_agent.py`中注册。

**Q: 如何自定义文章格式？**
A: 修改`src/tools/wechat_formatter.py`中的格式化逻辑。

## 许可证

MIT
