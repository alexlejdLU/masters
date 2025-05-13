#!/usr/bin/env python3
# rolling_ab_multi.py  – one (a,b) pair **per feature column**

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


def rolling_ab_multi(
    csv_path: Path | str,
    feature_cols: Sequence[str],
    window: int = 100,
    step: int = 1,
) -> pd.DataFrame:
    df = (
        pd.read_csv(csv_path, parse_dates=["date"])
          .set_index("date")
          .asfreq("D")
          .ffill()
    )

    z = df[list(feature_cols)].diff().dropna().abs()   # |Δx_t|
    rows, idx_end = [], []

    for start in range(0, len(z) - window + 1, step):
        block = z.iloc[start : start + window]
        row = {}
        for c in feature_cols:
            b = block[c].max()
            a = 0.1 * b
            row[f"a_{c}"] = a
            row[f"b_{c}"] = b
        rows.append(row)
        idx_end.append(block.index[-1])                # last day in window

    return pd.DataFrame(rows, index=idx_end)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--cols", nargs="+", required=True)
    p.add_argument("--window", type=int, default=100)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    rolling_ab_multi(args.csv, args.cols, args.window, args.step).to_csv(args.out)
