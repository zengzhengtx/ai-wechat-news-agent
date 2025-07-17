# AI资讯微信公众号智能体 / AI News WeChat Agent

[中文](#中文) | [English](#english)

---

## 中文

基于smolagents框架开发的AI智能体，能够自动获取最新AI资讯并将其改写为适合微信公众号发布的文章格式。

**作者**: zengzhengtx

### 功能特点

- 🔍 **多源资讯获取**：从arXiv、Hugging Face、GitHub和网络搜索等多个渠道获取最新AI资讯
- 🤖 **智能内容改写**：使用OpenAI GPT-4o将技术内容转换为通俗易懂的语言
- 📱 **微信公众号格式**：自动生成符合微信公众号排版规范的文章
- 🌐 **Web界面**：基于Gradio的友好用户界面，方便操作和管理
- 📊 **内容管理**：文章存储、预览和编辑功能
- ⏱️ **定时任务**：支持定时自动获取和生成内容

### 快速开始

#### 环境要求

- Python 3.10+ （推荐使用Python 3.11）
- OpenAI API密钥

#### 安装

1. 克隆仓库
```bash
git clone https://github.com/zengzhengtx/wechatAgent.git
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

#### 运行演示

我们提供了几种不同的演示方式，方便您快速体验系统功能：

1. **Web界面演示**（推荐）：
```bash
python simple_web_fixed.py
```

2. **稳定版演示**：
```bash
python stable_demo.py
```

3. **文章格式化演示**：
```bash
python demo.py --mode format
```

4. **内容筛选演示**：
```bash
python demo.py --mode filter
```

#### 运行完整系统

启动Web界面：
```bash
python app_fixed.py --simple
```

或者直接运行智能体：
```bash
python main.py
```

### 配置

编辑`config.yaml`文件可以自定义智能体的行为：

- 资讯源设置
- 内容筛选参数
- 输出格式选项
- Web界面配置

### 项目结构

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

### 主要文件说明

- `app_fixed.py` - 修复版Web界面入口
- `main.py` - 命令行入口
- `stable_demo.py` - 稳定版演示脚本
- `simple_web_fixed.py` - 修复版Web演示界面
- `config.yaml` - 配置文件
- `.env` - 环境变量配置

### 技术栈

- [smolagents](https://huggingface.co/docs/smolagents/index) - 智能体框架
- [OpenAI API](https://openai.com/blog/openai-api) - GPT-4o模型
- [Gradio](https://gradio.app/) - Web界面
- [SQLite](https://www.sqlite.org/) - 数据存储

### 常见问题

**Q: 如何更改OpenAI API密钥？**
A: 编辑`.env`文件，修改`OPENAI_API_KEY`值。

**Q: 如何添加新的资讯源？**
A: 在`src/tools/`目录下创建新的工具类，然后在`src/agent/ai_news_agent.py`中注册。

**Q: 如何自定义文章格式？**
A: 修改`src/tools/wechat_formatter.py`中的格式化逻辑。

---

## English

An AI agent based on the smolagents framework that automatically fetches the latest AI news and rewrites it into articles suitable for WeChat public account publishing.

**Author**: zengzhengtx

### Features

- 🔍 **Multi-source News Fetching**: Gather latest AI news from arXiv, Hugging Face, GitHub, and web search
- 🤖 **Intelligent Content Rewriting**: Use OpenAI GPT-4o to convert technical content into easy-to-understand language
- 📱 **WeChat Format**: Automatically generate articles that comply with WeChat public account formatting standards
- 🌐 **Web Interface**: User-friendly interface based on Gradio for easy operation and management
- 📊 **Content Management**: Article storage, preview, and editing capabilities
- ⏱️ **Scheduled Tasks**: Support for automatic scheduled content fetching and generation

### Quick Start

#### Requirements

- Python 3.10+ (Python 3.11 recommended)
- OpenAI API key

#### Installation

1. Clone the repository
```bash
git clone https://github.com/zengzhengtx/wechatAgent.git
cd wechatAgent
```

2. Create virtual environment (recommended)
```bash
# Using conda
conda create -n wechat-agent python=3.11 -y
conda activate wechat-agent

# Or using venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

#### Run Demo

We provide several demo modes for you to quickly experience the system:

1. **Web Interface Demo** (Recommended):
```bash
python simple_web_fixed.py
```

2. **Stable Demo**:
```bash
python stable_demo.py
```

3. **Article Formatting Demo**:
```bash
python demo.py --mode format
```

4. **Content Filtering Demo**:
```bash
python demo.py --mode filter
```

#### Run Full System

Start web interface:
```bash
python app_fixed.py --simple
```

Or run the agent directly:
```bash
python main.py
```

### Configuration

Edit the `config.yaml` file to customize the agent's behavior:

- News source settings
- Content filtering parameters
- Output format options
- Web interface configuration

### Project Structure

```
wechatAgent/
├── src/
│   ├── agent/       # Agent core logic
│   ├── tools/       # Tool collection
│   ├── database/    # Data storage
│   ├── utils/       # Utility functions
│   └── web/         # Web interface
├── data/            # Data files
├── logs/            # Log files
└── tests/           # Test code
```

### Key Files

- `app_fixed.py` - Fixed web interface entry
- `main.py` - Command line entry
- `stable_demo.py` - Stable demo script
- `simple_web_fixed.py` - Fixed web demo interface
- `config.yaml` - Configuration file
- `.env` - Environment variables

### Tech Stack

- [smolagents](https://huggingface.co/docs/smolagents/index) - Agent framework
- [OpenAI API](https://openai.com/blog/openai-api) - GPT-4o model
- [Gradio](https://gradio.app/) - Web interface
- [SQLite](https://www.sqlite.org/) - Data storage

### FAQ

**Q: How to change OpenAI API key?**
A: Edit the `.env` file and modify the `OPENAI_API_KEY` value.

**Q: How to add new news sources?**
A: Create a new tool class in the `src/tools/` directory, then register it in `src/agent/ai_news_agent.py`.

**Q: How to customize article format?**
A: Modify the formatting logic in `src/tools/wechat_formatter.py`.

## License

MIT
