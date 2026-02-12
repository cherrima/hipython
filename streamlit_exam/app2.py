import streamlit as st
import pandas as pd


st.title("안녕하세요")
st.write("Hello, Streamlit!!")

st.divider()  # 단락 구분 라인 생성
name = st.text_input("이름 : ")
st.write("이름 : " + name)

def btn1_clicked() :
    st.write("Hello, " + name)

# btn1 = st.button("Click here!", on_click=btn1_clicked)
btn1 = st.button("Click here!")
if btn1 :
    btn1_clicked()

df = pd.read_csv("./data/vehicle_prod.csv")
# st.write("DataFrame : \n" + df.head())

st.write("DataFrame : \n")
st.write(df.head())
