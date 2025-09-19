# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas>=2.0,<3",
#   "openpyxl>=3",
#   "xlrd>=2.0.1",
# ]
# ///
"""
boccredit2ynab.py – Convert xlsx spreadsheet representing credit card usage data → YNAB-friendly CSV

This handles sheets with columns:
交易日期, 記賬日期, 記賬幣別, 卡號, 入賬款項, 新簽賬項, 交易描述, 交易幣種, 交易金額

Usage
-----
python boccredit2ynab.py input.xlsx output.csv
"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

def _normalise_date(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, datetime):
        return value.strftime("%m/%d/%Y")
    try:
        return pd.to_datetime(value).strftime("%m/%d/%Y")
    except (ValueError, TypeError):
        return str(value)


def convert(infile: str | Path, outfile: str | Path) -> None:
    # 1) read and rename
    df = (
        pd.read_excel(infile, header=0, dtype=str)
          .rename(columns={
              "交易日期":   "Date",
              "交易描述":   "Payee",
              "卡號":       "Memo",       # shove card-number into Memo
              "入賬款項":   "InflowRaw",  # will parse into Inflow
              "新簽賬項":   "OutflowRaw", # will parse into Outflow
          })
    )

    # 2) normalize Date
    df["Date"] = df["Date"].apply(_normalise_date)

    # 3) strip currency code and commas, split off numeric part
    def _num(x: str) -> str:
        if pd.isna(x) or not x.strip():
            return ""
        # e.g. "USD 1,234.56" → "1,234.56"
        parts = x.strip().split()  # split on whitespace
        num = parts[-1]            # take last token
        return num.replace(",", "")

    df["Inflow"]  = df["InflowRaw"].apply(_num)
    df["Outflow"] = df["OutflowRaw"].apply(_num)

    # 4) select and write
    df.loc[:, ["Date", "Payee", "Memo", "Outflow", "Inflow"]] \
      .to_csv(outfile, index=False)


def _usage():
    print("Usage: boccredit2ynab.py <input.xlsx> <output.csv>", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        _usage()
    convert(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
