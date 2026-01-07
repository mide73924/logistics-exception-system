-- schema.sql
-- Initializes the database schema for the Logistics Shipment Exception Management System
--
-- Creates:
--   - shipments: core shipment records ingested from Excel
--   - exceptions: rule-based operational exceptions linked to shipments
--
-- Usage:
--   mysql -u <user> -p <database> < schema.sql
--
-- Notes:
--   - Assumes MySQL / MariaDB
--   - Safe to re-run (uses IF NOT EXISTS where applicable)

CREATE TABLE shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,

    shipment_ref VARCHAR(50) NOT NULL,
    origin VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    carrier VARCHAR(50),

    planned_departure DATE,
    planned_arrival DATE,
    actual_arrival DATE,

    status VARCHAR(30),
    source_file VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_shipment_ref (shipment_ref)
);

CREATE TABLE exceptions (
    id INT AUTO_INCREMENT PRIMARY KEY,

    shipment_id INT NOT NULL,
    rule_code VARCHAR(50) NOT NULL,
    rule_description VARCHAR(255),

    severity ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
    exception_value VARCHAR(100),

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (shipment_id)
        REFERENCES shipments(id)
        ON DELETE CASCADE
);