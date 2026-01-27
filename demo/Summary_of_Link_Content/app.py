"""
智能链接摘要 Web 应用
支持：B站视频（含CC字幕）、知乎、CSDN等文章链接
"""

import requests
import re
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)

# 配置 - 更完整的请求头，模拟真实浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

class ContentExtractor:
    """内容提取器"""

    @staticmethod
    def extract_bilibili(url):
        """提取B站视频信息"""
        try:
            # 提取视频ID
            if 'BV' in url:
                bvid = re.search(r'BV[a-zA-Z0-9]+', url).group()
            else:
                bvid = None

            if not bvid:
                return None, "无效的B站链接"

            # 获取视频基本信息
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = requests.get(api_url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                return None, "B站API请求失败"

            data = response.json()

            if data.get('code') != 0:
                return None, f"B站API错误: {data.get('message', '未知错误')}"

            video_data = data.get('data', {})
            video_info = {
                'title': video_data.get('title', ''),
                'desc': video_data.get('desc', ''),
                'owner': video_data.get('owner', {}).get('name', ''),
                'duration': video_data.get('duration', 0),
                'view': video_data.get('stat', {}).get('view', 0),
                'danmaku': video_data.get('stat', {}).get('danmaku', 0),
                'cid': video_data.get('cid', 0),
                'bvid': bvid
            }

            # 尝试获取CC字幕
            subtitle_content = ContentExtractor._get_bilibili_subtitle(bvid, video_info['cid'])

            # 如果没有CC字幕，尝试获取弹幕
            if not subtitle_content:
                danmaku_content = ContentExtractor._get_bilibili_danmaku(bvid, video_info['cid'])
                video_info['content'] = danmaku_content
                video_info['has_subtitle'] = False
            else:
                video_info['content'] = subtitle_content
                video_info['has_subtitle'] = True

            return video_info, None

        except Exception as e:
            return None, f"B站视频提取失败: {str(e)}"

    @staticmethod
    def _get_bilibili_subtitle(bvid, cid):
        """获取B站CC字幕"""
        try:
            # 获取字幕列表
            sub_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = requests.get(sub_url, headers=HEADERS, timeout=10)
            data = response.json()

            if data.get('code') != 0:
                return None

            video_data = data.get('data', {})
            subtitles = video_data.get('subtitle', {}).get('list', [])

            if not subtitles:
                return None

            # 获取字幕内容
            subtitle_url = subtitles[0].get('subtitle_url', '')
            if not subtitle_url:
                return None

            # B站字幕URL需要拼接前缀
            if subtitle_url.startswith('//'):
                subtitle_url = 'https:' + subtitle_url

            sub_response = requests.get(subtitle_url, headers=HEADERS, timeout=10)

            if sub_response.status_code != 200:
                return None

            subtitle_data = sub_response.json()
            if subtitle_data.get('code') != 0:
                return None

            # 提取字幕文本
            body = subtitle_data.get('body', [])
            subtitle_lines = []

            for item in body:
                content = item.get('content', '')
                if content:
                    subtitle_lines.append(content)

            return ' '.join(subtitle_lines) if subtitle_lines else None

        except Exception as e:
            print(f"获取B站字幕失败: {e}")
            return None

    @staticmethod
    def _get_bilibili_danmaku(bvid, cid):
        """获取B站弹幕"""
        try:
            # 获取弹幕地址
            danmaku_url = f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
            response = requests.get(danmaku_url, headers=HEADERS, timeout=10)

            if response.status_code != 200:
                return ""

            # 解析XML弹幕
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            danmakus = []
            for d in root.findall('d'):
                text = d.text
                if text:
                    danmakus.append(text)

            # 过滤无意义弹幕，保留有一定内容价值的弹幕
            meaningful_danmakus = []
            keywords = ['哈哈', '666', '???', '...']

            for dm in danmakus:
                dm = dm.strip()
                if len(dm) > 2 and not any(kw in dm for kw in keywords):
                    meaningful_danmakus.append(dm)

            return ' '.join(meaningful_danmakus[:50]) if meaningful_danmakus else ""

        except Exception as e:
            print(f"获取B站弹幕失败: {e}")
            return ""

    @staticmethod
    def extract_article(url):
        """提取文章内容（知乎、CSDN等）"""
        try:
            # 添加 Referer 头
            headers = HEADERS.copy()
            headers['Referer'] = url
            
            response = requests.get(url, headers=headers, timeout=15, verify=True, allow_redirects=True)

            if response.status_code != 200:
                return None, f"网页请求失败 (状态码: {response.status_code})"

            html_content = response.text

            # 检测平台类型
            if 'zhihu.com' in url:
                return ContentExtractor._extract_zhihu(html_content, url)
            elif 'csdn.net' in url:
                return ContentExtractor._extract_csdn(html_content, url)
            else:
                return ContentExtractor._extract_general(html_content, url)

        except requests.exceptions.Timeout:
            return None, "请求超时，目标网站响应太慢"
        except requests.exceptions.ConnectionError:
            return None, "连接失败，请检查网络或目标网站是否可访问"
        except requests.exceptions.SSLError:
            return None, "SSL证书验证失败"
        except Exception as e:
            return None, f"文章提取失败: {str(e)}"

    @staticmethod
    def _extract_zhihu(html_content, url):
        """提取知乎文章"""
        try:
            # 简化版本：提取主要文本内容
            # 实际生产环境需要更复杂的解析逻辑

            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
            title = title_match.group(1) if title_match else "知乎文章"

            # 提取正文（简化）
            content_pattern = r'<div[^>]*class="[^"]*RichContent[^"]*"[^>]*>(.*?)</div>'
            content_match = re.search(content_pattern, html_content, re.DOTALL)

            if not content_match:
                content_pattern = r'<article[^>]*>(.*?)</article>'
                content_match = re.search(content_pattern, html_content, re.DOTALL)

            if content_match:
                # 清理HTML标签
                content = re.sub(r'<[^>]+>', ' ', content_match.group(1))
                content = re.sub(r'\s+', ' ', content).strip()

                article_info = {
                    'title': title,
                    'content': content[:5000],  # 限制长度
                    'platform': '知乎',
                    'url': url
                }
                return article_info, None
            else:
                return None, "无法提取知乎文章内容"

        except Exception as e:
            return None, f"知乎文章解析失败: {str(e)}"

    @staticmethod
    def _extract_csdn(html_content, url):
        """提取CSDN文章"""
        try:
            title_match = re.search(r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</h1>', html_content, re.DOTALL)
            if not title_match:
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
            title = title_match.group(1) if title_match else "CSDN文章"

            # 提取正文
            content_pattern = r'<div[^>]*id="content_views"[^>]*>(.*?)</div>'
            content_match = re.search(content_pattern, html_content, re.DOTALL)

            if not content_match:
                content_pattern = r'<article[^>]*>(.*?)</article>'
                content_match = re.search(content_pattern, html_content, re.DOTALL)

            if content_match:
                content = re.sub(r'<[^>]+>', ' ', content_match.group(1))
                content = re.sub(r'\s+', ' ', content).strip()

                article_info = {
                    'title': title,
                    'content': content[:5000],
                    'platform': 'CSDN',
                    'url': url
                }
                return article_info, None
            else:
                return None, "无法提取CSDN文章内容"

        except Exception as e:
            return None, f"CSDN文章解析失败: {str(e)}"

    @staticmethod
    def _extract_general(html_content, url):
        """提取通用网页内容"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取标题
            title = soup.find('h1')
            if not title:
                title = soup.find('title')
            title = title.get_text().strip() if title else "未知标题"

            # 提取正文
            # 移除script和style
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # 尝试找到主要内容区域
            article = soup.find('article')
            if not article:
                article = soup.find('main')
            if not article:
                article = soup.find('div', class_=re.compile(r'content|article|post', re.I))

            if article:
                text = article.get_text(separator=' ')
            else:
                text = soup.body.get_text(separator=' ') if soup.body else ''

            # 清理文本
            text = re.sub(r'\s+', ' ', text).strip()

            if len(text) < 100:
                return None, "网页内容过少，无法提取有效信息"

            article_info = {
                'title': title,
                'content': text[:5000],
                'platform': '通用网页',
                'url': url
            }
            return article_info, None

        except ImportError:
            # 如果bs4不可用，使用正则表达式
            try:
                title_match = re.search(r'<title>(.*?)</title>', html_content, re.DOTALL)
                title = title_match.group(1) if title_match else "未知标题"

                # 提取段落文本
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
                content = ' '.join([re.sub(r'<[^>]+>', ' ', p).strip() for p in paragraphs])

                if len(content) < 100:
                    return None, "网页内容过少，无法提取有效信息"

                article_info = {
                    'title': title,
                    'content': content[:5000],
                    'platform': '通用网页',
                    'url': url
                }
                return article_info, None

            except Exception as e:
                return None, f"通用网页解析失败: {str(e)}"
        except Exception as e:
            return None, f"网页解析失败: {str(e)}"


class Summarizer:
    """摘要生成器"""

    @staticmethod
    def generate_summary(content, source_type='article'):
        """
        生成摘要
        注意：这是一个简化版本。实际使用时需要接入AI服务（如OpenAI、文心一言等）
        这里提供一个基于规则的简单摘要，你可以替换为真实的AI调用
        """
        try:
            if source_type == 'bilibili':
                return Summarizer._summarize_video(content)
            else:
                return Summarizer._summarize_article(content)

        except Exception as e:
            return {
                'summary': f"摘要生成失败: {str(e)}",
                'key_points': [],
                'error': str(e)
            }

    @staticmethod
    def _summarize_video(video_info):
        """摘要视频内容"""
        content = video_info.get('content', '')
        title = video_info.get('title', '')
        desc = video_info.get('desc', '')

        # 组合可用信息
        combined_text = f"{title} {desc} {content}"

        # 基于规则的简单摘要（实际应替换为AI调用）
        summary_parts = []

        # 标题分析
        if title:
            summary_parts.append(f"本视频主要讲解《{title}》")

        # 描述分析
        if desc:
            desc_lines = desc.split('\n')[:3]  # 取前3行
            desc_preview = ' '.join([line.strip() for line in desc_lines if line.strip()])
            if desc_preview:
                summary_parts.append(f"视频概述：{desc_preview}")

        # 内容分析
        if content:
            content_sentences = [s.strip() for s in content.split('。') if s.strip()]
            if len(content_sentences) > 0:
                summary_parts.append(f"视频内容涵盖：{content_sentences[0][:100]}")

        summary = '。'.join(summary_parts) + '。'

        # 提取关键点
        key_points = []
        if desc:
            desc_points = [line.strip() for line in desc.split('\n') if line.strip()]
            key_points.extend(desc_points[:3])

        if content:
            content_points = [s.strip() for s in content.split('。') if len(s.strip()) > 10][:4]
            key_points.extend(content_points)

        key_points = list(set(key_points))[:5]  # 去重并限制数量

        return {
            'summary': summary,
            'key_points': key_points,
            'has_subtitle': video_info.get('has_subtitle', False),
            'content_length': len(content)
        }

    @staticmethod
    def _summarize_article(article_info):
        """摘要文章内容"""
        title = article_info.get('title', '')
        content = article_info.get('content', '')

        # 基于规则的简单摘要（实际应替换为AI调用）
        summary_parts = []

        # 标题分析
        if title:
            summary_parts.append(f"本文《{title}》")

        # 内容分析
        sentences = [s.strip() for s in content.split('。') if s.strip()]
        if len(sentences) > 0:
            # 取第一句作为主题句
            summary_parts.append(sentences[0][:100])

            if len(sentences) > 2:
                # 取最后一句作为总结句
                summary_parts.append(sentences[-1][:100])

        summary = '。'.join(summary_parts) + '。'

        # 提取关键点
        key_points = []
        for i, sentence in enumerate(sentences):
            if i < 5 and len(sentence) > 15:
                key_points.append(sentence[:80])

        return {
            'summary': summary,
            'key_points': key_points[:4],
            'content_length': len(content)
        }


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/summarize', methods=['POST'])
def summarize():
    """摘要API"""
    try:
        data = request.json
        url = data.get('url', '').strip()

        if not url:
            return jsonify({
                'success': False,
                'error': '请输入有效的链接'
            })

        # 检测链接类型
        source_type = None
        if 'bilibili.com' in url:
            source_type = 'bilibili'
        elif 'zhihu.com' in url or 'csdn.net' in url:
            source_type = 'article'
        else:
            source_type = 'general'

        # 提取内容
        content_data = None
        error = None

        if source_type == 'bilibili':
            content_data, error = ContentExtractor.extract_bilibili(url)
        else:
            content_data, error = ContentExtractor.extract_article(url)

        if error or not content_data:
            return jsonify({
                'success': False,
                'error': error or '内容提取失败'
            })

        # 生成摘要
        summary_result = Summarizer.generate_summary(content_data, source_type)

        return jsonify({
            'success': True,
            'data': {
                'source_type': source_type,
                'title': content_data.get('title', ''),
                'url': url,
                'summary': summary_result['summary'],
                'key_points': summary_result['key_points'],
                'has_subtitle': summary_result.get('has_subtitle', False),
                'content_length': summary_result.get('content_length', 0),
                'platform': content_data.get('platform', ''),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"服务错误: {str(e)}"
        })


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


if __name__ == '__main__':
    port = 5500
    print("=" * 50)
    print("智能链接摘要 Web 应用")
    print("=" * 50)
    print(f"本地访问: http://localhost:{port}")
    print(f"局域网访问: http://0.0.0.0:{port}")
    print(f"API文档: http://localhost:{port}/api/health")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
