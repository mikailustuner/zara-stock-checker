from scraper import check_stock_v2

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

print("--- Test 1: Generic Stock Check ---")
in_stock, msg, screen = check_stock_v2(url)
print(f"Result: {in_stock}, Msg: {msg}")

print("\n--- Test 2: Specific Size Check (e.g. 'M') (Likely OOS or In Stock) ---")
in_stock, msg, screen = check_stock_v2(url, "M")
print(f"Result: {in_stock}, Msg: {msg}")

print("\n--- Test 3: Specific Size Check (e.g. 'XXL') (Likely OOS) ---")
in_stock, msg, screen = check_stock_v2(url, "XXL")
print(f"Result: {in_stock}, Msg: {msg}")
