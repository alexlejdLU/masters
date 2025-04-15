import pandas as pd
import json
from datetime import datetime


jsonl_file_posts = "data_raw/SNDL/r_sndl_comments.jsonl"

# Extract only created_utc and title from posts
comments_data = []

with open(jsonl_file_posts, 'r') as f:
    for line in f:
        obj = json.loads(line)
        created_utc = obj.get('created_utc')
        body = obj.get('body')
        if created_utc and body:
            comments_data.append({
                'created_utc': created_utc,
                'body': body
            })

# Create DataFrame with the data
df_comments = pd.DataFrame(comments_data)

# Convert UTC timestamp to datetime
df_comments['datetime'] = pd.to_datetime(df_comments['created_utc'], unit='s')

# Display the results
print(df_comments.head())
print(f"Total number of comments: {len(df_comments)}")

# Save to CSV for easy access
df_comments.to_csv("data_raw/SNDL/sndl_comments_utc_title.csv", index=False)
