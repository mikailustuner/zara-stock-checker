from playwright.sync_api import sync_playwright

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Listening for availability requests...")
        
        def handle_response(response):
            if "availability" in response.url or "stock" in response.url:
                print(f"\n[MATCH] URL: {response.url}")
                try:
                    json_data = response.json()
                    print(f"JSON: {str(json_data)[:500]}...") # Print first 500 chars
                except:
                    print("Could not parse JSON.")

        page.on("response", handle_response)
        
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        print("Finished loading.")
        browser.close()

if __name__ == "__main__":
    run()
