#!/usr/bin/env python3
"""
Epidemic-HMM: simplified implementation focusing on post_count only.
Based on Phillips & Gorse (2017) epidemic-detection hidden-Markov model.

Usage (bash):
    python epidemic_hmm.py data/bitcoin.csv --window 100 --n_init 20 --out btc_epidemic_probs.csv

The script reads a single CSV (one cryptocurrency / subreddit),
computes first-order differences for the post_count indicator, trains a
2-state switching AR(1) HMM on a rolling window, and writes the
probability that the **last** point in each window is in the epidemic
state.

Dependencies:
    pandas, numpy, statsmodels (>= 0.14), tqdm (optional progress bar).

See README.md for details.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import multiprocessing as mp

import numpy as np
import pandas as pd
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

try:
    from tqdm import tqdm  # type: ignore
    _tqdm = tqdm
except ImportError:  # pragma: no cover
    def _tqdm(x, **kwargs):
        return x

# --------------------------------------------------------------------------------------
# core utils
# --------------------------------------------------------------------------------------

def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Load CSV with a required **date** column and post_count indicator.

    The date column is parsed to pandas datetime and sorted ascending.
    Missing rows (dates) are *not* filled.
    """
    df = pd.read_csv(csv_path, parse_dates=["date"])
    if "date" not in df.columns:
        raise ValueError("CSV must contain a 'date' column.")
    if "post_count" not in df.columns:
        raise ValueError("CSV must contain a 'post_count' column.")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def difference(series: pd.Series) -> pd.Series:
    """Return first differences, dropping the initial NaN."""
    return series.diff().dropna()


def fit_switching_ar1(diff_series: pd.Series, n_init: int = 20, maxiter: int = 200):
    """Fit a two-state AR(1) Markov-switching model.

    Regime 1 (index 0): non-epidemic (Gaussian white noise)
    Regime 2 (index 1): epidemic       (AR(1) process)

    We use **statsmodels.tsa.regime_switching.MarkovRegression** with
    heteroskedastic variances and regime-dependent AR coefficients.
    Multiple random initialisations are tried; the fit with the highest
    log-likelihood is kept (to mitigate local maxima, as in the paper).
    """

    best_llf = -np.inf
    best_res = None

    # Model definition outside loop for speed
    # Create AR(1) model with 2 regimes - regime-specific intercepts, 
    # AR coefficients, and variances
    mod = MarkovRegression(
        diff_series,
        k_regimes=2,
        order=1,
        switching_trend=True,  # Allow different intercepts per regime
        switching_exog=True,   # Allow different AR coefficients per regime
        switching_variance=True,
        trend="c",  # constant mean
    )

    start_params = mod.start_params

    for _ in range(n_init):
        # jitter initial params -> random restart
        init = start_params + np.random.normal(scale=0.1, size=start_params.shape)
        try:
            res = mod.fit(
                start_params=init,
                maxiter=maxiter,
                disp=False,
            )
        except (ValueError, np.linalg.LinAlgError):
            continue  # failed fit, try another seed

        if res.llf > best_llf:
            best_llf = res.llf
            best_res = res

    if best_res is None:
        raise RuntimeError("All EM initialisations failed – check your data.")

    return best_res


def epidemic_probability(res) -> pd.Series:
    """Return smoothed probability P(state == epidemic) for every time-point."""
    # By convention, regime index 1 is epidemic because its variance > variance(regime0)
    prob_epidemic = res.smoothed_marginal_probabilities[1]
    return prob_epidemic


# --------------------------------------------------------------------------------------
# moving-window driver
# --------------------------------------------------------------------------------------

def window_task(args):
    """Helper for parallel pool: train HMM on one window, return last-point prob."""
    (idx_start, window_values, n_init) = args
    series = pd.Series(window_values)
    res = fit_switching_ar1(series, n_init=n_init)
    prob = epidemic_probability(res).iloc[-1]
    return idx_start, prob


def rolling_epidemic_probs(
    diff_series: pd.Series,
    window: int = 100,
    step: int = 1,
    n_init: int = 20,
    n_jobs: int = 1,
) -> pd.Series:
    """Compute epidemic probability for **last** point in each rolling window.

    Parameters
    ----------
    diff_series : pd.Series
        First-differenced time series.
    window      : int
        Window length (number of observations).
    step        : int
        How many observations to slide the window between fits.
    n_init      : int
        EM random restarts per window.
    n_jobs      : int
        Parallel workers (use >1 for speed).
    """
    if window < 10:
        raise ValueError("Window too small – needs to be >= 10 points.")

    # Build list of tasks: (start-idx, window-array, n_init)
    tasks = []
    values = diff_series.values
    for start in range(0, len(values) - window + 1, step):
        tasks.append((start, values[start : start + window], n_init))

    probs = np.full(len(values), np.nan)

    if n_jobs == 1:
        for t in _tqdm(tasks, desc="windows"):
            idx, p = window_task(t)
            probs[idx + window - 1] = p
    else:
        with mp.Pool(processes=n_jobs) as pool:
            for idx, p in _tqdm(pool.imap_unordered(window_task, tasks), total=len(tasks)):
                probs[idx + window - 1] = p

    return pd.Series(probs, index=diff_series.index)


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def parse_args():
    ap = argparse.ArgumentParser(description="Fit moving-window epidemic HMM on post_count.")
    ap.add_argument("csv", type=Path, help="CSV file with date + post_count columns")
    ap.add_argument("--window", type=int, default=100, help="Window size (default 100)")
    ap.add_argument("--step", type=int, default=1, help="Window step (default 1)")
    ap.add_argument("--n_init", type=int, default=20, help="Random restarts per window")
    ap.add_argument("--n_jobs", type=int, default=1, help="Parallel workers")
    ap.add_argument("--out", type=Path, required=True, help="Output CSV path")
    return ap.parse_args()


def main():
    args = parse_args()

    df = load_dataset(args.csv)

    # Process only post_count
    print(f"Processing post_count")
    diff = difference(df["post_count"])
    probs = rolling_epidemic_probs(
        diff,
        window=args.window,
        step=args.step,
        n_init=args.n_init,
        n_jobs=args.n_jobs,
    )
    
    # Create output dataframe with date and epidemic probability
    output_df = pd.DataFrame({
        "date": df["date"],
        "post_count": df["post_count"],
        "post_count_diff": pd.concat([pd.Series([np.nan]), diff]),  # Add NaN for first row
        "prob_epidemic": probs
    })
    
    output_df.to_csv(args.out, index=False)
    print(f"Saved epidemic probabilities -> {args.out}")


if __name__ == "__main__":
    main()
