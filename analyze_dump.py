from bs4 import BeautifulSoup

with open("zara_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print(f"Title: {soup.title.string}")
print(f"Body text length: {len(soup.body.get_text())}")
print(f"Body text start: {soup.body.get_text()[:500]}")

scripts = soup.find_all('script')
print(f"Found {len(scripts)} scripts.")

for i, script in enumerate(scripts):
    if script.string:
        if "size" in script.string.lower():
            print(f"Script {i} contains 'size'. Length: {len(script.string)}")
            # print(script.string[:200])
        if "viewpayload" in script.string.lower():
            print(f"Script {i} contains 'viewPayload'.")
