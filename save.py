import sys
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    print("URLを指定してください")
    sys.exit(1)

url = sys.argv[1]

# フォルダ名を作成（ドメイン＋パスを安全な文字に変換）
safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
folder_path = os.path.join("data", safe_name)
os.makedirs(folder_path, exist_ok=True)

# HTML取得
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
response.encoding = response.apparent_encoding
html = response.text

# タイムスタンプ付きファイル名
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
file_path = os.path.join(folder_path, f"{timestamp}.html")

# 保存
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"ローカル保存完了: {file_path}")

# ===== Internet Archive に保存 =====
try:
    archive_url = "https://web.archive.org/save/" + url
    r = requests.get(archive_url, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code in [200, 302]:
        # 保存先のURLを取得
        wayback_link = r.headers.get("Content-Location")
        if wayback_link:
            full_wayback_url = "https://web.archive.org" + wayback_link
            print(f"Internet Archiveに保存成功: {full_wayback_url}")
        else:
            print("Internet Archiveに保存はされた可能性がありますが、URL取得失敗")
    else:
        print(f"Internet Archive保存失敗: {r.status_code}")
except Exception as e:
    print(f"Internet Archive保存中にエラー: {e}")
