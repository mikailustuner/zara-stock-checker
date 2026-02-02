from playwright.sync_api import sync_playwright
import json

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def check_console():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        
        # Try to get window.zara
        try:
            data = page.evaluate("() => window.zara ? JSON.stringify(window.zara) : null")
            if data:
                print("Found window.zara!")
                # Print keys to see what we have
                zara_obj = json.loads(data)
                print(f"Keys: {list(zara_obj.keys())}")
                
                # Check for viewPayload
                if "viewPayload" in zara_obj:
                     print("Found viewPayload!")
                else:
                     print("viewPayload NOT in window.zara")
            else:
                print("window.zara is null")
        except Exception as e:
            print(f"Error evaluating: {e}")
            
        browser.close()

if __name__ == "__main__":
    check_console()
