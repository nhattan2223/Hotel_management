"""
Booking business logic layer.
All booking operations that involve multiple models or complex logic go here.
"""
import datetime
import sqlite3

from models import booking_model, room_model, customer_model, invoice_model, service_model, menu_model
from utils.config import (STATUS_AVAILABLE, STATUS_OCCUPIED, STATUS_DIRTY, STATUS_CLEAN,
                          BOOKING_CHECKED_IN, BOOKING_CHECKED_OUT, BOOKING_CANCELLED,
                          BOOKING_RESERVED,
                          VAT_RATE, DB_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────────────────────────────────────

def is_checkin_time_reached(booking: dict, now: datetime.datetime | None = None) -> bool:
    check_in = datetime.datetime.fromisoformat(booking["check_in_date"])
    if now is None:
        now = datetime.datetime.now(check_in.tzinfo) if check_in.tzinfo else datetime.datetime.now()
    elif check_in.tzinfo and now.tzinfo is None:
        now = now.replace(tzinfo=check_in.tzinfo)
    elif not check_in.tzinfo and now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    return now >= check_in


def format_booking_datetime(value: str) -> str:
    return datetime.datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M")


def cancel_expired_unchecked_bookings(hotel_id=None, now: datetime.datetime | None = None) -> int:
    if now is None:
        now = datetime.datetime.now()
    return booking_model.cancel_expired_unchecked_bookings(hotel_id, now.isoformat(timespec="seconds"))


def checkout_expired_checkedin_bookings(hotel_id=None, now: datetime.datetime | None = None) -> int:
    if now is None:
        now = datetime.datetime.now()
    return booking_model.checkout_expired_checkedin_bookings(hotel_id, now.isoformat(timespec="seconds"))


def compute_room_display_status(room: dict) -> str:
    """
    Tính trạng thái hiển thị của phòng cho màn hình lễ tân.
      - Dirty  → 'Dirty'
      - Occupied → 'Occupied'
      - Có reservation check-in trong ngày/hôm sau → 'Reserved'
      - Còn lại → 'Available'
    """
    if room["housekeeping"] == STATUS_DIRTY:
        return STATUS_DIRTY
    if room["occupancy_status"] == STATUS_OCCUPIED:
        return STATUS_OCCUPIED

    today = datetime.date.today()
    bookings = booking_model.get_bookings_for_room(room["id"])
    for b in bookings:
        if b["status"] in (BOOKING_CANCELLED, BOOKING_CHECKED_OUT):
            continue
        check_in = datetime.datetime.fromisoformat(b["check_in_date"]).date()
        if check_in - datetime.timedelta(days=1) <= today:
            return BOOKING_RESERVED

    return STATUS_AVAILABLE


# ─────────────────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────────────────

def create_booking_with_validation(customer_id, room_ids, user_id,
                                    check_in_str, check_out_str,
                                    deposit, note) -> dict:
    """
    Validate và tạo booking với một hoặc nhiều phòng.
    room_ids: int hoặc list[int]
    Returns {"ok": True, "booking_id": int} hoặc {"ok": False, "error": str}
    """
    if isinstance(room_ids, int):
        room_ids = [room_ids]
    room_ids = list(dict.fromkeys(room_ids))  # loại trùng, giữ thứ tự

    try:
        ci = datetime.datetime.fromisoformat(check_in_str)
        co = datetime.datetime.fromisoformat(check_out_str)
    except ValueError:
        return {"ok": False, "error": "Ngày không hợp lệ."}

    if co <= ci:
        return {"ok": False, "error": "Ngày trả phòng phải sau ngày nhận phòng."}

    # Kiểm tra availability cho tất cả phòng
    conflicts = booking_model.check_rooms_availability(room_ids, check_in_str, check_out_str)
    if conflicts:
        conflict_rooms = []
        for rid in conflicts:
            r = room_model.get_room(rid)
            conflict_rooms.append(r["room_number"] if r else str(rid))
        return {"ok": False, "error": f"Phòng {', '.join(conflict_rooms)} đã được đặt trong khoảng thời gian này."}

    # Lấy thông tin tất cả phòng
    rooms_info = []
    total_price_snapshot = 0
    for room_id in room_ids:
        room = room_model.get_room(room_id)
        if not room:
            return {"ok": False, "error": f"Không tìm thấy phòng ID={room_id}."}
        price = float(room.get("price_per_night", 0) or 0)
        rooms_info.append({"room": room, "price_snapshot": price})
        total_price_snapshot += price

    # Validate deposit dựa trên tổng tiền tất cả phòng
    nights = max((co.date() - ci.date()).days, 1)
    max_deposit = nights * total_price_snapshot
    try:
        dep = float(deposit or 0)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Đặt cọc không hợp lệ."}
    if dep > max_deposit:
        return {"ok": False, "error": f"Đặt cọc không được lớn hơn tổng tiền phòng ({int(max_deposit):,} đ)."}

    # Tạo booking
    bid = booking_model.create_booking(
        customer_id, user_id,
        check_in_str, check_out_str, deposit, note
    )

    # Lưu tất cả phòng vào BookingRooms
    room_entries = [{"room_id": ri["room"]["id"], "price_snapshot": ri["price_snapshot"]}
                    for ri in rooms_info]
    booking_model.set_booking_rooms(bid, room_entries)

    # Tạo RoomChargeHistory cho từng phòng
    for ri in rooms_info:
        booking_model.create_room_charge(
            bid,
            ri["room"]["id"],
            ri["room"]["room_number"],
            ri["room"]["type_id"],
            ri["room"]["type_name"],
            ri["price_snapshot"],
            check_in_str,
            None,
        )

    return {"ok": True, "booking_id": bid}


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def update_booking_with_validation(bid, room_ids, check_in_str, check_out_str,
                                    deposit, note, status) -> dict:
    """
    Validate và cập nhật booking.
    room_ids: int hoặc list[int] — danh sách phòng mới muốn áp dụng.
    """
    if isinstance(room_ids, int):
        room_ids = [room_ids]
    room_ids = list(dict.fromkeys(room_ids))

    try:
        ci = datetime.datetime.fromisoformat(check_in_str)
        co = datetime.datetime.fromisoformat(check_out_str)
    except ValueError:
        return {"ok": False, "error": "Ngày không hợp lệ."}

    if co <= ci:
        return {"ok": False, "error": "Ngày trả phòng phải sau ngày nhận phòng."}

    booking = booking_model.get_booking(bid)
    if not booking:
        return {"ok": False, "error": "Không tìm thấy booking."}

    # Kiểm tra availability (loại trừ booking này)
    conflicts = booking_model.check_rooms_availability(room_ids, check_in_str, check_out_str,
                                                        exclude_booking_id=bid)
    if conflicts:
        conflict_rooms = []
        for rid in conflicts:
            r = room_model.get_room(rid)
            b_conf = booking_model.get_booking_conflict(rid, check_in_str, check_out_str,
                                                         exclude_booking_id=bid)
            room_num = r["room_number"] if r else str(rid)
            if b_conf and b_conf["status"] == BOOKING_CHECKED_IN:
                conflict_rooms.append(f"{room_num} (đang có khách)")
            else:
                conflict_rooms.append(room_num)
        return {"ok": False, "error": f"Phòng {', '.join(conflict_rooms)} đã được đặt trong khoảng thời gian này."}

    # Lấy thông tin phòng cũ để giữ giá snapshot theo loại phòng
    old_rooms = booking_model.get_booking_rooms(bid)
    old_room_map = {br["room_id"]: br for br in old_rooms}
    # Map type_id -> price_snapshot (ưu tiên phòng đầu tiên của loại đó)
    old_type_snapshot = {}
    for br in old_rooms:
        if br["type_id"] not in old_type_snapshot:
            old_type_snapshot[br["type_id"]] = float(br["price_snapshot"] or 0)

    # Lấy thông tin phòng mới
    rooms_info = []
    total_price_snapshot = 0
    for room_id in room_ids:
        room = room_model.get_room(room_id)
        if not room:
            return {"ok": False, "error": f"Không tìm thấy phòng ID={room_id}."}

        if room_id in old_room_map:
            # Giữ nguyên giá snapshot nếu là phòng cũ
            price = float(old_room_map[room_id]["price_snapshot"] or 0)
        elif room["type_id"] in old_type_snapshot:
            # Cùng loại phòng với phòng cũ → dùng giá snapshot của loại đó
            price = old_type_snapshot[room["type_id"]]
        else:
            # Loại phòng mới → lấy giá hiện tại
            price = float(room.get("price_per_night", 0) or 0)

        rooms_info.append({"room": room, "price_snapshot": price})
        total_price_snapshot += price

    # Validate deposit
    nights = max((co.date() - ci.date()).days, 1)
    max_deposit = nights * total_price_snapshot
    try:
        dep = float(deposit or 0)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Đặt cọc không hợp lệ."}
    if dep > max_deposit:
        return {"ok": False, "error": f"Đặt cọc không được lớn hơn tổng tiền phòng ({int(max_deposit):,} đ)."}

    # Cập nhật Bookings
    booking_model.update_booking(bid, check_in_str, check_out_str, deposit, note, status)

    # Đồng bộ BookingRooms
    room_entries = [{"room_id": ri["room"]["id"], "price_snapshot": ri["price_snapshot"]}
                    for ri in rooms_info]
    booking_model.set_booking_rooms(bid, room_entries)

    # Cập nhật RoomChargeHistory cho phòng đầu tiên (nếu chưa checked-in)
    if booking["status"] != BOOKING_CHECKED_IN:
        for ri in rooms_info:
            booking_model.update_active_room_charge(
                bid,
                ri["room"]["id"],
                ri["room"]["room_number"],
                ri["room"]["type_id"],
                ri["room"]["type_name"],
                ri["price_snapshot"],
                check_in_str,
                None,
            )

    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────────
# INVOICE
# ─────────────────────────────────────────────────────────────────────────────

def compute_invoice(booking_id) -> dict:
    """Tính toán chi tiết hóa đơn cho một booking."""
    booking = booking_model.get_booking(booking_id)
    if not booking:
        return {}

    ci = datetime.datetime.fromisoformat(booking["check_in_date"])
    co = datetime.datetime.fromisoformat(booking["check_out_date"])
    nights = max((co.date() - ci.date()).days, 1)

    charges = booking_model.get_room_charges(booking_id)
    room_amt = 0
    room_detail_rows = []

    if charges:
        for charge in charges:
            start = datetime.datetime.fromisoformat(charge["start_date"])
            end = (datetime.datetime.fromisoformat(charge["end_date"])
                   if charge["end_date"] else co)
            if start < ci:
                start = ci
            if end > co:
                end = co
            if end <= start:
                continue
            segment_nights = max((end.date() - start.date()).days, 0)
            segment_amount = segment_nights * charge["price_per_night"]
            room_amt += segment_amount
            room_detail_rows.append({
                "room_number":    charge["room_number"],
                "room_type_name": charge["room_type_name"],
                "nights":         segment_nights,
                "price_snapshot": charge["price_per_night"],
                "amount":         segment_amount,
            })
    else:
        # Fallback: lấy từ BookingRooms
        booking_rooms = booking_model.get_booking_rooms(booking_id)
        for br in booking_rooms:
            room_amt += nights * br["price_snapshot"]
            room_detail_rows.append({
                "room_number":    br["room_number"],
                "room_type_name": br["type_name"],
                "nights":         nights,
                "price_snapshot": br["price_snapshot"],
                "amount":         nights * br["price_snapshot"],
            })

    if room_detail_rows and sum(item["nights"] for item in room_detail_rows) == 0 and nights == 1:
        room_detail_rows[0]["nights"] = 1
        room_detail_rows[0]["amount"] = room_detail_rows[0]["price_snapshot"]
        room_amt = room_detail_rows[0]["amount"]

    services = service_model.get_booking_services(booking_id)
    svc_amt  = sum(s["quantity"] * s["unit_price"] for s in services)

    meals    = menu_model.get_booking_meals(booking_id)
    meal_amt = sum(m["quantity"] * m["unit_price"] for m in meals)

    subtotal = room_amt + svc_amt + meal_amt
    tax      = round(subtotal * VAT_RATE, 0)
    discount = booking["deposit_amount"] or 0
    final    = subtotal + tax - discount

    return {
        "booking":            booking,
        "nights":             nights,
        "room_amount":        room_amt,
        "room_charge_details": room_detail_rows,
        "service_amount":     svc_amt,
        "meal_amount":        meal_amt,
        "subtotal":           subtotal,
        "tax":                tax,
        "discount":           discount,
        "final_amount":       final,
        "services":           services,
        "meals":              meals,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CHECK-IN / CHECK-OUT
# ─────────────────────────────────────────────────────────────────────────────

def do_checkin(booking_id) -> dict:
    booking = booking_model.get_booking(booking_id)
    if not booking:
        return {"ok": False, "error": "Không tìm thấy booking."}
    if booking["status"] != BOOKING_RESERVED:
        return {"ok": False, "error": f"Trạng thái booking là '{booking['status']}', không thể check-in."}
    if not is_checkin_time_reached(booking):
        check_in = format_booking_datetime(booking["check_in_date"])
        return {"ok": False, "error": f"Chưa đến thời gian check-in ({check_in}), không thể check-in."}

    # Kiểm tra housekeeping cho tất cả phòng
    rooms = booking_model.get_booking_rooms(booking_id)
    for br in rooms:
        room = room_model.get_room(br["room_id"])
        if room and room["housekeeping"] == STATUS_DIRTY:
            return {"ok": False, "error": f"Phòng {room['room_number']} đang được dọn dẹp, chưa thể check-in."}

    booking_model.checkin_booking(booking_id)
    return {"ok": True}


def do_checkout(booking_id, user_id) -> dict:
    booking = booking_model.get_booking(booking_id)
    if not booking:
        return {"ok": False, "error": "Không tìm thấy booking."}
    if booking["status"] != BOOKING_CHECKED_IN:
        return {"ok": False, "error": "Khách chưa check-in."}
    booking_model.checkout_booking(booking_id, user_id)
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────────
# SWITCH ROOM
# ─────────────────────────────────────────────────────────────────────────────

def switch_room(booking_id: int, old_room_id: int, new_room_id: int,
                switch_date_str: str) -> dict:
    """
    Đổi một phòng cụ thể trong booking đang Checked-in sang phòng mới.
    - Đóng RoomChargeHistory của old_room tại switch_date
    - Tạo RoomChargeHistory mới cho new_room từ switch_date
    - Cập nhật BookingRooms: thay old_room_id → new_room_id
    - Cập nhật occupancy_status của 2 phòng
    """
    booking = booking_model.get_booking(booking_id)
    if not booking:
        return {"ok": False, "error": "Không tìm thấy booking."}
    if booking["status"] != BOOKING_CHECKED_IN:
        return {"ok": False, "error": "Chỉ có thể đổi phòng khi booking đang Checked-in."}

    try:
        switch_dt = datetime.datetime.fromisoformat(switch_date_str)
        ci = datetime.datetime.fromisoformat(booking["check_in_date"])
        co = datetime.datetime.fromisoformat(booking["check_out_date"])
    except ValueError:
        return {"ok": False, "error": "Ngày đổi phòng không hợp lệ."}

    if switch_dt <= ci:
        return {"ok": False, "error": "Ngày đổi phòng phải sau ngày check-in."}
    if switch_dt >= co:
        return {"ok": False, "error": "Ngày đổi phòng phải trước ngày check-out."}

    if not booking_model.check_room_availability(
            new_room_id, switch_date_str, booking["check_out_date"],
            exclude_booking_id=booking_id):
        return {"ok": False, "error": "Phòng mới đã được đặt trong khoảng thời gian này."}

    new_room = room_model.get_room(new_room_id)
    if not new_room:
        return {"ok": False, "error": "Không tìm thấy phòng mới."}
    # Kiểm tra phòng mới có đang dọn dẹp không   <-- thêm mới
    if new_room["housekeeping"] == STATUS_DIRTY:
        return {"ok": False, "error": f"Phòng {new_room['room_number']} đang được dọn dẹp, chưa thể chuyển vào."}

    old_room = room_model.get_room(old_room_id)
    if not old_room:
        return {"ok": False, "error": "Không tìm thấy phòng cũ."}

    # Kiểm tra old_room có trong booking không
    booking_rooms = booking_model.get_booking_rooms(booking_id)
    if not any(br["room_id"] == old_room_id for br in booking_rooms):
        return {"ok": False, "error": "Phòng cũ không thuộc booking này."}

    # Tìm charge đang active của old_room
    charges = booking_model.get_room_charges(booking_id)
    old_charge = next(
        (c for c in charges if c["room_id"] == old_room_id and c["end_date"] is None),
        None
    )
    if old_charge is None:
        return {"ok": False, "error": "Không tìm thấy lịch sử tính tiền của phòng cũ."}

    # 1. Đóng charge cũ tại switch_date
    booking_model.update_room_charge_end_date(old_charge["id"], switch_date_str)

    # 2. Tạo charge mới cho phòng mới
    booking_model.create_room_charge(
        booking_id,
        new_room_id,
        new_room["room_number"],
        new_room["type_id"],
        new_room["type_name"],
        float(new_room["price_per_night"]),
        switch_date_str,
        None,
    )

    # 3. Cập nhật BookingRooms
    booking_model.replace_booking_room(booking_id, old_room_id, new_room_id,
                                       float(new_room["price_per_night"]))

    # 4. Cập nhật trạng thái phòng
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE Rooms SET occupancy_status=?, housekeeping=? WHERE id=?",
            (STATUS_AVAILABLE, STATUS_DIRTY, old_room_id)
        )
        conn.execute(
            "UPDATE Rooms SET occupancy_status=?, housekeeping=? WHERE id=?",
            (STATUS_OCCUPIED, STATUS_CLEAN, new_room_id)
        )
        conn.commit()
    finally:
        conn.close()

    return {"ok": True}
