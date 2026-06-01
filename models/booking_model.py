import datetime
from .base_model import get_conn
from utils.config import (BOOKING_CANCELLED, BOOKING_CHECKED_IN,
                          BOOKING_CHECKED_OUT, BOOKING_RESERVED,
                          STATUS_AVAILABLE, STATUS_CLEAN, STATUS_DIRTY,
                          STATUS_OCCUPIED)


# ─────────────────────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────────────────────

def get_bookings(hotel_id=None, status=None):
    """Trả về danh sách bookings, JOIN qua BookingRooms để lấy thông tin phòng.
    Mỗi booking hiển thị phòng đầu tiên (theo room_number) làm đại diện;
    tên tất cả phòng được gộp vào room_number_all.
    """
    conn = get_conn()
    try:
        q = """
            SELECT b.*,
                   c.full_name  AS customer_name,
                   c.id_card,
                   c.phone      AS customer_phone,
                   MIN(r.id)    AS room_id,
                   GROUP_CONCAT(r.room_number ORDER BY r.room_number)  AS room_number,
                   GROUP_CONCAT(r.room_number ORDER BY r.room_number)  AS room_number_all,
                   rt.type_name,
                   rt.price_per_night,
                   MIN(br.price_snapshot) AS price_snapshot,
                   h.name       AS hotel_name,
                   h.id         AS hotel_id,
                   u.full_name  AS staff_name
            FROM Bookings b
            JOIN Customers c  ON b.customer_id = c.id
            JOIN BookingRooms br ON br.booking_id = b.id
            JOIN Rooms r      ON br.room_id = r.id
            JOIN RoomTypes rt ON r.type_id  = rt.id
            JOIN Hotels h     ON r.hotel_id = h.id
            JOIN Users u      ON b.user_id  = u.id
            WHERE 1=1"""
        params = []
        if hotel_id:
            q += " AND h.id=?"
            params.append(hotel_id)
        if status:
            q += " AND b.status=?"
            params.append(status)
        q += " GROUP BY b.id ORDER BY b.check_in_date DESC"
        rows = conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_booking(bid):
    """Trả về một booking theo id, cùng thông tin phòng tổng hợp từ BookingRooms."""
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT b.*,
                      c.full_name  AS customer_name,
                      c.id_card,
                      c.phone      AS customer_phone,
                      MIN(r.id)    AS room_id,
                      GROUP_CONCAT(r.room_number ORDER BY r.room_number) AS room_number,
                      GROUP_CONCAT(r.room_number ORDER BY r.room_number) AS room_number_all,
                      rt.type_name,
                      rt.price_per_night,
                      MIN(br.price_snapshot) AS price_snapshot,
                      h.name       AS hotel_name,
                      h.id         AS hotel_id,
                      u2.full_name AS checked_out_by_name
               FROM Bookings b
               JOIN Customers c    ON b.customer_id = c.id
               JOIN BookingRooms br ON br.booking_id = b.id
               JOIN Rooms r        ON br.room_id = r.id
               JOIN RoomTypes rt   ON r.type_id  = rt.id
               JOIN Hotels h       ON r.hotel_id = h.id
               LEFT JOIN Users u2  ON b.check_out_by = u2.id
               WHERE b.id = ?
               GROUP BY b.id""",
            (bid,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_bookings_for_room(room_id):
    """Trả về các booking đang active có chứa phòng room_id (qua BookingRooms)."""
    conn = get_conn()
    try:
        rows = conn.execute(
            f"""SELECT DISTINCT b.*, c.full_name AS customer_name
                FROM Bookings b
                JOIN Customers c ON b.customer_id = c.id
                JOIN BookingRooms br ON br.booking_id = b.id
                WHERE b.status NOT IN ('{BOOKING_CANCELLED}','{BOOKING_CHECKED_OUT}')
                  AND br.room_id = ?
                ORDER BY b.check_in_date""",
            (room_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_booking_rooms(booking_id):
    """Trả về danh sách tất cả phòng trong một booking."""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT br.*, r.room_number, r.floor,
                      rt.type_name, rt.price_per_night,
                      r.type_id
               FROM BookingRooms br
               JOIN Rooms r      ON br.room_id = r.id
               JOIN RoomTypes rt ON r.type_id  = rt.id
               WHERE br.booking_id = ?
               ORDER BY r.room_number""",
            (booking_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# AVAILABILITY CHECK
# ─────────────────────────────────────────────────────────────────────────────

def check_room_availability(room_id, check_in, check_out, exclude_booking_id=None):
    """Trả về True nếu phòng trống trong khoảng check_in–check_out."""
    conn = get_conn()
    try:
        exclude_clause = "AND b.id != ?" if exclude_booking_id else ""
        q = f"""SELECT COUNT(*) FROM BookingRooms br
                JOIN Bookings b ON br.booking_id = b.id
                WHERE br.room_id = ?
                  AND b.status NOT IN ('{BOOKING_CANCELLED}','{BOOKING_CHECKED_OUT}')
                  AND b.check_in_date  < ?
                  AND b.check_out_date > ?
                  {exclude_clause}"""
        params = [room_id, check_out, check_in]
        if exclude_booking_id:
            params.append(exclude_booking_id)
        cnt = conn.execute(q, params).fetchone()[0]
        return cnt == 0
    finally:
        conn.close()


def check_rooms_availability(room_ids, check_in, check_out, exclude_booking_id=None):
    """Trả về list room_id bị conflict."""
    return [
        rid for rid in room_ids
        if not check_room_availability(rid, check_in, check_out, exclude_booking_id)
    ]


def get_booking_conflict(room_id, check_in, check_out, exclude_booking_id=None):
    """Trả về booking conflict nếu có, ngược lại None."""
    conn = get_conn()
    try:
        exclude_clause = "AND b.id != ?" if exclude_booking_id else ""
        q = f"""SELECT b.id, b.status, b.customer_id
                FROM BookingRooms br
                JOIN Bookings b ON br.booking_id = b.id
                WHERE br.room_id = ?
                  AND b.status NOT IN ('{BOOKING_CANCELLED}','{BOOKING_CHECKED_OUT}')
                  AND b.check_in_date  < ?
                  AND b.check_out_date > ?
                  {exclude_clause}"""
        params = [room_id, check_out, check_in]
        if exclude_booking_id:
            params.append(exclude_booking_id)
        row = conn.execute(q, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# CREATE / UPDATE / CANCEL
# ─────────────────────────────────────────────────────────────────────────────

def create_booking(customer_id, user_id, check_in, check_out, deposit, note):
    """Tạo booking mới (không có room_id — phòng lưu trong BookingRooms)."""
    conn = get_conn()
    try:
        c = conn.cursor()
        c.execute(
            """INSERT INTO Bookings(customer_id, user_id, check_in_date, check_out_date,
                                    deposit_amount, status, note)
               VALUES (?,?,?,?,?,?,?)""",
            (customer_id, user_id, check_in, check_out, deposit, BOOKING_RESERVED, note)
        )
        bid = c.lastrowid
        conn.commit()
        return bid
    finally:
        conn.close()


def update_booking(bid, check_in, check_out, deposit, note, status):
    """Cập nhật thông tin booking (không bao gồm phòng — dùng set_booking_rooms)."""
    conn = get_conn()
    try:
        conn.execute(
            """UPDATE Bookings
               SET check_in_date=?, check_out_date=?,
                   deposit_amount=?, note=?, status=?
               WHERE id=?""",
            (check_in, check_out, deposit, note, status, bid)
        )
        conn.commit()
    finally:
        conn.close()


def set_booking_rooms(booking_id, room_entries):
    """Đồng bộ danh sách phòng cho một booking.
    room_entries: list of dict {room_id, price_snapshot}
    """
    conn = get_conn()
    try:
        conn.execute("DELETE FROM BookingRooms WHERE booking_id=?", (booking_id,))
        for entry in room_entries:
            conn.execute(
                "INSERT INTO BookingRooms(booking_id, room_id, price_snapshot) VALUES (?,?,?)",
                (booking_id, entry["room_id"], entry["price_snapshot"])
            )
        conn.commit()
    finally:
        conn.close()


def replace_booking_room(booking_id, old_room_id, new_room_id, new_price_snapshot):
    """Thay thế một phòng trong BookingRooms (dùng khi đổi phòng giữa chừng)."""
    conn = get_conn()
    try:
        conn.execute(
            "DELETE FROM BookingRooms WHERE booking_id=? AND room_id=?",
            (booking_id, old_room_id)
        )
        exists = conn.execute(
            "SELECT 1 FROM BookingRooms WHERE booking_id=? AND room_id=?",
            (booking_id, new_room_id)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO BookingRooms(booking_id, room_id, price_snapshot) VALUES (?,?,?)",
                (booking_id, new_room_id, new_price_snapshot)
            )
        conn.commit()
    finally:
        conn.close()


def cancel_booking(bid):
    conn = get_conn()
    try:
        conn.execute(f"UPDATE Bookings SET status='{BOOKING_CANCELLED}' WHERE id=?", (bid,))
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# CHECK-IN / CHECK-OUT
# ─────────────────────────────────────────────────────────────────────────────

def checkin_booking(bid):
    """Chuyển trạng thái booking sang Checked-in và đánh dấu tất cả phòng Occupied."""
    conn = get_conn()
    try:
        room_rows = conn.execute(
            "SELECT room_id FROM BookingRooms WHERE booking_id=?", (bid,)
        ).fetchall()
        conn.execute(
            f"UPDATE Bookings SET status='{BOOKING_CHECKED_IN}' WHERE id=?", (bid,)
        )
        for rrow in room_rows:
            conn.execute(
                f"UPDATE Rooms SET occupancy_status='{STATUS_OCCUPIED}', housekeeping='{STATUS_CLEAN}' WHERE id=?",
                (rrow[0],)
            )
        conn.commit()
    finally:
        conn.close()


def checkout_booking(bid, user_id):
    """Chuyển trạng thái booking sang Checked-out và giải phóng tất cả phòng."""
    conn = get_conn()
    try:
        room_rows = conn.execute(
            "SELECT room_id FROM BookingRooms WHERE booking_id=?", (bid,)
        ).fetchall()
        conn.execute(
            f"UPDATE Bookings SET status='{BOOKING_CHECKED_OUT}', check_out_by=? WHERE id=?",
            (user_id, bid)
        )
        for rrow in room_rows:
            conn.execute(
                f"UPDATE Rooms SET occupancy_status='{STATUS_AVAILABLE}', housekeeping='{STATUS_DIRTY}' WHERE id=?",
                (rrow[0],)
            )
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# EXPIRED BOOKING JOBS
# ─────────────────────────────────────────────────────────────────────────────

def cancel_expired_unchecked_bookings(hotel_id=None, now_str=None):
    """Huỷ các booking Reserved đã quá hạn check-out."""
    if now_str is None:
        now_str = datetime.datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    try:
        q = f"""UPDATE Bookings
                SET status='{BOOKING_CANCELLED}'
                WHERE status='{BOOKING_RESERVED}'
                  AND check_out_date < ?"""
        params = [now_str]
        if hotel_id:
            q += """ AND id IN (
                        SELECT br.booking_id FROM BookingRooms br
                        JOIN Rooms r ON br.room_id = r.id
                        WHERE r.hotel_id = ?
                    )"""
            params.append(hotel_id)
        cur = conn.execute(q, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def checkout_expired_checkedin_bookings(hotel_id=None, now_str=None):
    """Tự động checkout các booking Checked-in đã quá giờ."""
    if now_str is None:
        now_str = datetime.datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    try:
        q = f"""SELECT DISTINCT b.id
                FROM Bookings b
                JOIN BookingRooms br ON br.booking_id = b.id
                JOIN Rooms r ON br.room_id = r.id
                WHERE b.status='{BOOKING_CHECKED_IN}'
                  AND datetime(b.check_out_date) < datetime(?)"""
        params = [now_str]
        if hotel_id:
            q += " AND r.hotel_id=?"
            params.append(hotel_id)
        rows = conn.execute(q, params).fetchall()
        if not rows:
            return 0
        booking_ids = [row[0] for row in rows]

        # Lấy tất cả room_id liên quan
        marks = ",".join("?" for _ in booking_ids)
        room_rows = conn.execute(
            f"SELECT DISTINCT room_id FROM BookingRooms WHERE booking_id IN ({marks})",
            booking_ids
        ).fetchall()
        room_ids = [r[0] for r in room_rows]

        conn.execute(
            f"UPDATE Bookings SET status='{BOOKING_CHECKED_OUT}' WHERE id IN ({marks})",
            booking_ids,
        )
        if room_ids:
            room_marks = ",".join("?" for _ in room_ids)
            conn.execute(
                f"""UPDATE Rooms
                    SET occupancy_status='{STATUS_AVAILABLE}', housekeeping='{STATUS_DIRTY}'
                    WHERE id IN ({room_marks})""",
                room_ids,
            )
        conn.commit()
        return len(booking_ids)
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# ROOM CHARGE HISTORY
# ─────────────────────────────────────────────────────────────────────────────

def create_room_charge(booking_id, room_id, room_number, room_type_id,
                       room_type_name, price_per_night, start_date, end_date=None):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO RoomChargeHistory(booking_id, room_id, room_number, room_type_id,
                                             room_type_name, price_per_night, start_date, end_date)
               VALUES (?,?,?,?,?,?,?,?)""",
            (booking_id, room_id, room_number, room_type_id,
             room_type_name, price_per_night, start_date, end_date)
        )
        conn.commit()
    finally:
        conn.close()


def get_room_charges(booking_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM RoomChargeHistory WHERE booking_id=? ORDER BY start_date ASC",
            (booking_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_active_room_charge(booking_id):
    conn = get_conn()
    try:
        row = conn.execute(
            """SELECT * FROM RoomChargeHistory
               WHERE booking_id=? AND end_date IS NULL
               ORDER BY start_date DESC LIMIT 1""",
            (booking_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_room_charge_end_date(charge_id, end_date):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE RoomChargeHistory SET end_date=? WHERE id=?",
            (end_date, charge_id)
        )
        conn.commit()
    finally:
        conn.close()


def update_active_room_charge(booking_id, room_id, room_number, room_type_id,
                               room_type_name, price_per_night, start_date, end_date=None):
    conn = get_conn()
    try:
        active = conn.execute(
            """SELECT id FROM RoomChargeHistory
               WHERE booking_id=? AND end_date IS NULL
               ORDER BY start_date DESC LIMIT 1""",
            (booking_id,)
        ).fetchone()
        if active:
            conn.execute(
                """UPDATE RoomChargeHistory
                   SET room_id=?, room_number=?, room_type_id=?, room_type_name=?,
                       price_per_night=?, start_date=?, end_date=?
                   WHERE id=?""",
                (room_id, room_number, room_type_id, room_type_name,
                 price_per_night, start_date, end_date, active["id"])
            )
        else:
            conn.execute(
                """INSERT INTO RoomChargeHistory(booking_id, room_id, room_number, room_type_id,
                                                 room_type_name, price_per_night, start_date, end_date)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (booking_id, room_id, room_number, room_type_id,
                 room_type_name, price_per_night, start_date, end_date)
            )
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# GANTT
# ─────────────────────────────────────────────────────────────────────────────

def get_all_bookings_for_gantt(hotel_id):
    """Trả về tất cả booking không bị huỷ cho Gantt chart.
    Mỗi row là 1 segment (phòng × khoảng thời gian) từ RoomChargeHistory.
    Fallback sang BookingRooms nếu chưa có RoomChargeHistory.
    """
    conn = get_conn()
    try:
        bookings = conn.execute(
            f"""SELECT b.id, b.check_in_date, b.check_out_date, b.status,
                       c.full_name AS customer_name
                FROM Bookings b
                JOIN Customers c ON b.customer_id = c.id
                JOIN BookingRooms br ON br.booking_id = b.id
                JOIN Rooms r ON br.room_id = r.id
                WHERE r.hotel_id = ? AND b.status != '{BOOKING_CANCELLED}'
                GROUP BY b.id""",
            (hotel_id,)
        ).fetchall()

        result = []

        for bk in bookings:
            bid = bk["id"]

            # Thử lấy từ RoomChargeHistory trước
            charges = conn.execute(
                """SELECT rch.room_id, rch.room_number, rch.room_type_name,
                          rch.start_date, rch.end_date,
                          r.floor, rt.type_name
                   FROM RoomChargeHistory rch
                   JOIN Rooms r     ON rch.room_id = r.id
                   JOIN RoomTypes rt ON r.type_id  = rt.id
                   WHERE rch.booking_id = ?
                   ORDER BY rch.start_date ASC""",
                (bid,)
            ).fetchall()

            if charges:
                for ch in charges:
                    end = ch["end_date"] if ch["end_date"] else bk["check_out_date"]
                    result.append({
                        "id":             bid,
                        "check_in_date":  ch["start_date"],
                        "check_out_date": end,
                        "status":         bk["status"],
                        "room_number":    ch["room_number"],
                        "room_id":        ch["room_id"],
                        "floor":          ch["floor"],
                        "type_name":      ch["type_name"],
                        "customer_name":  bk["customer_name"],
                    })
            else:
                # Fallback: BookingRooms
                br_rows = conn.execute(
                    """SELECT br.room_id, r.room_number, r.floor, rt.type_name
                       FROM BookingRooms br
                       JOIN Rooms r      ON br.room_id = r.id
                       JOIN RoomTypes rt ON r.type_id  = rt.id
                       WHERE br.booking_id = ?""",
                    (bid,)
                ).fetchall()

                for br in br_rows:
                    result.append({
                        "id":             bid,
                        "check_in_date":  bk["check_in_date"],
                        "check_out_date": bk["check_out_date"],
                        "status":         bk["status"],
                        "room_number":    br["room_number"],
                        "room_id":        br["room_id"],
                        "floor":          br["floor"],
                        "type_name":      br["type_name"],
                        "customer_name":  bk["customer_name"],
                    })

        return result
    finally:
        conn.close()
