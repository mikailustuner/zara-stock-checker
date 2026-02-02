from bs4 import BeautifulSoup
import json
import re

def inspect_zara_json():
    try:
        with open("zara_dump.html", "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for the script containing window.zara.viewPayload or catalog details
        scripts = soup.find_all('script')
        target_script = None
        
        for script in scripts:
            if script.string and "product" in script.string and "detail" in script.string:
                 # heuristic for the big payload
                 pass
            if script.string and ("zara.viewPayload" in script.string or "product-detail-view-payload" in script.string):
                target_script = script.string
                break
        
        # Fallback: regex search in whole html if script not found easily
        if not target_script:
            print("Direct script not found. Regex searching...")
            # Pattern: window.zara.viewPayload = {...};
            match = re.search(r"window\.zara\.viewPayload\s*=\s*(\{.*?\});", html, re.DOTALL)
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
                print("Found match via regex!")
                # Print structure
                # usually product -> detail -> colors -> sizes
                product = data.get('product', {})
                print(f"Product ID: {product.get('id')}")
                print(f"Name: {product.get('name')}")
                
                details = product.get('detail', {})
                colors = details.get('colors', [])
                
                for color in colors:
                    print(f"Color: {color.get('name')}")
                    for size in color.get('sizes', []):
                        print(f"  Size: {size.get('name')} | Availability: {size.get('availability')} | ID: {size.get('id')}")
                return

        print("Could not find payload via standard regex.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_zara_json()
