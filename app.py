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

if __name__ == "__main__":
    app()
