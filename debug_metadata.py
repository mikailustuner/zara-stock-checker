from scraper import fetch_product_metadata
import time

print("--- Starting Metadata Debug ---")
url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"
print(f"Target URL: {url}")

start = time.time()
print("Calling fetch_product_metadata... (This should open a browser)")

try:
    meta = fetch_product_metadata(url)
    elapsed = time.time() - start
    print(f"Function returned in {elapsed:.2f} seconds.")
    
    if meta:
        print("SUCCESS! Data received:")
        print(f"Product ID: {meta['product_id']}")
        print(f"Size Map: {meta['size_map']}")
    else:
        print("FAILED: Returned None.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")

print("--- End Debug ---")
