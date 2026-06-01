from .base_model import get_conn
from utils.config import BOOKING_CHECKED_IN


def get_meal_types():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM MealTypes").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_menu_items(meal_type_id=None, active_only=True):
    conn = get_conn()
    q = """SELECT mi.*, mt.name as meal_type_name
           FROM MenuItems mi JOIN MealTypes mt ON mi.meal_type_id=mt.id
           WHERE 1=1"""
    params = []
    if active_only:
        q += " AND mi.is_active=1"
    if meal_type_id:
        q += " AND mi.meal_type_id=?"
        params.append(meal_type_id)
    q += " ORDER BY mt.id, mi.item_name"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_menu_item(meal_type_id, item_name, price):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO MenuItems(meal_type_id,item_name,price) VALUES (?,?,?)",
            (meal_type_id, item_name, price)
        )
        conn.commit()
    finally:
        conn.close()


def update_menu_item(mid, meal_type_id, item_name, price, is_active):
    conn = get_conn()
    conn.execute(
        "UPDATE MenuItems SET meal_type_id=?,item_name=?,price=?,is_active=? WHERE id=?",
        (meal_type_id, item_name, price, is_active, mid)
    )
    conn.commit(); conn.close()


def delete_menu_item(mid):
    conn = get_conn()
    conn.execute("UPDATE MenuItems SET is_active=0 WHERE id=?", (mid,))
    conn.commit(); conn.close()


def add_booking_meal(booking_id, menu_item_id, quantity, unit_price):
    conn = get_conn()
    conn.execute(
        "INSERT INTO BookingMeals(booking_id,menu_item_id,quantity,unit_price) VALUES (?,?,?,?)",
        (booking_id, menu_item_id, quantity, unit_price)
    )
    conn.commit(); conn.close()


def get_booking_meals(booking_id):
    conn = get_conn()
    rows = conn.execute(
        """SELECT bm.*, mi.item_name, mt.name as meal_type_name
           FROM BookingMeals bm
           JOIN MenuItems mi ON bm.menu_item_id=mi.id
           JOIN MealTypes mt ON mi.meal_type_id=mt.id
           WHERE bm.booking_id=?
           ORDER BY bm.order_time""",
        (booking_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_booking_meal(bmid):
    conn = get_conn()
    conn.execute("DELETE FROM BookingMeals WHERE id=?", (bmid,))
    conn.commit(); conn.close()


def get_active_bookings_for_hotel(hotel_id):
    """Get active bookings for chef to select which room to order for."""
    conn = get_conn()
    rows = conn.execute(
        f"""SELECT b.id, b.check_in_date, b.check_out_date,
                   r.room_number, c.full_name as customer_name
            FROM Bookings b
            JOIN BookingRooms br ON br.booking_id=b.id
            JOIN Rooms r ON br.room_id=r.id
            JOIN Customers c ON b.customer_id=c.id
            WHERE r.hotel_id=? AND b.status='{BOOKING_CHECKED_IN}'
            ORDER BY r.room_number""",
        (hotel_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
