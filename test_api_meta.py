import requests
import json

# Product ID 500041235
product_id = "500041235"
store_id = "11766" 

# Try to get metadata (remove /availability)
url_meta = f"https://www.zara.com/itxrest/1/catalog/store/{store_id}/product/id/{product_id}" # ?languageId=-1 maybe?

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.zara.com/tr/en/',
    'Accept': 'application/json, text/plain, */*'
}

print(f"Testing Meta URL: {url_meta}")

try:
    response = requests.get(url_meta, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Response JSON:")
        params = response.json()
        # listing keys
        print(params.keys())
        if 'detail' in params:
             print("Found detail!")
             detail = params['detail']
             if 'colors' in detail:
                 # Check first color sizes
                 print("Found colors!")
    else:
        print("Blocked or failed.")
        print(response.text[:200])

except Exception as e:
    print(f"Error: {e}")
