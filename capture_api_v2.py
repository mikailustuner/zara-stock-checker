# capture_api_v2.py
from playwright.sync_api import sync_playwright

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Listening...")
        
        def handle_request(request):
            if "availability" in request.url:
                with open("api_log.txt", "w") as f:
                    f.write(f"URL: {request.url}\n")
                    f.write(f"Headers: {request.headers}\n")
                print("Captured to api_log.txt")

        page.on("request", handle_request)
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        browser.close()

if __name__ == "__main__":
    run()
