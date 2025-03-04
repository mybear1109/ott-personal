import requests
import streamlit as st
import json
import os

# ✅ TMDb API 설정
API_KEY = st.secrets["MOVIEDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"

# ✅ 사용자 데이터 저장 경로
USER_DATA_FILE = "data/user_profile.json"

### 🔹 **TMDb 인증 관련 함수들** 🔹 ###
def create_request_token():
    """TMDb에서 새 request_token 생성"""
    url = f"{BASE_URL}/authentication/token/new?api_key={API_KEY}"
    response = requests.get(url).json()
    return response.get("request_token")

def create_session():
    """사용자 로그인 후 세션 ID 생성"""
    request_token = create_request_token()
    if not request_token:
        return None

    auth_url = f"https://www.themoviedb.org/authenticate/{request_token}"
    st.write(f"🔗 [여기 클릭하여 승인하기]({auth_url})")

    url = f"{BASE_URL}/authentication/session/new?api_key={API_KEY}"
    response = requests.post(url, json={"request_token": request_token}).json()

    session_id = response.get("session_id")
    if session_id:
        st.session_state["SESSION_ID"] = session_id  # ✅ 세션 상태 저장
    return session_id

def create_guest_session():
    """게스트 세션 생성"""
    url = f"{BASE_URL}/authentication/guest_session/new?api_key={API_KEY}"
    response = requests.get(url).json()
    guest_session_id = response.get("guest_session_id")

    if guest_session_id:
        st.session_state["GUEST_SESSION_ID"] = guest_session_id  # ✅ 게스트 세션 저장
    return guest_session_id

def delete_session():
    """세션 삭제 (로그아웃)"""
    session_id = st.session_state.get("SESSION_ID")
    if session_id:
        url = f"{BASE_URL}/authentication/session?api_key={API_KEY}"
        requests.delete(url, json={"session_id": session_id})
        st.session_state.pop("SESSION_ID", None)  # ✅ 세션 제거

### 🔹 **사용자 프로필 관리 함수들** 🔹 ###
def save_user_preferences(watched_movies, favorite_movies, preferred_genres, preferred_styles=None):
    """사용자 프로필 데이터 저장 (세션 기반)"""
    user_preferences = {
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
        "preferred_genres": preferred_genres,
        "preferred_styles": preferred_styles or []  # 스타일이 없으면 빈 리스트
    }
    st.session_state["user_preferences"] = user_preferences  # ✅ Streamlit 세션에 저장

    # ✅ JSON 파일에 저장
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_preferences, f, ensure_ascii=False, indent=4)

def load_user_preferences():
    """사용자 프로필 데이터 불러오기"""
    if "user_preferences" in st.session_state:
        return st.session_state["user_preferences"]

    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"watched_movies": [], "favorite_movies": [], "preferred_genres": [], "preferred_styles": []}

### 🔹 **게스트 유저 프로필 관리 함수들** 🔹 ###
def save_guest_preferences(guest_id, watched_movies, favorite_movies, preferred_genres):
    """게스트 유저의 프로필 저장"""
    guest_data_file = f"data/guest_{guest_id}.json"
    guest_data = {
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
        "preferred_genres": preferred_genres
    }

    os.makedirs("data", exist_ok=True)
    with open(guest_data_file, "w", encoding="utf-8") as f:
        json.dump(guest_data, f, ensure_ascii=False, indent=4)

def load_guest_preferences(guest_id):
    """게스트 유저 프로필 불러오기"""
    guest_data_file = f"data/guest_{guest_id}.json"
    if os.path.exists(guest_data_file):
        with open(guest_data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"watched_movies": [], "favorite_movies": [], "preferred_genres": []}

### 🔹 **로그인 여부 확인 함수** 🔹 ###
def is_user_authenticated():
    """사용자가 로그인했는지 확인"""
    return "SESSION_ID" in st.session_state and st.session_state["SESSION_ID"]

def get_session_id():
    """현재 세션 ID 반환"""
    return st.session_state.get("SESSION_ID")
