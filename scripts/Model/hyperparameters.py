#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

# six source columns we always build (a,b) for
_FEATURES = [
    "post_count",
    "post_upvotes",
    "first_time_post_count",
    "comment_count",
    "comment_upvotes",
    "first_time_comment_count",
]

def rolling_ab(csv_path: Path | str,
               window: int = 100,
               step: int = 1) -> pd.DataFrame:
    df = (pd.read_csv(csv_path, parse_dates=["date"])
            .set_index("date").asfreq("D").ffill())

    missing = [c for c in _FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {', '.join(missing)}")

    z = df[_FEATURES].diff().dropna().abs()
    rows, idx_end = [], []
    for s in range(0, len(z) - window + 1, step):
        w = z.iloc[s:s + window]
        row = {f"a_{c}": 0.1 * w[c].max() for c in _FEATURES}
        row.update({f"b_{c}": w[c].max() for c in _FEATURES})
        rows.append(row)
        idx_end.append(w.index[-1])

    return pd.DataFrame(rows, index=pd.Index(idx_end, name="window_end"))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--window", type=int, default=100)
    p.add_argument("--step",   type=int, default=1)
    p.add_argument("--out",    type=Path, required=True)
    args = p.parse_args()

    rolling_ab(args.csv, args.window, args.step) \
        .to_csv(args.out, index_label="window_end", float_format="%.2f")
