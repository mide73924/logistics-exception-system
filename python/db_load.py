"""
Database loading utilities for the Logistics Exception System.

This module is responsible for inserting cleaned shipment records and
validation exceptions into a MySQL database. It reads database credentials
from environment variables and supports idempotent shipment inserts
via ON DUPLICATE KEY UPDATE.

Scope:
- Insert normalized shipment data into the `shipments` table
- Insert validation exceptions linked to shipments
- Assumes database schema already exists

Not responsible for:
- Excel ingestion
- Data validation logic
- API exposure
"""


import json
import os
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv


load_dotenv() 

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
TEST_DB_NAME = os.getenv("TEST_DB_NAME")

# MySQL connection
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cursor = conn.cursor()

# Load shipments from static files  
shipments = json.loads(Path("data/sample_shipments.json").read_text())
exceptions = json.loads(Path("data/exceptions.json").read_text())  

def load_shipments(cursor, shipments):
    """Insert shipments into the database."""
    for s in shipments:
        cursor.execute("""
            INSERT INTO shipments (shipment_ref, origin, destination, carrier, planned_departure,
                                   planned_arrival, actual_arrival, status, source_file)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                origin=VALUES(origin),
                destination=VALUES(destination),
                carrier=VALUES(carrier),
                planned_departure=VALUES(planned_departure),
                planned_arrival=VALUES(planned_arrival),
                actual_arrival=VALUES(actual_arrival),
                status=VALUES(status),
                source_file=VALUES(source_file)
        """, (
            s["shipment_ref"], s["origin"], s["destination"], s.get("carrier"),
            s.get("planned_departure"), s.get("planned_arrival"), s.get("actual_arrival"),
            s.get("status"), s.get("source_file")
        ))


def load_exceptions(cursor, exceptions, shipment_map):
    """Insert exceptions into the database."""
    for e in exceptions:
        shipment_id = shipment_map.get(e.get("shipment_ref"))
        if shipment_id:
            rule_code = e.get("rule_code")
            severity = e.get("severity")
            rule_description = e.get("rule_description", "")

            if not rule_code or not severity:
                raise ValueError(f"Missing rule_code or severity in exception: {e}")

            cursor.execute("""
                INSERT INTO exceptions (shipment_id, rule_code, rule_description, severity, exception_value)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                shipment_id, rule_code, rule_description, severity, e.get("exception_value")
            ))

conn.commit()
cursor.close()
conn.close()