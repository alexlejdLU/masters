#this file is written to extract the relevant forums from filtered subreddits
#the goal of this file is to minimize the irrelevant data so as to feed the cleaned version to an AI which extract relevant subreddits that are associated to a singular asset
#thus ultimately just to minimize costs of running it through a labelling AI
#Starting file is filtered_posts_comments_subreddits_nsfw_private.jsonl ergo - this is what was filtered initially (posts cutoff 1.5k, comments 3k, removed nsfw and private subreddits - as they are not related to asset specific discussions)


#!/usr/bin/env python3
import json
import os

# Input and output file paths
input_file = "subreddits_list/filtered_posts_comments_subreddits_nsfw_private.jsonl"
output_file = "subreddits_list/check.jsonl"

# Fields to extract
fields_to_extract = [
    "display_name_prefixed",  # FOR IDENTIFYING SUBREDDITS LATER
]

def process_file():
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as in_file, \
         open(output_file, 'w', encoding='utf-8') as out_file:
        
        line_count = 0
        for line in in_file:
            line_count += 1
            try:
                # Parse the JSON data from each line
                data = json.loads(line.strip())
                
                # Extract only the fields we want
                extracted_data = {field: data.get(field, "") for field in fields_to_extract}
                
                # Write the extracted data as a new JSON line
                out_file.write(json.dumps(extracted_data) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_count}: {e}")
                continue
            except Exception as e:
                print(f"Error processing line {line_count}: {e}")
                continue
    
    print(f"Processing complete. Extracted data saved to {output_file}")

if __name__ == "__main__":
    process_file() 