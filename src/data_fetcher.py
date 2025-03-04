import requests
import streamlit as st

# ---------------- TMDb API 기본 설정 ----------------
API_KEY = st.secrets["MOVIEDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"


# ---------------- 번역 데이터 및 영화 정보 관련 함수 ----------------
def fetch_translations(item_id, item_type="movie", season_number=None):
    """
    영화 또는 TV 프로그램의 번역 데이터를 가져옵니다.
    - item_type: "movie" 또는 "tv"
    - season_number: TV 시즌일 경우 필요한 시즌 번호
    """
    if item_type == "movie":
        url = f"{BASE_URL}/movie/{item_id}/translations?api_key={API_KEY}"
    elif item_type == "tv" and season_number is not None:
        url = f"{BASE_URL}/tv/{item_id}/season/{season_number}/translations?api_key={API_KEY}"
    else:
        return None, None

    try:
        response = requests.get(url)
        translations = response.json().get("translations", []) if response.status_code == 200 else []
        for t in translations:
            if t["iso_639_1"] == "ko":  # 한국어 데이터 찾기
                return t["data"].get("title", ""), t["data"].get("overview", "")
    except Exception as e:
        print(f"Error fetching translations: {e}")
    return None, None

def translate_movie(movie):
    """영화 정보를 한국어 번역으로 업데이트 (번역 없으면 원본 유지)"""
    title_ko, overview_ko = fetch_translations(movie.get("id", 0), item_type="movie")
    if title_ko:
        movie["title"] = title_ko
    if overview_ko:
        movie["overview"] = overview_ko
    return movie

def fetch_movies_by_category(category):
    """특정 카테고리(인기, 최신, 평점 높은) 영화 리스트를 가져옵니다."""
    url = f"{BASE_URL}/movie/{category}?api_key={API_KEY}&language=ko-KR"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    except Exception as e:
        print(f"Error fetching movies by category: {e}")
        return []

def fetch_genres_list():
    """TMDb에서 영화 장르 리스트를 가져옵니다."""
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=ko-KR"
    try:
        response = requests.get(url)
        return response.json().get("genres", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching genre list: {e}")
        return []

def fetch_movies_by_genre(genre_id):
    """특정 장르에 해당하는 영화 리스트를 가져옵니다."""
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&language=ko-KR"
    try:
        response = requests.get(url)
        movies = response.json().get("results", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error fetching movies by genre: {e}")
        return []

def fetch_movies_by_selected_genres(selected_genres):
    """여러 장르가 선택된 경우 해당 영화 리스트를 가져옵니다."""
    genre_ids = ",".join(str(genre) for genre in selected_genres)
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_ids}&language=ko-KR"
    try:
        response = requests.get(url)
        movies = response.json().get("results", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error fetching movies by selected genres: {e}")
        return []

def fetch_popular_movies():
    """인기 영화를 가져옵니다."""
    url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=ko-KR"
    try:
        response = requests.get(url)
        movies = response.json().get("results", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error fetching popular movies: {e}")
        return []

def search_movie(query):
    """영화 제목 또는 줄거리로 영화를 검색합니다."""
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&language=ko-KR&query={query}"
    try:
        response = requests.get(url)
        movies = response.json().get("results", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error searching for movie: {e}")
        return []

def fetch_movie_details(movie_id):
    """
    특정 영화의 세부 정보를 가져옵니다.
    append_to_response=credits 옵션을 통해 감독 및 출연진 정보도 함께 조회합니다.
    """
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR&append_to_response=credits"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            movie = response.json()
            return translate_movie(movie)
        return {}
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return {}

def get_movie_details(movie_id):
    """
    📌 영화 상세 정보 가져오기
    :param movie_id: TMDb 영화 ID
    :return: 영화 정보 (딕셔너리)
    """
    url = f"{BASE_URL}/movie/{movie_id}"
    params = { "api_key": API_KEY,"language": "ko-KR", "append_to_response": "credits,videos"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {}

def full_movie_details(movie):
    """
    영화의 전체 상세 정보를 출력합니다.
    fetch_movie_details()를 호출하여 영화의 세부 정보를 가져오고,
    제목, 개봉일, 평점, 줄거리, 감독, 출연진 등을 출력합니다.
    """
    # 영화 ID가 없는 경우 처리
    movie_id = movie.get("id")
    if not movie_id:
        st.write("상세 정보가 없습니다.")
        return

    # 영화 상세 정보(append_to_response=credits 포함)를 가져옵니다.
    details = fetch_movie_details(movie_id)  # 이미 fetch_movie_details() 함수가 구현되어 있다고 가정
    if not details:
        st.write("상세 정보가 없습니다.")
        return

    # 기본 정보 추출
    title = details.get("title", "제목 없음")
    release_date = details.get("release_date", "정보 없음")
    vote_average = details.get("vote_average", "정보 없음")
    overview = details.get("overview", "줄거리 없음")
    
    # Credits 정보 추출 (감독, 출연진)
    credits = details.get("credits", {})
    # 감독: crew에서 job이 "Director"인 항목을 추출
    directors = [member.get("name", "정보 없음") for member in credits.get("crew", []) if member.get("job") == "Director"]
    director_str = ", ".join(directors) if directors else "정보 없음"
    # 출연진: cast 배열에서 최대 10명까지 표시
    cast = [member.get("name", "정보 없음") for member in credits.get("cast", [])]
    cast_str = ", ".join(cast[:10]) if cast else "정보 없음"
    
    # 출력
    st.markdown(f"### {title}")
    st.write(f"**개봉일:** {release_date}")
    st.write(f"**평점:** {vote_average}/10")
    st.write(f"**줄거리:** {overview}")
    st.write(f"**감독:** {director_str}")
    st.write(f"**출연진:** {cast_str}")

    
def fetch_user_movie_list(category="watchlist"):
    """
    📌 사용자의 영화 목록 (예: watchlist, favorite) 가져오기
    :param category: "watchlist" 또는 "favorite"
    :return: 영화 목록 리스트
    """
    session_id = st.session_state.get("SESSION_ID")
    if not session_id:
        return []

    url = f"{BASE_URL}/account/{st.secrets['ACCOUNT_ID']}/{category}/movies"
    params = {"api_key": API_KEY, "session_id": session_id, "language": "ko-KR"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# 예시: fetch_movie_details() 함수는 아래와 같이 구현되어 있다고 가정합니다.
def fetch_movie_details(movie_id):
    """
    특정 영화의 세부 정보를 가져옵니다.
    append_to_response=credits 옵션을 통해 감독 및 출연진 정보도 함께 조회합니다.
    """
    API_KEY = st.secrets["MOVIEDB_API_KEY"]
    BASE_URL = "https://api.themoviedb.org/3"
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR&append_to_response=credits"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            movie = response.json()
            return movie
        return {}
    except Exception as e:
        st.error(f"Error fetching movie details: {e}")
        return {}



# ---------------- Credits 관련 함수 ----------------
def fetch_movie_credits(movie_id):
    """
    특정 영화의 크레딧(감독, 배우 등) 정보를 가져옵니다.
    credits 엔드포인트는 language 파라미터를 지원하지 않으므로 제거합니다.
    """
    url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            credits = response.json()
            # crew 배열에서 job이 "Director"인 항목을 감독으로 추출
            directors = [member for member in credits.get("crew", []) if member.get("job") == "Director"]
            credits["directors"] = directors
            return credits
        return {}
    except Exception as e:
        print(f"Error fetching movie credits: {e}")
        return {}

def get_movie_director_and_cast(movie_id):
    """
    특정 영화의 감독과 출연진 정보를 반환합니다.
    fetch_movie_credits() 함수를 이용하여 감독(directors)와 배우(cast) 목록을 추출합니다.
    """
    credits = fetch_movie_credits(movie_id)
    directors = credits.get("directors", [])
    cast = credits.get("cast", [])
    return directors, cast


# ---------------- 인물(배우) 관련 함수 ----------------
def search_person(query, include_adult=False, page=1, language="ko-KR"):
    """
    배우(또는 인물) 이름으로 검색하여 결과를 반환합니다.
    """
    url = f"{BASE_URL}/search/person"
    params = {
        "api_key": API_KEY,
        "query": query,
        "include_adult": include_adult,
        "page": page,
        "language": language
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    except Exception as e:
        print(f"Error searching for person: {e}")
        return []

def fetch_movies_by_person(person_id):
    """특정 배우가 출연한 영화 목록을 가져옵니다."""
    url = f"{BASE_URL}/person/{person_id}/movie_credits?api_key={API_KEY}&language=ko-KR"
    try:
        response = requests.get(url)
        movies = response.json().get("cast", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error fetching movies by person: {e}")
        return []

def fetch_person_movie_credits(person_id, language="ko-KR"):
    """
    특정 배우의 영화 크레딧 정보를 반환합니다.
    cast와 crew 배열 모두를 포함한 전체 데이터를 반환합니다.
    """
    url = f"{BASE_URL}/person/{person_id}/movie_credits?api_key={API_KEY}&language={language}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error fetching person movie credits: {e}")
        return {}

# ---------------- 키워드 관련 함수 ----------------
def search_keyword_movies(query):
    """키워드로 영화를 검색합니다."""
    url = f"{BASE_URL}/search/keyword?api_key={API_KEY}&query={query}"
    try:
        response = requests.get(url)
        return response.json().get("results", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error searching for keyword: {e}")
        return []

def fetch_movies_by_keyword(keyword_id):
    """특정 키워드에 해당하는 영화 목록을 가져옵니다."""
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_keywords={keyword_id}&language=ko-KR"
    try:
        response = requests.get(url)
        movies = response.json().get("results", []) if response.status_code == 200 else []
        return [translate_movie(movie) for movie in movies]
    except Exception as e:
        print(f"Error fetching movies by keyword: {e}")
        return []

def fetch_similar_movies(movie_id, page=1, language="ko-KR"):
    """
    특정 영화와 유사한 영화 목록을 가져옵니다.
    """
    url = f"{BASE_URL}/movie/{movie_id}/similar"
    params = {
        "api_key": API_KEY,
        "language": language,
        "page": page
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        return []
    except Exception as e:
        print(f"Error fetching similar movies: {e}")
        return []

def fetch_movie_reviews(movie_id, page=1, language="ko-KR"):
    """
    특정 영화의 사용자 리뷰를 가져옵니다.
    """
    url = f"{BASE_URL}/movie/{movie_id}/reviews"
    params = {
        "api_key": API_KEY,
        "language": language,
        "page": page
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        return []
    except Exception as e:
        print(f"Error fetching movie reviews: {e}")
        return []



def add_favorite_movie(movie_id):
    """영화를 즐겨찾기에 추가합니다."""
    session_id = st.session_state.get("SESSION_ID")
    if not session_id:
        return False
    url = f"{BASE_URL}/account/{session_id}/favorite?api_key={API_KEY}"
    payload = {
        "media_type": "movie",
        "media_id": movie_id,
        "favorite": True
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 201
    except Exception as e:
        print(f"Error adding favorite movie: {e}")
        return False
    
