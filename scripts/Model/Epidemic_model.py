#!/usr/bin/env python3
"""
prior_windows.py
----------------
Utility for computing Gelman-style weakly–informative *variance* priors
on a rolling window, exactly as described in Gorse et al. (2023).

Core outputs per window
=======================
    window_end   pandas.Timestamp      last day included in this window
    a            float                 lower bound for all σ-priors
    b            float                 upper bound for all σ-priors

The calling code (your EM/HMM routine) will read the `a` and `b` columns
row-by-row and set Uniform(a,b) priors for σ_E, σ_NE and d *before* running
expectation–maximisation on that same window.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Sequence

# ---------------------------------------------------------------------
# User-facing entry point
# ---------------------------------------------------------------------
def compute_window_priors(
    csv_path: Path | str,
    feature_cols: Sequence[str] = ("post_count", "comment_count", "Volume"),
    window: int = 100,
    step: int = 1,
) -> pd.DataFrame:
    """
    Parameters
    ----------
    csv_path      : path-like
        CSV containing at least a 'date' column plus the columns listed
        in `feature_cols`. Extra columns are ignored.
    feature_cols  : list/tuple of str
        Numeric columns to difference and feed to the HMM.  Add or
        remove names here as needed.
    window        : int
        Length of the sliding block (default = 100 days).
    step          : int
        How far to slide the window each iteration (default = 1 day).

    Returns
    -------
    priors_df     : pd.DataFrame
        Index aligns to the last day of every window (i.e. the first
        row corresponds to `window-1` in zero-based indexing).
        Columns = ["a", "b"].
    """
    # --------------------------------------------------------------
    # 1. Read CSV and force a daily DateTimeIndex.
    # --------------------------------------------------------------
    df = (
        pd.read_csv(csv_path, parse_dates=["date"])
        .set_index("date")
        .asfreq("D")               # pad gaps so diff() is day-to-day
        .ffill()                   # simple forward-fill for holidays
    )

    # Keep only the columns we actually model.
    z_raw = df[list(feature_cols)].copy()

    # --------------------------------------------------------------
    # 2. First differences  z_t = x_t - x_{t-1}.
    #    The first row after diff() is NaN and gets dropped.
    # --------------------------------------------------------------
    z = z_raw.diff().dropna()

    # --------------------------------------------------------------
    # 3. Roll a fixed-length window through |z_t| to get max-diff.
    #    Using pandas' rolling() with `step` implemented manually.
    # --------------------------------------------------------------
    abs_z = z.abs().to_numpy()                 # (T, M)  ndarray
    time_index = z.index

    a_list, b_list, t_end = [], [], []

    for start in range(0, len(abs_z) - window + 1, step):
        stop = start + window                  # slice end (exclusive)
        block = abs_z[start:stop, :]           # window array (w, M)

        b_w = block.max()                      # scalar max |Δ|
        a_w = 0.1 * b_w                        # weak prior lower bound

        a_list.append(a_w)
        b_list.append(b_w)
        t_end.append(time_index[stop - 1])     # last day in window

    priors_df = pd.DataFrame(
        {"a": a_list, "b": b_list},
        index=pd.Index(t_end, name="window_end"),
    )

    return priors_df


# ---------------------------------------------------------------------
# Demo / CLI
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Compute (a,b) variance-prior bounds on a rolling window."
    )
    ap.add_argument("csv", type=Path, help="Input CSV file")
    ap.add_argument("--window", type=int, default=100, help="Window length")
    ap.add_argument("--step", type=int, default=1, help="Step size")
    ap.add_argument(
        "--cols",
        nargs="+",
        default=["post_count", "comment_count", "Volume"],
        help="Feature columns to difference",
    )
    ap.add_argument("--out", type=Path, required=True, help="Output CSV")
    args = ap.parse_args()

    priors = compute_window_priors(
        csv_path=args.csv,
        feature_cols=args.cols,
        window=args.window,
        step=args.step,
    )
    priors.to_csv(args.out, index=True)
    print(f"Saved {len(priors)} windows → {args.out}")
