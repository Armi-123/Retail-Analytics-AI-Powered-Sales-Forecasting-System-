from db import get_connection

def log_activity(username, action):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO activity_logs (username, action) VALUES (%s, %s)",
              (username, action))
    conn.commit()
    conn.close()


