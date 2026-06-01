from .base_model import get_conn
from utils.config import BOOKING_CHECKED_IN, BOOKING_RESERVED


def get_all_customers():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM Customers WHERE is_active=1 ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_customer(cid):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM Customers WHERE id=?", (cid,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def find_by_id_card(id_card):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM Customers WHERE id_card=? AND is_active=1", (id_card,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
        

def create_customer(full_name, id_card, phone, email, address):
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO Customers(full_name,id_card,phone,email,address) VALUES (?,?,?,?,?)",
            (full_name, id_card, phone, email, address)
        )
        cid = c.lastrowid
        conn.commit()
        return cid
    finally:
        conn.close()


def update_customer(cid, full_name, id_card, phone, email, address):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE Customers SET full_name=?,id_card=?,phone=?,email=?,address=? WHERE id=?",
            (full_name, id_card, phone, email, address, cid)
        )
        conn.commit()
    finally:
        conn.close()


def delete_customer(cid):
    """Soft delete — giữ lại lịch sử booking."""
    conn = get_conn()
    try:
        # Kiểm tra có booking đang active không
        active = conn.execute(
            f"""SELECT COUNT(*) FROM Bookings
                WHERE customer_id=? AND status IN ('{BOOKING_RESERVED}','{BOOKING_CHECKED_IN}')""",
            (cid,)
        ).fetchone()[0]
        if active > 0:
            raise ValueError("Không thể xóa khách hàng đang có booking đang hoạt động.")
        conn.execute("UPDATE Customers SET is_active=0 WHERE id=?", (cid,))
        conn.commit()
    finally:
        conn.close()


def get_booking_history_by_id_card(id_card):
    """Get full booking history for a customer by ID card."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT b.id, b.check_in_date, b.check_out_date, b.status, b.deposit_amount,
                      r.room_number, h.name as hotel_name
               FROM Bookings b
               JOIN Customers c ON b.customer_id=c.id
               JOIN BookingRooms br ON br.booking_id=b.id
               JOIN Rooms r ON br.room_id=r.id
               JOIN Hotels h ON r.hotel_id=h.id
               WHERE c.id_card=?
               ORDER BY b.check_in_date DESC""",
            (id_card,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_customers(query):
    conn = get_conn()
    try:
        q = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM Customers WHERE is_active=1 AND (full_name LIKE ? OR id_card LIKE ? OR phone LIKE ?)",
            (q, q, q)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
