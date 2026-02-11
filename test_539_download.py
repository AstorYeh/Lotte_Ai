
import requests

url = "https://lotto.auzo.tw/daily539/list_2026_2.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    print(f"Downloading {url}...")
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        print("Download successful!")
        content = response.text
        if "history_view_table" in content:
            print("Found 'history_view_table' in HTML!")
        else:
            print("'history_view_table' NOT found.")
            
        # Check for ball structure
        if "history_ball" in content:
            print("Found 'history_ball' in HTML!")
            
        with open("test_539.html", "w", encoding="utf-8") as f:
            f.write(content)
            
    else:
        print(f"Failed: HTTP {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
