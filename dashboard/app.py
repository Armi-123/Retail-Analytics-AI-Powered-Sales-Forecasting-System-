import streamlit as st
from auth_jwt import authenticate, register_user, decode_token
from auth_jwt import request_password_reset, reset_password
import datetime
from report_generator import generate_pdf_report

st.set_page_config(page_title="Retail System", layout="centered")

st.title("🔐 Retail Analytics Platform")

menu = st.tabs(["Login", "Signup", "Forgot Password"])

# ---------------- LOGIN ----------------
with menu[0]:
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    remember = st.checkbox("Remember Me", key="login_remember")

    if st.button("Login", key="login_btn"):
        token = authenticate(username, password)

        if token:
            st.session_state.token = token
            user = decode_token(token)

            st.session_state.username = user["username"]
            st.session_state.role = user["role"]

            st.success(f"Welcome {user['username']} 👋")
            st.rerun()
        else:
            st.error("Invalid credentials")


# ---------------- SIGNUP ----------------
with menu[1]:
    st.subheader("Create Account")

    username = st.text_input("New Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("New Password", type="password", key="signup_password")

    role = st.selectbox("Select Role", ["user", "admin"], key="signup_role")

    if st.button("Create Account", key="signup_btn"):
        if register_user(username, email, password, role):
            st.success("Account created! Login now.")
        else:
            st.error("Username or email already exists")


# ---------------- FORGOT PASSWORD ----------------
with menu[2]:
    st.subheader("Forgot Password")

    # Request reset token
    forgot_email = st.text_input("Enter your registered email", key="forgot_email")
    if st.button("Send Reset Token", key="send_token_btn"):
        token = request_password_reset(forgot_email)
        if token:
            st.success("Reset token generated (demo)")
            st.code(token)  # Show token for demo
        else:
            st.error("Email not found")

    st.markdown("---")

    # Reset password
    reset_token = st.text_input("Enter Reset Token", key="reset_token_input")
    new_pass = st.text_input("New Password", type="password", key="reset_new_password_input")

    if st.button("Reset Password", key="reset_btn"):
        success = reset_password(reset_token, new_pass)
        if success:
            st.success("Password updated successfully. You can login now.")
        else:
            st.error("Invalid or expired token")

# ---------------- REDIRECT AFTER LOGIN ----------------
# ---------------- REDIRECT AFTER LOGIN ----------------
if st.session_state.get("token"):

    try:
        user = decode_token(st.session_state.token)

        role = user.get("role", "user")

        if role == "admin":
            st.switch_page("pages/admin_dashboard.py")
        else:
            st.switch_page("pages/user_dashboard.py")

    except Exception:
        st.error("Session expired. Please login again.")
        st.session_state.clear()

