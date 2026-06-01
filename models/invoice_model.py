from .base_model import get_conn
from utils.config import PAYMENT_STATUS_PAID, STATUS_OCCUPIED


def get_invoice(booking_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM Invoices WHERE booking_id=?", (booking_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def upsert_invoice(booking_id, room_amt, svc_amt, meal_amt, tax, discount, final_amt,
                   payment_method, payment_status):
    conn = get_conn()
    try:
        existing = conn.execute("SELECT id FROM Invoices WHERE booking_id=?", (booking_id,)).fetchone()
        if existing:
            conn.execute(
                """UPDATE Invoices SET total_room_amount=?,total_service_amount=?,
                   total_meal_amount=?,tax=?,discount=?,final_amount=?,
                   payment_method=?,payment_status=? WHERE booking_id=?""",
                (room_amt, svc_amt, meal_amt, tax, discount, final_amt,
                 payment_method, payment_status, booking_id)
            )
        else:
            conn.execute(
                """INSERT INTO Invoices(booking_id,total_room_amount,total_service_amount,
                   total_meal_amount,tax,discount,final_amount,payment_method,payment_status)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (booking_id, room_amt, svc_amt, meal_amt, tax, discount, final_amt,
                 payment_method, payment_status)
            )
        conn.commit()
    finally:
        conn.close()


def get_revenue_by_day(hotel_id, year, month):
    conn = get_conn()
    try:
        rows = conn.execute(
            f"""SELECT strftime('%d', i.created_at) as day,
                       SUM(i.final_amount) as total
                FROM Invoices i
                JOIN Bookings b ON i.booking_id=b.id
                WHERE EXISTS (
                    SELECT 1 FROM BookingRooms br
                    JOIN Rooms r ON br.room_id=r.id
                    WHERE br.booking_id=b.id AND r.hotel_id=?
                )
                  AND strftime('%Y', i.created_at)=?
                  AND strftime('%m', i.created_at)=?
                  AND i.payment_status='{PAYMENT_STATUS_PAID}'
                GROUP BY day ORDER BY day""",
            (hotel_id, str(year), str(month).zfill(2))
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_revenue_by_month(hotel_id, year):
    conn = get_conn()
    try:
        rows = conn.execute(
            f"""SELECT strftime('%m', i.created_at) as month,
                       SUM(i.final_amount) as total
                FROM Invoices i
                JOIN Bookings b ON i.booking_id=b.id
                WHERE EXISTS (
                    SELECT 1 FROM BookingRooms br
                    JOIN Rooms r ON br.room_id=r.id
                    WHERE br.booking_id=b.id AND r.hotel_id=?
                )
                  AND strftime('%Y', i.created_at)=?
                  AND i.payment_status='{PAYMENT_STATUS_PAID}'
                GROUP BY month ORDER BY month""",
            (hotel_id, str(year))
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_top_customers(hotel_id, limit=10):
    conn = get_conn()
    try:
        rows = conn.execute(
            f"""SELECT c.full_name, c.phone, COUNT(b.id) as stays,
                       SUM(i.final_amount) as total_spent
                FROM Customers c
                JOIN Bookings b ON b.customer_id=c.id
                LEFT JOIN Invoices i ON i.booking_id=b.id
                WHERE i.payment_status='{PAYMENT_STATUS_PAID}'
                  AND EXISTS (
                    SELECT 1 FROM BookingRooms br
                    JOIN Rooms r ON br.room_id=r.id
                    WHERE br.booking_id=b.id AND r.hotel_id=?
                )
                GROUP BY c.id ORDER BY total_spent DESC LIMIT ?""",
            (hotel_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_occupancy_stats(hotel_id):
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM Rooms WHERE hotel_id=?", (hotel_id,)).fetchone()[0]
        occupied = conn.execute(
            f"SELECT COUNT(*) FROM Rooms WHERE hotel_id=? AND occupancy_status='{STATUS_OCCUPIED}'",
            (hotel_id,)
        ).fetchone()[0]
        return {"total": total, "occupied": occupied,
                "rate": round(occupied / total * 100, 1) if total else 0}
    finally:
        conn.close()
