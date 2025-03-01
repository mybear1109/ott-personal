import streamlit as st
from src.data_fetcher import (
    fetch_movies_by_category, fetch_genres_list, fetch_movies_by_genre,
    search_movie, search_person, fetch_movies_by_person,
    search_keyword_movies, fetch_movies_by_keyword, get_movie_director_and_cast
)
from src.recommender import get_trending_movies, get_personalized_recommendations
from src.user_profile import save_user_preferences, load_user_preferences
from src.auth import create_session, delete_session, create_guest_session
import random
import importlib


# ----------------- 영화 상세 정보(감독 & 출연진) 출력 함수 -----------------
def show_movie_details(movie):
    """
    영화 상세 정보를 출력.
    감독은 전체 목록, 출연진은 최대 5명까지 출력.
    """
    movie_id = movie.get("id")
    if not movie_id:
        st.write("상세 정보가 없습니다. 정보없음.")
        return

    directors, cast = get_movie_director_and_cast(movie_id)
    """
    특정 영화의 감독과 출연진 정보를 반환합니다.
    fetch_movie_credits() 함수를 이용하여 감독(directors)와 배우(cast) 목록을 추출합니다.
    """
    director_names = ", ".join([d.get("name", "정보없음") for d in directors]) if directors else "정보없음"
    cast_names = ", ".join([c.get("name", "정보없음") for c in cast[:5]]) if cast else "정보없음"
    
    st.write(f"**감독:** {director_names}")
    st.write(f"**출연진:** {cast_names}")



# ----------------- 홈 페이지 -----------------
def show_home_page():
    st.markdown("<h2 class='sub-header'>🍿 오늘의 추천 영화</h2>", unsafe_allow_html=True)
    movies = get_trending_movies()
    if movies:
        cols = st.columns(5)
        for idx, movie in enumerate(movies[:5]):
            with cols[idx]:
                poster_url = movie.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
                st.image(poster_url, use_column_width=True)
                title = movie.get("title") or "정보없음"
                vote = movie.get("vote_average")
                vote_str = f"⭐ {vote}/10" if vote is not None else "정보없음"
                st.markdown(f"<p class='movie-title'>{title}</p><p class='movie-info'>{vote_str}</p>", unsafe_allow_html=True)
    else:
        st.warning("추천 영화를 불러오는 데 문제가 발생했습니다. 정보없음.")



# ----------------- 사용자 프로필 설정 -----------------
def show_profile_setup():
    st.subheader("🔰 선호하는 영화 스타일을 선택해주세요!")
    with st.spinner("선호하는 영화 스타일을 추천하는 중...⏳"):
        # 장르 리스트 가져오기
        genre_data = fetch_genres_list()
        genre_dict = {genre["id"]: genre["name"] for genre in genre_data if isinstance(genre, dict)}
        genre_list = list(genre_dict.values()) if genre_dict else ["액션", "코미디", "드라마", "SF", "스릴러"]

        # 선호하는 장르 선택
        selected_genres = st.multiselect("🎭 선호하는 장르를 선택하세요", genre_list)

        # 선택한 장르에 맞는 영화 목록(제목) 가져오기
        movie_titles = []
        if selected_genres:
            genre_ids = [key for key, value in genre_dict.items() if value in selected_genres]
            movies = []
            for genre_id in genre_ids:
                movies.extend(fetch_movies_by_genre(genre_id) or [])
            movie_titles = [movie.get("title") or "정보없음" for movie in movies]

        # 지금까지 본 영화 선택
        watched_movies = st.multiselect("📌 지금까지 본 영화를 선택하세요", movie_titles)

        # 좋아하는 영화 선택
        favorite_movies = st.multiselect("🌟 좋아하는 영화를 선택하세요", movie_titles)

        # 추가적인 영화 취향 선택
        additional_choices = [
            "감동적인", "긴장감 있는", "로맨틱한", "현실적인", "코미디 요소", "강렬한 액션", "미스터리한",
            "예술적인", "비주얼이 뛰어난", "기발한 설정", "다큐멘터리 스타일", "실화 기반", "철학적인"
        ]
        preferred_styles = st.multiselect("✨ 추가로 원하는 영화 스타일을 선택하세요", additional_choices)

        # 사용자 선택 정보 저장
        if st.button("저장하기"):
            save_user_preferences(watched_movies, favorite_movies, selected_genres)
            st.session_state["preferred_styles"] = preferred_styles
            st.success("🎉 프로필이 저장되었습니다! 이제 맞춤형 추천을 받을 수 있어요.")

# ----------------- 추천 영화 목록 -----------------
def show_recommendations():
    st.subheader("📌 당신을 위한 추천 영화")
    with st.spinner("추천 영화를 가져오는 중...⏳"):
        movies = get_trending_movies() or []
    if not movies:
        st.warning("추천할 영화가 없습니다. 정보없음.")
        return
    if "show_movie_count" not in st.session_state:
        st.session_state["show_movie_count"] = 5
    show_count = st.session_state["show_movie_count"]
    for movie in movies[:show_count]:
        poster_url = movie.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
        st.image(poster_url, width=150, caption=movie.get("title") or "정보없음")
        title = movie.get("title") or "정보없음"
        release_date = movie.get("release_date") or "정보없음"
        vote = movie.get("vote_average")
        vote_str = f"⭐ 평점: {vote}/10" if vote is not None else "정보없음"
        overview = movie.get("overview") or "정보없음"
        st.write(f"**{title}** ({release_date})")
        st.write(vote_str)
        st.write(f"📜 줄거리: {overview[:150]}...")
    if show_count < len(movies):
        if st.button("더 보기"):
            st.session_state["show_movie_count"] += 5
            st.experimental_rerun()



# ----------------- 영화 검색 -----------------
def show_movie_search():
    st.subheader("🔍 영화 검색")
    query = st.text_input("검색할 내용을 입력하세요", placeholder="예: 인셉션, 톰 크루즈, 액션, 우주 탐사")
    if st.button("검색"):
        if not query.strip():
            st.warning("검색어를 입력해주세요!")
            return
        with st.spinner("영화 정보를 검색하는 중...⏳"):
            movies = search_movie(query) or []
            actors = search_person(query) or []
            keywords = search_keyword_movies(query) or []
        # 배우 선택 UI 개선
        if actors:
            actor_dict = {actor["id"]: actor["name"] for actor in actors}
            selected_actor = st.selectbox("출연 배우를 선택하세요", options=list(actor_dict.keys()), format_func=lambda x: actor_dict[x])
            if selected_actor:
                movies.extend(fetch_movies_by_person(selected_actor))
        # 키워드 선택 UI 개선
        if keywords:
            keyword_dict = {keyword["id"]: keyword["name"] for keyword in keywords}
            selected_keyword = st.selectbox("키워드를 선택하세요", options=list(keyword_dict.keys()), format_func=lambda x: keyword_dict[x])
            if selected_keyword:
                movies.extend(fetch_movies_by_keyword(selected_keyword))
        if not movies:
            st.warning(f"'{query}'와 관련된 영화가 없습니다. 정보없음.")
            return
        if "num_display" not in st.session_state:
            st.session_state["num_display"] = 10
        num_display = st.session_state["num_display"]
        for movie in movies[:num_display]:
            poster_url = movie.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
            st.image(poster_url, width=150, caption=movie.get("title") or "정보없음")
            title = movie.get("title") or "정보없음"
            release_date = movie.get("release_date") or "정보없음"
            vote = movie.get("vote_average")
            vote_str = f"⭐ 평점: {vote}/10" if vote is not None else "정보없음"
            overview = movie.get("overview") or "정보없음"
            st.write(f"**{title}** ({release_date})")
            st.write(vote_str)
            st.write(f"📜 줄거리: {overview[:150]}...")
        if num_display < len(movies):
            if st.button("더 보기"):
                st.session_state["num_display"] += 10
                st.experimental_rerun()



# ----------------- 즐겨찾기한 영화 목록 -----------------
def show_favorite_movies():
    st.subheader("🌟 즐겨찾기한 영화")
    session_id = st.session_state.get("SESSION_ID", None)
    account_id = st.secrets.get("ACCOUNT_ID", None)
    if not session_id or not account_id:
        st.warning("로그인 없이도 즐겨찾기한 영화를 볼 수 있습니다. 정보없음.")
    with st.spinner("즐겨찾기한 영화를 불러오는 중...⏳"):
        movies = fetch_movies_by_category("favorite") or []
    if not movies:
        st.warning("즐겨찾기한 영화가 없습니다. 정보없음.")
        return
    for movie in movies[:5]:
        poster_url = movie.get("poster_path") or "https://via.placeholder.com/500x750?text=정보없음"
        st.image(poster_url, width=150, caption=movie.get("title") or "정보없음")
        title = movie.get("title") or "정보없음"
        release_date = movie.get("release_date") or "정보없음"
        vote = movie.get("vote_average")
        vote_str = f"⭐ 평점: {vote}/10" if vote is not None else "정보없음"
        overview = movie.get("overview") or "정보없음"
        st.write(f"**{title}** ({release_date})")
        st.write(vote_str)
        st.write(f"📜 줄거리: {overview[:150]}...")
