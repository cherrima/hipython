import streamlit as st

st.sidebar.radio("이동", ["메인페이지", "분석보고거", "설정"])

st.sidebar.metric("접속자수:", '백만명', "+백만명")

if st.sidebar.button('눌러봐') :
    st.balloons()
    
