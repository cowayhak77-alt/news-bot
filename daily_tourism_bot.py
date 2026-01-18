import os
from scrapers import TourismScraper
from datetime import datetime
import re

# 강조할 키워드 목록 (app.py와 동일)
HIGHLIGHT_KEYWORDS = ["여행", "참여", "숙박", "호텔", "할인", "이벤트", "축제", "패키지", "쿠폰"]

def highlight_text(text):
    """제목 내 주요 키워드에 하이라이트 적용 (이메일용 인라인 스타일)"""
    for keyword in HIGHLIGHT_KEYWORDS:
        if keyword in text:
            pattern = re.compile(f"({keyword})", re.IGNORECASE)
            # 이메일 클라이언트 호환성을 위해 인라인 스타일 사용
            text = pattern.sub(r'<span style="background-color: #fff176; font-weight: bold; color: #d32f2f; padding: 0 2px;">\1</span>', text)
    return text

def generate_html_report(news_data):
    """프리미엄 스타일의 이메일용 HTML 리포트 생성"""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8f9fa; }}
            .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #eee; }}
            .header {{ background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 30px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: bold; }}
            .header p {{ margin: 10px 0 0; font-size: 14px; opacity: 0.9; }}
            .content {{ padding: 20px; }}
            .stats {{ background: #f1f3f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; display: flex; justify-content: space-around; }}
            .news-item {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
            .news-item:last-child {{ border-bottom: none; }}
            .source-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: #1976D2; background: #E3F2FD; margin-bottom: 5px; }}
            .title {{ display: block; font-size: 17px; font-weight: bold; color: #1a1a1a; text-decoration: none; margin-bottom: 5px; line-height: 1.4; }}
            .date {{ font-size: 13px; color: #888; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
            .highlight {{ background-color: #fff176; font-weight: bold; color: #d32f2f; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🇰🇷 전국 관광 뉴스 일일 리포트</h1>
                <p>{now_str} 기준 최신 소식</p>
            </div>
            <div class="content">
                <div class="stats">
                    <span>전체 소식: <b>{len(news_data)}건</b></span>
                    <span>수집 소스: <b>{len(set(i['source'] for i in news_data))}개</b></span>
                </div>
    """
    
    if not news_data:
        html += "<p style='text-align:center; padding: 40px; color: #666;'>오늘 수집된 새로운 소식이 없습니다.</p>"
    else:
        for item in news_data[:30]:  # 이메일 용량을 고려하여 상위 30건만 포함
            highlighted_title = highlight_text(item['title'])
            html += f"""
                <div class="news-item">
                    <span class="source-tag">{item['source']}</span>
                    <a href="{item['link']}" class="title">{highlighted_title}</a>
                    <div class="date">📅 {item['date']}</div>
                </div>
            """
            
    html += f"""
            </div>
            <div class="footer">
                <p>본 메일은 설정된 스케줄에 따라 자동 발송되었습니다.</p>
                <p>© 2026 관광 뉴스 통합 엔진 | <a href="#" style="color:#999;">알림 설정 변경</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print("Starting daily news collection for email...")
    scraper = TourismScraper()
    news_list = scraper.fetch_all()
    
    print(f"Collected {len(news_list)} items. Generating HTML...")
    html_report = generate_html_report(news_list)
    
    # GitHub Action이 읽을 수 있도록 파일 저장
    with open("daily_news_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    
    # 텍스트 버전도 백업용으로 생성
    with open("daily_news_report.txt", "w", encoding="utf-8") as f:
        for item in news_list[:10]:
            f.write(f"[{item['source']}] {item['title']} - {item['link']}\n")
            
    print("Report files generated successfully.")

if __name__ == "__main__":
    main()
