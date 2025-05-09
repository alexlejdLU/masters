########THIS IS NLP script - yielded meh results not optimal.. 

# from sentence_transformers import SentenceTransformer, util
# import json
# from tqdm import tqdm

# # Load model
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # Reference descriptions representing stock/finance topics
# reference_phrases = [
#     "discussion about a specific stock",
#     "subreddit for a public company",
#     "talking about a single stock or crypto asset",
#     "community for a company or its ticker symbol",
#     "discussion of a specific traded asset",
#     "community for holders of a stock",
#     "updates and opinions about a single stock",
#     "investors following one company",
#     "price movement of one stock or asset",
#     "individual equity discussion","AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "NFLX", "JPM", "V",
#     "SHOP", "SQ", "U", "COIN", "ROKU", "PLTR", "DKNG", "RBLX", "HOOD", "CRWD",
#     "AMD", "INTC", "ASML", "AVGO", "MU",
#     "XOM", "CVX", "F", "GM", "NIO",
#     "MRNA", "BNTX", "PFE", "JNJ", "ABBV",
#     "PYPL", "BAC", "WFC", "MA", "SOFI",
#     "COST", "WMT", "TGT", "CROX", "NKE",
#     "LCID", "RIVN", "SPCE", "BB", "IONQ"
# ]
# reference_embeddings = model.encode(reference_phrases, batch_size=256, convert_to_tensor=True)

# input_file = "subreddits_list/filtered_posts_comments_subreddits.jsonl"
# output_file = "subreddits_list/nlp_matched_subreddits.jsonl"
# similarity_threshold = 0.4  # tune this if needed
# total_lines = 66500

# with open(input_file, "r") as infile, open(output_file, "w") as outfile:
#     for line in tqdm(infile, total=total_lines, desc="Matching subreddits"):
#         try:
#             data = json.loads(line)
#             fields = [
#                 data.get("display_name", ""),
#                 data.get("title", ""),
#                 data.get("public_description", ""),
#                 data.get("description", "")
#             ]
#             combined_text = " ".join(str(f or "") for f in fields)
#             subreddit_embedding = model.encode(combined_text, convert_to_tensor=True)
#             sim_scores = util.pytorch_cos_sim(subreddit_embedding, reference_embeddings)
#             max_sim = sim_scores.max().item()

#             if max_sim >= similarity_threshold:
#                 json.dump(data, outfile)
#                 outfile.write("\n")
#         except json.JSONDecodeError:
#             continue

#################### filtering more 
# import json
# import os

# # File paths
# input_file = "subreddits_list/filtered_posts_comments_subreddits.jsonl"
# output_file = "subreddits_list/filtered_posts_comments_subreddits_v2.jsonl"

# # Make sure output directory exists
# os.makedirs(os.path.dirname(output_file), exist_ok=True)

# # Counters
# public_count = 0
# sfw_count = 0
# kept_count = 0

# # Filter the file
# with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
#     for line in infile:
#         try:
#             data = json.loads(line.strip())
            
#             # Check if subreddit is public and not NSFW
#             is_public = data.get('subreddit_type') == 'public'
#             is_sfw = data.get('over18') is not True
            
#             # Keep only public subreddits that are SFW
#             if is_public and is_sfw:
#                 json.dump(data, outfile)
#                 outfile.write('\n')
#                 kept_count += 1
                
#                 # Update counts
#                 if is_public:
#                     public_count += 1
#                 if is_sfw:
#                     sfw_count += 1
                
#         except (json.JSONDecodeError, Exception):
#             continue


# print(f"Total public subreddits: {public_count}")
# print(f"Total SFW subreddits: {sfw_count}")
# print(f"Total kept subreddits: {kept_count}")


################### stock filtering based on company tickers
import json
import os
import re

# File paths
input_file = "subreddits_list/filtered_posts_comments_subreddits_v2.jsonl"
company_file = "subreddits_list/company_tickers.json"
output_file = "subreddits_list/subreddits_stock_filtered.jsonl"

# Make sure output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Load company tickers and titles
with open(company_file, 'r', encoding='utf-8') as f:
    companies = json.load(f)

# Extract tickers and titles to search for
search_terms = []
for company_id, company_data in companies.items():
    ticker = company_data.get('ticker', '').strip().lower()
    title = company_data.get('title', '').strip().lower()
    
    # Add ticker and all words in title to search terms
    if ticker:
        search_terms.append(ticker)
    if title:
        # Add full title for exact match
        search_terms.append(title)
        
        # Also add individual words from title (excluding common words)
        exclude_words = {'corp', 'corporation', 'inc', 'incorporated', 'co', 'company', 'ltd', 'limited', 'the', 'and', 'of', 'llc'}
        for word in title.split():
            if len(word) > 1 and word.lower() not in exclude_words:
                search_terms.append(word)

# Remove duplicates and sort by length (longer terms first for better matching)
search_terms = list(set(search_terms))
search_terms.sort(key=len, reverse=True)

# Filter the subreddits file
matched_count = 0
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        try:
            data = json.loads(line.strip())
            
            # Extract fields to search in
            fields = [
                data.get('display_name', ''),
                data.get('title', ''),
                data.get('description', ''),
                data.get('public_description', ''),
                data.get('url', '')
            ]
            
            # Combine all fields into one text for searching
            combined_text = ' '.join(str(field or '').lower() for field in fields)
            
            # Check if any search term is in the combined text
            for term in search_terms:
                # Use word boundary for more accurate matching
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, combined_text, re.IGNORECASE):
                    json.dump(data, outfile)
                    outfile.write('\n')
                    matched_count += 1
                    break
                    
        except (json.JSONDecodeError, Exception):
            continue

