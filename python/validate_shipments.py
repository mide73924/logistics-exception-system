"""
Shipment validation engine.

Responsibilities:
- Load validation rules from JSON
- Apply rules to shipment records
- Classify exceptions by severity
- Return a list of JSON-ready exception records

This module focuses on project-specific business logic.
Third-party library internals (e.g., datetime or JSON parsing) are not tested here.
"""


import json
from datetime import datetime
from pathlib import Path


def load_rules(json_path: str):
    with open(json_path, "r") as f:
        return json.load(f)


def apply_rule(shipment: dict, rule: dict):
    field = rule["field"]
    comparison = rule["comparison"]

    # Empty field check
    if comparison == "empty" and not shipment.get(field):
        return {
            "rule_code": rule["rule_code"],
            "rule_description": rule["description"],
            "severity": rule["severity"],
            "exception_value": shipment.get(field),
            "shipment_ref": shipment.get("shipment_ref")
        }

    # Date comparison
    if comparison == "after":
        ref_field = rule["reference_field"]
        if shipment.get(field) and shipment.get(ref_field):
            actual = datetime.strptime(str(shipment[field]), "%Y-%m-%d")
            planned = datetime.strptime(str(shipment[ref_field]), "%Y-%m-%d")
            if actual > planned:
                return {
                    "rule_code": rule["rule_code"],
                    "rule_description": rule["description"],
                    "severity": rule["severity"],
                    "exception_value": shipment[field],
                    "shipment_ref": shipment.get("shipment_ref")
                }

    return None


def validate_shipments(shipments: list[dict], rules: list[dict]):
    exceptions = []
    for shipment in shipments:
        for rule in rules:
            ex = apply_rule(shipment, rule)
            if ex:
                exceptions.append(ex)
    return exceptions


def main():
    shipments_path = "data/sample_shipments.json"  # JSON output from Day 3
    rules_path = "config/validation_rules.json"

    # Load
    shipments = json.loads(Path(shipments_path).read_text())
    rules = load_rules(rules_path)

    # Validate
    exceptions = validate_shipments(shipments, rules)

    # Output
    print(json.dumps(exceptions, indent=2))


if __name__ == "__main__":
    main()
