import requests
import streamlit as st
import json
import re
import os
import logging
from typing import List, Dict, Set, Tuple
import pandas as pd
from huggingface_hub import InferenceClient

# ---------------- TMDb API 설정 ----------------
API_KEY = st.secrets["MOVIEDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"

# ---------------- Hugging Face API 설정 ----------------
HUGGINGFACE_API_TOKEN = st.secrets.get("HUGGINGFACE_API_TOKEN")

# ✅ Hugging Face API 클라이언트 초기화
def get_huggingface_client(model_name: str = "google/gemma-2-9b-it"):
    """📌 Hugging Face API를 사용하여 텍스트를 생성하는 클라이언트 반환"""
    return InferenceClient(model=model_name, api_key=HUGGINGFACE_API_TOKEN)


# =========================== 📌 영화 데이터 가져오기 ===========================

def get_movie_details(movie_id: int) -> Dict:
    """📌 영화 ID를 기반으로 영화의 세부 정보를 가져옵니다."""
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def get_trending_movies() -> List[Dict]:
    """📌 주간 트렌딩 영화 목록을 가져옵니다."""
    url = f"{BASE_URL}/trending/movie/week?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])
    return [format_movie_details(get_movie_details(movie["id"])) for movie in movies if get_movie_details(movie["id"])]


def get_recommendations(movie_id: int) -> List[Dict]:
    """📌 특정 영화 ID를 기반으로 추천 영화 목록을 가져옵니다."""
    url = f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])
    return [format_movie_details(get_movie_details(movie["id"])) for movie in movies if get_movie_details(movie["id"])]


# =========================== 📌 사용자 맞춤형 추천 ===========================

def get_personalized_recommendations(profile: Dict) -> List[Dict]:
    """📌 사용자 프로필을 기반으로 맞춤 추천 영화를 가져옵니다."""
    genre_map = {
        "액션": 28, "코미디": 35, "드라마": 18, "로맨스": 10749,
        "스릴러": 53, "SF": 878, "애니메이션": 16, "판타지": 14,
        "공포": 27, "다큐멘터리": 99, "역사": 36
    }
    genre_ids = [genre_map[g] for g in profile.get("preferred_genres", []) if g in genre_map]
    movies = []
    for genre_id in genre_ids:
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&language=ko-KR"
        response = requests.get(url)
        movies.extend(response.json().get("results", []))
    return [format_movie_details(get_movie_details(movie["id"])) for movie in movies[:10]]


def get_mood_based_recommendations(mood: str) -> List[Dict]:
    """📌 사용자 감정(무드)에 따라 추천 영화 목록을 가져옵니다."""
    mood_to_genre = {
        "행복한": [35, 10751], "슬픈": [18, 10749], "신나는": [28, 12],
        "로맨틱한": [10749, 35], "무서운": [27, 53], "미스터리한": [9648, 80],
        "판타지한": [14, 12], "편안한": [99, 10770], "추억을 떠올리는": [10752, 36],
        "SF 같은": [878, 28]
    }
    genre_ids = mood_to_genre.get(mood, [35])
    movies = []
    for genre_id in genre_ids:
        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&language=ko-KR"
        response = requests.get(url)
        movies.extend(response.json().get("results", []))
    return [format_movie_details(get_movie_details(movie["id"])) for movie in movies[:10]]


# =========================== 📌 검색 기능 ===========================

def get_movies_by_keyword(keyword: str) -> List[Dict]:
    """📌 키워드 검색을 통해 영화 목록을 가져옵니다."""
    url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={keyword}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])
    return [format_movie_details(get_movie_details(movie["id"])) for movie in movies[:10]]


# =========================== 📌 AI 추천 시스템 ===========================

def clean_input(text: str) -> str:
    """📌 불필요한 단어 제거"""
    return re.sub(r"\b(해줘|알려줘|설명해 줘|말해 줘)\b", "", text, flags=re.IGNORECASE).strip()


def generate_text_via_api(prompt: str) -> str:
    """📌 Hugging Face API를 사용하여 텍스트를 생성합니다."""
    client = get_huggingface_client()
    response = client.text_generation(prompt=prompt)
    return response


def build_recommendation_prompt(profile: Dict, additional_info: str) -> str:
    """📌 사용자 프로필과 추가 정보를 바탕으로 영화 추천 프롬프트를 생성합니다."""
    preferred_genres = ", ".join(profile.get("preferred_genres", [])) if profile.get("preferred_genres") else "없음"
    
    return f"""
    영화 추천을 생성합니다.
    - 선호 장르: {preferred_genres}
    - 추가 정보: {additional_info}
    - TMDb에서 5개의 영화 추천을 가져와 상세 정보(제목, 개봉일, 평점, 줄거리, 감독, 출연진 포함)를 출력합니다.
    """


# =========================== 📌 데이터 포맷 ===========================

def format_movie_details(details: Dict) -> Dict:
    """📌 영화 데이터를 정리하여 반환"""
    overview = details.get("overview", "줄거리 없음")
    short_overview = overview[:100] + "..." if len(overview) > 100 else overview
    poster = details.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
    
    return {
        "title": details.get("title", "제목 없음"),
        "overview": short_overview,
        "release_date": details.get("release_date", "정보 없음"),
        "vote_average": details.get("vote_average", "N/A"),
        "poster_path": poster_url
    }


# =========================== 📌 실행 테스트 ===========================

if __name__ == "__main__":
    st.title("🎬 MovieMind - 영화 추천 시스템")
    
    st.sidebar.header("🔎 검색 및 추천")
    search_query = st.sidebar.text_input("영화 검색")
    
    if st.sidebar.button("검색"):
        results = get_movies_by_keyword(search_query)
        for movie in results:
            st.image(movie["poster_path"], width=150)
            st.write(f"**{movie['title']}** ({movie['release_date']})")
            st.write(f"⭐ 평점: {movie['vote_average']}/10")
            st.write(f"📜 줄거리: {movie['overview']}")
    
    st.sidebar.header("🎭 무드 기반 추천")
    mood = st.sidebar.selectbox("무드 선택", ["행복한", "슬픈", "신나는", "로맨틱한", "무서운"])
    
    if st.sidebar.button("추천 받기"):
        results = get_mood_based_recommendations(mood)
        for movie in results:
            st.image(movie["poster_path"], width=150)
            st.write(f"**{movie['title']}** ({movie['release_date']})")
            st.write(f"📜 {movie['overview']}")
