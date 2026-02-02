import requests
import json
import time

def check_one_product(product_id):
    store_id = "11766" 
    api_url = f"https://www.zara.com/itxrest/1/catalog/store/{store_id}/product/id/{product_id}/availability"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.zara.com/tr/tr/',
        'Accept': 'application/json, text/plain, */*'
    }

    print(f"Checking URL: {api_url}")
    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print("Response Response:")
            print(json.dumps(data, indent=2))
            with open("api_result.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    # Product ID from user: 464648894
    check_one_product("464648894")

