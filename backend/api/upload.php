<?php
/**
 * API endpoint to receive shipments JSON and insert into MySQL.
 *
 * Expects POST requests with JSON array of shipments:
 * [
 *   { "shipment_ref": "...", "origin": "...", "destination": "...", ... },
 *   ...
 * ]
 *
 * Responds with JSON status:
 * { "success": true, "inserted": N }
 */


header("Content-Type: application/json");

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    echo json_encode(["success" => false, "error" => "Invalid JSON"]);
    exit;
}

$mysqli = new mysqli("localhost", "DB_USER", "DB_PASSWORD", "DB_NAME");
if ($mysqli->connect_error) {
    echo json_encode(["success" => false, "error" => $mysqli->connect_error]);
    exit;
}

$inserted = 0;
$stmt = $mysqli->prepare("
    INSERT INTO shipments (shipment_ref, origin, destination, carrier, planned_departure,
                           planned_arrival, actual_arrival, status, source_file)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE
        origin=VALUES(origin),
        destination=VALUES(destination),
        carrier=VALUES(carrier),
        planned_departure=VALUES(planned_departure),
        planned_arrival=VALUES(planned_arrival),
        actual_arrival=VALUES(actual_arrival),
        status=VALUES(status),
        source_file=VALUES(source_file)
");

foreach ($input as $s) {
    $stmt->bind_param(
        "sssssssss",
        $s['shipment_ref'],
        $s['origin'],
        $s['destination'],
        $s['carrier'] ?? null,
        $s['planned_departure'] ?? null,
        $s['planned_arrival'] ?? null,
        $s['actual_arrival'] ?? null,
        $s['status'] ?? null,
        $s['source_file'] ?? null
    );
    if ($stmt->execute()) $inserted++;
}

echo json_encode(["success" => true, "inserted" => $inserted]);
