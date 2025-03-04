import streamlit as st
from src.auth_user import create_session, create_guest_session, delete_session, is_user_authenticated



# ✅ 세션 키 초기화 (앱 실행 시 로그인 상태를 관리)
st.session_state.setdefault("SESSION_ID", None)

def user_authentication():
    """📌 사용자 로그인 및 게스트 모드 처리"""
    
    # ✅ 현재 로그인 상태 확인
    session_active = is_user_authenticated()

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    if not session_active:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 로그인", key="login_btn"):
                session_id = create_session()
                if session_id:
                    st.session_state["SESSION_ID"] = session_id  # ✅ 세션 저장
                    st.success("✅ 로그인 성공!")
                    st.experimental_rerun()

        with col2:
            if st.button("🎭 게스트 모드", key="guest_btn"):
                guest_session_id = create_guest_session()
                if guest_session_id:
                    st.session_state["SESSION_ID"] = guest_session_id  # ✅ 게스트 세션 저장
                    st.success("✅ 게스트 모드 활성화!")
                    st.experimental_rerun()
                    
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<p class="auth-status">🎬 현재 로그인 상태입니다.</p>', unsafe_allow_html=True)
        with col2:
            if st.button("🚪 로그아웃", key="logout_btn"):
                delete_session()  # ✅ 세션 삭제
                st.session_state["SESSION_ID"] = None  # ✅ 세션 초기화
                st.success("🚪 로그아웃 완료!")
                st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)
