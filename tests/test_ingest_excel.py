"""
Unit tests for Excel ingestion and column normalization logic.

These tests validate project-specific data transformations and error handling,
not third-party library behavior (e.g., pandas internals).
"""

import pandas as pd
import pytest

from python.ingest_excel import ingest_excel, normalize_columns


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        ingest_excel("does_not_exist.xlsx")


def test_normalize_columns():
    df = pd.DataFrame(columns=[" Shipment Ref ", "Planned Arrival"])
    result = normalize_columns(df)

    assert list(result.columns) == ["shipment_ref", "planned_arrival"]
