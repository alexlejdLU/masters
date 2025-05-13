#!/usr/bin/env python3
# priors_postcount_stats_sigma.py – empirically compute means and 95% CIs for σ₀ and σ₁ via Monte Carlo simulation

from pathlib import Path
import numpy as np
import pandas as pd
import argparse

def sample_sigmas(a: float, b: float, n: int):
    """
    Draw n samples for σ0 and σ1 based on the hierarchy:
      θ_low  ~ U(a, b)
      θ_mid1 ~ U(θ_low, b)
      θ_mid2 ~ U(θ_mid1, b)
      θ_high~ U(θ_mid2, b)
      σ0     ~ U(θ_low, θ_mid1)
      σ1     ~ U(θ_mid2, θ_high)
    Returns two arrays of shape (n,): sigma0_samples and sigma1_samples
    """
    θ_low   = np.random.uniform(a, b, size=n)
    θ_mid1  = np.random.uniform(θ_low, b)
    θ_mid2  = np.random.uniform(θ_mid1, b)
    θ_high  = np.random.uniform(θ_mid2, b)
    σ0      = np.random.uniform(θ_low, θ_mid1)
    σ1      = np.random.uniform(θ_mid2, θ_high)
    return σ0, σ1


def compute_stats(samples: np.ndarray, alpha: float = 0.05):
    """
    Given a 1D samples array, compute mean and 100*(1-alpha)% CI.
    Returns mean, lower_bound, upper_bound
    """
    mean = samples.mean()
    lower = np.quantile(samples, alpha/2)
    upper = np.quantile(samples, 1 - alpha/2)
    return mean, lower, upper


def sample_sigma_stats(hyper_csv: Path | str,
                       out_csv:    Path | str,
                       seed:     int | None = None,
                       draws:    int = 10000) -> None:
    if seed is not None:
        np.random.seed(seed)

    ab = pd.read_csv(hyper_csv, parse_dates=["window_end"])
    if {"a_post_count", "b_post_count"} - set(ab.columns):
        raise ValueError("hyper_csv must contain a_post_count and b_post_count")

    records = []
    for row in ab.itertuples(index=False):
        a, b = row.a_post_count, row.b_post_count
        σ0_samples, σ1_samples = sample_sigmas(a, b, draws)
        σ0_mean, σ0_lo, σ0_hi = compute_stats(σ0_samples)
        σ1_mean, σ1_lo, σ1_hi = compute_stats(σ1_samples)

        records.append({
            "window_end": row.window_end,
            "σ0_mean": σ0_mean,
            "σ0_ci_lo": σ0_lo,
            "σ0_ci_hi": σ0_hi,
            "σ1_mean": σ1_mean,
            "σ1_ci_lo": σ1_lo,
            "σ1_ci_hi": σ1_hi,
        })

    out = pd.DataFrame.from_records(records)
    out.to_csv(out_csv, index=False, float_format="%.6f")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hyper_csv", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--draws", type=int, default=10000,
                        help="Number of Monte Carlo draws per row (default: 10000)")
    args = parser.parse_args()

    sample_sigma_stats(args.hyper_csv, args.out, args.seed, args.draws)
