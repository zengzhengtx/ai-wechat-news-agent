"""
微信公众号格式化工具
将内容格式化为符合微信公众号发布规范的格式

Author: zengzhengtx
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.tools.base_tool import NewsItem
from src.utils.logger import get_logger


class WeChatFormatterTool:
    """微信公众号格式化工具"""
    
    name = "wechat_formatter"
    description = "将内容格式化为符合微信公众号发布规范的格式"
    inputs = {
        "content": {
            "type": "string",
            "description": "需要格式化的内容"
        },
        "title": {
            "type": "string",
            "description": "文章标题"
        },
        "include_images": {
            "type": "boolean",
            "description": "是否包含配图建议"
        },
        "include_source_links": {
            "type": "boolean",
            "description": "是否包含原始来源链接"
        },
        "add_emojis": {
            "type": "boolean",
            "description": "是否添加表情符号"
        }
    }
    output_type = "string"
    
    def __init__(self):
        self.logger = get_logger()
        
        # 常用emoji表情
        self.emojis = {
            'ai': '🤖',
            'tech': '💻',
            'research': '🔬',
            'breakthrough': '🚀',
            'model': '🧠',
            'data': '📊',
            'code': '💻',
            'github': '🐙',
            'paper': '📄',
            'news': '📰',
            'hot': '🔥',
            'new': '✨',
            'important': '⚡',
            'warning': '⚠️',
            'success': '✅',
            'point': '👉',
            'thinking': '🤔',
            'idea': '💡',
            'star': '⭐',
            'heart': '❤️',
            'thumbs_up': '👍'
        }
    
    def forward(
        self,
        content: str,
        title: str,
        include_images: bool = True,
        include_source_links: bool = True,
        add_emojis: bool = True
    ) -> str:
        """
        格式化内容
        
        Args:
            content: 需要格式化的内容
            title: 文章标题
            include_images: 是否包含配图建议
            include_source_links: 是否包含原始来源链接
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的内容
        """
        try:
            formatted_content = self.format_content(
                content, title, include_images, include_source_links, add_emojis
            )
            return formatted_content
        
        except Exception as e:
            self.logger.error(f"内容格式化失败: {e}")
            return f"格式化失败: {str(e)}"
    
    def format_content(
        self,
        content: str,
        title: str,
        include_images: bool = True,
        include_source_links: bool = True,
        add_emojis: bool = True
    ) -> str:
        """
        格式化内容为微信公众号格式
        
        Args:
            content: 原始内容
            title: 文章标题
            include_images: 是否包含配图建议
            include_source_links: 是否包含原始来源链接
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的内容
        """
        # 1. 清理和预处理内容
        cleaned_content = self._clean_content(content)
        
        # 2. 添加标题
        formatted_content = self._format_title(title, add_emojis)
        
        # 3. 添加引言
        intro = self._generate_intro(cleaned_content)
        formatted_content += f"\n\n{intro}\n\n"
        
        # 4. 格式化正文
        formatted_body = self._format_body(cleaned_content, add_emojis)
        formatted_content += formatted_body
        
        # 5. 添加配图建议
        if include_images:
            image_suggestions = self._generate_image_suggestions(title, cleaned_content)
            if image_suggestions:
                formatted_content += f"\n\n{image_suggestions}"
        
        # 6. 添加来源信息
        if include_source_links:
            source_info = self._format_source_info()
            formatted_content += f"\n\n{source_info}"
        
        # 7. 添加结尾
        ending = self._generate_ending(add_emojis)
        formatted_content += f"\n\n{ending}"
        
        return formatted_content
    
    def format_news_item(self, news_item: NewsItem) -> str:
        """
        格式化资讯项
        
        Args:
            news_item: 资讯项
            
        Returns:
            str: 格式化后的内容
        """
        return self.format_content(
            content=news_item.content,
            title=news_item.title,
            include_images=True,
            include_source_links=True,
            add_emojis=True
        )
    
    def _clean_content(self, content: str) -> str:
        """
        清理内容
        
        Args:
            content: 原始内容
            
        Returns:
            str: 清理后的内容
        """
        # 移除多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # 移除行首行尾空格
        lines = [line.strip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        # 移除特殊字符
        content = content.replace('\r', '')
        
        return content.strip()
    
    def _format_title(self, title: str, add_emojis: bool = True) -> str:
        """
        格式化标题
        
        Args:
            title: 原始标题
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的标题
        """
        formatted_title = f"# {title}"
        
        if add_emojis:
            # 根据标题内容添加合适的emoji
            if any(keyword in title.lower() for keyword in ['ai', '人工智能', 'gpt']):
                formatted_title = f"# {self.emojis['ai']} {title}"
            elif any(keyword in title.lower() for keyword in ['突破', 'breakthrough', '新']):
                formatted_title = f"# {self.emojis['breakthrough']} {title}"
            elif any(keyword in title.lower() for keyword in ['研究', 'research', '论文']):
                formatted_title = f"# {self.emojis['research']} {title}"
            elif any(keyword in title.lower() for keyword in ['github', '开源']):
                formatted_title = f"# {self.emojis['github']} {title}"
            else:
                formatted_title = f"# {self.emojis['news']} {title}"
        
        return formatted_title
    
    def _generate_intro(self, content: str) -> str:
        """
        生成引言
        
        Args:
            content: 内容
            
        Returns:
            str: 引言
        """
        # 提取内容的前几句作为引言
        sentences = content.split('。')[:2]
        intro = '。'.join(sentences)
        
        if len(intro) > 200:
            intro = intro[:200] + "..."
        
        return f"**{self.emojis['point']} 导读**\n\n{intro}。"
    
    def _format_body(self, content: str, add_emojis: bool = True) -> str:
        """
        格式化正文
        
        Args:
            content: 原始内容
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的正文
        """
        # 分段处理
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            
            # 检查是否是标题行
            if self._is_heading(paragraph):
                formatted_paragraph = self._format_heading(paragraph, add_emojis)
            else:
                formatted_paragraph = self._format_paragraph(paragraph, add_emojis)
            
            formatted_paragraphs.append(formatted_paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _is_heading(self, text: str) -> bool:
        """
        判断是否是标题
        
        Args:
            text: 文本
            
        Returns:
            bool: 是否是标题
        """
        # 简单的标题判断逻辑
        return (
            len(text) < 50 and
            not text.endswith('。') and
            not text.endswith('.') and
            ('：' in text or ':' in text or text.isupper() or 
             any(keyword in text for keyword in ['什么是', '如何', '为什么', '介绍', '概述']))
        )
    
    def _format_heading(self, heading: str, add_emojis: bool = True) -> str:
        """
        格式化小标题
        
        Args:
            heading: 标题文本
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的标题
        """
        if add_emojis:
            emoji = self.emojis.get('point', '👉')
            return f"## {emoji} {heading}"
        else:
            return f"## {heading}"
    
    def _format_paragraph(self, paragraph: str, add_emojis: bool = True) -> str:
        """
        格式化段落
        
        Args:
            paragraph: 段落文本
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的段落
        """
        # 处理列表
        if self._is_list_item(paragraph):
            return self._format_list_item(paragraph, add_emojis)
        
        # 处理引用
        if paragraph.startswith('"') or paragraph.startswith('"'):
            return f"> {paragraph}"
        
        # 处理代码块
        if '```' in paragraph or paragraph.strip().startswith('```'):
            return paragraph
        
        # 普通段落
        return paragraph
    
    def _is_list_item(self, text: str) -> bool:
        """
        判断是否是列表项
        
        Args:
            text: 文本
            
        Returns:
            bool: 是否是列表项
        """
        return (
            text.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')) or
            re.match(r'^\d+\.', text.strip())
        )
    
    def _format_list_item(self, item: str, add_emojis: bool = True) -> str:
        """
        格式化列表项
        
        Args:
            item: 列表项文本
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 格式化后的列表项
        """
        if add_emojis:
            emoji = self.emojis.get('point', '👉')
            # 替换列表标记
            item = re.sub(r'^[\d\-\*\•]+\.?\s*', f'{emoji} ', item.strip())
            return item
        else:
            return item
    
    def _generate_image_suggestions(self, title: str, content: str) -> str:
        """
        生成配图建议
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            str: 配图建议
        """
        suggestions = []
        
        # 根据内容类型生成建议
        if 'github' in content.lower() or '开源' in content:
            suggestions.append("GitHub项目截图或代码示例")
        
        if 'arxiv' in content.lower() or '论文' in content:
            suggestions.append("论文首页截图或研究结果图表")
        
        if 'huggingface' in content.lower() or '模型' in content:
            suggestions.append("模型架构图或性能对比图表")
        
        if any(keyword in content.lower() for keyword in ['ai', '人工智能', 'gpt']):
            suggestions.append("AI相关的概念图或技术示意图")
        
        if not suggestions:
            suggestions.append("与主题相关的配图")
        
        suggestion_text = '\n'.join([f"• {s}" for s in suggestions[:3]])
        
        return f"**{self.emojis['idea']} 配图建议**\n\n{suggestion_text}"
    
    def _format_source_info(self) -> str:
        """
        格式化来源信息
        
        Returns:
            str: 来源信息
        """
        return f"""**{self.emojis['point']} 声明**

本文内容由AI智能体自动整理生成，仅供参考学习。如有错误或侵权，请联系我们及时处理。

原始来源已在文中标注，感谢原作者的贡献。"""
    
    def _generate_ending(self, add_emojis: bool = True) -> str:
        """
        生成结尾
        
        Args:
            add_emojis: 是否添加表情符号
            
        Returns:
            str: 结尾内容
        """
        if add_emojis:
            return f"""---

{self.emojis['heart']} 如果觉得有用，请点赞支持！
{self.emojis['star']} 关注我们，获取更多AI资讯！
{self.emojis['thinking']} 有什么想法，欢迎留言讨论！"""
        else:
            return """---

如果觉得有用，请点赞支持！
关注我们，获取更多AI资讯！
有什么想法，欢迎留言讨论！"""
    
    def generate_tags(self, content: str) -> List[str]:
        """
        生成文章标签
        
        Args:
            content: 内容
            
        Returns:
            List[str]: 标签列表
        """
        tags = []
        
        # 技术相关标签
        tech_keywords = {
            'ai': ['AI', '人工智能'],
            'machine-learning': ['机器学习', 'ML'],
            'deep-learning': ['深度学习', 'DL'],
            'nlp': ['自然语言处理', 'NLP'],
            'computer-vision': ['计算机视觉', 'CV'],
            'gpt': ['GPT', 'ChatGPT'],
            'transformer': ['Transformer', '注意力机制'],
            'github': ['GitHub', '开源'],
            'arxiv': ['arXiv', '论文'],
            'huggingface': ['Hugging Face', '模型库']
        }
        
        content_lower = content.lower()
        for tag, keywords in tech_keywords.items():
            if any(keyword.lower() in content_lower for keyword in keywords):
                tags.append(tag)
        
        return tags[:10]  # 限制标签数量
