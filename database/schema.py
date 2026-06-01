from utils.config import BOOKING_RESERVED, PAYMENT_STATUS_UNPAID, STATUS_AVAILABLE, STATUS_CLEAN


def create_tables(conn) -> None:
    c = conn.cursor()
    c.executescript(f"""
    CREATE TABLE IF NOT EXISTS Hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        email TEXT UNIQUE,
        role_id INTEGER NOT NULL REFERENCES Roles(id),
        hotel_id INTEGER NOT NULL REFERENCES Hotels(id),
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS RoomTypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT NOT NULL UNIQUE,
        price_per_night REAL NOT NULL,
        max_guest INTEGER DEFAULT 2,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL REFERENCES Hotels(id),
        type_id INTEGER NOT NULL REFERENCES RoomTypes(id),
        room_number TEXT NOT NULL,
        floor INTEGER NOT NULL DEFAULT 1,
        occupancy_status TEXT NOT NULL DEFAULT '{STATUS_AVAILABLE}',
        housekeeping TEXT NOT NULL DEFAULT '{STATUS_CLEAN}',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(hotel_id, room_number)
    );

    CREATE TABLE IF NOT EXISTS Customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        id_card TEXT UNIQUE,
        phone TEXT,
        email TEXT,
        address TEXT,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES Customers(id),
        user_id INTEGER NOT NULL REFERENCES Users(id),
        check_in_date DATETIME NOT NULL,
        check_out_date DATETIME NOT NULL,
        deposit_amount REAL DEFAULT 0,
        status TEXT NOT NULL DEFAULT '{BOOKING_RESERVED}',
        note TEXT,
        check_out_by INTEGER REFERENCES Users(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS BookingRooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL REFERENCES Bookings(id) ON DELETE CASCADE,
        room_id    INTEGER NOT NULL REFERENCES Rooms(id),
        price_snapshot REAL NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(booking_id, room_id)
    );

    CREATE TABLE IF NOT EXISTS RoomChargeHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL REFERENCES Bookings(id),
        room_id INTEGER NOT NULL REFERENCES Rooms(id),
        room_number TEXT NOT NULL,
        room_type_id INTEGER NOT NULL,
        room_type_name TEXT NOT NULL,
        price_per_night REAL NOT NULL,
        start_date DATETIME NOT NULL,
        end_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stocking INTEGER DEFAULT NULL,
        service_name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL,
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS BookingServices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL REFERENCES Bookings(id),
        service_id INTEGER NOT NULL REFERENCES Services(id),
        quantity INTEGER DEFAULT 1,
        unit_price REAL NOT NULL,
        order_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS MealTypes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS MenuItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_type_id INTEGER NOT NULL REFERENCES MealTypes(id),
        item_name TEXT NOT NULL,
        price REAL NOT NULL,
        is_active INTEGER DEFAULT 1,
        UNIQUE(meal_type_id, item_name)
    );

    CREATE TABLE IF NOT EXISTS BookingMeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL REFERENCES Bookings(id),
        menu_item_id INTEGER NOT NULL REFERENCES MenuItems(id),
        quantity INTEGER DEFAULT 1,
        unit_price REAL NOT NULL,
        order_time DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL UNIQUE REFERENCES Bookings(id),
        total_room_amount REAL DEFAULT 0,
        total_service_amount REAL DEFAULT 0,
        total_meal_amount REAL DEFAULT 0,
        tax REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        final_amount REAL DEFAULT 0,
        payment_method TEXT,
        payment_status TEXT DEFAULT '{PAYMENT_STATUS_UNPAID}',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
