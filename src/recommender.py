import requests
import streamlit as st
from src.data_fetcher import fetch_movies_by_genre
import json
import re
import os
import logging
from typing import List, Dict, Set, Tuple
import pandas as pd
from huggingface_hub import InferenceClient

# TMDb API 설정
API_KEY = st.secrets["MOVIEDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"


### 🟢 **영화 ID를 기반으로 영화의 세부 정보 가져오기**
def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


### 🟢 **트렌딩 영화 가져오기**
def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])

    movie_list = []
    for movie in movies:
        details = get_movie_details(movie["id"])
        if details:
            movie_list.append(format_movie_details(details))
    return movie_list


### 🟢 **추천 영화 가져오기**
def get_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])

    movie_list = []
    for movie in movies:
        details = get_movie_details(movie["id"])
        if details:
            movie_list.append(format_movie_details(details))
    return movie_list


### 🟢 **사용자 프로필 기반 추천 영화**
def get_personalized_recommendations(profile):
    preferred_genres = profile.get("preferred_genres", [])
    genre_map = {
        "액션": 28, "코미디": 35, "드라마": 18,
        "로맨스": 10749, "스릴러": 53, "SF": 878, "애니메이션": 16,
        "판타지": 14, "공포": 27, "다큐멘터리": 99, "역사": 36
    }
    genre_ids = [genre_map[g] for g in preferred_genres if g in genre_map]

    movie_list = []
    for genre_id in genre_ids:
        movies = fetch_movies_by_genre(genre_id)
        for movie in movies:
            details = get_movie_details(movie["id"])
            if details:
                movie_list.append(format_movie_details(details))

    return movie_list[:10]


### 🟢 **무드(감정) 기반 영화 추천**
def get_mood_based_recommendations(mood):
    mood_to_genre = {
        "행복한": [35, 10751],  # 코미디, 가족
        "슬픈": [18, 10749],  # 드라마, 로맨스
        "신나는": [28, 12],  # 액션, 모험
        "로맨틱한": [10749, 35],  # 로맨스, 코미디
        "무서운": [27, 53],  # 공포, 스릴러
        "미스터리한": [9648, 80],  # 미스터리, 범죄
        "판타지한": [14, 12],  # 판타지, 모험
        "편안한": [99, 10770],  # 다큐멘터리, TV 영화
        "추억을 떠올리는": [10752, 36],  # 전쟁, 역사
        "SF 같은": [878, 28],  # SF, 액션
    }

    genre_ids = mood_to_genre.get(mood, [35])  # 기본값은 코미디
    movie_list = []

    for genre_id in genre_ids:
        movies = fetch_movies_by_genre(genre_id)
        for movie in movies:
            details = get_movie_details(movie["id"])
            if details:
                movie_list.append(format_movie_details(details))

    return movie_list[:10]


### 🟢 **키워드 기반 영화 검색**
def get_movies_by_keyword(keyword):
    url = f"{BASE_URL}/search/keyword?api_key={API_KEY}&query={keyword}"
    response = requests.get(url)
    keywords = response.json().get("results", [])

    if not keywords:
        return []

    keyword_id = keywords[0]["id"]
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_keywords={keyword_id}&language=ko-KR"
    response = requests.get(url)
    movies = response.json().get("results", [])

    movie_list = []
    for movie in movies:
        details = get_movie_details(movie["id"])
        if details:
            movie_list.append(format_movie_details(details))

    return movie_list


### 🟢 **영화 리뷰 가져오기**
def get_movie_reviews(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/reviews?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    reviews = response.json().get("results", [])

    review_list = []
    for review in reviews:
        review_list.append({
            "author": review["author"],
            "rating": review["author_details"]["rating"],
            "content": review["content"][:200] + "..." if len(review["content"]) > 200 else review["content"],
            "created_at": review["created_at"],
        })
    return review_list


### 🟢 **트렌디한 TV 쇼 가져오기**
def get_trending_tv_shows():
    url = f"{BASE_URL}/trending/tv/week?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    shows = response.json().get("results", [])

    show_list = []
    for show in shows:
        show_list.append(format_movie_details(show, is_tv=True))
    return show_list


### 🟢 **트렌디한 인물 가져오기**
def get_trending_people():
    url = f"{BASE_URL}/trending/person/week?api_key={API_KEY}&language=ko-KR"
    response = requests.get(url)
    people = response.json().get("results", [])

    people_list = []
    for person in people:
        people_list.append({
            "name": person["name"],
            "popularity": person["popularity"],
            "known_for": [work["title"] for work in person["known_for"] if "title" in work],
            "profile_path": f"https://image.tmdb.org/t/p/w500{person['profile_path']}" if person.get("profile_path") else None
        })
    return people_list


### 🟢 **영화 데이터 포맷팅 함수 (줄거리 일부 표시 + 더 보기 버튼)**
def format_movie_details(details, is_tv=False):
    short_overview = details["overview"][:100] + "..." if len(details["overview"]) > 100 else details["overview"]
    
    return {
        "title": details["title"] if not is_tv else details["name"],
        "overview": short_overview,
        "full_overview": details["overview"],
        "release_date": details["release_date"] if not is_tv else details["first_air_date"],
        "vote_average": details["vote_average"],
        "poster_path": f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else None
    }


def get_huggingface_token():
    """환경 변수 또는 Streamlit secrets에서 Hugging Face API 토큰을 가져옵니다."""
    return st.secrets.get("HUGGINGFACE_API_TOKEN")

def clean_input(text: str) -> str:
    """불필요한 단어(해줘, 알려줘 등)를 제거한 사용자 입력을 반환"""
    return re.sub(r"\b(해줘|알려줘|설명해 줘|말해 줘)\b", "", text, flags=re.IGNORECASE).strip()

def generate_text_via_api(prompt: str, model_name: str = "google/gemma-2-9b-it"):
    """Hugging Face API를 사용하여 텍스트를 생성합니다."""
    token = get_huggingface_token()
    client = InferenceClient(model=model_name, api_key=token)
    response = client.text_generation(prompt=prompt)
    return response

def get_user_info_with_default(user_data: Dict[str, str]) -> Dict[str, str]:
    """사용자 정보를 가져오고, 없는 경우 기본값을 반환합니다."""
    user_info = st.session_state.get("user_info", user_data)
    st.session_state["user_info"] = user_info
    return user_info

