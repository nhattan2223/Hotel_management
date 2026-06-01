"""Test that all modules can be imported without errors."""


def test_config_import():
    from utils import config
    assert config.APP_NAME == "Hotel Management System"
    assert config.VAT_RATE == 0.08


def test_security_import():
    from utils.security import hash_password, verify_password
    assert callable(hash_password)
    assert callable(verify_password)


def test_models_import():
    from models import user_model, hotel_model, room_model
    from models import customer_model, booking_model, service_model
    from models import menu_model, invoice_model
    assert callable(hotel_model.get_all_hotels)
    assert callable(room_model.get_rooms)
    assert callable(customer_model.find_by_id_card)


def test_database_import():
    from database import schema, seed_data, connection
    from database.connection import get_connection
    assert callable(schema.create_tables)
    assert callable(seed_data.seed_all)


def test_services_import():
    from services import booking_service, invoice_service


def test_views_receptionist_import():
    from views.receptionist.rooms.rooms_tab import ReceptionRoomsTab
    from views.receptionist.booking.booking_tab import BookingTab
    from views.receptionist.gantt.gantt_tab import GanttTab
    from views.receptionist.service.service_tab import ServiceTab
    from views.receptionist.customer.customer_tab import CustomerTab
    from views.receptionist.invoice.invoice_tab import InvoiceTab
    from views.receptionist.receptionist_window import ReceptionistWindow


def test_views_admin_import():
    from views.admin.staff.staff_tab import StaffTab
    from views.admin.statistics.statistics_tab import StatisticsTab
    from views.admin.branch.branch_tab import BranchTab
    from views.admin.rooms.rooms_tab import AdminRoomsTab
    from views.admin.admin_window import AdminWindow


def test_views_chef_import():
    from views.chef.menu.menu_tab import MenuManagementTab
    from views.chef.order.order_tab import OrderTab
    from views.chef.chef_window import ChefWindow


def test_views_housekeeping_import():
    from views.housekeeping.housekeeping_tab import HousekeepingRoomsTab
    from views.housekeeping.housekeeping_window import HousekeepingWindow


def test_views_widgets_import():
    from views.widgets.sidebar import SidebarWidget
    from views.widgets.room_card import RoomCard


def test_main_import():
    import main


def test_dialogs_import():
    from views.receptionist.booking.booking_dialog import BookingDialog
    from views.receptionist.booking.booking_dialog_ui import setup_booking_dialog_ui
    from views.receptionist.booking.room_switch_dialog import RoomSwitchDialog
    from views.receptionist.service.service_dialogs import AddServiceOrderDialog, ServiceDialog
    from views.receptionist.customer.customer_dialog import CustomerDialog
    from views.receptionist.rooms.room_action_dialog import RoomActionDialog
    from views.admin.rooms.room_dialogs import RoomDialog, RoomTypeDialog
    from views.admin.staff.user_dialog import UserDialog
    from views.admin.branch.hotel_dialog import HotelDialog
    from views.chef.menu.menu_item_dialog import MenuItemDialog


def test_helpers_import():
    from views.receptionist.invoice.invoice_helpers import _bold, _make_table, _fill_row
    from views.receptionist.invoice.invoice_presenter import clear_preview, populate_preview
    from views.receptionist.invoice.invoice_ui import setup_invoice_ui
    from views.receptionist.service.service_helpers import make_table, cell
    from views.admin.rooms.rooms_ui import setup_rooms_ui
    from views.admin.rooms.rooms_presenter import populate_rooms_table, populate_room_types_table
    from views.admin.statistics.statistics_charts import draw_revenue, draw_occupancy, draw_top
    from views.chef.order.order_panels import build_menu_panel, build_orders_panel
