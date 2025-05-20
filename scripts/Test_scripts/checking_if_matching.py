import os

def extract_subreddits_from_file(file_path):
    """Extract subreddit names (r/something) from a CSV file."""
    subreddits = set()
    
    try:
        with open(file_path, 'r') as f:
            # Skip header
            next(f, None)
            for line in f:
                # Extract the first column (display_name_prefixed) which contains r/subredditname
                if line.strip() and ',' in line:
                    subreddit = line.split(',')[0].strip()
                    if subreddit.startswith('r/'):
                        subreddits.add(subreddit)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return subreddits

def main():
    # Get the absolute path to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '../..'))
    
    # Define full paths to the CSV files
    original_path = os.path.join(project_root, 'subreddits_list', 'true_asset_specific_subreddits.csv')
    true_filtered_path = os.path.join(project_root, 'subreddits_list', 'true_asset_specific_subreddits_filter.csv')
    false_filtered_path = os.path.join(project_root, 'subreddits_list', 'false_asset_specific_subreddits_filter.csv')
    
    # Extract subreddits from each file
    original_subreddits = extract_subreddits_from_file(original_path)
    true_filtered_subreddits = extract_subreddits_from_file(true_filtered_path)
    false_filtered_subreddits = extract_subreddits_from_file(false_filtered_path)
    
    # Print counts for verification
    print(f"Original file has {len(original_subreddits)} subreddits")
    print(f"True filtered file has {len(true_filtered_subreddits)} subreddits")
    print(f"False filtered file has {len(false_filtered_subreddits)} subreddits")
    
    # All classified subreddits (union of true and false filtered)
    all_classified = true_filtered_subreddits.union(false_filtered_subreddits)
    print(f"Total classified subreddits: {len(all_classified)}")
    
    # Find missing subreddits (in original but not in classified)
    missing_subreddits = original_subreddits - all_classified
    
    # Print results
    print(f"\nFound {len(missing_subreddits)} missing subreddits:")
    for subreddit in sorted(missing_subreddits):
        print(subreddit)

if __name__ == "__main__":
    main()
