import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import random
from datetime import datetime
# 수집 대상 사이트 설정 (필요에 따라 추가/수정 가능)
TARGET_SITES = [
    {"name": "고용노동부", "url": "https://www.moel.go.kr/news/enews/report/enewsList.do"},
    {"name": "중소벤처기업부", "url": "https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=248"},
    {"name": "서울시청", "url": "https://www.seoul.go.kr/news/news_report.do"},
    {"name": "경기도청", "url": "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1536"},
    {"name": "산업통상자원부", "url": "https://www.motie.go.kr/motie/ne/presse/press.jsp"}
]


class IntegratedNewsEngine:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        # 돈이 되는 키워드 리스트
        self.money_keywords = ["보도", "자료", "공고", "지원", "사업", "모집", "선정", "예산", "투자", "육성", "혜택", "보조금"]
        self.table_patterns = [
            "table.board-list", "table.list_table", "table.bbs_list", 
            "table.tbl_board", "table.tstyle_list", ".board_list table",
            "table[summary*='게시판']", "table.table", ".board_list", ".list_type",
            ".news_list", ".bbsList", ".boardList", ".list_item"
        ]

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }

    def is_money_news(self, title):
        # 키워드 필터링 로직
        for kw in self.money_keywords:
            if kw in title:
                return True
        return False

    def smart_scrape(self, url):
        try:
            session = requests.Session()
            response = session.get(url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
                
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = []
            for pattern in self.table_patterns:
                areas = soup.select(pattern)
                for area in areas:
                    found = area.select("tbody tr, tr, li, .item, .list_item, .post-item")
                    if found: rows.extend(found)
            
            if not rows:
                content_area = soup.select_one("#contents, #content, .content, main")
                if content_area:
                    rows = content_area.select("tr, li, div[class*='item']")
                else:
                    rows = soup.select("tr, li")

            results = []
            seen_titles = set()
            
            for row in rows:
                links = row.find_all("a")
                if not links: continue
                
                valid_links = [l for l in links if len(l.get_text(strip=True)) > 5]
                if not valid_links: continue
                
                title_tag = max(valid_links, key=lambda x: len(x.get_text(strip=True)))
                title = title_tag.get_text(strip=True)
                title = re.sub(r"\[공지\]|\[새글\]|NEW", "", title).strip()
                
                if title in seen_titles or len(title) < 5: continue
                
                # 키워드 필터링 적용
                if not self.is_money_news(title): continue
                
                seen_titles.add(title)
                link = urljoin(url, title_tag['href'])
                
                results.append({
                    "title": title,
                    "link": link,
                    "date": datetime.now().strftime("%Y-%m-%d") # 실제 날짜 추출 로직은 이전 코드 참고
                })
                if len(results) >= 5: break # 사이트당 최대 5건만 수집
                
            return results
        except Exception as e:
            return None

    def run(self):
        report = []
        report.append(f"📅 수집 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔍 필터 키워드: {', '.join(self.money_keywords)}")
        report.append("="*60)

        total_count = 0
        for site in TARGET_SITES:
            print(f"[{site['name']}] 수집 중...")
            news_list = self.smart_scrape(site['url'])
            if news_list:
                report.append(f"\n📌 {site['name']} ({len(news_list)}건)")
                for news in news_list:
                    report.append(f"- {news['title']}")
                    report.append(f"  🔗 {news['link']}")
                total_count += len(news_list)
            time.sleep(random.uniform(0.5, 1.5))

        report.append("\n" + "="*60)
        report.append(f"✅ 총 {total_count}건의 '돈 되는 정보'를 수집했습니다.")
        
        final_report = "\n".join(report)
        
        # 파일로 저장 (이메일 발송 대신 파일 저장으로 대체하여 확인 가능하게 함)
        with open("daily_news_report.txt", "w", encoding="utf-8") as f:
            f.write(final_report)
        
        print(f"\n수집 완료! 총 {total_count}건. 결과가 /home/ubuntu/daily_news_report.txt 에 저장되었습니다.")
        return final_report

if __name__ == "__main__":
    engine = IntegratedNewsEngine()
    engine.run()
