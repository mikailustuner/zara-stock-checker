from playwright.sync_api import sync_playwright
import json

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def dump_payload():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        
        data = page.evaluate("() => window.zara ? window.zara.viewPayload : null")
        if data:
            with open("payload_dump.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Saved payload_dump.json")
        else:
            print("viewPayload not found")
            
        browser.close()

if __name__ == "__main__":
    dump_payload()
