from .base_model import get_conn


# ── Helpers ───────────────────────────────────────────────────

def _validate_stock(service: dict, quantity: int):
    """Raise ValueError nếu tồn kho không đủ."""
    stk = service["stocking"]
    if stk is None:
        return  # không giới hạn
    if stk == 0:
        raise ValueError("Dịch vụ này đã hết hàng.")
    if quantity > stk:
        raise ValueError(f"Số lượng đặt vượt quá tồn kho. Hiện còn {stk}.")


def _adjust_stock(conn, service_id: int, delta: int):
    """Cộng/trừ tồn kho. delta âm = trừ, dương = hoàn trả."""
    conn.execute(
        "UPDATE Services SET stocking = stocking + ? WHERE id = ? AND stocking IS NOT NULL",
        (delta, service_id)
    )


# ── Services CRUD ─────────────────────────────────────────────

def get_services(active_only: bool = True) -> list[dict]:
    conn = get_conn()
    q = "SELECT * FROM Services"
    if active_only:
        q += " WHERE is_active = 1"
    q += " ORDER BY service_name"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_service(service_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM Services WHERE id = ?", (service_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_service(stocking: int | None, name: str, price: float):
    conn = get_conn()
    conn.execute(
        "INSERT INTO Services(stocking, service_name, price) VALUES (?, ?, ?)",
        (stocking, name, price)
    )
    conn.commit()
    conn.close()


def update_service(sid: int, stocking: int | None, name: str, price: float, is_active: int):
    conn = get_conn()
    conn.execute(
        "UPDATE Services SET stocking=?, service_name=?, price=?, is_active=? WHERE id=?",
        (stocking, name, price, is_active, sid)
    )
    conn.commit()
    conn.close()


def delete_service(sid: int):
    """Soft delete — chỉ tắt kích hoạt."""
    conn = get_conn()
    conn.execute("UPDATE Services SET is_active = 0 WHERE id = ?", (sid,))
    conn.commit()
    conn.close()


# ── Booking Services ──────────────────────────────────────────

def get_booking_services(booking_id: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """SELECT bs.*, s.service_name, s.stocking
           FROM BookingServices bs
           JOIN Services s ON bs.service_id = s.id
           WHERE bs.booking_id = ?""",
        (booking_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_booking_service(booking_id: int, service_id: int, quantity: int, unit_price: float):
    service = get_service(service_id)
    if service is None:
        raise ValueError("Dịch vụ không tồn tại.")

    _validate_stock(service, quantity)

    conn = get_conn()
    conn.execute(
        "INSERT INTO BookingServices(booking_id, service_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        (booking_id, service_id, quantity, unit_price)
    )
    _adjust_stock(conn, service_id, -quantity)
    conn.commit()
    conn.close()


def delete_booking_service(bsid: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT service_id, quantity FROM BookingServices WHERE id = ?", (bsid,)
    ).fetchone()
    if row:
        _adjust_stock(conn, row["service_id"], row["quantity"])
    conn.execute("DELETE FROM BookingServices WHERE id = ?", (bsid,))
    conn.commit()
    conn.close()