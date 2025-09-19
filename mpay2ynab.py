# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas>=2.0,<3",
#   "openpyxl>=3",
#   "xlrd>=2.0.1",
# ]
# ///
"""
mpay2ynab.py – Convert new‑statement.xlsx → YNAB‑friendly CSV

The xlsx file can be downloaded in https://pay.macaupass.com/payment/#/tradeManagement

Usage
-----
python mpay2ynab.py statement.xlsx output.csv
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

INFLOW_TYPES  = {"轉入", "利是轉入", "加值", "退款"}
OUTFLOW_TYPES = {"交易", "轉出", "利是轉出"}
ALL_TYPES     = INFLOW_TYPES | OUTFLOW_TYPES

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _normalise_date(value) -> str:
    """Return *value* formatted as ``MM/DD/YYYY`` or the original string.

    Accepts ``pandas.NA``, :class:`datetime.datetime` or arbitrary strings.
    Anything that cannot be parsed as a date is returned unchanged.
    """
    if pd.isna(value):
        return ""

    if isinstance(value, datetime):
        return value.strftime("%m/%d/%Y")

    try:
        return pd.to_datetime(value).strftime("%m/%d/%Y")
    except (ValueError, TypeError):
        return str(value)

# ──────────────────────────────────────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────────────────────────────────────

def convert(infile: str | Path, outfile: str | Path) -> None:
    """Read *infile* (xlsx) and write *outfile* (csv) in YNAB format."""
    df = (
        pd.read_excel(infile, header=0, dtype=str)
        .rename(
            columns={
                "交易時間": "Date",
                "項目名稱": "Payee",
                "交易編號": "Memo",
                "分類"  : "Category",
                "對方賬號": "Account",
                "金額"  : "Amount",
            }
        )
    )

    # ── Filter & validate ────────────────────────────────────────────────────
    df = df[df["餘額/快捷支付"].fillna("") != "快捷支付"]

    unknown = set(df["Category"].dropna().unique()) - ALL_TYPES
    if unknown:
        raise ValueError(f"Unexpected 分類 values: {', '.join(sorted(unknown))}")

    # ── Transform columns ───────────────────────────────────────────────────
    df["Date"]   = df["Date"].apply(_normalise_date)
    df["Amount"] = df["Amount"].str.replace(",", "", regex=False).fillna("")

    df["Inflow"]  = df.apply(lambda r: r["Amount"] if r["Category"] in INFLOW_TYPES  else "", axis=1)
    df["Outflow"] = df.apply(lambda r: r["Amount"] if r["Category"] in OUTFLOW_TYPES else "", axis=1)

    df["Memo"] = df.apply(
        lambda r: f"({r['Account']}) {r['Memo']}" if pd.notna(r["Account"]) and str(r["Account"]).strip() else r["Memo"],
        axis=1,
    )

    # ── Export ──────────────────────────────────────────────────────────────
    df[["Date", "Payee", "Memo", "Outflow", "Inflow"]].to_csv(outfile, index=False)

# ──────────────────────────────────────────────────────────────────────────────
# CLI wrapper
# ──────────────────────────────────────────────────────────────────────────────

def _usage() -> None:
    print("Usage: mpay2ynab.py <input.xlsx> <output.csv>", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 3:
        _usage()

    convert(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
