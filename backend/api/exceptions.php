<?php
/**
 * API endpoint to fetch shipment exceptions.
 *
 * Responds with JSON array:
 * [
 *   { "shipment_ref": "...", "rule_code": "...", "severity": "...", ... },
 *   ...
 * ]
 */


header("Content-Type: application/json");

$mysqli = new mysqli("localhost", "DB_USER", "DB_PASSWORD", "DB_NAME");
if ($mysqli->connect_error) {
    echo json_encode(["success" => false, "error" => $mysqli->connect_error]);
    exit;
}

$result = $mysqli->query("
    SELECT s.shipment_ref, e.rule_code, e.rule_description, e.severity, e.exception_value
    FROM exceptions e
    JOIN shipments s ON e.shipment_id = s.id
");

$exceptions = [];
while ($row = $result->fetch_assoc()) {
    $exceptions[] = $row;
}

echo json_encode($exceptions);

