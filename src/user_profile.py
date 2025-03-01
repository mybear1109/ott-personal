import streamlit as st
import json
import os

USER_DATA_FILE = "data/user_profile.json"

def save_user_preferences(watched_movies, favorite_movies, preferred_genres):
    """사용자의 프로필을 저장하는 함수"""
    user_data = {
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
        "preferred_genres": preferred_genres
    }

    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)

    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def load_user_preferences():
    """사용자 프로필 데이터를 불러오는 함수"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"watched_movies": [], "favorite_movies": [], "preferred_genres": []}

def save_guest_preferences(guest_id, watched_movies, favorite_movies, preferred_genres):
    """게스트 유저의 프로필을 저장하는 함수"""
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
    """게스트 유저의 프로필 데이터를 불러오는 함수"""
    guest_data_file = f"data/guest_{guest_id}.json"
    if os.path.exists(guest_data_file):
        with open(guest_data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"watched_movies": [], "favorite_movies": [], "preferred_genres": []}

def save_user_preferences(watched_movies, favorite_movies, preferred_genres):
    """사용자 선호 데이터를 저장"""
    user_preferences = {
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
        "preferred_genres": preferred_genres,
    }
    st.session_state["user_preferences"] = user_preferences

def save_user_preferences(watched_movies, favorite_movies, preferred_genres, preferred_styles=None):
    """사용자 선호 데이터를 저장 (추가 스타일 포함)"""
    user_preferences = {
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
        "preferred_genres": preferred_genres,
        "preferred_styles": preferred_styles or []  # 스타일이 없으면 빈 리스트로 저장
    }
    st.session_state["user_preferences"] = user_preferences


