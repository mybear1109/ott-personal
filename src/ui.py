import streamlit as st
from typing import Dict
from src.auth_user import create_session, create_guest_session, delete_session
from src.data_fetcher import (
    fetch_genres_list,
    fetch_movies_by_category,
    fetch_movies_by_genre,
    search_movie,
    search_person,
    fetch_movies_by_person,
    search_keyword_movies,
    fetch_movies_by_keyword,
    get_movie_director_and_cast,


)
from src.movie_recommend import generate_text_via_api
from src.movie_recommend import get_movie_details, get_trending_movies
from src.auth_user import load_user_preferences, save_user_preferences


# ---------------- CSS 스타일 로드 함수 ----------------
def load_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            color: #1DB954;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 2rem;
            font-weight: 600;
            color: #1DB954;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .movie-card {
            background-color: #282828;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .movie-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #FFFFFF;
        }
        .movie-info {
            font-size: 0.9rem;
            color: #B3B3B3;
        }
        .section-divider {
            margin-top: 2rem;
            margin-bottom: 2rem;
            border-top: 1px solid #333333;
        }
        /* 인증 영역 스타일 */
        .auth-container {
            background: linear-gradient(135deg, #34495E, #2C3E50);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .auth-container p.auth-status {
            font-size: 18px;
            font-weight: bold;
            color: #ECF0F1;
        }
        .auth-button {
            background: linear-gradient(135deg, #3498DB, #2980B9);
            color: white;
            padding: 10px 20px;
            text-align: center;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 12px;
            border: none;
            width: 100%;
            cursor: pointer;
            transition: background 0.3s, transform 0.3s;
        }
        .logout-button {
            background: linear-gradient(135deg, #E74C3C, #C0392B);
        }
        .logout-button:hover {
            background: linear-gradient(135deg, #C0392B, #A93226);
        }
        /* 네비게이션 버튼 스타일 */
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            padding: 10px;
        }
        .nav-button {
            background: linear-gradient(135deg, #2C3E50, #1ABC9C);
            border: none;
            border-radius: 8px;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
        }
        .nav-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.2);
        }
        .nav-button-active {
            background: linear-gradient(135deg, #1ABC9C, #16A085);
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 메인 헤더 출력 ----------------
def main_header():
    st.markdown("<h1 class='main-header'>MovieMind: 당신만의 영화 여정</h1>", unsafe_allow_html=True)

# ---------------- 사용자 인증 함수 ----------------
# ✅ 세션 키 초기화 (앱 실행 시 로그인 상태를 관리)
st.session_state.setdefault("SESSION_ID", None)

def user_authentication():
    """📌 사용자 로그인 및 게스트 모드 처리"""
    session_active = bool(st.session_state["SESSION_ID"])

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    if not session_active:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 로그인", key="login_btn"):
                session_id = create_session()
                if session_id:
                    st.session_state["SESSION_ID"] = session_id
                    st.success("✅ 로그인 성공!")
                    st.experimental_rerun()

        with col2:
            if st.button("🎭 게스트 모드", key="guest_btn"):
                guest_session_id = create_guest_session()
                if guest_session_id:
                    st.session_state["SESSION_ID"] = guest_session_id
                    st.success("✅ 게스트 모드 활성화!")
                    st.experimental_rerun()
                    
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<p class="auth-status">🎬 현재 로그인 상태입니다.</p>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 로그아웃", key="logout_btn"):
                delete_session()  # ✅ 세션 삭제 함수 호출
                st.session_state["SESSION_ID"] = None  # ✅ 세션 상태 초기화
                st.success("🚪 로그아웃 완료!")
                st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def delete_session():
    """📌 사용자 세션 삭제 (로그아웃)"""
    if st.session_state.get("SESSION_ID"):
        st.session_state["SESSION_ID"] = None
        st.success("🚪 로그아웃 완료!")
        st.experimental_rerun()
    else:
        st.warning("⚠ 현재 로그인되어 있지 않습니다.")

# ---------------- 네비게이션 메뉴 함수 ----------------
def navigation_menu():
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "홈"
    
    nav_cols = st.columns(5)
    if nav_cols[0].button("🏠 홈", key="nav_home"):
        st.session_state.selected_page = "홈"
        st.experimental_rerun()
    if nav_cols[1].button("🎬 영화 스타일 선택", key="nav_profile"):
        st.session_state.selected_page = "영화 스타일 선택"
        st.experimental_rerun()
    if nav_cols[2].button("🔍 영화 검색", key="nav_search"):
        st.session_state.selected_page = "영화 검색"
        st.experimental_rerun()
    if nav_cols[3].button("🎞️ 추천 생성", key="nav_generate"):
        st.session_state.selected_page = "추천 생성"
        st.experimental_rerun()
    if nav_cols[4].button("🌟 즐겨찾기", key="nav_favorite"):
        st.session_state.selected_page = "즐겨찾기"
        st.experimental_rerun()
    
    return st.session_state.selected_page


# ---------------- 즐겨찾기 영화 함수 ----------------
def show_favorite_movies():
    st.subheader("🌟 즐겨찾기한 영화")
    session_id = st.session_state.get("SESSION_ID", None)
    account_id = st.secrets.get("ACCOUNT_ID", None)
    if not session_id or not account_id:
        st.warning("로그인 없이도 즐겨찾기한 영화를 볼 수 있습니다.")
        return
    with st.spinner("즐겨찾기한 영화를 불러오는 중..."):
        movies = fetch_movies_by_category("favorite") or []
    if not movies:
        st.warning("즐겨찾기한 영화가 없습니다.")
        return
    for movie in movies[:5]:
        poster_url = movie.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
        st.image(poster_url, width=150, caption=movie.get("title") or "정보없음")
        st.write(f"**{movie.get('title', '정보없음')}** ({movie.get('release_date', '정보없음')})")
        st.write(f"⭐ 평점: {movie.get('vote_average', '정보없음')}/10")
        st.write(f"📜 줄거리: {movie.get('overview', '정보없음')[:150]}...")

# ---------------- 영화 검색 함수 ----------------
def show_movie_search():
    st.subheader("🔍 영화 검색")
    query = st.text_input("검색할 영화를 입력하세요", placeholder="예: 인셉션, 톰 크루즈")
    if st.button("검색", key="search_btn"):
        if not query.strip():
            st.warning("검색어를 입력해주세요!")
            return
        with st.spinner("영화 정보를 검색하는 중..."):
            movies = search_movie(query) or []
            actors = search_person(query) or []
            keywords = search_keyword_movies(query) or []
        # 배우 선택 및 영화 검색 결과 추가
        if actors:
            actor_dict = {actor["id"]: actor["name"] for actor in actors}
            selected_actor = st.selectbox("출연 배우를 선택하세요", options=list(actor_dict.keys()), format_func=lambda x: actor_dict[x])
            if selected_actor:
                movies.extend(fetch_movies_by_person(selected_actor))
        # 키워드 선택 및 영화 검색 결과 추가
        if keywords:
            keyword_dict = {keyword["id"]: keyword["name"] for keyword in keywords}
            selected_keyword = st.selectbox("키워드를 선택하세요", options=list(keyword_dict.keys()), format_func=lambda x: keyword_dict[x])
            if selected_keyword:
                movies.extend(fetch_movies_by_keyword(selected_keyword))
        if not movies:
            st.warning(f"'{query}'와 관련된 영화가 없습니다.")
            return
        for movie in movies:
            # Assume get_movie_details() returns a dict with keys including "poster_path", "title", etc.

            # Helper function to ensure full URL for images
            def get_full_image_url(url: str) -> str:
                if url and url.startswith("/"):
                    return f"https://image.tmdb.org/t/p/w500{url}"
                return url

            details = get_movie_details(movie["id"])
            if details:
                poster_url = details.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
                poster_url = get_full_image_url(poster_url)
                st.image(poster_url, width=150, caption=details.get("title") or "정보없음")
                st.write(f"**{details.get('title', '정보없음')}** ({details.get('release_date', '정보없음')})")
                st.write(f"⭐ 평점: {details.get('vote_average', '정보없음')}/10")
                st.write(f"📜 줄거리: {details.get('overview', '정보없음')[:150]}...")
# ---------------- 맞춤 추천 생성 함수 ----------------
def show_generated_recommendations():
    st.subheader("🎬 맞춤 영화 추천 생성")
    user_profile = st.session_state.get("user_profile", {})
    preferred_genres = ", ".join(user_profile.get("preferred_genres", [])) if user_profile.get("preferred_genres") else "없음"
    preferred_styles = ", ".join(st.session_state.get("preferred_styles", [])) if st.session_state.get("preferred_styles") else "없음"
    
    additional_info = st.text_area("추가 정보를 입력하세요", placeholder="예: 최근 개봉한 영화 위주, 인기 영화 등")
    
    prompt = f"""
    영화의 전체 상세 정보를 출력합니다.
    fetch_movie_details() 함수를 호출하여 영화의 세부 정보를 가져오고, 이미지, 제목, 개봉일, 평점, 줄거리, 감독, 출연진 등을 출력합니다.
    사용자가 선호하는 장르는 {preferred_genres}입니다.
    추가 정보: {additional_info}
    위의 방식으로, 다음 카테고리별로 각각 5개씩, 총 25개의 영화를 추천해 주세요:
    - 장르별 영화 추천 5개,
    - 영화 스타일별 추천 5개,
    - 지금까지 본 영화 기반 추천 5개,
    - 좋아하는 영화 기반 추천 5개,
    - 검색 키워드 기반 추천 5개.
        """
    st.write("생성된 추천 프롬프트:")
    st.code(prompt)
    result = generate_text_via_api(prompt)
    st.markdown("### 추천 결과")
    st.write(result)



# ---------------- 푸터 출력 함수 ----------------
def show_footer():
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    footer_html = """
    <div style='text-align: center; color: #B3B3B3; padding: 1rem;'>
        <p>© 2025 MovieMind. All rights reserved.</p>
        <p>Developed by <a href="https://github.com/mybear1109" style="color: #9A2EFE; text-decoration: none;">mybear1109 😻</a></p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# ---------------- 프로필 설정 함수 (UI 내에서 정의) ----------------
def show_profile_setup():
    st.subheader("🔰 선호하는 영화 스타일을 선택해주세요!")
    with st.spinner("선호하는 영화 스타일을 추천하는 중...⏳"):
        from src.data_fetcher import fetch_genres_list, fetch_movies_by_genre
        genre_data = fetch_genres_list()
        genre_dict = {genre["id"]: genre["name"] for genre in genre_data if isinstance(genre, dict)}
        genre_list = list(genre_dict.values()) if genre_dict else ["액션", "코미디", "드라마", "SF", "스릴러"]

        selected_genres = st.multiselect("🎭 선호하는 장르를 선택하세요", genre_list)
        movie_titles = []
        if selected_genres:
            genre_ids = [key for key, value in genre_dict.items() if value in selected_genres]
            movies = []
            for genre_id in genre_ids:
                movies.extend(fetch_movies_by_genre(genre_id) or [])
            movie_titles = [movie.get("title") or "정보없음" for movie in movies]

        watched_movies = st.multiselect("📌 지금까지 본 영화를 선택하세요", movie_titles)
        favorite_movies = st.multiselect("🌟 좋아하는 영화를 선택하세요", movie_titles)
        additional_choices = [
            "감동적인", "긴장감 있는", "로맨틱한", "현실적인", "코미디 요소", "강렬한 액션", "미스터리한",
            "예술적인", "비주얼이 뛰어난", "기발한 설정", "다큐멘터리 스타일", "실화 기반", "철학적인"
        ]
        preferred_styles = st.multiselect("✨ 추가로 원하는 영화 스타일을 선택하세요", additional_choices)
        
        if st.button("저장하기"):
            save_user_preferences(watched_movies, favorite_movies, selected_genres, preferred_styles)
            st.success("🎉 프로필이 저장되었습니다! 이제 맞춤형 추천을 받을 수 있어요.")

