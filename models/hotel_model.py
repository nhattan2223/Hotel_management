from .base_model import get_conn
from utils.config import STATUS_AVAILABLE


def get_all_hotels():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM Hotels ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_hotel(hotel_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM Hotels WHERE id=?", (hotel_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_hotel(name, address, phone, email):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO Hotels(name,address,phone,email) VALUES (?,?,?,?)",
            (name, address, phone, email)
        )
        conn.commit()
    finally:
        conn.close()


def update_hotel(hid, name, address, phone, email):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE Hotels SET name=?,address=?,phone=?,email=? WHERE id=?",
            (name, address, phone, email, hid)
        )
        conn.commit()
    finally:
        conn.close()


def delete_hotel(hid):
    """Soft delete — kiểm tra không còn nhân viên/phòng active trước khi xóa."""
    conn = get_conn()
    try:
        active_users = conn.execute(
            "SELECT COUNT(*) FROM Users WHERE hotel_id=? AND is_active=1", (hid,)
        ).fetchone()[0]
        if active_users > 0:
            raise ValueError(f"Không thể xóa chi nhánh đang có {active_users} nhân viên hoạt động.")
        # Soft delete: đánh dấu tất cả rooms là inactive thay vì xóa
        conn.execute(f"UPDATE Rooms SET occupancy_status='{STATUS_AVAILABLE}' WHERE hotel_id=?", (hid,))
        conn.execute("DELETE FROM Hotels WHERE id=?", (hid,))
        conn.commit()
    finally:
        conn.close()
