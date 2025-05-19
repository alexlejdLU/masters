import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types


# --- Configuration ---
INPUT_FILE = "subreddits_list/pre_processed_forums_AI.jsonl"
OUTPUT_FILE = "subreddits_list/asset_specific_subreddits.csv"
BATCH_SIZE = 500
SLEEP_SECONDS = 2

# Initialize the GenAI client
def init_client():
    api_key = "AIzaSyCK5ehdPfU_yV0juuYJNT2I_e67zkqGU5s"
    if not api_key:
        raise EnvironmentError("Set API key")
    return genai.Client(api_key=api_key)

# --- Schema Definition ---
class SubredditResult(BaseModel):
    display_name_prefixed: str
    is_asset_specific: bool
    identified_asset: Optional[str]
    confidence_score: float

# --- Helper Functions ---
def build_prompt(subreddits: List[dict]) -> str:
    prompt = (
  "You are an expert in identifying subreddits that are specifically and primarily dedicated to the discussion of a single financial asset.\n"
    "IMPORTANT: Financial assets are instruments that can be traded on a market.\n"
    "Examples of assets with subreddits include individual stocks (e.g., TSLA) or specific cryptocurrencies (e.g., Bitcoin). Exclude commodities such as (e.g., Gold).\n"
    "The data is 50000 of the largest subreddits. This will be handed in batches of 500 at a time.\n"
    "!IMPORTANT: Not all batches will include subreddits that relate to a financial asset. If none of the inputs in the batch relate to a financial asset, do not interpret this system instruction in another way.\n"
    "Celebrity names, topics or general items do not constitute as financial assets or single-instrument-focused assets.\n"
    "\n"
    "EXPLICIT EXAMPLES:\n"
    "- r/Bitcoin, true, Bitcoin, 0.95 (cryptocurrency)\n"
    "- r/Madonna, false, null, 0.0 (celebrity)\n"
    "- r/Marijuana, false, null, 0.0 (recreational drug)\n"
    "- r/MadnessCombat, false, null, 0.0 (entertainment/game)\n"
    "\n"
    "CRITERIA:\n"
    "Primary Asset Focus: The subreddit name, title, description or public description must clearly focus on one asset.\n"
    "EXCLUDE GENERICS: Broad-market or multi-asset communities (like stocks, crypto, investing).\n"
    "Evaluate each subreddit independently. You will be given a list of 500 subreddits per batch with display_name_prefixed, title, description and public description. Evaluate each subreddit independently.\n"
    "Asset Identification: If a subreddit is identified, attempt to extract the common name or ticker symbol of the specific asset (e.g., TSLA, Bitcoin, GME, XAU).\n"
    "Return exactly ONE output per subreddit that is strictly related to ONE financial asset. If the subreddit discusses multiple financial assets do not label this subreddit as true for identified asset.\n"
    "INPUT: JSON array of objects with display_name_prefixed, title, description, public_description.\n"
    "OUTPUT: JSON array matching schema of SubredditResult (display_name_prefixed, is_asset_specific, identified_asset, confidence_score)."
        f"Subreddits: {json.dumps(subreddits, ensure_ascii=False)}"
    )
    return prompt

# --- API Call ---
def call_api(client, prompt: str) -> List[SubredditResult]:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type= "application/json",
            response_schema= {"type": "array", "items": SubredditResult.model_json_schema()},
        )
    )
    return response.parsed or []

# --- Main Processing ---
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

        batch = []
        total_processed = processed
        batch_count = 0

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
                print(f"Batch {batch_count}: processing {len(batch)} entries")
                prompt = build_prompt(batch)
                results = call_api(client, prompt)
                for r in results:
                    outfile.write(
                        f"{r['display_name_prefixed']},"
                        f"{r['is_asset_specific']},"
                        f"{r.get('identified_asset', '')},"
                        f"{r['confidence_score']}\n"
                    )
                batch = []
                time.sleep(SLEEP_SECONDS)

        if batch:
            batch_count += 1
            print(f"Final batch {batch_count}: processing {len(batch)} entries")
            prompt = build_prompt(batch)
            results = call_api(client, prompt)
            for r in results:
                outfile.write(
                    f"{r['display_name_prefixed']},"
                    f"{r['is_asset_specific']},"
                    f"{r.get('identified_asset', '')},"
                    f"{r['confidence_score']}\n"
                )

    print(f"Done: Processed {total_processed} lines in {batch_count} batches.")

if __name__ == '__main__':
    main()
########## NEW SCRIPT #######
import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types

# --- Configuration ---
INPUT_FILE = "subreddits_list/pre_processed_forums_AI.jsonl"
OUTPUT_FILE = "subreddits_list/asset_specific_subreddits.csv"
BATCH_SIZE = 100  
SLEEP_SECONDS = 1

# --- Initialize the GenAI client ---
def init_client():
    api_key = "AIzaSyCe3XFJZNJtJWwYCXmCO8scjc1HPV9zS7A"
    if not api_key:
        raise EnvironmentError("Set API key")
    return genai.Client(api_key=api_key)

# --- Schema Definition ---
class SubredditResult(BaseModel):
    display_name_prefixed: str
    is_asset_specific: bool
    identified_asset: Optional[str]
    confidence_score: float

# --- Helper Functions ---
def build_prompt(subreddits: List[dict]) -> tuple:
    system_instruction = (
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

    user_content = json.dumps(subreddits, ensure_ascii=False)
    return system_instruction, user_content

# --- API Call with explicit debugging ---
def call_api(client, system_instruction: str, user_content: str) -> List[SubredditResult]:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[user_content],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=8192,
            response_mime_type="application/json",
            response_schema={
                "type": "array",
                "items": SubredditResult.model_json_schema(),
            },
        )
    )

    if not response.parsed:
        print("❌ Gemini returned an empty parsed response. Raw response:")
        print(response.text)
        return []

    return response.parsed

# --- Main Processing ---
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

        batch = []
        total_processed = processed
        batch_count = 0

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
                print(f"Batch {batch_count}: processing {len(batch)} entries")
                system_instruction, user_content = build_prompt(batch)
                results = call_api(client, system_instruction, user_content)

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
            batch_count += 1
            print(f"Final batch {batch_count}: processing {len(batch)} entries")
            system_instruction, user_content = build_prompt(batch)
            results = call_api(client, system_instruction, user_content)

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

    print(f"Done: Processed {total_processed} lines in {batch_count} batches.")

if __name__ == '__main__':
    main()
