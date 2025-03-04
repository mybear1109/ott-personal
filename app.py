import streamlit as st
import src.auth_user
import src.data_fetcher
import src.movie_recommend
import src.movie_recommend 
import src.ui
import src.home

# 페이지 설정: 반드시 가장 먼저 호출해야 합니다.
st.set_page_config(
    page_title="MovieMind: 당신만의 영화 여정",
    page_icon="🎬",
    layout="wide"
)

def app():
    src.ui.load_css()
    src.ui.main_header()
    src.ui.user_authentication()
    selected_page = src.ui.navigation_menu()
    
    if selected_page == "홈":
        src.home.show_home_page()
    elif selected_page == "영화 스타일 선택":
        # Now defined in ui.py instead of user_profile.py
        src.ui.show_profile_setup()
    elif selected_page == "영화 검색":
        src.ui.show_movie_search()
    elif selected_page == "추천 생성":
        src.ui.show_generated_recommendations()
    elif selected_page == "즐겨찾기":
        src.ui.show_favorite_movies()
    
    src.ui.show_footer()

if __name__ == "__main__":
    app()
