"""
Unit tests for shipment validation rules.

These tests verify that the validation engine correctly identifies exceptions
based on the JSON-defined business rules, including severity classification.
Third-party behavior (e.g., Python datetime or JSON parsing) is not tested.
"""

import pytest
from python.validate_shipments import validate_shipments, load_rules


def test_missing_carrier_rule():
    shipment = {"shipment_ref": "A1", "carrier": ""}
    rules = load_rules("config/validation_rules.json")
    exceptions = validate_shipments([shipment], rules)
    assert any(ex["rule_code"] == "MISSING_CARRIER" for ex in exceptions)
