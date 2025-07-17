# AI News WeChat Agent

An AI agent based on the smolagents framework that automatically fetches the latest AI news and rewrites it into articles suitable for WeChat public account publishing.

**Author**: zengzhengtx

## Features

- 🔍 **Multi-source News Fetching**: Gather latest AI news from arXiv, Hugging Face, GitHub, and web search
- 🤖 **Intelligent Content Rewriting**: Use OpenAI GPT-4o to convert technical content into easy-to-understand language
- 📱 **WeChat Format**: Automatically generate articles that comply with WeChat public account formatting standards
- 🌐 **Web Interface**: User-friendly interface based on Gradio for easy operation and management
- 📊 **Content Management**: Article storage, preview, and editing capabilities
- ⏱️ **Scheduled Tasks**: Support for automatic scheduled content fetching and generation

## Quick Start

### Requirements

- Python 3.10+ (Python 3.11 recommended)
- OpenAI API key

### Installation

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

### Run Demo

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

### Run Full System

Start web interface:
```bash
python app_fixed.py --simple
```

Or run the agent directly:
```bash
python main.py
```

## Configuration

Edit the `config.yaml` file to customize the agent's behavior:

- News source settings
- Content filtering parameters
- Output format options
- Web interface configuration

## Project Structure

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

## Key Files

- `app_fixed.py` - Fixed web interface entry
- `main.py` - Command line entry
- `stable_demo.py` - Stable demo script
- `simple_web_fixed.py` - Fixed web demo interface
- `config.yaml` - Configuration file
- `.env` - Environment variables

## Tech Stack

- [smolagents](https://huggingface.co/docs/smolagents/index) - Agent framework
- [OpenAI API](https://openai.com/blog/openai-api) - GPT-4o model
- [Gradio](https://gradio.app/) - Web interface
- [SQLite](https://www.sqlite.org/) - Data storage

## FAQ

**Q: How to change OpenAI API key?**  
A: Edit the `.env` file and modify the `OPENAI_API_KEY` value.

**Q: How to add new news sources?**  
A: Create a new tool class in the `src/tools/` directory, then register it in `src/agent/ai_news_agent.py`.

**Q: How to customize article format?**  
A: Modify the formatting logic in `src/tools/wechat_formatter.py`.

## License

MIT

## Contributing

Issues and Pull Requests are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Contact

- GitHub: [@zengzhengtx](https://github.com/zengzhengtx)
- Project: [https://github.com/zengzhengtx/wechatAgent](https://github.com/zengzhengtx/wechatAgent)
