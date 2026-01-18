import streamlit as st
import pandas as pd
from scrapers import TourismScraper
from datetime import datetime
import re

# 페이지 설정
st.set_page_config(
    page_title="대한민국 관광 뉴스 통합 대시보드 v2.0",
    page_icon="🇰🇷",
    layout="wide"
)

# 커스텀 CSS (Premium Feel & Keyword Highlighting)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .news-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
        border-left: 6px solid #007bff;
        position: relative;
        overflow: hidden;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        border-left-color: #0056b3;
    }
    
    .source-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 소스별 태그 색상 */
    .tag-visitseoul { background-color: #E3F2FD; color: #1976D2; }
    .tag-visitkorea { background-color: #F3E5F5; color: #7B1FA2; }
    .tag-ggtour { background-color: #E8F5E9; color: #388E3C; }
    .tag-mcst { background-color: #FFF3E0; color: #E65100; }
    .tag-busan { background-color: #E0F2F1; color: #00796B; }
    .tag-jeju { background-color: #FCE4EC; color: #C2185B; }
    .tag-incheon { background-color: #E8EAF6; color: #303F9F; }
    .tag-gangwon { background-color: #F1F8E9; color: #558B2F; }
    .tag-gyeongbuk { background-color: #EFEBE9; color: #5D4037; }
    
    .news-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.6rem;
        text-decoration: none;
        display: block;
        line-height: 1.4;
    }
    
    .news-title:hover {
        color: #007bff;
    }
    
    .news-date {
        font-size: 0.85rem;
        color: #888;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* 키워드 하이라이트 스타일 */
    .highlight {
        background: linear-gradient(120deg, #fff176 0%, #fff176 100%);
        background-repeat: no-repeat;
        background-size: 100% 40%;
        background-position: 0 90%;
        padding: 0 2px;
        font-weight: 700;
        color: #d32f2f;
    }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# 강조할 키워드 목록
HIGHLIGHT_KEYWORDS = ["여행", "참여", "숙박", "호텔", "할인", "이벤트", "축제", "패키지", "쿠폰"]

def highlight_text(text):
    """제목 내 주요 키워드에 하이라이트 적용"""
    for keyword in HIGHLIGHT_KEYWORDS:
        if keyword in text:
            # 대소문자 구분 없이 강조 (한국어는 해당 없으나 패턴 유지를 위해)
            pattern = re.compile(f"({keyword})", re.IGNORECASE)
            text = pattern.sub(r'<span class="highlight">\1</span>', text)
    return text

# 데이터 로딩 함수 (캐싱)
@st.cache_data(ttl=1800) # 30분 캐시
def load_data():
    scraper = TourismScraper()
    return scraper.fetch_all()

# 사이드바 구성
st.sidebar.title("🇰🇷 관광 뉴스 통합 필터")
st.sidebar.markdown("---")

# 검색 및 필터
search_query = st.sidebar.text_input("제목 내 키워드 검색", "")

sources = ["전체", "MCST", "VisitKorea", "VisitSeoul", "GGTour", "Busan", "Jeju", "Incheon", "Gangwon", "Gyeongbuk"]
selected_source = st.sidebar.selectbox("뉴스 소스 선택", sources)

# 새로고침
if st.sidebar.button("데이터 강제 업데이트"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 강조 키워드")
cols = st.sidebar.columns(3)
for i, kw in enumerate(HIGHLIGHT_KEYWORDS):
    cols[i % 3].markdown(f"`{kw}`")

# 메인 화면
st.title("🇰🇷 전국 관광 뉴스 통합 엔진 v2.0")
st.markdown("**중앙 부처 및 8개 지자체**의 실시간 여행, 참여, 할인 정보를 한눈에 확인하세요.")

# 데이터 가져오기
with st.spinner('실시간 전국 관광 정보를 수집하는 중...'):
    all_news = load_data()

if not all_news:
    st.error("데이터를 수집하는 중 오류가 발생했거나 데이터가 없습니다.")
else:
    # 필터링 로직
    filtered_news = all_news
    
    # 소스 필터
    if selected_source != "전체":
        filtered_news = [i for i in filtered_news if i['source'] == selected_source]
    
    # 검색 필터
    if search_query:
        filtered_news = [i for i in filtered_news if search_query.lower() in i['title'].lower()]
    
    # 요약 통계
    c1, c2, c3 = st.columns(3)
    c1.metric("총 수집 뉴스", f"{len(all_news)}건")
    c2.metric("필터링 결과", f"{len(filtered_news)}건")
    c3.metric("활성 소스", f"{len(set(i['source'] for i in all_news))}개")
    
    st.markdown("---")
    
    if not filtered_news:
        st.info("검색 조건에 맞는 뉴스가 없습니다.")
    else:
        # 뉴스 카드 루프
        for item in filtered_news:
            source_class = f"tag-{item['source'].lower()}"
            highlighted_title = highlight_text(item['title'])
            
            st.markdown(f"""
            <div class="news-card">
                <span class="source-tag {source_class}">{item['source']}</span>
                <a href="{item['link']}" target="_blank" class="news-title">{highlighted_title}</a>
                <div class="news-date">📅 {item['date']}</div>
            </div>
            """, unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #999; font-size: 0.85rem; padding: 20px;">
    © 2026 관광 뉴스 통합 엔진 | 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)
