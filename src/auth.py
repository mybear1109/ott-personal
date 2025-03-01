import requests
import streamlit as st

API_KEY = st.secrets["MOVIEDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"

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

    return response.get("session_id")

def create_guest_session():
    """게스트 세션 생성"""
    url = f"{BASE_URL}/authentication/guest_session/new?api_key={API_KEY}"
    response = requests.get(url).json()
    return response.get("guest_session_id")

def delete_session():
    """세션 삭제 (로그아웃)"""
    session_id = st.session_state.get("SESSION_ID")
    if session_id:
        url = f"{BASE_URL}/authentication/session?api_key={API_KEY}"
        requests.delete(url, json={"session_id": session_id})
        st.session_state.pop("SESSION_ID", None)
