import requests
import json

# URL v1=500041235
product_id = "500041235"
store_id = "11766" # Assuming TR store ID is constant or we can hardcode for now

url = f"https://www.zara.com/itxrest/1/catalog/store/{store_id}/product/id/{product_id}/availability"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.zara.com/tr/en/',
    'Accept': 'application/json, text/plain, */*'
}

print(f"Testing URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! Response JSON:")
        print(response.text[:500])
    else:
        print("Blocked or failed.")
        print(response.text[:200])

except Exception as e:
    print(f"Error: {e}")
