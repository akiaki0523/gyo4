import sys
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# urls.txt からURLを読み込み
with open("urls.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

if not urls:
    print("urls.txt にURLがありません")
    sys.exit(1)

for url in urls:
    # フォルダ名作成
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
    folder_path = os.path.join("data", safe_name)
    os.makedirs(folder_path, exist_ok=True)

    # HTML取得
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.encoding = response.apparent_encoding
    html = response.text

    # タイムスタンプ付き保存
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_path = os.path.join(folder_path, f"{timestamp}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"保存完了: {file_path}")
