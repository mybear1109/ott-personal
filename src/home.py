import streamlit as st
import random  # 랜덤 샘플링을 위한 모듈
import importlib
import src.data_fetcher 
from src.auth import create_session, delete_session, create_guest_session, create_session
from src.recommender import get_trending_movies, get_personalized_recommendations
from src.user_profile import load_user_preferences
# 추가: 영화 감독 및 출연진 정보를 가져오는 함수와 영화 상세 정보를 가져오는 함수
from src.data_fetcher import get_movie_director_and_cast, fetch_movie_details

importlib.reload(src.data_fetcher)


# ---------------- 영화 상세 정보 전체 출력 함수 ----------------
def show_full_movie_details(movie):
    """
    영화의 전체 상세 정보를 출력합니다.
    fetch_movie_details()를 호출하여 영화의 세부 정보를 가져오고,
    제목, 개봉일, 평점, 줄거리, 감독, 출연진 등을 출력합니다.
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
    
    credits = details.get("credits", {})
    directors = [member.get("name", "정보 없음") for member in credits.get("crew", []) if member.get("job") == "Director"]
    director_str = ", ".join(directors) if directors else "정보 없음"
    cast = [member.get("name", "정보 없음") for member in credits.get("cast", [])]
    cast_str = ", ".join(cast[:10]) if cast else "정보 없음"
    
    st.markdown(f"### {title}")
    st.write(f"**개봉일:** {release_date}")
    st.write(f"**평점:** {vote_average}/10")
    st.write(f"**줄거리:** {overview}")
    if director_str != "정보 없음":
        st.write(f"**감독:** {director_str}")
    if cast_str != "정보 없음":
        st.write(f"**출연진:** {cast_str}")

# ---------------- 메인 페이지: 추천 영화 & 트렌딩 영화 ----------------
def show_home_page():
    # 추천 영화 섹션
    st.markdown("<h2 class='sub-header'>🍿 오늘의 추천 영화</h2>", unsafe_allow_html=True)
    user_profile = load_user_preferences()
    movies = get_personalized_recommendations(user_profile) if user_profile else get_trending_movies()
    if movies:
        selected_movies = random.sample(movies, min(5, len(movies)))  # 랜덤 5개 선택
        rec_cols = st.columns(5)
        for idx, movie in enumerate(selected_movies):
            with rec_cols[idx]:
                # 영화 객체에 감독 및 출연진 정보가 없으면 추가
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
                
                # 감독 또는 출연진 정보가 "정보 없음"이면 해당 라인을 빈 문자열로 처리
                director_html = f"<p class='movie-info'>🎬 감독: {director_names}</p>" if director_names != "정보 없음" else ""
                cast_html = f"<p class='movie-info'>👥 출연진: {cast_names}</p>" if cast_names != "정보 없음" else ""
                
                st.image(poster_url, width=220, use_column_width=False)
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
        st.warning("추천 영화를 불러오는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    # 트렌딩 영화 섹션
    st.markdown("<h2 class='sub-header'>🔥 트렌딩 영화</h2>", unsafe_allow_html=True)
    trending_movies = get_trending_movies()
    if trending_movies:
        selected_trending = random.sample(trending_movies, min(5, len(trending_movies)))  # 랜덤 5개 선택
        trend_cols = st.columns(5)
        for idx, movie in enumerate(selected_trending):
            with trend_cols[idx]:
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
                
                st.image(poster_url, width=220, use_column_width=False)
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
        st.warning("트렌딩 영화를 불러오는 데 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")

