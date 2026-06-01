from .base_model import get_conn
from utils.config import BOOKING_CHECKED_IN, BOOKING_RESERVED, STATUS_DIRTY


def get_rooms(hotel_id=None):
    conn = get_conn()
    try:
        q = """SELECT r.*, rt.type_name, rt.price_per_night, h.name as hotel_name
               FROM Rooms r
               JOIN RoomTypes rt ON r.type_id=rt.id
               JOIN Hotels h ON r.hotel_id=h.id
               WHERE 1=1"""
        params = []
        if hotel_id:
            q += " AND r.hotel_id=?"
            params.append(hotel_id)
        q += " ORDER BY r.hotel_id, r.floor, r.room_number"
        rows = conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_room(room_id):
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT r.*, rt.type_name, rt.price_per_night
               FROM Rooms r JOIN RoomTypes rt ON r.type_id=rt.id
               WHERE r.id=?""", (room_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_room(hotel_id, type_id, room_number, floor):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO Rooms(hotel_id,type_id,room_number,floor) VALUES (?,?,?,?)",
            (hotel_id, type_id, room_number, floor)
        )
        conn.commit()
    finally:
        conn.close()


def update_room(room_id, type_id, room_number, floor):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE Rooms SET type_id=?,room_number=?,floor=? WHERE id=?",
            (type_id, room_number, floor, room_id)
        )
        conn.commit()
    finally:
        conn.close()


def delete_room(room_id):
    """Soft delete — kiểm tra không có booking active trước khi xóa."""
    conn = get_conn()
    try:
        active = conn.execute(
            f"""SELECT COUNT(*) FROM BookingRooms br
                JOIN Bookings b ON br.booking_id=b.id
                WHERE br.room_id=? AND b.status IN ('{BOOKING_RESERVED}','{BOOKING_CHECKED_IN}')""",
            (room_id,)
        ).fetchone()[0]
        if active > 0:
            raise ValueError("Không thể xóa phòng đang có booking đang hoạt động.")
        conn.execute("DELETE FROM Rooms WHERE id=?", (room_id,))
        conn.commit()
    finally:
        conn.close()


def set_housekeeping_status(room_id, status):
    """Only housekeeping role can call this."""
    conn = get_conn()
    try:
        conn.execute("UPDATE Rooms SET housekeeping=? WHERE id=?", (status, room_id))
        conn.commit()
    finally:
        conn.close()


def set_occupancy_status(room_id, status):
    conn = get_conn()
    try:
        conn.execute("UPDATE Rooms SET occupancy_status=? WHERE id=?", (status, room_id))
        conn.commit()
    finally:
        conn.close()


def get_room_types():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM RoomTypes ORDER BY price_per_night").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_room_type(type_name, price, max_guest, description):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO RoomTypes(type_name,price_per_night,max_guest,description) VALUES (?,?,?,?)",
            (type_name, price, max_guest, description)
        )
        conn.commit()
    finally:
        conn.close()


def update_room_type(tid, type_name, price, max_guest, description):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE RoomTypes SET type_name=?,price_per_night=?,max_guest=?,description=? WHERE id=?",
            (type_name, price, max_guest, description, tid)
        )
        conn.commit()
    finally:
        conn.close()
