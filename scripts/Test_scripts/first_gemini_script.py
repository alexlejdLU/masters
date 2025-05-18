from google import genai

client = genai.Client(api_key="AIzaSyCK5ehdPfU_yV0juuYJNT2I_e67zkqGU5s")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)

from google import genai
import json
import os
import time
# You'll need a library to make HTTP requests, e.g., 'requests'
# pip install requests
import requests # Assuming you'll use requests for the API call

# --- Configuration ---
INPUT_FILE = "subreddits_list/pre_processed_forums_AI.jsonl"  # Your 50,000 line JSON Lines file
OUTPUT_FILE = "subreddits_list/asset_specific_subreddits.csv"
# FLASH_API_KEY = os.environ.get("FLASH_API_KEY") # Recommended to use environment variables
client = genai.Client(api_key="AIzaSyCK5ehdPfU_yV0juuYJNT2I_e67zkqGU5s")

FLASH_API_KEY = "YOUR_FLASH_2_0_API_KEY" # Replace with your actual key
FLASH_API_ENDPOINT = "YOUR_FLASH_2_0_API_ENDPOINT" # Replace with the actual API endpoint


BATCH_SIZE = 500 # Number of subreddit entries to send per API call

# --- Helper Functions ---

def construct_prompt_for_batch(subreddit_batch_data):

    system_message = (
        "You are an expert AI assistant specializing in identifying Reddit subreddits "
        "that are *specifically and primarily* dedicated to the discussion of a single "
        "financial asset. Examples of such assets include individual stocks (e.g., TSLA, AAPL), "
        "specific cryptocurrencies (e.g., Bitcoin, Ethereum, DOGE), or other singular, "
        "tradable financial instruments (e.g., Gold, a specific ETF like SPY if the sub is *only* about SPY).\n\n"
        "CRITERIA:\n"
        "1. PRIMARY FOCUS: The subreddit's name, title, description, and public description must "
        "   clearly indicate a primary focus on *one specific asset*.\n"
        "2. AVOID GENERAL SUBREDDITS: Do NOT identify subreddits with general themes like 'investing', "
        "   'stocks', 'daytrading', 'crypto', 'personal finance', 'FIRE', or broad market discussions, "
        "   *unless* their name or description unequivocally ties them to a single, specific asset "
        "   (e.g., a subreddit named 'r/OnlyTeslaStockTalk' would be a match, but 'r/StockMarket' is not).\n"
        "INPUT FORMAT:\n"
        "You will receive a JSON array of subreddit objects. Each object contains: "
        "'id', 'description', 'display_name', 'display_name_prefixed', 'public_description', 'title', 'url'.\n\n"
        "OUTPUT FORMAT:\n"
        "Return a VALID JSON array of objects. Each object in the array should represent a subreddit "
        "you've identified as meeting the criteria. For each identified subreddit, include:\n"
        "- 'id': (string) The original ID of the subreddit.\n"
        "- 'display_name_prefixed': (string) The prefixed display name (e.g., 'r/Bitcoin').\n"
        "- 'is_asset_specific': (boolean) true if it meets the criteria, false otherwise.\n"
        "- 'identified_asset': (string) The common name or ticker of the specific asset if identified (e.g., 'Bitcoin', 'TSLA'). Null or empty string if not applicable or not asset-specific.\n"
        "- 'confidence_score': (float) A score from 0.0 to 1.0 indicating your confidence in this assessment. 1.0 for high confidence.\n"
        "- 'reasoning': (string) A brief explanation for your decision, especially why you believe it is (or is not) asset-specific.\n\n"
        "If a subreddit in the batch does NOT meet the criteria, include it in the output array with 'is_asset_specific': false, and appropriate values for other fields (e.g., confidence_score reflecting low confidence in it being asset-specific).\n"
        "Ensure your entire response is ONLY the JSON array, nothing else before or after."
    )

    # This is a common structure for chat-based models. Adjust if flash 2.0 uses a different format.
    # Some models prefer a single long string prompt.
    prompt_payload = {
        "model": "gemini-2.0-flash", # Replace with actual model name if needed
        "messages": [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    "Please analyze the following batch of subreddit data and identify those "
                    "that are specifically focused on a single financial asset, according to the criteria "
                    "and output format I provided.\n\n"
                    "Subreddit Data Batch:\n"
                    f"{json.dumps(subreddit_batch_data, indent=2)}"
                )
            }
        ],
        "max_tokens": 4000, # Max tokens for the *response*. Adjust as needed.
        "temperature": 0.1 # Low temperature for more deterministic, factual output
        # Add other parameters like 'top_p' if supported and desired
    }
    return prompt_payload

def call_flash_2_0_api(payload):
    """
    Makes the API call to Flash 2.0.
    THIS IS A MOCKUP. You need to implement the actual API call.
    """
    if not FLASH_API_KEY or FLASH_API_KEY == "YOUR_FLASH_2_0_API_KEY":
        print("ERROR: FLASH_API_KEY not set or is placeholder.")
        # Simulate a response structure for testing without a real API
        print("--- SIMULATING API CALL ---")
        mock_response_data = []
        # Let's assume the payload has messages and the user content contains the actual data
        try:
            batch_data_str = payload["messages"][1]["content"].split("Subreddit Data Batch:\n")[1]
            batch_data = json.loads(batch_data_str)
            for item in batch_data:
                if "bitcoin" in item.get("display_name","").lower() or \
                   "tsla" in item.get("display_name","").lower() or \
                   "gme" in item.get("display_name","").lower():
                    asset = "Bitcoin" if "bitcoin" in item.get("display_name","").lower() else \
                            "TSLA" if "tsla" in item.get("display_name","").lower() else "GME"
                    mock_response_data.append({
                        "id": item["id"],
                        "display_name_prefixed": item["display_name_prefixed"],
                        "is_asset_specific": True,
                        "identified_asset": asset,
                        "confidence_score": 0.95,
                        "reasoning": f"Simulated: Display name {item['display_name_prefixed']} suggests focus on {asset}."
                    })
                else:
                    mock_response_data.append({
                        "id": item["id"],
                        "display_name_prefixed": item["display_name_prefixed"],
                        "is_asset_specific": False,
                        "identified_asset": None,
                        "confidence_score": 0.1,
                        "reasoning": "Simulated: Does not appear to be asset-specific based on name."
                    })
            return json.dumps(mock_response_data) # API often returns a string response
        except Exception as e:
            print(f"Error in mock data generation: {e}")
            return "[]" # Empty JSON array on error

    headers = {
        "Authorization": f"Bearer {FLASH_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(FLASH_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        # Assuming the API directly returns the JSON content string in the response body.
        # Some APIs wrap it, e.g., response.json()['choices'][0]['message']['content']
        return response.text # Or response.json() if it's already parsed
    except requests.exceptions.RequestException as e:
        print(f"API Call Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None # Indicate failure

# --- Main Processing Logic ---
def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        return

    print(f"Starting processing of '{INPUT_FILE}'...")
    print(f"Batch size: {BATCH_SIZE} entries per API call.")
    print(f"Output will be written to '{OUTPUT_FILE}'.")

    all_identified_subreddits = []
    batch_data = []
    line_count = 0
    batch_count = 0

    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:

        # Write CSV Header
        outfile.write("id,display_name_prefixed,is_asset_specific,identified_asset,confidence_score,reasoning\n")

        for line in infile:
            line_count += 1
            try:
                subreddit_info = json.loads(line)
                # Ensure all required fields are present for the model (as per your list)
                # You might want to add default values if some fields can be missing in your JSONL
                required_fields = ["id", "description", "display_name", "display_name_prefixed", "public_description", "title", "url"]
                # For simplicity, we assume all fields are present. Add validation if needed.
                selected_data = {key: subreddit_info.get(key) for key in required_fields}
                batch_data.append(selected_data)
            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed JSON line at line number {line_count}")
                continue

            if len(batch_data) >= BATCH_SIZE:
                batch_count += 1
                print(f"\nProcessing batch {batch_count} (lines {line_count-BATCH_SIZE+1}-{line_count})...")
                
                api_payload = construct_prompt_for_batch(batch_data)
                # print(f"--- Prompt Payload for Batch {batch_count} ---")
                # print(json.dumps(api_payload, indent=2)) # For debugging the prompt
                # print("--- End Prompt Payload ---")

                api_response_str = call_flash_2_0_api(api_payload)

                if api_response_str:
                    try:
                        # The model should return a JSON string which is an array of objects
                        results = json.loads(api_response_str)
                        if not isinstance(results, list):
                            print(f"Error: API response for batch {batch_count} was not a JSON list. Response: {api_response_str[:200]}...")
                        else:
                            print(f"Batch {batch_count}: Received {len(results)} results from API.")
                            for item in results:
                                # Write to CSV
                                outfile.write(
                                    f"\"{item.get('id', '')}\","
                                    f"\"{item.get('display_name_prefixed', '')}\","
                                    f"{item.get('is_asset_specific', False)},"
                                    f"\"{item.get('identified_asset', '')}\","
                                    f"{item.get('confidence_score', 0.0)},"
                                    f"\"{str(item.get('reasoning', '')).replace('\"', '\"\"')}\"\n" # Escape quotes for CSV
                                )
                                if item.get('is_asset_specific'):
                                    all_identified_subreddits.append(item)
                    except json.JSONDecodeError:
                        print(f"Error: Could not decode JSON response from API for batch {batch_count}. Response: {api_response_str[:500]}...")
                else:
                    print(f"Error: No response or failed API call for batch {batch_count}.")

                batch_data = [] # Reset batch
                print(f"Batch {batch_count} processed. Sleeping for a bit to respect rate limits...")
                time.sleep(2) # IMPORTANT: Adjust based on API rate limits

        # Process any remaining data in the last batch
        if batch_data:
            batch_count += 1
            print(f"\nProcessing final batch {batch_count} (lines {line_count-len(batch_data)+1}-{line_count})...")
            api_payload = construct_prompt_for_batch(batch_data)
            api_response_str = call_flash_2_0_api(api_payload)
            if api_response_str:
                try:
                    results = json.loads(api_response_str)
                    if not isinstance(results, list):
                         print(f"Error: API response for final batch {batch_count} was not a JSON list. Response: {api_response_str[:200]}...")
                    else:
                        print(f"Final Batch {batch_count}: Received {len(results)} results from API.")
                        for item in results:
                             outfile.write(
                                f"\"{item.get('id', '')}\","
                                f"\"{item.get('display_name_prefixed', '')}\","
                                f"{item.get('is_asset_specific', False)},"
                                f"\"{item.get('identified_asset', '')}\","
                                f"{item.get('confidence_score', 0.0)},"
                                f"\"{str(item.get('reasoning', '')).replace('\"', '\"\"')}\"\n"
                            )
                             if item.get('is_asset_specific'):
                                all_identified_subreddits.append(item)
                except json.JSONDecodeError:
                    print(f"Error: Could not decode JSON response from API for final batch. Response: {api_response_str[:500]}...")
            else:
                print(f"Error: No response or failed API call for final batch {batch_count}.")

    print(f"\n--- Processing Complete ---")
    print(f"Total lines processed: {line_count}")
    print(f"Total batches sent to API: {batch_count}")
    asset_specific_count = sum(1 for item in all_identified_subreddits if item.get('is_asset_specific'))
    print(f"Total asset-specific subreddits identified (across all batches): {asset_specific_count}")
    print(f"Results saved to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    # --- Create a dummy input file for testing ---
    if not os.path.exists(INPUT_FILE):
        print(f"Creating dummy input file: {INPUT_FILE}")
        dummy_data = [
            {"id": "t1", "description": "All about Tesla stock and company news.", "display_name": "TSLA", "display_name_prefixed": "r/TSLA", "public_description": "Tesla motors discussion.", "title": "Tesla Motors Stock", "url": "/r/TSLA/"},
            {"id": "t2", "description": "Discussion of Bitcoin, the original cryptocurrency.", "display_name": "Bitcoin", "display_name_prefixed": "r/Bitcoin", "public_description": "Bitcoin news and price talk.", "title": "Bitcoin", "url": "/r/Bitcoin/"},
            {"id": "t3", "description": "General investing strategies and market analysis.", "display_name": "investing", "display_name_prefixed": "r/investing", "public_description": "Learn about investing.", "title": "Investing", "url": "/r/investing/"},
            {"id": "t4", "description": "Memes and fun about GameStop stock.", "display_name": "GME", "display_name_prefixed": "r/GME", "public_description": "To the moon! GME discussion.", "title": "GameStop (GME)", "url": "/r/GME/"},
            {"id": "t5", "description": "Cooking recipes and tips.", "display_name": "cooking", "display_name_prefixed": "r/cooking", "public_description": "Share your favorite recipes.", "title": "Cooking", "url": "/r/cooking/"}
        ]
        with open(INPUT_FILE, 'w') as f:
            for item in dummy_data * 200: # Make it a bit larger for batching demo
                f.write(json.dumps(item) + '\n')
    
    # --- Run main logic ---
    main()