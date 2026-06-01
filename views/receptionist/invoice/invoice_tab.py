import os
import datetime

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from utils.config import BOOKING_STATUS_VN
from models import booking_model, hotel_model
from services.booking_service import compute_invoice
from services.invoice_service import generate_invoice_pdf
from views.receptionist.invoice.invoice_presenter import clear_preview, populate_preview
from views.receptionist.invoice.invoice_ui import (
    INVOICE_EXPORT_STATUS,
    PAYMENT_CODES,
    setup_invoice_ui,
)


class InvoiceTab(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self.user = user
        self.hotel_id = user["hotel_id"]
        self._current_data = None
        setup_invoice_ui(self)
        self.refresh()

    # ──────────────────────────────────────────────────────────
    def refresh(self):
        """Reload booking list without spurious signal calls."""
        status = self.status_combo.currentData()
        self.booking_combo.blockSignals(True)
        self.booking_combo.clear()

        bookings = booking_model.get_bookings(self.hotel_id, status=status)
        self._bookings = bookings
        for b in bookings:
            ci = datetime.datetime.fromisoformat(b["check_in_date"]).strftime("%d/%m/%Y")
            status = BOOKING_STATUS_VN.get(b["status"], b["status"])
            self.booking_combo.addItem(
                f"#{b['id']}  Phòng {b['room_number']}  –  {b['customer_name']}"
                f"  [{status}]  {ci}",
                b["id"]
            )
        self.booking_combo.blockSignals(False)

        self.empty_lbl.setVisible(len(bookings) == 0)
        self._load_invoice()   # single controlled call

    # ──────────────────────────────────────────────────────────
    def _load_invoice(self):
        """Compute and display invoice for selected booking."""
        bid = self.booking_combo.currentData()
        if bid is None:
            clear_preview(self)
            return

        data = compute_invoice(bid)
        if not data:
            clear_preview(self)
            return

        populate_preview(self, data, INVOICE_EXPORT_STATUS)

    def _export_pdf(self):
        if self._current_data is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một booking để xuất hóa đơn.")
            return

        bid = self.booking_combo.currentData()
        if bid is None:
            return

        bk = self._current_data["booking"]
        if bk.get("status") != INVOICE_EXPORT_STATUS:
            QMessageBox.warning(
                self, "Lỗi",
                "Chỉ được xuất hóa đơn sau khi phòng đã check-out."
            )
            return

        payment_method = PAYMENT_CODES[self.payment_combo.currentIndex()]
        hotel = hotel_model.get_hotel(self.hotel_id) or {}
        default_name = (
            f"hoadon_{bk['room_number']}_"
            f"{bk['customer_name'].replace(' ', '_')}_{bid}.pdf"
        )

        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu hóa đơn PDF",
            os.path.expanduser(f"~/{default_name}"),
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        try:
            ok = generate_invoice_pdf(bid, path, hotel, payment_method)
            if ok:
                QMessageBox.information(
                    self, "✅ Xuất PDF thành công",
                    f"Hóa đơn đã được lưu tại:\n{path}"
                )
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể tạo file PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi PDF", str(e))


