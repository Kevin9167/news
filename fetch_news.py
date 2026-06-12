#!/usr/bin/env python3
"""
AI 芯片新闻收集脚本
使用 NewsAPI 每天自动收集 20 条最新的 AI 芯片相关新闻
"""

import requests
import json
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NewsCollector:
    def __init__(self):
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # 添加调试信息
        print("\n=== 环境变量检查 ===")
        print(f"NEWSAPI_KEY: {'✓ 已设置' if self.newsapi_key else '✗ 未设置'}")
        print(f"SMTP_SERVER: {self.smtp_server if self.smtp_server else '✗ 未设置'}")
        print(f"SMTP_PORT: {self.smtp_port if self.smtp_port else '✗ 未设置'}")
        print(f"SENDER_EMAIL: {'✓ 已设置' if self.sender_email else '✗ 未设置'}")
        print(f"SENDER_PASSWORD: {'✓ 已设置' if self.sender_password else '✗ 未设置'}")
        print(f"RECIPIENT_EMAIL: {'✓ 已设置' if self.recipient_email else '✗ 未设置'}")
        print("=" * 50 + "\n")
        
        if not self.newsapi_key:
            raise ValueError("NEWSAPI_KEY environment variable is required")
        
        self.newsapi_url = "https://newsapi.org/v2/everything"
    
    def fetch_news(self, page_size=20):
        """
        从 NewsAPI 获取 AI 芯片相关新闻
        
        Args:
            page_size: 返回的新闻数量，默认 20 条
        
        Returns:
            新闻列表
        """
        # 获取过去 7 天的日期
        from_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # 搜索关键词（支持多语言）
        queries = [
            "AI chip OR AI芯片",
            "semiconductor AI OR 半导体 AI",
            "GPU chip OR GPU芯片",
            "neural processor OR 神经处理器"
        ]
        
        all_articles = []
        
        for query in queries:
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.newsapi_key,
                'pageSize': 100
            }
            
            try:
                response = requests.get(self.newsapi_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok':
                    articles = data.get('articles', [])
                    all_articles.extend(articles)
                    print(f"✓ 获取 {query} 相关新闻: {len(articles)} 条")
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"✗ 获取 {query} 出错: {error_msg}")
            
            except requests.exceptions.RequestException as e:
                print(f"✗ 网络请求出错 ({query}): {e}")
        
        # 去重（基于 URL）
        seen_urls = set()
        unique_articles = []
        
        for article in all_articles:
            url = article.get('url')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        # 按发布时间排序并取前 20 条
        unique_articles.sort(
            key=lambda x: x.get('publishedAt', ''), 
            reverse=True
        )
        
        return unique_articles[:page_size]
    
    def format_news_html(self, articles):
        """
        将新闻格式化为 HTML
        
        Args:
            articles: 新闻列表
        
        Returns:
            HTML 字符串
        """
        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .header h1 { margin: 0; }
                .header p { margin: 5px 0 0 0; font-size: 14px; }
                .article { border-left: 4px solid #667eea; padding: 15px; margin-bottom: 15px; 
                          background: #f9f9f9; border-radius: 3px; }
                .article-title { font-size: 16px; font-weight: bold; color: #667eea; margin: 0 0 8px 0; }
                .article-meta { font-size: 12px; color: #666; margin-bottom: 8px; }
                .article-description { font-size: 14px; color: #555; margin-bottom: 8px; }
                .article-source { display: inline-block; background: #667eea; color: white; 
                                 padding: 3px 8px; border-radius: 3px; font-size: 12px; }
                .article-link { display: inline-block; margin-left: 8px; }
                .article-link a { color: #667eea; text-decoration: none; font-weight: bold; }
                .article-link a:hover { text-decoration: underline; }
                .footer { border-top: 1px solid #ddd; padding-top: 15px; font-size: 12px; color: #666; }
                .count { color: #667eea; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI 芯片新闻日报</h1>
                    <p>AI Chip News Daily Report</p>
                </div>
        """
        
        # 添加新闻统计
        html += f"""
                <p>📊 今日收集: <span class="count">{len(articles)}</span> 条新闻</p>
                <p>📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <hr style="border: none; border-top: 2px solid #ddd; margin: 20px 0;">
        """
        
        # 添加每条新闻
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'N/A')
            description = article.get('description', '')
            source = article.get('source', {}).get('name', 'Unknown')
            url = article.get('url', '#')
            published_at = article.get('publishedAt', '')
            image_url = article.get('urlToImage', '')
            
            # 格式化发布时间
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                pub_time_str = pub_time.strftime('%Y-%m-%d %H:%M')
            except:
                pub_time_str = published_at
            
            html += f"""
                <div class="article">
                    <p class="article-title">{i}. {title}</p>
                    <div class="article-meta">
                        <span class="article-source">{source}</span>
                        <span style="margin-left: 10px;">📅 {pub_time_str}</span>
                    </div>
                    <p class="article-description">{description}</p>
            """
            
            if image_url:
                html += f'                    <img src="{image_url}" style="max-width: 100%; height: auto; border-radius: 3px; margin-bottom: 8px;">\n'
            
            html += f'                    <div class="article-link"><a href="{url}" target="_blank">阅读原文 →</a></div>\n'
            html += '                </div>\n'
        
        html += """
                <hr style="border: none; border-top: 2px solid #ddd; margin: 20px 0;">
                <div class="footer">
                    <p>✨ 此报告由 AI 芯片新闻收集系统自动生成</p>
                    <p>数据来源: <a href="https://newsapi.org" style="color: #667eea;">NewsAPI.org</a></p>
                    <p style="font-size: 11px; margin-top: 10px;">请勿回复此邮件，如有问题请访问项目页面。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, articles):
        """
        发送邮件
        
        Args:
            articles: 新闻列表
        """
        print("\n=== 邮件发送步骤 ===")
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("⚠️  邮件配置不完整:")
            print(f"  - SENDER_EMAIL: {'✓' if self.sender_email else '✗'}")
            print(f"  - SENDER_PASSWORD: {'✓' if self.sender_password else '✗'}")
            print(f"  - RECIPIENT_EMAIL: {'✓' if self.recipient_email else '✗'}")
            print("跳过邮件发送")
            return
        
        try:
            print(f"📧 正在连接到 {self.smtp_server}:{self.smtp_port}...")
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🤖 AI 芯片新闻日报 - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # 纯文本版本
            text_content = f"""
AI 芯片新闻日报
今日收集: {len(articles)} 条新闻
日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            for i, article in enumerate(articles, 1):
                text_content += f"""
{i}. {article.get('title', 'N/A')}
   来源: {article.get('source', {}).get('name', 'Unknown')}
   链接: {article.get('url', 'N/A')}
   描述: {article.get('description', 'N/A')}
"""
            
            part1 = MIMEText(text_content, 'plain')
            
            # HTML 版本（优先显示）
            html_content = self.format_news_html(articles)
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # 发送邮件
            print(f"🔑 正在进行 TLS 认证...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                print(f"✓ TLS 连接成功")
                
                print(f"👤 正在登录 {self.sender_email}...")
                server.login(self.sender_email, self.sender_password)
                print(f"✓ 登录成功")
                
                print(f"📨 正在发送邮件到 {self.recipient_email}...")
                server.send_message(msg)
                print(f"✓ 邮件发送成功: {self.recipient_email}")
        
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ 邮件认证失败: {e}")
            print("  请检查:")
            print("  - SENDER_EMAIL 是否正确")
            print("  - SENDER_PASSWORD 是否正确（应为应用专用密码）")
        except smtplib.SMTPException as e:
            print(f"✗ SMTP 错误: {e}")
        except Exception as e:
            print(f"✗ 邮件发送错误: {type(e).__name__}: {e}")
        
        print("=" * 50 + "\n")
    
    def save_to_file(self, articles):
        """
        将新闻保存到本地文件
        
        Args:
            articles: 新闻列表
        """
        try:
            # 创建 news 目录（如果不存在）
            os.makedirs('news', exist_ok=True)
            
            # 生成文件名
            filename = f"news/ai_chip_news_{datetime.now().strftime('%Y%m%d')}.json"
            
            # 保存为 JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'date': datetime.now().isoformat(),
                    'total': len(articles),
                    'articles': articles
                }, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 新闻已保存: {filename}")
            
            # 同时保存最新的新闻摘要
            summary_file = 'NEWS_LATEST.md'
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# AI 芯片新闻日报 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"**总计:** {len(articles)} 条新闻\n\n")
                
                for i, article in enumerate(articles, 1):
                    f.write(f"## {i}. {article.get('title', 'N/A')}\n\n")
                    f.write(f"**来源:** {article.get('source', {}).get('name', 'Unknown')}\n\n")
                    f.write(f"**发布时间:** {article.get('publishedAt', 'N/A')}\n\n")
                    f.write(f"**摘要:** {article.get('description', 'N/A')}\n\n")
                    f.write(f"[阅读原文]({article.get('url', '#')})\n\n")
                    f.write("---\n\n")
            
            print(f"✓ 摘要已保存: {summary_file}")
        
        except Exception as e:
            print(f"✗ 保存文件出错: {e}")
    
    def run(self):
        """
        执行完整的新闻收集流程
        """
        print("=" * 50)
        print("🚀 开始收集 AI 芯片新闻")
        print("=" * 50 + "\n")
        
        # 获取新闻
        articles = self.fetch_news()
        
        if not articles:
            print("⚠️  没有找到相关新闻")
            return
        
        print(f"\n✓ 成功获取 {len(articles)} 条新闻\n")
        
        # 保存到文件
        self.save_to_file(articles)
        
        # 发送邮件
        self.send_email(articles)
        
        print("=" * 50)
        print("✓ 新闻收集完成")
        print("=" * 50)


if __name__ == '__main__':
    try:
        collector = NewsCollector()
        collector.run()
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        exit(1)
    except Exception as e:
        print(f"✗ 运行出错: {e}")
        exit(1)
