#!/usr/bin/env python3
"""
epidemic_model.py

Compute rolling‐window priors for a single feature (e.g. post_count):
   – (a,b) = (0.1*max|Δ|, max|Δ|) over each 100-day block
   – σ0, σ1 from their 4-level Uniform hierarchy
   – Markov priors: π ~ Dirichlet(0.5,0.5), α_ii ~ Beta(0.5,0.5), ρ ~ Uniform(−1,1)
"""
from pathlib import Path
import argparse
from typing import Dict, Any

import numpy as np
import pandas as pd


def compute_ab(series: pd.Series, window: int = 100) -> pd.DataFrame:
    s  = series.asfreq("D").ffill()
    dz = s.diff().abs().dropna()
    dates = dz.index

    rows, idxs = [], []
    arr = dz.values
    for start in range(len(arr) - window + 1):
        block = arr[start : start + window]
        b = block.max()
        a = 0.1 * b
        rows.append((a, b))
        idxs.append(dates[start + window - 1])

    return pd.DataFrame(rows, columns=["a", "b"], index=pd.Index(idxs, name="window_end"))


def sample_sigma(a: float, b: float) -> Dict[str, float]:
    # 4-level Uniform on [a,b] → θ_low…θ_high → then σ0, σ1
    θ_low  = np.random.uniform(a, b)
    θ_mid1 = np.random.uniform(θ_low, b)
    θ_mid2 = np.random.uniform(θ_mid1, b)
    θ_high = np.random.uniform(θ_mid2, b)
    σ0     = np.random.uniform(θ_low,  θ_mid1)
    σ1     = np.random.uniform(θ_mid2, θ_high)
    return {"σ0": σ0, "σ1": σ1}


def initialize_markov_priors() -> Dict[str, Any]:
    # π ~ Dirichlet(0.5,0.5)
    pi0, pi1 = np.array([0.5, 0.5])

    # α_00, α_11 ~ Beta(0.5,0.5)
    α00 = np.random.beta(0.5, 0.5)
    α11 = np.random.beta(0.5, 0.5)
    A = np.array([[α00, 1 - α00],
                  [1 - α11, α11]])
    rho = np.random.uniform(-1, 1)
    return {"pi0": pi0, "pi1": pi1,
            "α00": α00, "α01": 1 - α00,
            "α10": 1 - α11, "α11": α11,
            "rho": rho}


def setup_hmm_priors(csv_path: Path, feature_col: str, window: int
                     ) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["date"]).set_index("date")
    series = df[feature_col]

    ab = compute_ab(series, window=window)
    rows = []
    for tup in ab.itertuples():   # (window_end, a, b)
        _, a, b = tup
        sigma = sample_sigma(a, b)
        markov = initialize_markov_priors()
        row = {"a": a, "b": b, **sigma, **markov}
        rows.append(row)

    return pd.DataFrame(rows, index=ab.index)


def main():
    p = argparse.ArgumentParser(
        description="Compute σ₀,σ₁ and Markov‐priors for each rolling window."
    )
    p.add_argument("csv",     type=Path, help="input CSV with 'date' + feature")
    p.add_argument("--feature", type=str, required=True,
                   help="name of feature column (e.g. post_count)")
    p.add_argument("--window",  type=int, default=100,
                   help="rolling window length")
    p.add_argument("--seed",    type=int, default=None,
                   help="optional RNG seed")
    p.add_argument("--out",    type=Path, required=True,
                   help="output CSV path")
    args = p.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    priors = setup_hmm_priors(args.csv, args.feature, window=args.window)
    priors.to_csv(args.out, index_label="window_end", float_format="%.6f")
    print(f"Saved {len(priors)} rows → {args.out}")


if __name__ == "__main__":
    main()
