from utils.security import hash_password
from utils.config import ROLE_ADMIN, ROLE_RECEPTIONIST, ROLE_HOUSEKEEPING, ROLE_CHEF


def seed_all(conn) -> None:
    c = conn.cursor()

    # Seed roles
    roles = [(ROLE_ADMIN,), (ROLE_RECEPTIONIST,), (ROLE_HOUSEKEEPING,), (ROLE_CHEF,)]
    c.executemany("INSERT OR IGNORE INTO Roles(role_name) VALUES (?)", roles)

    # Seed hotels
    hotels = [
        ("Grand Palace Hotel", "123 Nguyen Hue, Ho Chi Minh City", "028-1234567", "grandpalace@hotel.vn"),
        ("Ocean View Resort", "45 Tran Phu, Da Nang", "0236-7654321", "oceanview@hotel.vn"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO Hotels(name,address,phone,email) VALUES (?,?,?,?)", hotels
    )

    # Seed room types
    room_types = [
        ("Standard",    500000, 2, "Phòng tiêu chuẩn"),
        ("Deluxe",      800000, 2, "Phòng cao cấp"),
        ("Suite",      1500000, 4, "Phòng suite sang trọng"),
        ("Family",     1200000, 4, "Phòng gia đình"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO RoomTypes(type_name,price_per_night,max_guest,description) VALUES (?,?,?,?)",
        room_types
    )

    conn.commit()

    # Seed rooms for hotel 1 & 2
    type_rows = {r["type_name"]: r["id"] for r in c.execute("SELECT id,type_name FROM RoomTypes").fetchall()}
    rooms_h1 = [
        (1, type_rows["Standard"], "101", 1),
        (1, type_rows["Standard"], "102", 1),
        (1, type_rows["Standard"], "103", 1),
        (1, type_rows["Standard"], "104", 1),
        (1, type_rows["Deluxe"],   "105", 1),
        (1, type_rows["Deluxe"],   "201", 2),
        (1, type_rows["Deluxe"],   "202", 2),
        (1, type_rows["Deluxe"],   "203", 2),
        (1, type_rows["Family"],   "204", 2),
        (1, type_rows["Family"],   "205", 2),
        (1, type_rows["Family"],   "301", 3),
        (1, type_rows["Suite"],    "302", 3),
        (1, type_rows["Suite"],    "303", 3),
    ]
    rooms_h2 = [
        (2, type_rows["Standard"], "101", 1),
        (2, type_rows["Standard"], "102", 1),
        (2, type_rows["Standard"], "103", 1),
        (2, type_rows["Standard"], "104", 1),
        (2, type_rows["Deluxe"],   "105", 1),
        (2, type_rows["Deluxe"],   "201", 2),
        (2, type_rows["Deluxe"],   "202", 2),
        (2, type_rows["Deluxe"],   "203", 2),
        (2, type_rows["Family"],   "204", 2),
        (2, type_rows["Family"],   "205", 2),
        (2, type_rows["Family"],   "301", 3),
        (2, type_rows["Suite"],    "302", 3),
        (2, type_rows["Suite"],    "303", 3),
    ]
    for r in rooms_h1 + rooms_h2:
        c.execute(
            "INSERT OR IGNORE INTO Rooms(hotel_id,type_id,room_number,floor) VALUES (?,?,?,?)", r
        )

    pw = hash_password("123456")
    role_map = {r["role_name"]: r["id"] for r in c.execute("SELECT id,role_name FROM Roles").fetchall()}
    users = [
        ("admin",      pw, "Quản trị viên",       "0901000000", "admin@hotel.vn",      role_map[ROLE_ADMIN],       1),
        ("letan1",     pw, "Lễ Tân",       "0901000001", "letan1@hotel.vn",     role_map[ROLE_RECEPTIONIST],1),
        ("manh",     pw, "Lễ Tân",       "0901000011", "manh1@hotel.vn",     role_map[ROLE_RECEPTIONIST],1),
        ("buongphong1",pw, "Buồng Phòng",    "0901000002", "bp1@hotel.vn",        role_map[ROLE_HOUSEKEEPING],1),
        ("beptruong1", pw, "Bếp Trưởng",       "0901000003", "bep1@hotel.vn",       role_map[ROLE_CHEF],        1),
        ("letan2",     pw, "Lễ Tân 2",         "0901000004", "letan2@hotel.vn",     role_map[ROLE_RECEPTIONIST],2),
        ("buongphong2",pw, "Buồng Phòng 2",   "0901000005", "bp2@hotel.vn",        role_map[ROLE_HOUSEKEEPING],2),
        ("beptruong2", pw, "Bếp Trưởng 2",       "0901000006", "bep2@hotel.vn",       role_map[ROLE_CHEF],        2),
    ]
    for u in users:
        c.execute(
            "INSERT OR IGNORE INTO Users(username,password,full_name,phone,email,role_id,hotel_id) VALUES (?,?,?,?,?,?,?)",
            u
        )

    # Seed meal types
    meal_types = [("Sáng",), ("Trưa",), ("Tối",), ("Khuya",)]
    c.executemany("INSERT OR IGNORE INTO MealTypes(name) VALUES (?)", meal_types)
    conn.commit()

    mt = {r["name"]: r["id"] for r in c.execute("SELECT id,name FROM MealTypes").fetchall()}
    menu_items = [
        (mt["Sáng"], "Phở bò",           45000),
        (mt["Sáng"], "Bánh mì trứng",    25000),
        (mt["Sáng"], "Cơm tấm sườn",     55000),
        (mt["Trưa"], "Cơm phần",         65000),
        (mt["Trưa"], "Bún bò Huế",       60000),
        (mt["Tối"],  "Lẩu thái",        250000),
        (mt["Tối"],  "Steak bò Mỹ",     350000),
        (mt["Khuya"],"Cháo gà",          50000),
        (mt["Khuya"],"Mì tôm trứng",     35000),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO MenuItems(meal_type_id,item_name,price) VALUES (?,?,?)",
        menu_items
    )

    # Seed services
    services = [
        (None, "Giặt ủi",        50000),
        (None, "Đưa đón sân bay",250000),
        (None, "Thuê xe máy",    150000),
        (50,   "Nước suối",        5000),
        (20,   "Bia Tiger",       30000),
        (None, "Spa massage",    300000),
        (None, "Thuê phòng hội nghị", 500000),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO Services(stocking,service_name,price) VALUES (?,?,?)",
        services
    )

    conn.commit()

