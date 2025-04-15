import requests
import re
import json
from datetime import datetime, timedelta

# NOTE: ScraperAPI charges 25 credits per Google search request
# This script makes 5 requests, totaling 125 credits
# For more information on pricing, see: https://www.scraperapi.com/pricing

def get_google_results_count(date, api_key):
    """
    Get the number of Google search results for "$SNDL stock" 
    for a specific date.
    """
    # Format the date as M/D/YYYY for Google search
    formatted_date = date.strftime("%-m/%-d/%Y")
    
    # Construct the search URL with date range
    query = "$SNDL stock"
    params = {
        'api_key': api_key,
        'url': f'https://www.google.com/search?q={query}&tbs=cdr:1,cd_min:{formatted_date},cd_max:{formatted_date}'
    }
    
    # Send the request through ScraperAPI
    response = requests.get('https://api.scraperapi.com', params=params)
    
    if response.status_code == 200:
        # Extract the result count using regex
        result_pattern = r'About ([0-9,]+) results'
        match = re.search(result_pattern, response.text)
        
        if match:
            # Remove commas and convert to integer
            result_count = match.group(1).replace(',', '')
            return date.strftime("%Y-%m-%d"), result_count
    
    return date.strftime("%Y-%m-%d"), "N/A"

def main():
    # Your API key
    api_key = "b4fc87b8eee815ebafc244d781007b4c"
    
    # Specific date range: January 1-5, 2021
    start_date = datetime(2021, 1, 1)
    
    # Get results for each individual day
    results = []
    for i in range(5):
        current_date = start_date + timedelta(days=i)
        date_str, count = get_google_results_count(current_date, api_key)
        results.append({
            "date": date_str,
            "result_count": count
        })
        # No sleep between requests
    
    # Print the results
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
