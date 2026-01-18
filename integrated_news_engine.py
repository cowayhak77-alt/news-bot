import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time
import random
from datetime import datetime
# 수집 대상 사이트 설정 (필요에 따라 추가/수정 가능)
# 수집 대상 사이트 설정 (특별시, 광역시, 도청, 서울 구청 포함)
TARGET_SITES = [
    # 특별시 및 광역시
    {"name": "서울특별시청", "url": "https://www.seoul.go.kr/news/news_report.do"},
    {"name": "부산광역시청", "url": "https://www.busan.go.kr/nbgosi"},
    {"name": "대구광역시청", "url": "https://www.daegu.go.kr/index.do?menu_id=00000052"},
    {"name": "인천광역시청", "url": "https://www.incheon.go.kr/ic010205"},
    {"name": "광주광역시청", "url": "https://www.gwangju.go.kr/boardList.do?boardId=BD_0000000027&menuId=gwangju0303010000"},
    {"name": "대전광역시청", "url": "https://www.daejeon.go.kr/drh/drhBoardList.do?boardId=normal_0007&menuSeq=1631"},
    {"name": "울산광역시청", "url": "https://www.ulsan.go.kr/u/rep/bbs/list.ulsan?bbsId=BBS_0000000000000027&mId=001004003001000000"},
    {"name": "세종특별자치시청", "url": "https://www.sejong.go.kr/bbs/R0071/list.do"},

    # 도청 단위
    {"name": "경기도청", "url": "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1535"},
    {"name": "강원특별자치도청", "url": "https://www.provin.gangwon.kr/gw/portal/sub03_01_01"},
    {"name": "충청북도청", "url": "https://www.chungbuk.go.kr/www/selectBbsNttList.do?bbsNo=3271&key=1552"},
    {"name": "충청남도청", "url": "https://www.chungnam.go.kr/cnportal/cnapcPressList/cnapcPress/list.do?menuNo=500498"},
    {"name": "전북특별자치도청", "url": "https://www.jeonbuk.go.kr/board/list.jeonbuk?boardId=BODO_DATA&menuId=DOM_000000102001001000"},
    {"name": "전라남도청", "url": "https://www.jeonnam.go.kr/M7124/boardList.do?menuId=jeonnam0201000000"},
    {"name": "경상북도청", "url": "https://www.gb.go.kr/Main/page.do?mnu_uid=6792"},
    {"name": "경상남도청", "url": "https://www.gyeongnam.go.kr/board/list.gyeongnam?boardId=BBS_0000057&menuId=DOM_000000102001001000"},
    {"name": "제주특별자치도청", "url": "https://www.jeju.go.kr/news/bodo.htm"},

    # 서울시 25개 구청
    {"name": "종로구청", "url": "https://www.jongno.go.kr/portal/bbs/B0000002/list.do?menuNo=1754"},
    {"name": "중구청", "url": "https://www.junggu.seoul.kr/news/board/list.do?bbsId=BBSMSTR_000000000031&menuNo=200045"},
    {"name": "용산구청", "url": "https://www.yongsan.go.kr/portal/bbs/B0000002/list.do?menuNo=200190"},
    {"name": "성동구청", "url": "https://www.sd.go.kr/main/selectBbsNttList.do?bbsNo=183&key=1476"},
    {"name": "광진구청", "url": "https://www.gwangjin.go.kr/portal/bbs/B0000002/list.do?menuNo=200191"},
    {"name": "동대문구청", "url": "https://www.ddm.go.kr/www/selectBbsNttList.do?bbsNo=41&key=69"},
    {"name": "중랑구청", "url": "https://www.jungnang.go.kr/portal/bbs/B0000002/list.do?menuNo=200461"},
    {"name": "성북구청", "url": "https://www.sb.go.kr/main/selectBbsNttList.do?bbsNo=3&key=151"},
    {"name": "강북구청", "url": "https://www.gangbuk.go.kr/portal/bbs/B0000002/list.do?menuNo=200192"},
    {"name": "도봉구청", "url": "https://www.dobong.go.kr/bbs.asp?code=10004132"},
    {"name": "노원구청", "url": "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1001&q_menuSn=12"},
    {"name": "은평구청", "url": "https://www.ep.go.kr/CmsWeb/viewPage.do?version=1&menuId=MN20210204000000002"},
    {"name": "서대문구청", "url": "https://www.sdm.go.kr/news/news/report.do"},
    {"name": "마포구청", "url": "https://www.mapo.go.kr/site/main/board/news/list"},
    {"name": "양천구청", "url": "https://www.yangcheon.go.kr/site/main/board/news/list"},
    {"name": "강서구청", "url": "https://www.gangseo.seoul.kr/news/news010101"},
    {"name": "구로구청", "url": "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=642&key=1787"},
    {"name": "금천구청", "url": "https://www.geumcheon.go.kr/portal/selectBbsNttList.do?bbsNo=151&key=198"},
    {"name": "영등포구청", "url": "https://www.ydp.go.kr/www/selectBbsNttList.do?bbsNo=40&key=2791"},
    {"name": "동작구청", "url": "https://www.dongjak.go.kr/portal/bbs/B0000002/list.do?menuNo=200635"},
    {"name": "관악구청", "url": "https://www.gwanak.go.kr/site/gwanak/ex/bbs/List.do?cbIdx=239"},
    {"name": "서초구청", "url": "https://www.seocho.go.kr/site/seocho/ex/bbs/List.do?cbIdx=243"},
    {"name": "강남구청", "url": "https://www.gangnam.go.kr/board/B_000001/list.do?menuNo=GS040101"},
    {"name": "송파구청", "url": "https://www.songpa.go.kr/www/selectBbsNttList.do?bbsNo=7&key=2775"},
    {"name": "강동구청", "url": "https://www.gangdong.go.kr/web/newportal/press/list"}
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
        collected_data = []
        total_count = 0
        
        for site in TARGET_SITES:
            print(f"[{site['name']}] 수집 중...")
            news_list = self.smart_scrape(site['url'])
            if news_list:
                collected_data.append({"site_name": site['name'], "news_list": news_list})
                total_count += len(news_list)
            time.sleep(random.uniform(0.1, 0.5))

        # 1. 텍스트 리포트 생성
        report = []
        report.append(f"📅 수집 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔍 필터 키워드: {', '.join(self.money_keywords)}")
        report.append("="*60)
        
        for entry in collected_data:
            report.append(f"\n📌 {entry['site_name']} ({len(entry['news_list'])}건)")
            for news in entry['news_list']:
                report.append(f"- {news['title']}")
                report.append(f"  🔗 {news['link']}")
        
        report.append("\n" + "="*60)
        report.append(f"✅ 총 {total_count}건의 '돈 되는 정보'를 수집했습니다.")
        final_report_txt = "\n".join(report)
        
        with open("daily_news_report.txt", "w", encoding="utf-8") as f:
            f.write(final_report_txt)

        # 2. HTML 리포트 생성 (클릭 가능한 링크용)
        html_lines = [
            "<html><head><meta charset='utf-8'><style>",
            "body { font-family: 'Malgun Gothic', dotum, sans-serif; line-height: 1.6; max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }",
            "h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }",
            "h3 { color: #2980b9; margin-top: 30px; border-left: 5px solid #3498db; padding-left: 10px; }",
            "ul { list-style: none; padding: 0; }",
            "li { margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px; }",
            "a { color: #3498db; text-decoration: none; font-weight: bold; font-size: 1.1em; }",
            "a:hover { text-decoration: underline; color: #2980b9; }",
            ".info { color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }",
            ".footer { margin-top: 40px; text-align: center; color: #95a5a6; font-size: 0.9em; border-top: 1px solid #eee; padding-top: 20px; }",
            "</style></head><body>",
            f"<h1>📅 오늘자 뉴스 수집 리포트</h1>",
            f"<div class='info'>📅 <b>수집 일시:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>",
            f"🔍 <b>필터 키워드:</b> {', '.join(self.money_keywords)}</div>"
        ]

        for entry in collected_data:
            html_lines.append(f"<h3>📌 {entry['site_name']} ({len(entry['news_list'])}건)</h3><ul>")
            for news in entry['news_list']:
                html_lines.append(f"<li><a href='{news['link']}' target='_blank'>{news['title']}</a></li>")
            html_lines.append("</ul>")

        html_lines.append(f"<div class='footer'>✅ 총 {total_count}건의 정보를 수집했습니다.</div>")
        html_lines.append("</body></html>")
        
        final_report_html = "".join(html_lines)
        with open("daily_news_report.html", "w", encoding="utf-8") as f:
            f.write(final_report_html)
        
        print(f"\n수집 완료! 총 {total_count}건. TXT/HTML 리포트가 생성되었습니다.")
        return final_report_txt


if __name__ == "__main__":
    engine = IntegratedNewsEngine()
    engine.run()
