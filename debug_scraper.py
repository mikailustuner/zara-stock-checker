from playwright.sync_api import sync_playwright
import time

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def debug_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(10) # Wait a long time for full hydration
        
        # Take a screenshot to see what the bot sees
        page.screenshot(path="debug_view.png")
        print("Saved debug_view.png")
        
        # 1. Print all text that looks like a size
        # We'll look for the size selector container specifically
        # Common Zara selectors:
        selectors = [
            ".product-detail-size-selector__size-list", 
            "ul[role='radiogroup']",
            ".size-selector-list"
        ]
        
        found_container = False
        for sel in selectors:
            cnt = page.locator(sel).count()
            if cnt > 0:
                print(f"DEBUG: Found container '{sel}'")
                found_container = True
                
                # Print all items inside
                items = page.locator(f"{sel} li")
                print(f"DEBUG: Found {items.count()} items in container.")
                for i in range(items.count()):
                    item = items.nth(i)
                    txt = item.inner_text().replace('\n', ' ')
                    cls = item.get_attribute("class")
                    print(f"  Item {i}: Text='{txt}', Class='{cls}'")
                    
        if not found_container:
            print("DEBUG: No standard size container found.")
            # Dump all buttons/spans with short text to see if we can spot valid sizes
            print("Scanning likely size elements...")
            elements = page.locator("li, button, span").all()
            for el in elements:
                try:
                    txt = el.inner_text().strip()
                    if len(txt) > 0 and len(txt) < 10 and txt.isupper(): # heuristic
                        # Only print if visible
                        if el.is_visible():
                            print(f"  Possible Size: '{txt}' (Tag: {el.evaluate('el => el.tagName')})")
                except:
                    pass

        browser.close()

if __name__ == "__main__":
    debug_page()
