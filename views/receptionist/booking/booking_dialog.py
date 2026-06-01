import datetime
import re

from PyQt6.QtWidgets import QDialog, QListWidgetItem, QMessageBox
from PyQt6.QtCore import QDateTime, Qt

from utils.config import BOOKING_STATUS_VN, STATUS_DIRTY
from models import room_model, customer_model
from services.booking_service import (
    create_booking_with_validation,
    update_booking_with_validation,
)
from views.receptionist.booking.booking_dialog_ui import setup_booking_dialog_ui


STATUS_VN = BOOKING_STATUS_VN


class BookingDialog(QDialog):
    """Dialog tạo mới / chỉnh sửa booking — hỗ trợ nhiều phòng."""

    def __init__(self, user: dict, booking: dict = None, parent=None):
        super().__init__(parent)
        self.user     = user
        self.booking  = booking
        self.hotel_id = user["hotel_id"]
        self._customer_id = None
        self._selected_rooms = []
        self._all_rooms = []

        self.setWindowTitle(
            "Tạo booking mới" if not booking else f"Sửa Booking #{booking['id']}"
        )
        self.setMinimumWidth(620)
        self.resize(640, 750)
        setup_booking_dialog_ui(self)
        if booking:
            self._fill(booking)

    # ── Room loading helpers ───────────────────────────────────────────────────

    def _load_room_types(self):
        self.room_type_combo.clear()
        self.room_type_combo.addItem("Tất cả loại phòng", None)
        self._room_types = room_model.get_room_types()
        for rt in self._room_types:
            self.room_type_combo.addItem(rt["type_name"], rt["id"])

    def _load_all_rooms(self):
        self._all_rooms = room_model.get_rooms(self.hotel_id)
        self._refresh_available_list()

    def _refresh_available_list(self):
        selected_type = self.room_type_combo.currentData()
        chosen_ids = {r["id"] for r in self._selected_rooms}

        self.available_list.clear()
        for r in self._all_rooms:
            if selected_type and r["type_id"] != selected_type:
                continue
            if r["id"] in chosen_ids:
                continue
            status = r["housekeeping"] if r["housekeeping"] == STATUS_DIRTY else r["occupancy_status"]
            display_price = self._get_display_price(r)
            label = f"Phòng {r['room_number']} – {r['type_name']} ({int(display_price):,}đ/đêm) [{status}]"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.available_list.addItem(item)

    def _refresh_chosen_list(self):
        self.chosen_list.clear()
        for r in self._selected_rooms:
            display_price = self._get_display_price(r)
            label = f"Phòng {r['room_number']} – {r['type_name']} ({int(display_price):,}đ/đêm)"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, r)
            self.chosen_list.addItem(item)
        self._update_price_summary()

    def _add_selected(self):
        for item in self.available_list.selectedItems():
            r = item.data(Qt.ItemDataRole.UserRole)
            if r not in self._selected_rooms:
                self._selected_rooms.append(r)
        self._refresh_available_list()
        self._refresh_chosen_list()

    def _remove_selected(self):
        for item in self.chosen_list.selectedItems():
            r = item.data(Qt.ItemDataRole.UserRole)
            if r in self._selected_rooms:
                self._selected_rooms.remove(r)
        self._refresh_available_list()
        self._refresh_chosen_list()

    def _get_display_price(self, room):
        """Trả về giá hiển thị: snapshot nếu có, nếu không thì giá hiện tại."""
        if hasattr(self, '_snapshot_map') and room["id"] in self._snapshot_map:
            return self._snapshot_map[room["id"]]
        if hasattr(self, '_type_snapshot_map') and room["type_id"] in self._type_snapshot_map:
            return self._type_snapshot_map[room["type_id"]]
        return room["price_per_night"]

    def _update_price_summary(self):
        if not self._selected_rooms:
            self.price_summary.setText("")
            return
        ci = self.checkin_dt.dateTime().toPyDateTime()
        co = self.checkout_dt.dateTime().toPyDateTime()
        nights = max((co.date() - ci.date()).days, 1)
        total = sum(self._get_display_price(r) for r in self._selected_rooms)
        grand = total * nights
        rooms_count = len(self._selected_rooms)
        self.price_summary.setText(
            f"🏨 {rooms_count} phòng × {nights} đêm | "
            f"Tổng/đêm: {int(total):,}đ | "
            f"<b>Tổng cộng: {int(grand):,}đ</b>"
        )

    # ── Customer search ────────────────────────────────────────────────────────

    def _search_customer(self):
        id_card = self.id_card_input.text().strip()
        if not id_card:
            return
        cust = customer_model.find_by_id_card(id_card)
        if cust:
            self._customer_id = cust["id"]
            self.cust_name.setText(cust["full_name"])
            self.cust_phone.setText(cust["phone"] or "")
            self.cust_email.setText(cust["email"] or "")
            self.cust_address.setText(cust["address"] or "")
            QMessageBox.information(self, "Tìm thấy", f"Đã tìm thấy khách: {cust['full_name']}")
        else:
            self._customer_id = None
            QMessageBox.information(self, "Không tìm thấy",
                "Không tìm thấy khách. Hãy nhập thông tin để tạo khách mới.")

    # ── Fill (edit mode) ───────────────────────────────────────────────────────

    def _fill(self, bk: dict):
        self.id_card_input.setText(bk.get("id_card") or "")
        self.cust_name.setText(bk["customer_name"])
        self.cust_phone.setText(bk.get("customer_phone") or "")
        self._customer_id = bk["customer_id"]

        ci = datetime.datetime.fromisoformat(bk["check_in_date"])
        co = datetime.datetime.fromisoformat(bk["check_out_date"])
        self.checkin_dt.setDateTime(QDateTime(ci.year, ci.month, ci.day, ci.hour, ci.minute))
        self.checkout_dt.setDateTime(QDateTime(co.year, co.month, co.day, co.hour, co.minute))
        self.deposit.setValue(bk["deposit_amount"] or 0)
        self.note.setPlainText(bk.get("note") or "")

        if hasattr(self, "status_combo"):
            for i, (k, _) in enumerate(STATUS_VN.items()):
                if k == bk["status"]:
                    self.status_combo.setCurrentIndex(i)

        # Lấy danh sách phòng từ BookingRooms (nguồn chính thức duy nhất)
        from models import booking_model as bm
        booked_rooms = bm.get_booking_rooms(bk["id"])
        booked_ids = {br["room_id"] for br in booked_rooms}
        self._selected_rooms = [r for r in self._all_rooms if r["id"] in booked_ids]

        # Lưu snapshot prices để hiển thị đúng giá khi đổi phòng cùng loại
        self._snapshot_map = {}
        self._type_snapshot_map = {}
        for br in booked_rooms:
            self._snapshot_map[br["room_id"]] = float(br["price_snapshot"] or 0)
            if br["type_id"] not in self._type_snapshot_map:
                self._type_snapshot_map[br["type_id"]] = float(br["price_snapshot"] or 0)

        self._refresh_available_list()
        self._refresh_chosen_list()

    # ── Validation & Save ──────────────────────────────────────────────────────

    def _validate_inputs(self, name, id_card, phone):
        if not name:
            return "Vui lòng nhập tên khách hàng."
        if re.search(r'[0-9!@#\$%\^\&\*()_\+=\[\]{};:\"\\\|,.<>\/?`~\-]', name):
            return "Họ tên không được chứa chữ số hoặc kí tự đặc biệt."
        if id_card and not re.match(r'^\d{12}$', id_card):
            return "CCCD phải gồm 12 chữ số."
        if phone and not re.match(r'^0\d{9}$', phone):
            return "Số điện thoại phải gồm 10 chữ số, bắt đầu bằng số 0."
        return None

    def _save(self):
        name    = self.cust_name.text().strip()
        id_card = self.id_card_input.text().strip()
        phone   = self.cust_phone.text().strip()
        email   = self.cust_email.text().strip()
        address = self.cust_address.text().strip()

        err = self._validate_inputs(name, id_card, phone)
        if err:
            QMessageBox.warning(self, "Lỗi", err)
            return

        if not self._selected_rooms:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất một phòng.")
            return

        ci      = self.checkin_dt.dateTime().toPyDateTime()
        co      = self.checkout_dt.dateTime().toPyDateTime()
        ci_str  = ci.isoformat()
        co_str  = co.isoformat()
        deposit = self.deposit.value()
        note    = self.note.toPlainText()

        if not self.booking and ci.date() < datetime.date.today():
            QMessageBox.warning(self, "Lỗi", "Ngày check-in không hợp lệ.")
            return

        if not self._customer_id:
            id_card_val = id_card or None
            if id_card_val:
                existing = customer_model.find_by_id_card(id_card_val)
                if existing:
                    self._customer_id = existing["id"]
                    customer_model.update_customer(
                        self._customer_id, name, id_card_val,
                        phone or None, email or None, address or None,
                    )
            if not self._customer_id:
                try:
                    self._customer_id = customer_model.create_customer(
                        name, id_card_val, phone or None, email or None, address or None,
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Tạo khách thất bại: {e}")
                    return

        room_ids = [r["id"] for r in self._selected_rooms]

        if self.booking:
            status = (self.status_combo.currentData()
                      if hasattr(self, "status_combo") else self.booking["status"])
            # Truyền toàn bộ room_ids — update_booking_with_validation sẽ đồng bộ BookingRooms
            result = update_booking_with_validation(
                self.booking["id"], room_ids, ci_str, co_str, deposit, note, status
            )
        else:
            result = create_booking_with_validation(
                self._customer_id, room_ids, self.user["id"],
                ci_str, co_str, deposit, note,
            )

        if result["ok"]:
            room_numbers = ", ".join(f"#{r['room_number']}" for r in self._selected_rooms)
            QMessageBox.information(self, "Thành công",
                f"Booking đã được lưu!\nPhòng: {room_numbers}")
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", result["error"])
