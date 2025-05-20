import pandas as pd

# Read the CSV file
file_path = 'subreddits_list/true_asset_specific_subreddits_filter.csv'
df = pd.read_csv(file_path)

# Group by identified_asset and sum the posts and comments
asset_totals = df.groupby('identified_asset').agg({
    'num_posts': 'sum',
    'num_comments': 'sum',
    'display_name_prefixed': lambda x: list(x),
    'true_name': 'first',  # Take the first true name for each asset
    'asset_type': 'first'  # Take the first asset type for each asset
}).reset_index()

# Count unique assets
unique_assets_count = len(asset_totals)

# Sort by total comments (descending)
asset_totals = asset_totals.sort_values('num_comments', ascending=False)

# Create output file
output_file = 'asset_engagement_stats.csv'
with open(output_file, 'w') as f:
    f.write("identified_asset,true_name,asset_type,total_posts,total_comments,subreddits\n")
    for _, row in asset_totals.iterrows():
        subreddits = ', '.join(row['display_name_prefixed'])
        line = f"{row['identified_asset']},{row['true_name']},{row['asset_type']},{row['num_posts']},{row['num_comments']},{subreddits}\n"
        f.write(line)

# Print summary
print(f"Analysis complete! Found {unique_assets_count} unique assets.")
print(f"Top 5 assets by comment volume:")
for i, row in asset_totals.head(5).iterrows():
    print(f"{row['identified_asset']} ({row['true_name']}): {row['num_comments']} comments, {row['num_posts']} posts")
print(f"Results written to {output_file}") 