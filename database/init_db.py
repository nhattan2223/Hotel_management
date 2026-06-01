def init_db():
    import os
    from utils.config import DB_PATH

    if os.path.exists(DB_PATH):
        print("Database already exists, skipping initialization.")
        return

    from database.connection import get_connection
    from database.schema import create_tables
    from database.seed_data import seed_all

    conn = get_connection()
    try:
        create_tables(conn)
        seed_all(conn)
    finally:
        conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
