import streamlit as st

# 반드시 모든 Streamlit 호출 전에 set_page_config() 호출
st.set_page_config(
    page_title="MovieMind: 당신만의 영화 여정",
    page_icon="🎬",
    layout="wide"
)

import random
import importlib
import src.data_fetcher
import src.auth
import src.recommender
import src.user_profile
import src.ui
import src.home



# 이후에 CSS, 헤더, 인증, 네비게이션 등의 코드 작성
st.markdown("""
<style>
    .main-header {font-size: 3rem; font-weight: 700; color: #1DB954; text-align: center; margin-bottom: 2rem;}
    .sub-header {font-size: 2rem; font-weight: 600; color: #1DB954; margin-top: 2rem; margin-bottom: 1rem;}
    .movie-card {background-color: #282828; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;}
    .movie-title {font-size: 1.2rem; font-weight: 600; color: #FFFFFF;}
    .movie-info {font-size: 0.9rem; color: #B3B3B3;}
    .section-divider {margin-top: 2rem; margin-bottom: 2rem; border-top: 1px solid #333333;}
    .stButton>button {background-color: #1DB954; color: white;}
    .stButton>button:hover {background-color: #1ED760;}
</style>
""", unsafe_allow_html=True)
# 메인 헤더
st.markdown("<h1 class='main-header'>MovieMind: 당신만의 영화 여정</h1>", unsafe_allow_html=True)

# ---------------- 사용자 인증 ----------------
session_active = "SESSION_ID" in st.session_state and st.session_state["SESSION_ID"]

if not session_active:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 로그인"):
            try:
                session_id = src.auth.create_session()
                if session_id:
                    st.session_state["SESSION_ID"] = session_id
                    st.success("✅ 로그인 성공!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ 로그인 오류: {e}")
    with col2:
        if st.button("🎭 게스트 모드"):
            try:
                guest_session_id = src.auth.create_guest_session()
                if guest_session_id:
                    st.session_state["SESSION_ID"] = guest_session_id
                    st.success("✅ 게스트 모드 활성화!")
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ 게스트 로그인 오류: {e}")
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.success("🎬 현재 로그인 상태입니다.")
    with col2:
        if st.button("🚪 로그아웃"):
            try:
                src.auth.delete_session()
                del st.session_state["SESSION_ID"]
                st.success("🚪 로그아웃 완료!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ 로그아웃 오류: {e}")

# ---------------- 상단 네비게이션 메뉴 (버튼) ----------------
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

# 기본적으로 홈 화면을 표시하도록 초기값 설정
show_home = True  
show_search = show_favorites = show_profile = False

with nav_col1:
    if st.button("🏠 홈"):
        show_home = True
        show_search = show_favorites = show_profile = False
with nav_col2:
    if st.button("🎬 영화 스타일 선택"):
        show_profile = True
        show_home = show_search = show_favorites = False
with nav_col3:
    if st.button("🔍 영화 검색"):
        show_search = True
        show_home = show_favorites = show_profile = False
with nav_col4:
    if st.button("🌟 즐겨찾기"):
        show_favorites = True
        show_home = show_search = show_profile = False

# ---------------- 페이지별 콘텐츠 출력 ----------------
if show_home:
    src.home.show_home_page()  # 홈 페이지 (추천 영화, 트렌딩 영화 등)
elif show_profile:
    src.ui.show_profile_setup()  # 영화 스타일 선택 페이지
elif show_search:
    src.ui.show_movie_search()   # 영화 검색 페이지
elif show_favorites:
    src.ui.show_favorite_movies()  # 즐겨찾기 페이지


# ---------------- 푸터 ----------------
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
footer_html = """
<style>
    .footer {
        text-align: center;
        color: #B3B3B3;
        padding: 1rem;
        margin-top: 2rem;
    }
    .footer a {
        color: #9A2EFE;
        padding: 1rem;
        margin-top: 2rem;
        text-decoration: none;
    }
    .footer a:hover {
        color: #170B3B;
    }
</style>
<div class='footer'>
    <p>© 2025 MovieMind. All rights reserved.</p>
    <p>Developed with by <a href="https://github.com/mybear1109">mybear1109 😻</a></p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)


