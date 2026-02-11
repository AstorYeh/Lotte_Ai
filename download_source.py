import requests

urls = {
    "power": "https://lotto.auzo.tw/power/list_2026_2.html",
    "lotto": "https://lotto.auzo.tw/biglotto/list_2026_2.html",
    "star3": "https://lotto.auzo.tw/lotto_historylist_three-star.html",
    "star4": "https://lotto.auzo.tw/lotto_historylist_four-star.html"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for name, url in urls.items():
    print(f"Downloading {name} from {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # Ensure UTF-8 decoding
        filename = f"{name}_source.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Saved to {filename}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
