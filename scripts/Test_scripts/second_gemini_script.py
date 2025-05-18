import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

# --- Configuration ---
INPUT_FILE = "subreddits_list/pre_processed_forums_AI.jsonl"    # Input JSONL file (50k lines)
OUTPUT_FILE = "subreddits_list/asset_specific_subreddits.csv"   # Output CSV file
BATCH_SIZE = 500                                 # Number of entries per API call
SLEEP_SECONDS = 2                                # Pause between batches to respect rate limits

# Initialize the GenAI client
def init_client():
    api_key = "AIzaSyCK5ehdPfU_yV0juuYJNT2I_e67zkqGU5s"
    if not api_key:
        raise EnvironmentError("Please set FLASH_API_KEY as an environment variable.")
    return genai.Client(api_key=api_key)

# --- Schema Definition ---
class SubredditResult(BaseModel):
    display_name_prefixed: str
    is_asset_specific: bool
    identified_asset: Optional[str]
    confidence_score: float

# --- Helper Functions ---
def build_prompt(subreddits: List[dict]) -> List[dict]:
    # Detailed system instructions
    contents = (
        "You are an expert AI assistant specializing in identifying Reddit subreddits "
        "that are specifically and primarily dedicated to the discussion of a single financial asset.\n"
        "Examples include individual stocks (e.g., TSLA), specific cryptocurrencies (e.g., Bitcoin), "
        "or singular tradable instruments (e.g., Gold).\n\n"
        "CRITERIA:\n"
        "1. PRIMARY ASSET FOCUS: The subreddit name, title, description, or public_description must clearly focus on one asset.\n"
        "2. EXCLUDE GENERICS: Do not mark broad-market or multi-asset communities (like 'stocks', 'crypto', 'investing') unless they explicitly name one asset.\n\n"
        "3. ASSET IDENTIFICATION: If a subreddit is identified, attempt to extract the common name or ticker "
        "   symbol of the specific asset (e.g., 'TSLA', 'Bitcoin', 'GME', 'XAU').\n\n"
        "INPUT: JSON array of objects with id, display_name_prefixed, title, description, public_description.\n"
        "OUTPUT: JSON array matching schema of SubredditResult ( display_name_prefixed, is_asset_specific, identified_asset, confidence_score)."
    )
    user_msg = json.dumps(subreddits, ensure_ascii=False)
    return [
        {"role": "system", "content": contents},
        {"role": "user",   "content": user_msg}
    ]

# --- API Call ---
def call_api(client, contents: List[dict]) -> List[SubredditResult]:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=List[SubredditResult],
            max_output_tokens=8192,
        )
    )
    # response.parsed is a list[SubredditResult]
    return response.parsed or []

# --- Main Processing ---
def main():
    client = init_client()

    # Determine resume offset
    processed = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as fout:
            processed = sum(1 for _ in fout) - 1  # subtract header
        print(f"Resuming at entry #{processed + 1}")

    batch: List[dict] = []
    total_processed = 0
    batch_count = 0

    mode = 'a' if processed else 'w'
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, mode, encoding='utf-8') as outfile:

        # write header if fresh
        if not processed:
            outfile.write("display_name_prefixed,is_asset_specific,identified_asset,confidence_score\n")
        # skip processed lines
        for _ in range(processed):
            next(infile, None)
        total_processed = processed

        for line in infile:
            total_processed += 1
            data = json.loads(line)
            batch.append({
                'display_name_prefixed': data.get('display_name_prefixed'),
                'title': data.get('title'),
                'description': data.get('description'),
                'public_description': data.get('public_description')
            })

            if len(batch) >= BATCH_SIZE:
                batch_count += 1
                start = total_processed - len(batch) + 1
                end = total_processed
                print(f"Batch {batch_count}: processing lines {start}-{end}")
                msgs = build_prompt(batch)
                results = call_api(client, msgs)
                for r in results:
                    outfile.write(
                        f"{r.display_name_prefixed},"
                        f"{r.is_asset_specific},"
                        f"{r.identified_asset or ''},"
                        f"{r.confidence_score}\n"
                    )
                batch = []
                print(f"Sleeping {SLEEP_SECONDS}s...")
                break
                time.sleep(SLEEP_SECONDS)

        # final batch
        if batch:
            batch_count += 1
            start = total_processed - len(batch) + 1
            end = total_processed
            print(f"Final batch {batch_count}: lines {start}-{end}")
            msgs = build_prompt(batch)
            results = call_api(client, msgs)
            for r in results:
                outfile.write(
                    f"{r.display_name_prefixed},"
                    f"{r.is_asset_specific},"
                    f"{r.identified_asset or ''},"
                    f"{r.confidence_score}\n"
                )

    print(f"Done: {total_processed} lines in {batch_count} batches.")

if __name__ == '__main__':
    main()

