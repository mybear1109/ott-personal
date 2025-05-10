import streamlit as st
from src import login, ui, home, auth_user, movie_recommend, data_fetcher

# ✅ Debugging - ui 모듈이 제대로 import 되었는지 확인
print(dir(ui))  # ui.py에 정의된 함수 및 변수 목록 출력

st.set_page_config(page_title="MovieMind", page_icon="🎬", layout="wide")

def app():
    """📌 MovieMind 메인 실행 함수"""
    
    # ✅ CSS 스타일 로드
    ui.load_css()

    # ✅ 메인 헤더 표시
    ui.main_header()

    # ✅ 사용자 로그인 & 인증
    login.user_authentication()

    # ✅ 네비게이션 메뉴
    selected_page = ui.navigation_menu()  # ✅ navigation_menu() 호출

    # ✅ 페이지 라우팅
    if selected_page == "홈":
        home.show_home_page()
    elif selected_page == "사용자 페이지":
        ui.show_user_page()
    elif selected_page == "영화 스타일 선택":
        ui.show_profile_setup()
    elif selected_page == "영화 검색":
        ui.show_movie_search()
    elif selected_page == "추천 생성":
        ui.show_generated_recommendations()
    elif selected_page == "즐겨찾기":
        ui.show_favorite_movies()

    # ✅ 푸터 표시
    ui.show_footer()



from flask import Flask, jsonify, request
import requests
import os
import webbrowser

app = Flask(__name__)

# ✅ 환경 변수에서 API Key와 Bearer Token 가져오기
API_KEY = os.getenv("MOVIEDB_API_KEY")
BEARER_TOKEN = os.getenv("MOVIEDB_BEARER_TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
BASE_URL = "https://api.themoviedb.org/3"
LANGUAGE = "ko-KR"
REGION = "KR"

if not API_KEY or not BEARER_TOKEN:
    print("❌ API_KEY 또는 BEARER_TOKEN이 설정되지 않았습니다.")
    exit(1)

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# ✅ Configuration 엔드포인트
@app.route("/configuration", methods=["GET"])
def configuration():
    url = f"{BASE_URL}/configuration"
    params = {
        "api_key": API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": f"구성 정보를 가져오지 못했습니다. (상태 코드: {response.status_code})"}), 500

# ✅ Request Token 생성 (v3)
@app.route("/request_token", methods=["GET"])
def create_request_token():
    url = f"{BASE_URL}/authentication/token/new"
    params = {"api_key": API_KEY}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        request_token = data["request_token"]
        return jsonify({"request_token": request_token})
    else:
        return jsonify({"error": f"Request Token 생성 실패 (상태 코드: {response.status_code})"}), 500

# ✅ Request Token 승인 (필수 단계)
@app.route("/authorize_request_token", methods=["GET"])
def authorize_request_token():
    request_token = request.args.get("request_token")
    if not request_token:
        return jsonify({"error": "Request Token이 필요합니다."}), 400

    url = f"https://www.themoviedb.org/authenticate/{request_token}"
    return jsonify({"message": "승인 페이지가 열렸습니다.", "url": url})

# ✅ Session ID 생성 (v3)
@app.route("/session_id", methods=["POST"])
def create_session_id():
    request_token = request.json.get("request_token")
    if not request_token:
        return jsonify({"error": "Request Token이 필요합니다."}), 400

    url = f"{BASE_URL}/authentication/session/new"
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    payload = {
        "request_token": request_token
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        return jsonify({"session_id": session_id})
    else:
        return jsonify({"error": f"Session ID 생성 실패 (상태 코드: {response.status_code})"}), 500

# ✅ 게스트 세션 생성 (v3)
@app.route("/guest_session", methods=["GET"])
def create_guest_session():
    url = f"{BASE_URL}/authentication/guest_session/new"
    params = {
        "api_key": API_KEY
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": f"게스트 세션 생성 실패 (상태 코드: {response.status_code})"}), 500



def fetch_movies(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "accept": "application/json"
    }
    if not params:
        params = {}
    
    # 기본 파라미터 추가
    params["api_key"] = API_KEY
    params["language"] = LANGUAGE
    params["region"] = REGION

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 오류 발생: {response.status_code} - {response.text}")
        return {"error": f"영화 데이터를 가져오는 중 오류가 발생했습니다. (상태 코드: {response.status_code})"}



# ✅ 영화 데이터 가져오기 (공통)
def fetch_movies(category, page=1, append_to_response=None):
    url = f"{BASE_URL}/movie/{category}"
    params = {
        "api_key": API_KEY,
        "language": LANGUAGE,
        "region": REGION,
        "page": page
    }

    if append_to_response:
        params["append_to_response"] = append_to_response

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 오류 발생: {response.status_code} - {response.text}")
        return {"error": f"영화 데이터를 가져오는 중 오류가 발생했습니다. (상태 코드: {response.status_code})"}

# ✅ Discover Movies
@app.route("/discover/movie", methods=["GET"])
def discover_movie():
    # 지원하는 필터 파라미터 수집
    allowed_params = [
        "certification", "certification_country", "certification.gte", "certification.lte",
        "include_adult", "include_video", "language", "page", "primary_release_year",
        "primary_release_date.gte", "primary_release_date.lte", "region", "release_date.gte",
        "release_date.lte", "sort_by", "vote_average.gte", "vote_average.lte", "vote_count.gte",
        "vote_count.lte", "watch_region", "with_cast", "with_companies", "with_crew", "with_genres",
        "with_keywords", "with_origin_country", "with_original_language", "with_people",
        "with_release_type", "with_runtime.gte", "with_runtime.lte", "with_watch_monetization_types",
        "with_watch_providers", "without_companies", "without_genres", "without_keywords",
        "without_watch_providers", "year"
    ]
    
    # 클라이언트가 전달한 파라미터 필터링
    params = {k: v for k, v in request.args.items() if k in allowed_params}
    
    # API 호출
    data = fetch_movies("discover/movie", params)
    return jsonify(data)

# ✅ Now Playing
@app.route("/now_playing", methods=["GET"])
def now_playing():
    page = request.args.get("page", 1)
    data = fetch_movies("movie/now_playing", {"page": page})
    return jsonify(data)

# ✅ Popular
@app.route("/popular", methods=["GET"])
def popular():
    page = request.args.get("page", 1)
    data = fetch_movies("movie/popular", {"page": page})
    return jsonify(data)

# ✅ Top Rated
@app.route("/top_rated", methods=["GET"])
def top_rated():
    page = request.args.get("page", 1)
    data = fetch_movies("movie/top_rated", {"page": page})
    return jsonify(data)

# ✅ Upcoming
@app.route("/upcoming", methods=["GET"])
def upcoming():
    page = request.args.get("page", 1)
    data = fetch_movies("movie/upcoming", {"page": page})
    return jsonify(data)





















if __name__ == "__main__":
    app.run(port=5000, debug=True)























# if __name__ == "__main__":
#     app()
