#!/usr/bin/env python3

import json

def print_subreddit_info(data):
    """Print only relevant fields from subreddit data."""
    name = data.get("display_name", "Unknown")
    description = data.get("description", "No description")
    subscribers = data.get("subscribers", 0)
    
    # Get post and comment counts from _meta if available
    meta = data.get("_meta", {})
    num_posts = meta.get("num_posts", 0)
    num_comments = meta.get("num_comments", 0)
    
    print(f"\n{'=' * 50}")
    print(f"SUBREDDIT: r/{name}")
    print(f"{'=' * 50}")
    print(f"Subscribers: {subscribers}")
    print(f"Posts: {num_posts}")
    print(f"Comments: {num_comments}")
    print(f"\nDESCRIPTION:")
    
    # Handle None description
    if description is None:
        description = "No description available"
    
    # Truncate description if it's too long
    if len(description) > 500:
        print(f"{description[:500]}...\n[Description truncated]")
    else:
        print(description)
    print(f"{'=' * 50}\n")

def main():
    filepath = "subreddits_list/subreddits_stock_filtered.jsonl"
    
    try:
        with open(filepath, 'r') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    print_subreddit_info(data)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON line: {line[:50]}...")
                except Exception as e:
                    print(f"Error processing subreddit: {str(e)}")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        print("Please make sure the file path is correct.")

if __name__ == "__main__":
    main() 