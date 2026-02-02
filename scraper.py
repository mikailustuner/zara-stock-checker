from playwright.sync_api import sync_playwright
import time
import os
import json
import requests
import re
from urllib.parse import urlparse, parse_qs

# --- Metadata Fetcher (One-time run) ---
def fetch_product_metadata(url):
    """
    Uses Playwright to fetch the product ID and Size->SKU mapping.
    Returns:
        {
            "product_id": "500041235",
            "size_map": {"S": 499809719, "M": 499809721, ...}
        }
    """
    try:
         with sync_playwright() as p:
            print("Fetching metadata...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)
            except:
                browser.close()
                return None

            try:
                data = page.evaluate("() => window.zara ? window.zara.viewPayload : null")
            except:
                 browser.close()
                 return None

            if not data:
                browser.close()
                return None
            
            product = data.get('product', {})
            details = product.get('detail', {})
            colors = details.get('colors', [])
            
            size_map = {}
            found_pid = None
            
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            primary_pid = params.get('v1', [None])[0]
            
            for color in colors:
                if not found_pid:
                    found_pid = color.get('productId') 
                    
                sizes = color.get('sizes', [])
                for size_obj in sizes:
                    s_name = size_obj.get('name', '').strip()
                    s_sku = size_obj.get('sku')
                    if s_name and s_sku:
                        size_map[s_name.upper()] = s_sku
            
            browser.close()
            
            return {
                "product_id": primary_pid or found_pid,
                "size_map": size_map
            }

    except Exception as e:
        print(f"Meta error: {e}")
        return None


# --- API Mode (Fast/Silent) ---
def check_stock_api(product_id, target_sku=None, size_map=None):
    """
    Checks stock using Zara's ITXRest API.
    Returns:
        found (bool), message (str), details (str)
    """
    try:
        if not product_id:
             return False, "No Product ID", "Missing metadata"

        store_id = "11766" 
        api_url = f"https://www.zara.com/itxrest/1/catalog/store/{store_id}/product/id/{product_id}/availability"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.zara.com/tr/en/',
            'Accept': 'application/json, text/plain, */*'
        }

        r = requests.get(api_url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            return False, f"API {r.status_code}", f"HTTP Error: {r.text}"
            
        data = r.json()
        skus = data.get('skusAvailability', [])
        
        # Build Detailed Report
        details_lines = []
        
        # Invert size map for display: SKU -> Name
        sku_to_name = {v: k for k, v in (size_map or {}).items()}
        
        # Create a dict of known status
        sku_status = {}
        for item in skus:
            sku_id = item.get('sku')
            status = item.get('availability', 'unknown')
            sku_status[sku_id] = status

        # If we have a map, list all sizes in standard order
        if size_map:
            for size_name, sku_id in size_map.items():
                status = sku_status.get(sku_id, "unknown")
                if status == "in_stock":
                    details_lines.append(f"{size_name}: ✅ In Stock")
                elif status == "out_of_stock":
                    details_lines.append(f"{size_name}: ❌ OOS")
                else:
                     details_lines.append(f"{size_name}: ❓ {status}")
        else:
            # No map, just list raw SKUs
            for item in skus:
                s = item.get('availability')
                sym = "✅" if s == "in_stock" else "❌"
                details_lines.append(f"SKU {item.get('sku')}: {sym} {s}")
        
        details_str = " | ".join(details_lines)

        # Main Decision Logic
        if target_sku:
            # Specific
            specific_status = sku_status.get(target_sku, "out_of_stock")
            if specific_status == "in_stock":
                return True, "Size In Stock!", details_str
            else:
                return False, "Size OOS", details_str
        else:
            # Any
            any_stock = any(item.get('availability') == 'in_stock' for item in skus)
            if any_stock:
                return True, "Available", details_str
            else:
                return False, "Out of Stock", details_str

    except Exception as e:
        return False, f"API Fail: {str(e)}", str(e)

# --- Browser Mode (Legacy) ---
def check_stock_browser(url, target_size=None):
    try:
         with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3) 
            except:
                browser.close()
                return False, "Nav Timeout", None

            data = page.evaluate("() => window.zara ? window.zara.viewPayload : null")
            if not data:
                browser.close()
                return False, "No Payload", None

            product = data.get('product', {})
            details = product.get('detail', {})
            colors = details.get('colors', [])
            
            available_sizes = []
            for color in colors:
                sizes = color.get('sizes', [])
                for size_obj in sizes:
                    if size_obj.get('availability') == 'in_stock':
                        available_sizes.append(size_obj.get('name', '').strip())
            
            found = False
            msg = "Out of Stock"
            
            if target_size:
                if target_size.upper() in [s.upper() for s in available_sizes]:
                    found = True
                    msg = f"Size {target_size} In Stock!"
            else:
                if available_sizes:
                    found = True
                    msg = "In Stock!"
            
            screenshot_path = None
            if found:
                if not os.path.exists("screenshots"): os.makedirs("screenshots")
                screenshot_path = os.path.abspath(f"screenshots/stock_{int(time.time())}.png")
                page.screenshot(path=screenshot_path)
            
            browser.close()
            return found, msg, screenshot_path
    except Exception as e:
        return False, f"Err: {e}", None
