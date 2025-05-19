## This script is for handling the subreddits that are true for asset specific subreddits

import pandas as pd
import os

# Input file path
input_file = 'subreddits_list/asset_specific_subreddits.csv'

# Output file path 
output_file = 'subreddits_list/true_asset_specific_subreddits.csv'

def extract_true_subreddits():
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Filter rows where is_asset_specific is True
    true_subreddits = df[df['is_asset_specific'] == True]
    
    # Write the filtered data to a new CSV file
    true_subreddits.to_csv(output_file, index=False)
    
    print(f"Extracted {len(true_subreddits)} subreddits with is_asset_specific=True")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    extract_true_subreddits()

#############Appending the subreddits posts and comments to the existing data########################

import pandas as pd
import json
import os

# Input files
true_subreddits_file = 'subreddits_list/true_asset_specific_subreddits.csv'
posts_comments_file = 'subreddits_list/filtered_posts_comments_subreddits_nsfw_private.jsonl'  # Updated path with .jsonl extension

def append_posts_comments_data():
    # Read the true subreddits CSV file
    df_subreddits = pd.read_csv(true_subreddits_file)
    
    # Create a dictionary to store posts and comments counts for each subreddit
    subreddit_metrics = {}
    
    # Read the JSONL file line by line to avoid loading the entire file into memory
    with open(posts_comments_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                display_name_prefixed = data.get('display_name_prefixed')
                
                if display_name_prefixed and display_name_prefixed in df_subreddits['display_name_prefixed'].values:
                    # Extract posts and comments metrics
                    meta_data = data.get('_meta', {})
                    num_posts = meta_data.get('num_posts', 0)
                    num_comments = meta_data.get('num_comments', 0)
                    
                    # Store the metrics
                    subreddit_metrics[display_name_prefixed] = {
                        'num_posts': num_posts,
                        'num_comments': num_comments
                    }
            except json.JSONDecodeError:
                continue
    
    # Add the posts and comments data to the dataframe
    df_subreddits['num_posts'] = df_subreddits['display_name_prefixed'].map(
        lambda x: subreddit_metrics.get(x, {}).get('num_posts', 0)
    )
    df_subreddits['num_comments'] = df_subreddits['display_name_prefixed'].map(
        lambda x: subreddit_metrics.get(x, {}).get('num_comments', 0)
    )
    
    # Save the updated dataframe to the same CSV file
    df_subreddits.to_csv(true_subreddits_file, index=False)
    
    print(f"Added posts and comments data to {len(subreddit_metrics)} subreddits")
    print(f"Results saved to {true_subreddits_file}")

if __name__ == "__main__":
    append_posts_comments_data()