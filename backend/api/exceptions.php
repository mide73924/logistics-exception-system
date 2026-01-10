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

require_once __DIR__ . '/../../vendor/autoload.php'; // if using Composer

use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__ . '/../../');
$dotenv->load();

$mysqli = new mysqli(
    $_ENV['DB_HOST'],
    $_ENV['DB_USER'],
    $_ENV['DB_PASSWORD'],
    $_ENV['DB_NAME']
);

if ($mysqli->connect_error) {
    echo json_encode(["success" => false, "error" => $mysqli->connect_error]);
    exit;
}

header("Content-Type: application/json");

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

