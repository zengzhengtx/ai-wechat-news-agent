"""
内容改写工具
将技术性内容转换为通俗易懂的语言，适合微信公众号发布
"""

import json
import time
from typing import Dict, Any, List, Optional
import openai

from src.tools.base_tool import BaseNewsTool, NewsItem
from src.utils.logger import get_logger


class ContentRewriteTool:
    """内容改写工具"""
    
    name = "content_rewriter"
    description = "将技术性内容改写为通俗易懂的语言，适合微信公众号发布"
    inputs = {
        "content": {
            "type": "string",
            "description": "需要改写的原始内容"
        },
        "title": {
            "type": "string",
            "description": "原始标题"
        },
        "style": {
            "type": "string",
            "description": "改写风格，如'通俗易懂'、'专业深度'、'幽默风趣'等"
        },
        "max_length": {
            "type": "integer",
            "description": "改写后的最大长度"
        }
    }
    output_type = "string"
    
    def __init__(self, api_key: Optional[str] = None):
        self.logger = get_logger()
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.rate_limit_delay = 1.0
        self.last_request_time = 0
    
    def forward(
        self, 
        content: str, 
        title: str, 
        style: str = "通俗易懂", 
        max_length: int = 3000
    ) -> str:
        """
        执行内容改写
        
        Args:
            content: 需要改写的原始内容
            title: 原始标题
            style: 改写风格
            max_length: 改写后的最大长度
            
        Returns:
            str: 改写后的内容
        """
        try:
            result = self.rewrite_content(content, title, style, max_length)
            return result
        
        except Exception as e:
            self.logger.error(f"内容改写失败: {e}")
            return f"改写失败: {str(e)}"
    
    def rewrite_content(
        self, 
        content: str, 
        title: str, 
        style: str = "通俗易懂", 
        max_length: int = 3000
    ) -> str:
        """
        改写内容
        
        Args:
            content: 需要改写的原始内容
            title: 原始标题
            style: 改写风格
            max_length: 改写后的最大长度
            
        Returns:
            str: 改写后的内容
        """
        # 构建提示词
        prompt = self._build_rewrite_prompt(content, title, style, max_length)
        
        # 调用OpenAI API
        response = self._call_openai_api(prompt)
        
        # 解析结果
        rewritten_content = self._parse_rewrite_response(response)
        
        return rewritten_content
    
    def rewrite_news_item(self, news_item: NewsItem, style: str = "通俗易懂") -> NewsItem:
        """
        改写资讯项
        
        Args:
            news_item: 原始资讯项
            style: 改写风格
            
        Returns:
            NewsItem: 改写后的资讯项
        """
        self.logger.info(f"开始改写资讯: {news_item.title}")
        
        try:
            # 改写标题
            rewritten_title = self.rewrite_title(news_item.title, style)
            
            # 改写内容
            rewritten_content = self.rewrite_content(
                news_item.content, 
                news_item.title, 
                style
            )
            
            # 生成摘要
            summary = self.generate_summary(rewritten_content)
            
            # 创建新的资讯项
            rewritten_item = NewsItem(
                title=rewritten_title,
                content=rewritten_content,
                url=news_item.url,
                source=news_item.source,
                published_date=news_item.published_date,
                tags=news_item.tags + ["rewritten"]
            )
            
            # 保留原始分数
            rewritten_item.score = news_item.score
            
            self.logger.info(f"资讯改写完成: {rewritten_title}")
            return rewritten_item
            
        except Exception as e:
            self.logger.error(f"资讯改写失败: {e}")
            return news_item  # 返回原始资讯项
    
    def rewrite_title(self, title: str, style: str = "通俗易懂") -> str:
        """
        改写标题
        
        Args:
            title: 原始标题
            style: 改写风格
            
        Returns:
            str: 改写后的标题
        """
        prompt = f"""
        请将以下技术性标题改写为{style}的微信公众号标题，使其更吸引人、更容易理解，
        同时保持原意。标题应当简洁有力，能够吸引读者点击。

        原标题: {title}

        要求:
        1. 保持原意，不要添加虚假信息
        2. 使用吸引人的表达方式
        3. 可以适当使用emoji表情
        4. 长度控制在30个字以内
        5. 风格要{style}

        直接返回改写后的标题，不要有任何前缀或解释。
        """
        
        response = self._call_openai_api(prompt, max_tokens=100)
        
        # 清理结果
        rewritten_title = response.strip().replace('"', '').replace("'", "")
        
        return rewritten_title
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """
        生成内容摘要
        
        Args:
            content: 内容
            max_length: 最大长度
            
        Returns:
            str: 摘要
        """
        prompt = f"""
        请为以下内容生成一个简洁的摘要，用于微信公众号文章的开头引言。
        摘要应当概括文章的主要内容，吸引读者继续阅读。

        内容:
        {content[:2000]}  # 只使用前2000个字符

        要求:
        1. 摘要长度不超过200字
        2. 语言简洁明了
        3. 突出内容的价值和亮点
        4. 适合中文读者阅读习惯

        直接返回摘要内容，不要有任何前缀或解释。
        """
        
        response = self._call_openai_api(prompt, max_tokens=300)
        
        return response.strip()
    
    def _build_rewrite_prompt(
        self, 
        content: str, 
        title: str, 
        style: str, 
        max_length: int
    ) -> str:
        """
        构建改写提示词
        
        Args:
            content: 原始内容
            title: 原始标题
            style: 改写风格
            max_length: 最大长度
            
        Returns:
            str: 提示词
        """
        return f"""
        请将以下技术性内容改写为{style}的微信公众号文章，使其更易于普通读者理解，
        同时保持原始信息的准确性。

        原标题: {title}

        原内容:
        {content}

        要求:
        1. 使用{style}的风格，让内容更容易理解
        2. 保持原始信息的准确性，不要添加虚假信息
        3. 适当添加emoji表情，增加可读性
        4. 使用微信公众号适合的排版格式
        5. 可以适当组织内容结构，使其更符合阅读习惯
        6. 总字数控制在{max_length}字以内
        7. 在文章末尾注明原始来源
        8. 为文章添加小标题，使结构更清晰
        9. 可以适当解释专业术语

        直接返回改写后的完整文章内容，不要有任何前缀或解释。
        """
    
    def _call_openai_api(
        self, 
        prompt: str, 
        model: str = "gpt-4o", 
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        调用OpenAI API
        
        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
            
        Returns:
            str: API响应内容
        """
        # 速率限制
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一位专业的内容编辑，擅长将技术性内容改写为通俗易懂的文章。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content or ""
        
        except Exception as e:
            self.logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    def _parse_rewrite_response(self, response: str) -> str:
        """
        解析API响应
        
        Args:
            response: API响应内容
            
        Returns:
            str: 解析后的内容
        """
        # 简单清理响应
        cleaned_response = response.strip()
        
        return cleaned_response
    
    def batch_rewrite(self, news_items: List[NewsItem], style: str = "通俗易懂") -> List[NewsItem]:
        """
        批量改写资讯项
        
        Args:
            news_items: 资讯项列表
            style: 改写风格
            
        Returns:
            List[NewsItem]: 改写后的资讯项列表
        """
        rewritten_items = []
        
        for item in news_items:
            try:
                rewritten_item = self.rewrite_news_item(item, style)
                rewritten_items.append(rewritten_item)
                
                # 速率限制
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                self.logger.error(f"改写资讯项失败: {e}")
                rewritten_items.append(item)  # 添加原始项
        
        return rewritten_items
