import pandas as pd
import json
from datetime import datetime
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

jsonl_file_posts = "data_raw/SNDL/r_sndl_posts.jsonl"
jsonl_file_comments = "data_raw/SNDL/r_sndl_comments.jsonl"

######################### - Reddit data - posts per day 
posts = []
with open(jsonl_file_posts, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' in obj:
            posts.append({
                'created_utc': obj['created_utc']
            })
df_posts = pd.DataFrame(posts)
df_posts['date'] = pd.to_datetime(df_posts['created_utc'], unit='s').dt.date
posts_per_day = df_posts.groupby('date').size().reset_index(name='post_count')

######################### - Reddit data - comments per day 
comments = []
with open(jsonl_file_comments, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' in obj:
            comments.append({
                'created_utc': obj['created_utc']
            })
df_comments = pd.DataFrame(comments)
df_comments['date'] = pd.to_datetime(df_comments['created_utc'], unit='s').dt.date
comments_per_day = df_comments.groupby('date').size().reset_index(name='comment_count')


######################### - Reddit data - upvotes on posts per day 
votes_posts = []
with open(jsonl_file_posts, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' in obj and 'ups' in obj and 'score' in obj and 'upvote_ratio' in obj:
            ups = obj['ups']
            score = obj['score']
            upvote_ratio = obj['upvote_ratio']

            # Calculate downvotes
            downvotes = ups - (score * upvote_ratio)

            votes_posts.append({
                'created_utc': obj['created_utc'],
                'upvotes': ups,
                'score': score,
                'downvotes': downvotes
            })

df_votes_posts = pd.DataFrame(votes_posts)
df_votes_posts['date'] = pd.to_datetime(df_votes_posts['created_utc'], unit='s').dt.date
upvotes_per_day_posts = df_votes_posts.groupby('date')['upvotes'].sum().reset_index(name='post_upvotes')
downvotes_per_day_posts = df_votes_posts.groupby('date')['downvotes'].sum().reset_index(name='post_downvotes')
score_per_day_posts = df_votes_posts.groupby('date')['score'].sum().reset_index(name='post_score')




######################### - Reddit data - upvotes on comments per day 
votes_comments = []
with open(jsonl_file_comments, 'r') as f:
    for line in f:
        obj = json.loads(line)
        if 'created_utc' in obj and 'ups' in obj and 'score' in obj:
            ups = obj['ups']
            score = obj['score']

            votes_comments.append({
                'created_utc': obj['created_utc'],
                'upvotes': ups,
                'score': score,
            })

df_comments_posts = pd.DataFrame(votes_comments)
df_comments_posts['date'] = pd.to_datetime(df_comments_posts['created_utc'], unit='s').dt.date
upvotes_per_day_comments = df_comments_posts.groupby('date')['upvotes'].sum().reset_index(name='comment_upvotes')
score_per_day_comments = df_comments_posts.groupby('date')['score'].sum().reset_index(name='comment_score')


######################### - Reddit data - first-time posts per day
first_time_posters = []
seen_posters = set()

with open(jsonl_file_posts, 'r') as f:
    for line in f:
        obj = json.loads(line)
        author = obj.get('author')
        created_utc = obj.get('created_utc')
        if author and created_utc and author not in seen_posters:
            seen_posters.add(author)
            first_time_posters.append({
                'created_utc': created_utc,
                'author': author
            })

df_first_time_posts = pd.DataFrame(first_time_posters)
df_first_time_posts['date'] = pd.to_datetime(df_first_time_posts['created_utc'], unit='s').dt.date
first_time_posting_per_day = df_first_time_posts.groupby('date').size().reset_index(name='first_time_post_count')

######################### - Reddit data - first-time comments per day
first_time_commenters = []
seen_commenters = set()

with open(jsonl_file_comments, 'r') as f:
    for line in f:
        obj = json.loads(line)
        author = obj.get('author')
        created_utc = obj.get('created_utc')
        if author and created_utc and author not in seen_commenters:
            seen_commenters.add(author)
            first_time_commenters.append({
                'created_utc': created_utc,
                'author': author
            })

df_first_time_comments = pd.DataFrame(first_time_commenters)
df_first_time_comments['date'] = pd.to_datetime(df_first_time_comments['created_utc'], unit='s').dt.date
first_time_commenting_per_day = df_first_time_comments.groupby('date').size().reset_index(name='first_time_comment_count')


# Reindex the comments and posts to include all dates in the specified range
complete_date_range = pd.date_range(start=df_posts['date'].min(), end=df_posts['date'].max())
posts_per_day.set_index('date', inplace=True)
posts_per_day = posts_per_day.reindex(complete_date_range, fill_value=0).reset_index()
posts_per_day.rename(columns={'index': 'date'}, inplace=True)
comments_per_day.set_index('date', inplace=True)
comments_per_day = comments_per_day.reindex(complete_date_range, fill_value=0).reset_index()
comments_per_day.rename(columns={'index': 'date'}, inplace=True)
upvotes_per_day_posts.set_index('date', inplace=True)
upvotes_per_day_posts = upvotes_per_day_posts.reindex(complete_date_range, fill_value=0).reset_index()
upvotes_per_day_posts.rename(columns={'index': 'date'}, inplace=True)
downvotes_per_day_posts.set_index('date', inplace=True)
downvotes_per_day_posts = downvotes_per_day_posts.reindex(complete_date_range, fill_value=0).reset_index()
downvotes_per_day_posts.rename(columns={'index': 'date'}, inplace=True)
score_per_day_posts.set_index('date', inplace=True)
score_per_day_posts = score_per_day_posts.reindex(complete_date_range, fill_value=0).reset_index()
score_per_day_posts.rename(columns={'index': 'date'}, inplace=True)
upvotes_per_day_comments.set_index('date', inplace=True)
upvotes_per_day_comments = upvotes_per_day_comments.reindex(complete_date_range, fill_value=0).reset_index()
upvotes_per_day_comments.rename(columns={'index': 'date'}, inplace=True)
score_per_day_comments.set_index('date', inplace=True)
score_per_day_comments = score_per_day_comments.reindex(complete_date_range, fill_value=0).reset_index()
score_per_day_comments.rename(columns={'index': 'date'}, inplace=True)
first_time_posting_per_day.set_index('date', inplace=True)
first_time_posting_per_day = first_time_posting_per_day.reindex(complete_date_range, fill_value=0).reset_index()
first_time_posting_per_day.rename(columns={'index': 'date'}, inplace=True)
first_time_commenting_per_day.set_index('date', inplace=True)
first_time_commenting_per_day = first_time_commenting_per_day.reindex(complete_date_range, fill_value=0).reset_index()
first_time_commenting_per_day.rename(columns={'index': 'date'}, inplace=True)


######################### - Volume and close price data  Y-finance

# Volume and close price data Y-finance
sndl = yf.download("SNDL", start=df_posts['date'].min(), end=df_posts['date'].max())
close_prices = sndl['Close'].to_numpy()
open_prices = sndl['Open'].to_numpy()
volumes = sndl['Volume'].to_numpy()
dfYf = pd.DataFrame(np.column_stack([close_prices, volumes, open_prices]), columns=['Close', 'Volume', 'Open'], index=sndl.index)
#fixing non trading days
dfYf = dfYf.reindex(complete_date_range)
dfYf[['Close', 'Volume', 'Open']] = dfYf[['Close', 'Volume', 'Open']].ffill()
dfYf[['Close', 'Volume', 'Open']] = dfYf[['Close', 'Volume', 'Open']].bfill()
dfYf.reset_index(inplace=True)
dfYf.rename(columns={'index': 'date'}, inplace=True)


############################## Merge datasets on the 'date' column
merged_df = pd.merge(posts_per_day, comments_per_day, on='date', how='inner')
merged_df = pd.merge(merged_df, dfYf, on='date', how='inner')
merged_df = pd.merge(merged_df, upvotes_per_day_posts, on='date', how='inner')
merged_df = pd.merge(merged_df, downvotes_per_day_posts, on='date', how='inner')
merged_df = pd.merge(merged_df, score_per_day_posts, on='date', how='inner')
merged_df = pd.merge(merged_df, upvotes_per_day_comments, on='date', how='inner')
merged_df = pd.merge(merged_df, score_per_day_comments, on='date', how='inner')
merged_df = pd.merge(merged_df, first_time_posting_per_day, on='date', how='inner')
merged_df = pd.merge(merged_df, first_time_commenting_per_day, on='date', how='inner')


######################### - print data to check symmetry and for future references 
# print(dfYf.head())
# print(dfYf.tail())
# print(posts_per_day.head())
# print(posts_per_day.tail())
# print(dfYf.shape)
# print(posts_per_day.shape)
# total_first_time_posters = first_time_posting_per_day['post_count'].sum()
# total_first_time_commenters = first_time_commenting_per_day['comment_count'].sum()
# print(f"Total first-time posters: {total_first_time_posters}")
# print(f"Total first-time commenters: {total_first_time_commenters}")
# filename_posts = "data_raw/SNDL/r_sndl_posts.jsonl"
# with open(filename_posts, 'r') as file:
#     non_empty_lines_posts = sum(1 for line in file if line.strip())
# print(f"Total number of posts: {non_empty_lines_posts}")
# filename_comments = "data_raw/SNDL/r_sndl_comments.jsonl"
# with open(filename_comments, 'r') as file:
#     non_empty_lines_comments = sum(1 for line in file if line.strip())
# print(f"Total number of comments: {non_empty_lines_comments}")
print(merged_df.head())
print(merged_df.tail())
print(merged_df.shape)


######################## - plot data - Create a subplot with two y-axes
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=merged_df['date'], y=merged_df['post_count'], name='Post Count', mode='lines'),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=merged_df['date'], y=merged_df['Close'], name='Close Price', mode='lines'),
    secondary_y=True,
)
fig.update_layout(title_text='Reddit Post Count and SNDL Close Price')
fig.update_xaxes(title_text='Date')
fig.update_yaxes(title_text='Post Count', secondary_y=False)
fig.update_yaxes(title_text='Close Price', secondary_y=True)
fig.show()