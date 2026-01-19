import requests
from bs4 import BeautifulSoup
import os
import time
import re
import random

class WaterDataCrawler:
    def __init__(self, output_dir="data_collection"):
        self.output_dir = output_dir
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]
        self.domain_keywords = [
            '水库', '水位', '流量', '库容', '调度', '闸门', '溢洪道', '防汛', '汛限', 
            '库区', '发电', '供水', '灌溉', '水位计', '传感器', '测站', '降雨', 
            '水利部', '委员会', '管理局', '枢纽', '堤防', '除险加固', '运行规程'
        ]
        self.output_path = r"c:\Users\Administrator\Desktop\ebuy\back\massive_water_data.txt"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.seen_lines = self._load_seen_lines()

    def _load_seen_lines(self):
        """启动时加载已有数据，实现跨任务去重"""
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, "r", encoding="utf-8") as f:
                    return set(line.strip() for line in f if line.strip())
            except:
                return set()
        return set()

    def get_headers(self, engine="bing"):
        ua = random.choice(self.user_agents)
        if engine == "bing":
            return {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://www.bing.com/",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive"
            }
        else:
            return {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://www.baidu.com/",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

    def is_relevant(self, text):
        """校验文本是否属于水利专业领域且低噪音"""
        noise_words = ['洗发水', '装修', '龙头', '测评', '售价', '购买', '包邮', '京东', '淘宝', '抖音', '教程', '八卦', '博主', '回答']
        if any(noise in text for noise in noise_words):
            return False
        # 必须包含至少两个核心关键词，且明确包含专业动作或领域词
        match_count = sum(1 for word in self.domain_keywords if word in text)
        professional_actions = ['水利', '工程', '调度', '运行', '规范', '规程', '办法', '条例', '监测']
        return match_count >= 2 and any(action in text for action in professional_actions)

    def clean_and_split(self, text):
        """将全文切分为适合 doccano 的短句/段落"""
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = re.split(r'([。！？；\n])', text)
        results = []
        i = 0
        while i < len(sentences):
            s = sentences[i]
            if i + 1 < len(sentences):
                s += sentences[i+1]
                i += 2
            else:
                i += 1
            s = s.strip()
            if 25 < len(s) < 450 and self.is_relevant(s):
                results.append(s)
        return results

    def search_and_crawl(self, keywords, pages=5):
        """支持双引擎切换的抓取逻辑"""
        total_valid_count = 0
        junk_keywords = ['zhihu.com', 'baidu.com', 'sohu.com', 'porn', 'video', 'shop']
        
        engines = [
            {"name": "Bing", "url": "https://www.bing.com/search?q={query}&first={offset}", "selector": ".b_algo h2 a"},
            {"name": "Baidu", "url": "https://www.baidu.com/s?wd={query}&pn={offset}", "selector": "h3.t a"}
        ]

        for base_keyword in keywords:
            query = f"{base_keyword} 规程 调度"
            print(f"\n[任务] 正在检索关键词: {query}")

            for page in range(pages):
                # 轮换引擎
                engine = engines[page % 2]
                offset = (page * 10 + 1) if engine['name'] == "Bing" else (page * 10)
                search_url = engine['url'].format(query=query, offset=offset)
                
                print(f"  [引擎: {engine['name']}] 正在页码: {page+1}")
                
                try:
                    time.sleep(random.uniform(5, 10))
                    resp = requests.get(search_url, headers=self.get_headers(engine['name'].lower()), timeout=15)
                    
                    if "captcha" in resp.text.lower() or "验证码" in resp.text:
                        print(f"    ! {engine['name']} 触发验证码拦截，跳过本页")
                        continue

                    soup = BeautifulSoup(resp.text, 'html.parser')
                    results = soup.select(engine['selector'])
                    
                    if not results:
                        print(f"    ? 未找到结果，可能是结构变化或屏蔽")
                        continue

                    for link in results:
                        target_url = link.get('href', '')
                        # 仅提取有效的外部链接
                        if not target_url.startswith('http'): continue
                        
                        raw_content = self.extract_content_from_url(target_url)
                        if raw_content:
                            valid_sentences = self.clean_and_split(raw_content)
                            if valid_sentences:
                                self.append_to_file(valid_sentences)
                                total_valid_count += len(valid_sentences)
                                print(f"    + 发现数据: {len(valid_sentences)} 条 (累计: {total_valid_count})")
                        time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"    ! 检索异常: {e}")

        print(f"\n[任务结束] 总计获取高质量数据: {total_valid_count} 条")
        print(f"数据文件路径: {os.path.abspath(self.output_path)}")

    def append_to_file(self, entries):
        """实时追加到结果文件，去重并过滤源码残留"""
        with open(self.output_path, "a", encoding="utf-8") as f:
            for line in entries:
                if line not in self.seen_lines:
                    if line.count('{') > 2 or line.count('}') > 2: continue
                    f.write(line + "\n")
                    self.seen_lines.add(line)

    def extract_content_from_url(self, url):
        """智能正文提取"""
        try:
            if url.lower().endswith('.pdf'): return None
            resp = requests.get(url, headers=self.get_headers(), timeout=12)
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for tag in soup(["script", "style", "nav", "footer", "header", "form", "aside"]):
                tag.decompose()
                
            main_content = soup.find('article') or \
                           soup.find('div', class_=re.compile(r'content|article|body|post|main|text')) or \
                           soup.body
            
            paragraphs = main_content.find_all(['p', 'div', 'section'])
            text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
            return text
        except:
            return None

if __name__ == "__main__":
    crawler = WaterDataCrawler()
    
    # 采用更稳健的搜索词，去掉括号等高级语法
    search_keywords = [
        "水利工程 调度 规程",
        "水库 运行 管理 办法",
        "大坝 安全 监测 规范",
        "水电站 闸门 启闭机 规程",
        "南水北调 运行 管理条例",
        "水资源 调度 方案",
        "防汛 预案 调度 流程",
        "泵站 运行 维护 手册",
        "河湖 治理 运行 规范",
        "水行政 执法 规定"
    ]
    
    print("--- 启动高精度水利语料采集程序 (增强过滤版) ---")
    crawler.search_and_crawl(search_keywords, pages=50)
