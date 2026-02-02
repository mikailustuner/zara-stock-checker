# capture_api.py
from playwright.sync_api import sync_playwright

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Listening for availability requests...")
        
        def handle_request(request):
            # Look for availability or stock endpoint
            # Zara often uses 'wcs/resources/store/.../product/...' or 'itxrest'
            if "availability" in request.url or "stock" in request.url:
                print(f"\n[FOUND API] URL: {request.url}")
                print(f"Headers: {request.headers}")
                # We stop after finding one relevant request
                
        page.on("request", handle_request)
        
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        print("Finished.")
        browser.close()

if __name__ == "__main__":
    run()
