"""
Unit tests for Python MySQL integration (db_load.py).

These tests verify that shipments and exceptions can be inserted correctly
into a test database and that simple queries return expected results.
Third-party MySQL connector behavior is not tested.
"""

import pytest
import os
import mysql.connector
from dotenv import load_dotenv
from python.db_load import load_shipments, load_exceptions  # functions from db_load.py

# Load .env variables
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TEST_DB = os.getenv("TEST_DB_NAME", "test_logistics_db")


@pytest.fixture(scope="module")
def db_connection():
    """Fixture to create a temporary test database with tables."""
    # Connect to MySQL server (no database yet)
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    # Create test database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
    cursor.execute(f"USE {TEST_DB}")

    # Create shipments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        shipment_ref VARCHAR(50) NOT NULL,
        origin VARCHAR(50),
        destination VARCHAR(50),
        carrier VARCHAR(50),
        planned_departure DATE,
        planned_arrival DATE,
        actual_arrival DATE,
        status VARCHAR(30),
        source_file VARCHAR(100),
        UNIQUE KEY uniq_shipment_ref (shipment_ref)
    )
    """)

    # Create exceptions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exceptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        shipment_id INT NOT NULL,
        rule_code VARCHAR(50) NOT NULL,
        rule_description VARCHAR(255),
        severity ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
        exception_value VARCHAR(100),
        FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
    )
    """)

    # Provide connection and cursor to tests
    yield conn, cursor

    # Teardown: drop test database
    cursor.execute(f"DROP DATABASE {TEST_DB}")
    cursor.close()
    conn.close()


def test_shipments_insert(db_connection):
    """Test inserting a shipment into the database."""
    conn, cursor = db_connection

    shipment = {
        "shipment_ref": "TEST1",
        "origin": "A",
        "destination": "B",
        "carrier": "DHL",
        "planned_departure": "2026-01-01",
        "planned_arrival": "2026-01-05",
        "actual_arrival": "2026-01-06",
        "status": "DELIVERED",
        "source_file": "sample.xlsx"
    }

    # Insert using the function from db_load.py
    load_shipments(cursor, [shipment])
    conn.commit()

    # Verify insertion
    cursor.execute("SELECT shipment_ref, origin FROM shipments WHERE shipment_ref='TEST1'")
    row = cursor.fetchone()
    assert row == ("TEST1", "Tokyo")


def test_exceptions_insert(db_connection):
    """Test inserting an exception linked to a shipment."""
    conn, cursor = db_connection

    # Build shipment map (shipment_ref → id)
    cursor.execute("SELECT id, shipment_ref FROM shipments")
    shipment_map = {ref: id for (id, ref) in cursor.fetchall()}

    exception = {
        "shipment_ref": "TEST1",
        "rule_code": "ARRIVAL_LATE",
        "rule_description": "Late arrival",
        "severity": "HIGH",
        "exception_value": "2026-01-06"
    }

    # Insert using the function from db_load.py
    load_exceptions(cursor, [exception], shipment_map)
    conn.commit()

    # Verify insertion
    cursor.execute("SELECT rule_code, severity FROM exceptions WHERE shipment_id=%s", (shipment_map["TEST1"],))
    row = cursor.fetchone()
    assert row == ("ARRIVAL_LATE", "HIGH")