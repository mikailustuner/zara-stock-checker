from playwright.sync_api import sync_playwright
import time

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

with sync_playwright() as p:
    # Launch with headless=False to appear as a real user
    browser = p.chromium.launch(headless=False) 
    page = browser.new_page()
    
    # Set extra headers to look simpler
    page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    print(f"Navigating to {url}...")
    try:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5) # Wait for JS to hydrate
        
        content = page.content()
        with open("zara_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("Dumped HTML to zara_dump.html using headless=False")
    except Exception as e:
        print(f"Error: {e}")
        
    browser.close()
