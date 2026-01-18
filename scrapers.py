import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import urllib3
import re

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 터미널 출력 인코딩 설정 (Windows 대응)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

class TourismScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _safe_get(self, url, params=None):
        try:
            res = requests.get(url, params=params, headers=self.headers, verify=False, timeout=10)
            res.encoding = 'utf-8'
            res.raise_for_status()
            return res
        except Exception as e:
            print(f"Request failed for {url}: {repr(e)}")
            return None

    def fetch_visit_seoul(self):
        """VisitSeoul 공지사항"""
        url = "https://korean.visitseoul.net/announcements"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('.qna-list-table tbody tr')
        for row in rows:
            title_elem = row.select_one('td.text-align-left a')
            if not title_elem: continue
            
            items.append({
                'source': 'VisitSeoul',
                'title': title_elem.get_text(strip=True),
                'date': row.select('td')[2].get_text(strip=True),
                'link': "https://korean.visitseoul.net" + title_elem['href']
            })
        return items

    def fetch_visit_korea(self):
        """VisitKorea 뉴스/공지사항 (API)"""
        url = "https://korean.visitkorea.or.kr/call"
        payload = {'cmd': 'NOTICE_LIST_VIEW', 'page': '1', 'cnt': '10', 'sortkind': '1'}
        try:
            res = requests.post(url, data=payload, headers=self.headers, verify=False, timeout=10)
            res.encoding = 'utf-8'
            data = res.json()
            items = []
            for res_item in data.get('body', {}).get('result', []):
                raw_date = res_item.get('createDate', '')
                items.append({
                    'source': 'VisitKorea',
                    'title': res_item.get('title'),
                    'date': f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}" if len(raw_date) >= 8 else raw_date,
                    'link': f"https://korean.visitkorea.or.kr/notice/news_detail.do?nwsId={res_item.get('nwsId')}"
                })
            return items
        except Exception as e:
            print(f"Error VisitKorea: {repr(e)}")
            return []

    def fetch_gg_tour(self):
        """경기관광공사 (API)"""
        url = "https://ggtour.or.kr/api/v1/service/notice"
        res = self._safe_get(url)
        if not res: return []
        
        data = res.json()
        items = []
        for res_item in data.get('data', {}).get('items', []):
            items.append({
                'source': 'GGTour',
                'title': res_item.get('title'),
                'date': res_item.get('createdAt', '').split(' ')[0],
                'link': res_item.get('contentLink')
            })
        return items

    def fetch_mcst(self):
        """문화체육관광부 공지사항"""
        url = "https://www.mcst.go.kr/site/s_notice/notice/noticeList.jsp"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('table.board tbody tr')
        for row in rows:
            title_elem = row.select_one('td.subject a')
            if not title_elem: continue
            
            date_tds = row.select('td')
            # 문체부 테이블 구조에 따라 날짜 위치 확인 필요 (보통 끝에서 두번째 또는 네번째)
            date = date_tds[-2].get_text(strip=True) if len(date_tds) > 2 else ""
            
            items.append({
                'source': 'MCST',
                'title': title_elem.get_text(strip=True),
                'date': date,
                'link': "https://www.mcst.go.kr/site/s_notice/notice/" + title_elem['href']
            })
        return items

    def fetch_visit_busan(self):
        """비짓부산 공지사항"""
        url = "https://www.visitbusan.net/board/list.do?boardId=BBS_0000001&menuCd=DOM_000000204001000000"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('table.bbs_default.list tbody tr')
        for row in rows:
            title_elem = row.select_one('td.tit a')
            if not title_elem: continue
            
            items.append({
                'source': 'Busan',
                'title': title_elem.get_text(strip=True),
                'date': row.select('td.date')[0].get_text(strip=True) if row.select('td.date') else "",
                'link': "https://www.visitbusan.net" + title_elem['href']
            })
        return items

    def fetch_jeju(self):
        """제주관광공사 공지사항"""
        url = "https://ijto.or.kr/korean/Bd/list.php?btable=notice"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        # Ttable_wrap 구조 확인 결과 반영
        rows = soup.select('.Ttable_wrap.notice table tbody tr')
        for row in rows:
            title_elem = row.select_one('.board_title.table_a')
            if not title_elem: continue
            
            # 날짜 위치 (td 중 보통 하나)
            date = ""
            tds = row.select('td')
            for td in tds:
                txt = td.get_text(strip=True)
                if re.match(r'\d{4}-\d{2}-\d{2}', txt):
                    date = txt
                    break
            
            items.append({
                'source': 'Jeju',
                'title': title_elem.get_text(strip=True),
                'date': date,
                'link': "https://ijto.or.kr/korean/Bd/" + title_elem['href'] if 'href' in title_elem.attrs else url
            })
        return items

    def fetch_incheon(self):
        """인천관광공사 공지사항"""
        url = "https://www.ito.or.kr/main/board/notice.jsp"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('table tbody tr')
        for row in rows:
            title_elem = row.select_one('td.tit a')
            if not title_elem: continue
            
            items.append({
                'source': 'Incheon',
                'title': title_elem.get_text(strip=True),
                'date': row.select('td.date')[0].get_text(strip=True) if row.select('td.date') else "",
                'link': "https://www.ito.or.kr" + title_elem['href']
            })
        return items

    def fetch_gangwon(self):
        """강원관광재단 공지사항"""
        url = "https://www.gwto.or.kr/www/selectBbsNttList.do?bbsNo=1&key=21"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('table.bbs_list tbody tr') or soup.select('.bbs_list table tbody tr')
        for row in rows:
            title_elem = row.select_one('td.subject a')
            if not title_elem: continue
            
            items.append({
                'source': 'Gangwon',
                'title': title_elem.get_text(strip=True),
                'date': row.select('td.date')[0].get_text(strip=True) if row.select('td.date') else "",
                'link': "https://www.gwto.or.kr" + title_elem['href']
            })
        return items

    def fetch_gyeongbuk(self):
        """경북관광공사 공지사항"""
        url = "https://www.gtc.co.kr/page/10059/10007.tc"
        res = self._safe_get(url)
        if not res: return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        rows = soup.select('.Ttable_wrap.notice table tbody tr')
        for row in rows:
            title_elem = row.select_one('.board_title.table_a')
            if not title_elem: continue
            
            date = ""
            for td in row.select('td'):
                txt = td.get_text(strip=True)
                if re.match(r'\d{4}-\d{2}-\d{2}', txt):
                    date = txt
                    break

            items.append({
                'source': 'Gyeongbuk',
                'title': title_elem.get_text(strip=True),
                'date': date,
                'link': "https://www.gtc.co.kr" + title_elem['href'] if 'href' in title_elem.attrs else url
            })
        return items

    def fetch_all(self):
        """모든 소스 통합"""
        all_items = []
        fetchers = [
            self.fetch_visit_seoul, self.fetch_visit_korea, self.fetch_gg_tour,
            self.fetch_mcst, self.fetch_visit_busan, self.fetch_jeju,
            self.fetch_incheon, self.fetch_gangwon, self.fetch_gyeongbuk
        ]
        
        for fetcher in fetchers:
            try:
                all_items.extend(fetcher())
            except Exception as e:
                print(f"Fetcher error: {repr(e)}")
        
        # 유효한 날짜 데이터가 있는 것만 필터링 및 정렬
        valid_items = [i for i in all_items if i['date']]
        valid_items.sort(key=lambda x: x['date'], reverse=True)
        return valid_items

if __name__ == "__main__":
    scraper = TourismScraper()
    print("Fetching news from all expanded sources...")
    results = scraper.fetch_all()
    print(f"Finished. Total {len(results)} items found.")
    for item in results[:20]:
        print(f"[{item['source']}] {item['date']} - {item['title'][:60]}...")
