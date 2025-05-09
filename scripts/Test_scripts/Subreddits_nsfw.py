import json
from collections import Counter
import os

# Path to the data file
file_path = "subreddits_list/filtered_posts_comments_subreddits.jsonl"

# Initialize counters
nsfw_count = 0  # Count of subreddits with "over18": true
non_english_count = 0  # Count of subreddits with "lang" not equal to "en"
subreddit_types = Counter()  # Counter for each "subreddit_type"

# Check if file exists
if not os.path.exists(file_path):
    print(f"Error: File {file_path} not found.")
    exit(1)

print(f"Analyzing file: {file_path}")
print("Counting NSFW subreddits, non-English subreddits, and all subreddit types...")

# Process the file
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        line_count = 0
        for line in f:
            line_count += 1
            try:
                data = json.loads(line.strip())
                
                # Check for NSFW subreddits
                if data.get('over18') is True:
                    nsfw_count += 1
                
                # Check for non-English subreddits
                if data.get('lang') != 'en':
                    non_english_count += 1
                    
                # Count subreddit types
                subreddit_type = data.get('subreddit_type')
                if subreddit_type:
                    subreddit_types[subreddit_type] += 1
                
            except json.JSONDecodeError:
                print(f"Warning: Skipped invalid JSON at line {line_count}")
                continue
            except Exception as e:
                print(f"Error processing line {line_count}: {e}")
                continue
                
    # Print results
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    
    print(f"\nTotal subreddits processed: {line_count}")
    print(f"NSFW subreddits (over18=true): {nsfw_count} ({nsfw_count/line_count*100:.2f}%)")
    print(f"Non-English subreddits: {non_english_count} ({non_english_count/line_count*100:.2f}%)")
    
    print("\nSubreddit types distribution:")
    for subreddit_type, count in subreddit_types.most_common():
        print(f"  {subreddit_type}: {count} ({count/line_count*100:.2f}%)")
    
except Exception as e:
    print(f"Error reading file: {e}")
