from .base_model import get_conn
from utils.security import hash_password, verify_password


def authenticate(username: str, password: str):
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT u.*, r.role_name, h.name as hotel_name
               FROM Users u
               JOIN Roles r ON u.role_id = r.id
               JOIN Hotels h ON u.hotel_id = h.id
               WHERE u.username=? AND u.is_active=1""",
            (username,)
        ).fetchone()
        if row and verify_password(password, row["password"]):
            return dict(row)
        return None
    finally:
        conn.close()


def get_all_users(hotel_id=None):
    conn = get_conn()
    try:
        if hotel_id:
            rows = conn.execute(
                """SELECT u.*, r.role_name, h.name as hotel_name
                   FROM Users u JOIN Roles r ON u.role_id=r.id JOIN Hotels h ON u.hotel_id=h.id
                   WHERE u.hotel_id=? ORDER BY u.id""", (hotel_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT u.*, r.role_name, h.name as hotel_name
                   FROM Users u JOIN Roles r ON u.role_id=r.id JOIN Hotels h ON u.hotel_id=h.id
                   ORDER BY u.id"""
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_user(username, password, full_name, phone, email, role_id, hotel_id):
    conn = get_conn()
    try:
        # Kiểm tra username trùng lặp trước để báo lỗi rõ ràng
        existing = conn.execute(
            "SELECT id FROM Users WHERE username=?", (username,)
        ).fetchone()
        if existing:
            raise ValueError(f"Tên đăng nhập '{username}' đã tồn tại.")
        conn.execute(
            "INSERT INTO Users(username,password,full_name,phone,email,role_id,hotel_id) VALUES (?,?,?,?,?,?,?)",
            (username, hash_password(password), full_name, phone, email, role_id, hotel_id)
        )
        conn.commit()
    finally:
        conn.close()


def update_user(uid, full_name, phone, email, role_id, hotel_id, is_active):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE Users SET full_name=?,phone=?,email=?,role_id=?,hotel_id=?,is_active=? WHERE id=?",
            (full_name, phone, email, role_id, hotel_id, is_active, uid)
        )
        conn.commit()
    finally:
        conn.close()


def change_password(uid, new_password):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE Users SET password=? WHERE id=?", (hash_password(new_password), uid)
        )
        conn.commit()
    finally:
        conn.close()


def delete_user(uid):
    conn = get_conn()
    try:
        conn.execute("UPDATE Users SET is_active=0 WHERE id=?", (uid,))
        conn.commit()
    finally:
        conn.close()


def get_roles():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM Roles").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
