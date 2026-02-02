import requests

url = "https://www.zara.com/tr/en/wool-blend-contrast-jumper-p05755008.html?v1=500041235&v2=2546081"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.zara.com/tr/en/'
}

print(f"Downloading HTML: {url}")
try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {r.status_code}")
    with open("debug_zara.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved to debug_zara.html")
except Exception as e:
    print(f"Error: {e}")
