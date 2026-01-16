import streamlit as st
from auth_jwt import decode_token

user = decode_token(st.session_state.token)

st.title("👤 My Profile")
st.write("Username:", user["username"])
st.write("Email:", user["email"])
st.write("Role:", user["role"])
