# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas>=2.0,<3",
#   "openpyxl>=3",
#   "xlrd >= 2.0.1",
# ]
# ///

"""
boc2ynab.py – Convert a BOC bank-statement worksheet to a YNAB-compatible CSV.

The xlsx file can be downloaded from https://its.bocmacau.com/prelogin.do?_locale=zh_TW&BankId=9999&LoginType=R

Usage
-----
    python boc2ynab.py statement.xlsx output.csv
"""

from __future__ import annotations

import sys
from datetime import datetime
import pandas as pd


def _find_header_row(raw: pd.DataFrame) -> int:
    """Return the index of the row whose first cell is '交易日期'."""
    for i, val in enumerate(raw.iloc[:, 0]):
        if str(val).strip() == "交易日期":
            return i
    raise RuntimeError("Header row with '交易日期' not found.")


def _normalise_date(val) -> str:
    """Convert date-like values to MM/DD/YYYY; otherwise return blank."""
    if pd.isna(val):
        return ""
    if isinstance(val, datetime):
        return val.strftime("%m/%d/%Y")
    try:
        return pd.to_datetime(val).strftime("%m/%d/%Y")
    except Exception:  # noqa: BLE001
        return str(val)


def convert(infile: str, outfile: str) -> None:
    # Pass 1 – locate the header row.
    raw = pd.read_excel(infile, header=None, dtype=str)
    header_row = _find_header_row(raw)

    # Pass 2 – re-read with the proper header.
    df = pd.read_excel(infile, header=header_row, dtype=str)

    # Chinese → YNAB column names.
    col_map = {
        "交易日期": "Date",
        "對方帳戶名稱": "Payee",
        "備註": "Memo",          # preferred memo
        "業務類型": "Memo_alt",  # fallback memo
        "支出金額": "Outflow",
        "存入金額": "Inflow",
    }
    df = df.rename(columns=col_map)

    # Build the final frame.
    df = df.reindex(columns=["Date", "Payee", "Memo", "Memo_alt", "Outflow", "Inflow"])
    df["Memo"] = df["Memo"].fillna(df["Memo_alt"]).fillna("")

    df["Date"] = df["Date"].apply(_normalise_date)
    for col in ("Outflow", "Inflow"):
        df[col] = df[col].str.replace(",", "", regex=False).fillna("")

    df[["Date", "Payee", "Memo", "Outflow", "Inflow"]].to_csv(outfile, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: xls2ynab.py <input.xlsx> <output.csv>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
