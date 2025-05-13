#!/usr/bin/env python3
# sample_priors.py
#
# Read the (a,b) bounds per window and sample the hierarchical
# Uniform priors for θ’s and σ’s exactly as specified.

from pathlib import Path
import pandas as pd
import numpy as np
import argparse


def sample_one(a: float, b: float) -> dict[str, float]:
    """
    Draw a single set of hierarchical uniforms given outer bounds (a, b).
    """
    θ_low  = np.random.uniform(a, b)
    θ_mid1 = np.random.uniform(θ_low, b)
    θ_mid2 = np.random.uniform(θ_mid1, b)
    θ_high = np.random.uniform(θ_mid2, b)

    σ0 = np.random.uniform(θ_low,  θ_mid1)
    σ1 = np.random.uniform(θ_mid2, θ_high)

    return dict(
        θ_low=θ_low, θ_mid1=θ_mid1, θ_mid2=θ_mid2, θ_high=θ_high,
        σ0=σ0, σ1=σ1
    )


def sample_priors(csv_in: Path | str,
                  csv_out: Path | str,
                  seed: int | None = None) -> None:
    if seed is not None:
        np.random.seed(seed)

    ab = pd.read_csv(csv_in, parse_dates=["window_end"])
    draws = [sample_one(row.a, row.b) for row in ab.itertuples(index=False)]
    out  = pd.concat([ab[["window_end"]], pd.DataFrame(draws)], axis=1)
    out.to_csv(csv_out, index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Sample θ_low, θ_mid1, θ_mid2, θ_high, σ0, σ1 "
                    "for every (a,b) row in hyperparameters.csv")
    p.add_argument("hyper_csv", type=Path,
                   help="CSV produced by prior_windows_min.py (must have a,b cols)")
    p.add_argument("--out", required=True, type=Path,
                   help="Output CSV with sampled priors")
    p.add_argument("--seed", type=int, default=None,
                   help="Optional RNG seed for reproducibility")
    args = p.parse_args()

    sample_priors(args.hyper_csv, args.out, args.seed)
