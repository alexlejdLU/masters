import pandas as pd
import csv
from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification

# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Model roberta performance - sorta meh 
# tokenizer = AutoTokenizer.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
# model = AutoModelForSequenceClassification.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

# Model roberta performance - sorta meh 
# model = BertForSequenceClassification.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis",num_labels=3)
# tokenizer = BertTokenizer.from_pretrained("ahmedrachid/FinancialBERT-Sentiment-Analysis")


# Path to the CSV file
csv_file = "data_raw/SNDL/sndl_posts_utc_title.csv"

# Create a sentiment analysis pipeline with FinTwitBERT
nlp = pipeline(
    "sentiment-analysis",
    model="StephanAkkerman/FinTwitBERT-sentiment",
)

# Read the first 100 rows from the CSV file
posts = []
try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Skip header if it exists
        next(reader, None)
        count = 0
        for row in reader:
            if count >= 5000:
                break
            if len(row) >= 2:  # Make sure row has enough columns
                utc_timestamp = row[0]
                title = row[1]
                datetime = row[2] if len(row) > 2 else ""
                posts.append((utc_timestamp, title, datetime))
                count += 1
except Exception as e:
    print(f"Error reading CSV: {e}")

# Perform sentiment analysis on each post
results = []
for utc, title, datetime in posts:
    try:
        sentiment = nlp(title)[0]
        results.append({
            'utc': utc,
            'title': title,
            'datetime': datetime,
            'sentiment': sentiment['label'],
            'score': sentiment['score']
        })
        # Print the post and its sentiment
        print(f"{utc},{title},{datetime}")
        print(f"Sentiment: {sentiment['label']} (Score: {sentiment['score']:.4f})")
        print("-" * 80)
    except Exception as e:
        print(f"Error analyzing '{title}': {e}")

# Calculate overall sentiment statistics
bullish_count = sum(1 for r in results if r['sentiment'] == 'BULLISH')
bearish_count = sum(1 for r in results if r['sentiment'] == 'BEARISH')
neutral_count = sum(1 for r in results if r['sentiment'] == 'NEUTRAL')

print("\nSentiment Analysis Summary:")
print(f"Total posts analyzed: {len(results)}")
print(f"BULLISH: {bullish_count} ({bullish_count/len(results)*100:.1f}%)")
print(f"BEARISH: {bearish_count} ({bearish_count/len(results)*100:.1f}%)")
print(f"NEUTRAL: {neutral_count} ({neutral_count/len(results)*100:.1f}%)") 


######## to write to csv for the above thingy

# import pandas as pd
# import json
# from datetime import datetime


# jsonl_file_posts = "data_raw/SNDL/r_sndl_comments.jsonl"

# # Extract only created_utc and title from posts
# comments_data = []

# with open(jsonl_file_posts, 'r') as f:
#     for line in f:
#         obj = json.loads(line)
#         created_utc = obj.get('created_utc')
#         body = obj.get('body')
#         if created_utc and body:
#             comments_data.append({
#                 'created_utc': created_utc,
#                 'body': body
#             })

# # Create DataFrame with the data
# df_comments = pd.DataFrame(comments_data)

# # Convert UTC timestamp to datetime
# df_comments['datetime'] = pd.to_datetime(df_comments['created_utc'], unit='s')

# # Display the results
# print(df_comments.head())
# print(f"Total number of comments: {len(df_comments)}")

# # Save to CSV for easy access
# df_comments.to_csv("data_raw/SNDL/sndl_comments_utc_title.csv", index=False)
