import sqlite3
import os

from utils.config import DB_PATH


def get_connection():
    """Dùng riêng cho init_db vì cần tạo thư mục trước."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

