import json

# Path to the subreddit data file
file_path = "subreddits_list/subreddits_stock_filtered.jsonl"

print(f"Reading ALL subreddit data from {file_path}")
print("This will print EVERY entry in the file, without any limit")

# Counter to track how many entries we process
entry_count = 0

# Open and process the file
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        # Process every line in the file without any limitations
        for line in f:
            try:
                # Parse the JSON data
                data = json.loads(line.strip())
                entry_count += 1
                
                # Print basic subreddit info (ALL of it)
                print("\n" + "="*50)
                print(f"ENTRY #{entry_count}")
                print(f"Subreddit: {data.get('display_name_prefixed', 'N/A')}")
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"URL: {data.get('url', 'N/A')}")
                
                # Full description without truncation
                print(f"Description: {data.get('description', 'N/A')}")
                
                # Print post/comment stats
                if "_meta" in data:
                    print(f"Posts: {data['_meta'].get('num_posts', 'N/A')}, Comments: {data['_meta'].get('num_comments', 'N/A')}")
            except json.JSONDecodeError:
                print(f"Warning: Skipped invalid JSON at line")
                continue
    
    print(f"\nProcessed ALL {entry_count} entries from the file")
except Exception as e:
    print(f"Error: {e}")
