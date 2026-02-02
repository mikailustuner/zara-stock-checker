import requests
import json

url = "https://www.zara.com/itxrest/1/catalog/store/11766/product/id/500265159/availability"

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
