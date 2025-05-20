##This script was created to find all forums related to specific assets after cleaning up all of the subreddits - all 20M subreddits have been filtered down to 50000 prior to this
##This was done by removing all nsfw and private subreddits, and removing all subreddits with less than 3000 comments and 1500 posts.
##This script utilized the google genai api with the model flash 2.0 and a custom was created after some initial testing of results 

import os, json, time
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError, ServerError

# --- Configuration ---
INPUT_FILE  = "subreddits_list/pre_processed_forums_AI.jsonl"
OUTPUT_FILE = "subreddits_list/asset_specific_subreddits.csv"
BATCH_SIZE  = 100
SLEEP_SECONDS = 1

# --- Initialize the GenAI client ---
def init_client():
    return genai.Client(api_key="putapikeyhere")

# --- Schema Definition ---
class SubredditResult(BaseModel):
    display_name_prefixed: str
    is_asset_specific    : bool
    identified_asset     : Optional[str]
    confidence_score     : float

# --- Helper Functions (UNCHANGED) ------------------------------------------
def build_prompt(subreddits: List[dict]) -> tuple:
    system_instruction = (
        # ------------- entire system instruction text UNCHANGED -------------
        "You are an expert in identifying subreddits that are specifically and primarily dedicated to the discussion of a single financial asset.\n"
        "IMPORTANT: Financial assets are instruments that can be traded on a market.\n"
        "Examples of assets with subreddits include individual stocks (e.g., TSLA) or specific cryptocurrencies (e.g., Bitcoin). Exclude commodities such as (e.g., Gold).\n"
        "The data is 50000 of the largest subreddits. This will be handed in batches of 100 at a time. - meaning there should be 100 results per batch\n"
        "!IMPORTANT: Not all batches will include subreddits that relate to a financial asset. If none of the inputs in the batch relate to a financial asset, do not interpret this system instruction in another way.\n"
        "Celebrity names, topics or general items do not constitute as financial assets or single-instrument-focused assets.\n"
        "\n"
        "EXPLICIT EXAMPLES:\n"
        "- r/Bitcoin, true, Bitcoin, 1.0 (cryptocurrency)\n"
        "- r/AgameofthronesLCG, false, null, 0.0 (entertainment/game)\n"
        "- r/Marijuana, false, null, 0.0 (recreational drug)\n"
        "- r/SNP, false, null, 0.0 (scottish national party)\n"
        "- r/Superstonk, True, GME, 1.0 (stock)\n"
        "\n"
        "CRITERIA:\n"
        "Primary Asset Focus: The subreddit name, title, description or public description must clearly focus on one asset.\n"
        "EXCLUDE GENERICS: Broad-market or multi-asset communities (like stocks, crypto, investing).\n"
        "Evaluate each subreddit independently. You will be given a list of 100 subreddits per batch with display_name_prefixed, title, description and public description. Evaluate each subreddit independently.\n"
        "Asset Identification: If a subreddit is identified, attempt to extract the common name or ticker symbol of the specific asset (e.g., TSLA, Bitcoin, GME, XAU).\n"
        "Return exactly ONE output per subreddit that is strictly related to ONE financial asset. If the subreddit discusses multiple financial assets do not label this subreddit as true for identified asset.\n"
        "Return one schema/output per subreddit irregardless of results, e.g., if false - return false for is_asset_specific and null for identified_asset and confidence_score.\n"
        "INPUT: JSON array of objects with display_name_prefixed, title, description, public_description.\n"
        "OUTPUT: JSON array matching schema of SubredditResult (display_name_prefixed, is_asset_specific, identified_asset, confidence_score)."
    )
    return system_instruction, json.dumps(subreddits, ensure_ascii=False)

# --- API Call WITH RETRY ONLY ----------------------------------------------
def call_api(client, sys_instr: str, user_json: str,
             retries: int = 5, backoff: float = 2.0) -> List[SubredditResult]:
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[user_json],
                config=types.GenerateContentConfig(
                    system_instruction=sys_instr,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "array",
                        "items": SubredditResult.model_json_schema(),
                    },
                )
            )
            return resp.parsed or []
        except (ServerError, APIError) as e:
            if getattr(e, "status_code", 500) in (500, 502, 503, 504, 429):
                wait = backoff * (2 ** attempt)
                print(f"⚠️  {e.status_code} – retry {attempt+1}/{retries} in {wait}s")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Exceeded retry limit")

# --- Main Processing (UNCHANGED EXCEPT FOR CALL) ---------------------------
def main():
    client = init_client()

    processed = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as fout:
            processed = sum(1 for _ in fout) - 1

    mode = 'a' if processed else 'w'
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, mode, encoding='utf-8') as outfile:

        if not processed:
            outfile.write("display_name_prefixed,is_asset_specific,identified_asset,confidence_score\n")

        for _ in range(processed):
            next(infile, None)

        batch, total, batch_no = [], processed, 0

        for line in infile:
            total += 1
            data = json.loads(line)
            batch.append({
                'display_name_prefixed': data.get('display_name_prefixed'),
                'title'               : data.get('title'),
                'description'         : data.get('description'),
                'public_description'  : data.get('public_description')
            })

            if len(batch) >= BATCH_SIZE:
                batch_no += 1
                print(f"Batch {batch_no}: processing {BATCH_SIZE} entries")
                sys_i, user_j = build_prompt(batch)
                results = call_api(client, sys_i, user_j)

                if not results:
                    print("❌ No results returned for this batch.")
                else:
                    for r in results:
                        outfile.write(
                            f"{r['display_name_prefixed']},"
                            f"{r['is_asset_specific']},"
                            f"{r.get('identified_asset', '')},"
                            f"{r['confidence_score']}\n"
                        )
                    print(f"✅ Successfully processed {len(results)} entries.")

                batch = []
                time.sleep(SLEEP_SECONDS)

        if batch:
            batch_no += 1
            print(f"Final batch {batch_no}: processing {len(batch)} entries")
            sys_i, user_j = build_prompt(batch)
            results = call_api(client, sys_i, user_j)

            if not results:
                print("❌ No results returned for final batch.")
            else:
                for r in results:
                    outfile.write(
                        f"{r['display_name_prefixed']},"
                        f"{r['is_asset_specific']},"
                        f"{r.get('identified_asset', '')},"
                        f"{r['confidence_score']}\n"
                    )
                print(f"✅ Successfully processed final {len(results)} entries.")

    print(f"Done: Processed {total} lines in {batch_no} batches.")

if __name__ == '__main__':
    main()
