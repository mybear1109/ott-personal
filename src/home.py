import streamlit as st
import random
from src.movie_recommend  import get_trending_movies, get_personalized_recommendations
from src.auth_user import load_user_preferences
from src.data_fetcher import get_movie_director_and_cast, fetch_movie_details

# ---------------- 전역 변수 ----------------
# 전역 변수로 이미 표시된 영화 ID를 저장하여 중복 방지
displayed_movie_ids = set()

# ---------------- 새로운 함수 추가 ----------------
def get_latest_popular_movies():
    """최신 인기 영화 목록을 반환"""
    return get_trending_movies()

def get_current_popular_movies():
    """현재 인기 영화 목록을 반환"""
    return get_trending_movies()

def get_realtime_popular_movies():
    """실시간 인기 영화 목록을 반환"""
    return get_trending_movies()

def show_full_movie_details(movie):
    """
    영화의 전체 상세 정보를 출력
    """
    movie_id = movie.get("id")
    if not movie_id:
        st.write("상세 정보가 없습니다.")
        return

    details = fetch_movie_details(movie_id)
    if not details:
        st.write("상세 정보가 없습니다.")
        return

    title = details.get("title", "제목 없음")
    release_date = details.get("release_date", "정보 없음")
    vote_average = details.get("vote_average", "정보 없음")
    overview = details.get("overview", "줄거리 없음")
    
    # 감독 및 출연진 정보 가져오기
    directors, cast = get_movie_director_and_cast(movie_id)
    director_str = ", ".join(directors) if directors else "정보 없음"
    cast_str = ", ".join(cast[:10]) if cast else "정보 없음"

    # 상세 정보 출력
    st.markdown(f"### {title}")
    st.write(f"**개봉일:** {release_date}")
    st.write(f"**평점:** {vote_average}/10")
    st.write(f"**줄거리:** {overview}")
    if director_str != "정보 없음":
        st.write(f"**감독:** {director_str}")
    if cast_str != "정보 없음":
        st.write(f"**출연진:** {cast_str}")

def show_movie_section(title, movies):
    st.markdown(f"<h2 class='sub-header'>{title}</h2>", unsafe_allow_html=True)
    if movies:
        selected_movies = random.sample(movies, min(5, len(movies)))
        cols = st.columns(5)
        for idx, movie in enumerate(selected_movies):
            with cols[idx]:
                if not movie.get("directors") or not movie.get("cast"):
                    directors, cast_list = get_movie_director_and_cast(movie.get("id"))
                    movie["directors"] = [d.get("name", "정보 없음") for d in directors] if directors else ["정보 없음"]
                    movie["cast"] = [c.get("name", "정보 없음") for c in cast_list] if cast_list else ["정보 없음"]
                poster_url = movie.get("poster_path", "https://via.placeholder.com/500x750?text=No+Image")
                title = movie.get("title", "제목 없음")
                rating = movie.get("vote_average", "N/A")
                release_date = movie.get("release_date", "정보 없음")
                director_names = ", ".join(movie.get("directors", ["정보 없음"]))
                cast_names = ", ".join(movie.get("cast", ["정보 없음"])[:3])
                overview = movie.get("overview", "줄거리 없음")[:100] + "..."
                
                director_html = f"<p class='movie-info'>🎬 감독: {director_names}</p>" if director_names != "정보 없음" else ""
                cast_html = f"<p class='movie-info'>👥 출연진: {cast_names}</p>" if cast_names != "정보 없음" else ""
                
                st.image(poster_url, width=250, use_container_width=False)
                st.markdown(f"""
                <div class='movie-card'>
                    <p class='movie-title'>{title}</p>
                    <p class='movie-info'>⭐ 평점: {rating}/10</p>
                    <p class='movie-info'>🗓 개봉일: {release_date}</p>
                    <p class='movie-info'>📜 줄거리: {overview}</p>
                    {director_html}
                    {cast_html}
                </div>
                """, unsafe_allow_html=True)
                with st.expander("자세히 보기"):
                    show_full_movie_details(movie)
    else:
        st.warning(f"{title}를 불러오는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")

def show_home_page():
    """홈페이지에서 영화 섹션을 표시하는 함수"""
    # ✅ 트렌딩 영화 섹션
    show_movie_section("🔝 트렌드 영화", get_trending_movies())
    
    # ✅ 최신 인기 영화 섹션
    show_movie_section("🚀 최신 인기 영화", get_latest_popular_movies())
    
    # ✅ 현재 인기 영화 섹션
    show_movie_section("🎥 현재 인기 영화", get_current_popular_movies())
    
    # ✅ 실시간 인기 영화 섹션
    show_movie_section("📈 실시간 인기 영화", get_realtime_popular_movies())
    
    # ✅ 맞춤형 추천 영화 섹션
    user_profile = load_user_preferences()
    recommended_movies = get_personalized_recommendations(user_profile) if user_profile else []
    show_movie_section("🍿 오늘의 추천 영화", recommended_movies)
