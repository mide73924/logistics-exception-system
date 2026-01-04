"""
Excel ingestion module for shipment data.

Responsibilities:
- Read shipment data from Excel files
- Normalize column names to a consistent schema
- Perform basic structural validation
- Output cleaned data as JSON-ready structures

This module focuses on project-specific logic and assumptions,
not on validating pandas or Excel file internals.
"""

import pandas as pd
import json
import sys
from pathlib import Path


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def ingest_excel(excel_path: str) -> list[dict]:
    if not Path(excel_path).exists():
        raise FileNotFoundError(f"File not found: {excel_path}")

    df = pd.read_excel(excel_path)

    if df.empty:
        raise ValueError("Excel file contains no data")

    df = normalize_columns(df)

    return df.to_dict(orient="records")


def main():
    if len(sys.argv) != 2:
        print("Usage: python ingest_excel.py <excel_file>")
        sys.exit(1)

    excel_path = sys.argv[1]

    try:
        records = ingest_excel(excel_path)
        print(json.dumps(records, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
