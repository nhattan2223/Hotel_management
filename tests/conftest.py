import os
import sys
import tempfile
import sqlite3

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.schema import create_tables
from database.seed_data import seed_all


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary database for testing, yield the connection, then clean up."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    seed_all(conn)
    yield conn, db_path
    conn.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def test_db_path(test_db):
    """Return just the test database path."""
    _, db_path = test_db
    return db_path
