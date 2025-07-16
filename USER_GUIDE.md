# AI资讯微信公众号智能体使用指南

本文档提供了AI资讯微信公众号智能体的详细使用说明，帮助您快速上手并充分利用系统功能。

## 目录

1. [系统概述](#系统概述)
2. [安装与配置](#安装与配置)
3. [演示功能](#演示功能)
4. [Web界面使用](#Web界面使用)
5. [命令行使用](#命令行使用)
6. [自定义配置](#自定义配置)
7. [常见问题](#常见问题)

## 系统概述

AI资讯微信公众号智能体是一个基于smolagents框架开发的智能系统，能够自动获取最新AI资讯并将其改写为适合微信公众号发布的文章格式。系统具有以下核心功能：

- **多源资讯获取**：从arXiv、Hugging Face、GitHub和网络搜索等多个渠道获取最新AI资讯
- **智能内容改写**：使用OpenAI GPT-4o将技术内容转换为通俗易懂的语言
- **微信公众号格式化**：自动生成符合微信公众号排版规范的文章
- **内容管理**：提供文章存储、预览和编辑功能
- **质量控制**：自动评估和筛选高质量内容

## 安装与配置

### 系统要求

- Python 3.8+
- OpenAI API密钥
- 互联网连接

### 安装步骤

1. 克隆或下载代码库：
```bash
git clone https://github.com/yourusername/wechatAgent.git
cd wechatAgent
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```

4. 编辑`.env`文件，填入您的OpenAI API密钥：
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 演示功能

系统提供了多种演示方式，方便您快速体验核心功能：

### Web演示界面

启动Web演示界面，体验所有核心功能：
```bash
python demo_web.py
```

这将启动一个简化版的Web界面，包含以下功能：
- 文章格式化演示
- 内容筛选演示
- 数据库管理演示

### 命令行演示

系统提供了多种命令行演示模式：

1. **文章格式化演示**：
```bash
python demo.py --mode format
```
这将生成一篇格式化的微信公众号文章，并保存到`output/demo_article.md`。

2. **内容筛选演示**：
```bash
python demo.py --mode filter
```
这将展示内容筛选和去重功能。

3. **数据库操作演示**：
```bash
python demo.py --mode save
```
这将演示如何将文章保存到数据库并查询统计信息。

## Web界面使用

### 启动Web界面

```bash
python app.py
```

或者使用参数指定主机和端口：
```bash
python app.py --host 0.0.0.0 --port 8080
```

### 界面功能说明

Web界面分为四个主要标签页：

#### 1. 控制台

- **启动智能体**：开始资讯收集和处理流程
- **停止智能体**：中断正在运行的流程
- **运行信息**：显示当前运行状态和统计信息
- **日志输出**：实时显示系统日志

#### 2. 文章管理

- **文章列表**：显示所有生成的文章
- **状态过滤**：按状态（草稿、已发布、已归档）筛选文章
- **文章预览**：查看和编辑文章内容
- **导出文章**：将文章导出为Markdown文件

#### 3. 配置

- **基本配置**：设置OpenAI API密钥、模型和文章数量
- **资讯源配置**：启用或禁用不同的资讯源
- **输出配置**：自定义文章格式化选项

#### 4. 统计

- **文章统计**：显示文章数量和状态分布
- **来源分布**：显示不同资讯来源的文章数量

## 命令行使用

### 基本用法

```bash
python main.py
```

这将使用默认配置运行智能体，获取和处理资讯。

### 高级选项

```bash
python main.py --config custom_config.yaml --max-articles 3
```

参数说明：
- `--config`：指定配置文件路径
- `--max-articles`：设置最大文章数量
- `--web`：启动Web界面

## 自定义配置

### 配置文件

编辑`config.yaml`文件可以自定义智能体的行为：

```yaml
agent:
  model_id: "gpt-4o"
  max_articles_per_run: 5

sources:
  arxiv:
    enabled: true
    categories: ["cs.AI", "cs.LG", "cs.CL"]
  
  web_search:
    enabled: true
    queries: 
      - "AI news today"
      - "machine learning breakthrough"

output:
  format: "wechat"
  include_images: true
  add_emojis: true
```

### 资讯源配置

您可以启用或禁用以下资讯源：
- **arXiv**：学术论文
- **Web搜索**：网络新闻和博客
- **Hugging Face**：模型和数据集
- **GitHub**：开源项目

### 输出格式配置

您可以自定义以下输出选项：
- **包含配图建议**：是否添加配图建议
- **包含原始链接**：是否包含原始资讯链接
- **添加表情符号**：是否在文章中添加emoji表情

## 常见问题

### API相关问题

**Q: 如何解决OpenAI API区域限制问题？**  
A: 您可能需要使用VPN或代理服务器，或者在`.env`文件中设置`OPENAI_API_BASE`指向替代API端点。

**Q: API调用失败怎么办？**  
A: 检查API密钥是否正确，以及是否有足够的API额度。您也可以尝试降低请求频率或使用备用模型。

### 内容相关问题

**Q: 如何提高内容质量？**  
A: 在`config.yaml`中调整`content.min_quality_score`参数，或修改`src/utils/validators.py`中的质量评估逻辑。

**Q: 如何自定义文章格式？**  
A: 修改`src/tools/wechat_formatter.py`中的格式化模板和逻辑。

### 系统问题

**Q: 数据库在哪里？**  
A: 默认位置是`data/articles.db`，您可以在`.env`文件中修改`DATABASE_PATH`变量。

**Q: 如何备份生成的文章？**  
A: 您可以通过Web界面导出文章，或者直接备份`data/articles.db`文件。

**Q: 如何添加新的资讯源？**  
A: 在`src/tools/`目录下创建新的工具类，然后在`src/agent/ai_news_agent.py`中注册。

## 高级定制

如需进一步定制系统，您可以：

1. 修改`src/tools/`目录下的工具实现
2. 调整`src/utils/validators.py`中的内容筛选逻辑
3. 自定义`src/tools/wechat_formatter.py`中的格式化模板
4. 扩展`src/web/interface.py`中的Web界面功能

## 联系与支持

如有问题或建议，请通过以下方式联系我们：

- GitHub Issues: [https://github.com/yourusername/wechatAgent/issues](https://github.com/yourusername/wechatAgent/issues)
- Email: your.email@example.com
