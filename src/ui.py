import streamlit as st
import time
from src.auth_user import (
    create_session, create_guest_session, delete_session, is_user_authenticated
)
from src.data_fetcher import (
    fetch_genres_list, fetch_movies_by_category, fetch_movies_by_genre,
    search_movie, search_person, fetch_movies_by_person,
    search_keyword_movies, fetch_movies_by_keyword,
    get_movie_details,
)
from src.movie_recommend import (
    get_personalized_recommendations, 
    get_mood_based_recommendations, 
    get_movies_by_keyword, get_trending_movies,
    generate_text_via_api
)
from src.auth_user import load_user_preferences, save_user_preferences


# ---------------- CSS 스타일 로드 함수 ----------------
def load_css():
    """📌 UI 스타일 적용"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1DB954;
            text-align: center;
            margin-bottom: 2rem;
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
        .selectbox-label {
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------- 메인 헤더 출력 ----------------
def main_header():
    """📌 메인 페이지 헤더"""
    st.markdown("<h1 class='main-header'>MovieMind: 당신만의 영화 여정</h1>", unsafe_allow_html=True)
# ---------------- 네비게이션 메뉴 함수 ----------------
def navigation_menu():
    """📌 네비게이션 메뉴 (로그인 여부에 따라 다르게 표시)"""
    logged_in = bool(st.session_state.get("SESSION_ID"))

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "홈"

    nav_cols = st.columns(5)

    if not logged_in:
        if nav_cols[0].button("🏠 홈"):
            st.session_state["selected_page"] = "홈"
            st.rerun()
    else:
        if nav_cols[0].button("🎬 사용자 페이지"):
            st.session_state["selected_page"] = "사용자 페이지"
            st.rerun()

    if nav_cols[1].button("🌟 즐겨찾기"):
        st.session_state["selected_page"] = "즐겨찾기"
        st.rerun()
    if nav_cols[2].button("🎬 영화 스타일 선택"):
        st.session_state["selected_page"] = "영화 스타일 선택"
        st.rerun()
    if nav_cols[3].button("🎞️ 추천 생성"):
        st.session_state["selected_page"] = "추천 생성"
        st.rerun()

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




# ---------------- 프로필 설정 함수 ----------------
def show_profile_setup():
    """📌 사용자 프로필 설정"""
    st.subheader("🔰 선호하는 영화 스타일을 선택해주세요!")
    
    with st.spinner(" 영화 스타일 정보를 불러오는 중...⏳"):
        time.sleep(2)  # ✅ 로딩 효과 추가
        from src.data_fetcher import fetch_genres_list, fetch_movies_by_genre
        genre_data = fetch_genres_list()
        genre_dict = {genre["id"]: genre["name"] for genre in genre_data if isinstance(genre, dict)}
        genre_list = list(genre_dict.values()) if genre_dict else ["액션", "코미디", "드라마", "SF", "스릴러"]

    # ✅ 사용자가 선택할 수 있는 옵션
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
    
    if st.button("💾 저장하기"):
        save_user_preferences(watched_movies, favorite_movies, selected_genres, preferred_styles)
        st.success("🎉 프로필이 저장되었습니다! 이제 맞춤형 추천을 받을 수 있어요.")

# ---------------- 기분에 따른 추천 ----------------
def show_mood_based_recommendations():
    """🌟 사용자의 기분에 따른 영화 추천"""
    st.subheader("🌟 기분에 따른 영화 추천")

    mood_dict = {
        "행복한": [35, 10751],
        "슬픈": [18, 10749],
        "신나는": [28, 12],
        "로맨틱한": [10749, 35],
        "무서운": [27, 53],
        "신비로운": [9648, 80],
        "판타지": [14, 12],
        "편안한": [99, 10770],
        "향수를 불러일으키는": [10752, 36],
        "SF": [878, 28]
    }

    selected_mood = st.selectbox("오늘 기분은?", list(mood_dict.keys()))
    genre_ids = mood_dict.get(selected_mood, [])

    mood_movies = []
    for genre_id in genre_ids:
        mood_movies.extend(fetch_movies_by_genre(genre_id))

    if not mood_movies:
        st.warning(f"❌ {selected_mood} 분위기의 추천 영화가 없습니다. 다른 기분을 선택해 보세요!")
        return

    for movie in mood_movies[:5]:
        poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image"
        st.image(poster_url, use_container_width=True, caption=movie.get("title", "Unknown"))
        st.write(f"**{movie.get('title', 'Unknown')}** ({movie.get('release_date', 'Unknown')[:4]})")



# ---------------- 영화 검색 함수 ----------------
def show_movie_search():
    st.subheader("🔍 영화 검색")
    
    # 🔎 검색 입력 받기
    query = st.text_input("검색할 영화를 입력하세요", placeholder="예: 인셉션, 톰 크루즈")
    
    # ✅ '검색 결과' 상태를 저장할 공간 (초기화)
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
        st.session_state.display_count = 10  # 초기에 표시할 영화 개수

    if st.button("검색", key="search_btn"):
        if not query.strip():
            st.warning("❌ 검색어를 입력해주세요!")
            return
        
        with st.spinner("영화 정보를 검색하는 중...⏳"):
            time.sleep(2)  # ✅ 로딩 효과 추가
            movies = search_movie(query) or []
            actors = search_person(query) or []
            keywords = search_keyword_movies(query) or []

        # ✅ 배우 선택 및 영화 검색 결과 추가
        if actors:
            actor_dict = {actor["id"]: actor["name"] for actor in actors}
            selected_actor = st.selectbox(
                "🎭 출연 배우를 선택하세요",
                options=list(actor_dict.keys()),
                format_func=lambda x: actor_dict[x]
            )
            if selected_actor:
                movies.extend(fetch_movies_by_person(selected_actor))

        # ✅ 키워드 선택 및 영화 검색 결과 추가
        if keywords:
            keyword_dict = {keyword["id"]: keyword["name"] for keyword in keywords}
            selected_keyword = st.selectbox(
                "🔑 키워드를 선택하세요",
                options=list(keyword_dict.keys()),
                format_func=lambda x: keyword_dict[x]
            )
            if selected_keyword:
                movies.extend(fetch_movies_by_keyword(selected_keyword))

        # ✅ 검색 결과 저장
        if movies:
            st.session_state.search_results = movies
            st.session_state.display_count = 10  # 결과 초기화
        else:
            st.warning(f"❌ '{query}'와 관련된 영화가 없습니다.")
    
    # ✅ 검색 결과 표시
    if st.session_state.search_results:
        st.markdown("### 🎬 검색 결과")

        # ✅ 처음 10개만 표시 (더보기 버튼 클릭 시 확장)
        displayed_movies = st.session_state.search_results[: st.session_state.display_count]

        for movie in displayed_movies:
            details = get_movie_details(movie["id"])
            if details:
                poster_url = f"https://image.tmdb.org/t/p/w500{details.get('poster_path', '')}" if details.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image"
                st.image(poster_url, width=150, caption=details.get("title", "정보없음"))
                st.write(f"**{details.get('title', '정보없음')}** ({details.get('release_date', '정보없음')})")
                st.write(f"⭐ 평점: {details.get('vote_average', '정보없음')}/10")
                st.write(f"📜 줄거리: {details.get('overview', '정보없음')[:150]}...")
                st.write("---")

        # ✅ "더보기" 버튼 (남은 영화가 있을 경우)
        if st.session_state.display_count < len(st.session_state.search_results):
            if st.button("➕ 더보기", key="load_more_btn"):
                st.session_state.display_count += 10  # 10개씩 추가 표시
                st.experimental_rerun()  # UI 업데이트

# ---------------- 맞춤 추천 생성 함수 ----------------
def show_generated_recommendations():
    """📌 맞춤형 영화 추천 생성"""
    st.subheader("🎬 맞춤 영화 추천 생성")
    
    # ✅ 사용자 프로필 로드
    user_preferences = st.session_state.get("user_profile", {})
    
    # ✅ 사용자 데이터 확인
    selected_genres = ", ".join(user_preferences.get("preferred_genres", [])) if user_preferences.get("preferred_genres") else None
    preferred_styles = ", ".join(user_preferences.get("preferred_styles", [])) if user_preferences.get("preferred_styles") else None
    watched_movies = user_preferences.get("watched_movies", [])
    favorite_movies = user_preferences.get("favorite_movies", [])

    # ✅ 추가 정보 입력
    additional_info = st.text_area("📝 추가 정보를 입력하세요", placeholder="예: 최근 개봉한 영화 위주, 인기 영화 등")

    # ✅ 사용자 정보 또는 추가 정보가 없는 경우 경고
    if not (selected_genres or preferred_styles or watched_movies or favorite_movies or additional_info.strip()):
        st.warning("⚠️ 사용자 정보 또는 추가 정보를 입력해 주세요. 최소한 하나의 정보를 제공해야 합니다.")
        return

    # ✅ "추천 생성" 버튼
    if st.button("🎬 추천 생성", key="generate_btn"):
        with st.spinner("⏳ 추천 영화를 찾는 중... 잠시만 기다려 주세요!"):
            time.sleep(2)  # ✅ 로딩 효과
            
            # ✅ 추천 결과 초기화
            recommendations = {}

            # ✅ 1. 장르 기반 추천 (사용자 정보가 있을 경우)
            if selected_genres:
                recommendations["장르별 추천"] = get_personalized_recommendations(user_preferences)[:5]

            # ✅ 2. 영화 스타일 기반 추천 (사용자 정보가 있을 경우)
            if preferred_styles:
                recommendations["영화 스타일별 추천"] = get_mood_based_recommendations(preferred_styles)[:5]

            # ✅ 3. 지금까지 본 영화 기반 추천 (사용자 정보가 있을 경우)
            if watched_movies:
                recommendations["지금까지 본 영화 기반 추천"] = get_movies_by_keyword(watched_movies[0])[:5]  # ✅ 첫 번째 영화 키워드 검색

            # ✅ 4. 좋아하는 영화 기반 추천 (사용자 정보가 있을 경우)
            if favorite_movies:
                recommendations["좋아하는 영화 기반 추천"] = get_movies_by_keyword(favorite_movies[0])[:5]  # ✅ 첫 번째 영화 키워드 검색

            # ✅ 추가 입력한 키워드 기반 추천 (사용자 정보가 없더라도 가능)
            if additional_info.strip():
                print(f"🔎 검색 키워드: {additional_info.strip()}")  # 디버깅용 로그 출력
                recommendations["검색 키워드 기반 추천"] = get_movies_by_keyword(additional_info.strip())[:5]

                # ✅ 검색 결과가 없을 경우 대체 추천 제공
                if not recommendations["검색 키워드 기반 추천"]:
                    st.warning(f"🔎 '{additional_info.strip()}'에 대한 영화가 없습니다. 대신 최신 영화를 추천해드립니다!")
                    recommendations["최신 개봉 영화 추천"] = get_trending_movies()[:5]

            # ✅ 결과 출력
            st.markdown("### 🎥 추천된 영화 목록")

            for category, movies in recommendations.items():
                if movies:
                    st.markdown(f"#### 🔹 {category}")
                    for movie in movies:
                        st.write(f"**🎬 {movie['title']}**")
                        st.write(f"📜 {movie['overview']}\n")
                else:
                    st.markdown(f"#### 🔹 {category}")
                    st.warning("❌ 관련 추천 영화가 없습니다.")

        st.success("✅ 추천이 완료되었습니다!")


# ---------------- 푸터 출력 함수 ----------------
def show_footer():
    """📌 푸터"""
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #B3B3B3; padding: 1rem;'>
        <p>© 2025 MovieMind. All rights reserved.</p>
        <p>Developed by <a href="https://github.com/mybear1109" style="color: #9A2EFE; text-decoration: none;">mybear1109 😻</a></p>
    </div>
    """, unsafe_allow_html=True)
