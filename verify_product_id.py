import requests
import re
import json

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Fetching HTML: {url}")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    
    # Need to find productId
    # Patterns to look for:
    # "productId": 500041235
    # "product":{"id":500041235
    
    match = re.search(r'"product":{"id":(\d+)', r.text)
    if match:
        print(f"Found Product ID (Method 1): {match.group(1)}")
    else:
        # Try generic match
        match2 = re.search(r'"productId":(\d+)', r.text)
        if match2:
             print(f"Found Product ID (Method 2): {match2.group(1)}")
        else:
             print("Could not find Product ID.")

    # Also check for storeId if possible, often in window.zara.dataLayer or similar
    
except Exception as e:
    print(f"Error: {e}")
