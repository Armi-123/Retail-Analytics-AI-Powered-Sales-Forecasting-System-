import jwt
import datetime
import bcrypt
from db import get_connection
import secrets

# ---------- REQUEST RESET ----------
def request_password_reset(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    token = secrets.token_hex(16)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    cursor.execute(
        "UPDATE users SET reset_token=%s, reset_expiry=%s WHERE email=%s",
        (token, expiry, email)
    )
    conn.commit()
    conn.close()

    return token


# ---------- RESET PASSWORD ----------

def reset_password(token, new_password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE reset_token=%s", (token,))
    user = cursor.fetchone()

    print("Token entered:", token)  # ✅ debug
    print("DB user:", user)         # ✅ debug
    if user:
        print("Token in DB:", user["reset_token"])
        print("Expiry:", user["reset_expiry"])
        print("Now UTC:", datetime.datetime.utcnow())

    if not user:
        conn.close()
        return False
    if user["reset_expiry"] < datetime.datetime.utcnow():
        conn.close()
        return False

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "UPDATE users SET password=%s, reset_token=NULL, reset_expiry=NULL WHERE id=%s",
        (hashed, user["id"])
    )
    conn.commit()
    conn.close()

    return True

SECRET_KEY = "supersecretkey"

def request_password_reset(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    token = secrets.token_hex(16)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    cursor.execute(
        "UPDATE users SET reset_token=%s, reset_expiry=%s WHERE email=%s",
        (token, expiry, email)
    )

    conn.commit()
    conn.close()

    return token

# ---------- REGISTER ----------
def register_user(username, email, password, role="user"):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s,%s,%s,%s)",
            (username, email, hashed, role)
        )
        conn.commit()
        return True

    except Exception as e:
        print("Register error:", e)
        return False

    finally:
        conn.close()


# ---------- LOGIN ----------
def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            payload = {
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }
            return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return None

    except Exception as e:
        print("Login error:", e)
        return None

    finally:
        conn.close()


# ---------- DECODE ----------
def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])



