import pandas as pd

# Read the CSV file
file_path = 'data_clean/AMD_data.csv'
df = pd.read_csv(file_path)

# Calculate total counts
total_posts = df['post_count'].sum()
total_comments = df['comment_count'].sum()

# Print the results
print(f"Total number of posts: {total_posts}")
print(f"Total number of comments: {total_comments}") 