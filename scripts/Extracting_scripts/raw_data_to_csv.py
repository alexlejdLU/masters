import pandas as pd
import json
import yfinance as yf
import numpy as np

# Define stock ticker IMPORTANT (DO NOT FORGET)

ticker = "AMD"
jsonl_file_posts    = "data_raw/AMD/r_amd_stock_posts.jsonl"
jsonl_file_comments = "data_raw/AMD/r_amd_stock_comments.jsonl"
name = "AMD_data"

# ── 1) Load & aggregate posts ──────────────────────────────────────────────────
posts = []
seen_posters = set()

with open(jsonl_file_posts, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' not in obj:
            continue

        date = pd.to_datetime(obj['created_utc'], unit='s').normalize()
        ups   = obj.get('ups', 0)
        ratio = obj.get('upvote_ratio', 1.0)
        author = obj.get('author')

        posts.append({
            'date': date,
            'ups': ups,
            'first_time_post': int(author and author not in seen_posters)
        })
        if author and author not in seen_posters:
            seen_posters.add(author)

df_posts = pd.DataFrame(posts)
posts_per_day = (
    df_posts
      .groupby('date')
      .agg(
          post_count            = ('ups',       'size'),
          post_upvotes          = ('ups',       'sum'),
          first_time_post_count = ('first_time_post','sum')
      )
      .reset_index()
)

# ── 2) Load & aggregate comments ─────────────────────────────────────────────
comments = []
seen_commenters = set()

with open(jsonl_file_comments, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' not in obj:
            continue

        date   = pd.to_datetime(obj['created_utc'], unit='s').normalize()
        ups    = obj.get('ups',   0)
        author = obj.get('author')

        comments.append({
            'date': date,
            'ups': ups,
            'first_time_comment': int(author and author not in seen_commenters)
        })
        if author and author not in seen_commenters:
            seen_commenters.add(author)

df_comments = pd.DataFrame(comments)
comments_per_day = (
    df_comments
      .groupby('date')
      .agg(
          comment_count            = ('ups',   'size'),
          comment_upvotes          = ('ups',   'sum'),
          first_time_comment_count = ('first_time_comment','sum')
      )
      .reset_index()
)

# ── 3) Build full date index & zero‐fill posts/comments ────────────────────────
start = min(posts_per_day['date'].min(), comments_per_day['date'].min())
end   = max(posts_per_day['date'].max(), comments_per_day['date'].max())
complete_date_range = pd.date_range(start=start, end=end, freq='D')

def reindex_zero(df):
    return (
        df
          .set_index('date')
          .reindex(complete_date_range, fill_value=0)
          .rename_axis('date')
          .reset_index()
    )

posts_per_day    = reindex_zero(posts_per_day)
comments_per_day = reindex_zero(comments_per_day)

# ── 4) Pull stock data from yfinance & fix the multi‐index issue ────────────────────
amd = yf.download(
    ticker,
    start = complete_date_range.min(),
    end   =(complete_date_range.max() + pd.Timedelta(days=1)),
    auto_adjust=False
)

# yf.download returned a MultiIndex (e.g. Price/Ticker), drop the extra level:
if isinstance(amd.columns, pd.MultiIndex):
    amd.columns = amd.columns.get_level_values(0)

close_prices = amd['Close'].to_numpy()
open_prices  = amd['Open'].to_numpy()
volumes      = amd['Volume'].to_numpy()

dfYf = pd.DataFrame(
    np.column_stack([close_prices, volumes, open_prices]),
    columns=['Close','Volume','Open'],
    index=amd.index
)

# align to full date range, filling non-trading days
dfYf = dfYf.reindex(complete_date_range)
dfYf[['Close','Volume','Open']] = dfYf[['Close','Volume','Open']].ffill().bfill()
dfYf.reset_index(inplace=True)
dfYf.rename(columns={'index':'date'}, inplace=True)

# ── 5) Merge all three & export to CSV ─────────────────────────────────────────
merged_df = (
    posts_per_day
      .merge(comments_per_day, on='date', how='inner')
      .merge(dfYf,             on='date', how='inner')
)

merged_df.to_csv(f"{name}.csv", index=False)
print(f"Wrote {merged_df.shape[0]} rows × {merged_df.shape[1]} cols to {name}.csv")
