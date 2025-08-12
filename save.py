import os
import re
import sys
from datetime import datetime
import requests

URL_FILE = "urls.txt"  # 保存対象URL一覧

# コマンドライン引数から履歴名を受け取る
if len(sys.argv) > 1:
    history_label = sys.argv[1]
else:
    history_label = "history1"

if not os.path.exists(URL_FILE):
    print(f"{URL_FILE} が見つかりません。終了します。")
    exit(1)

with open(URL_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

if not urls:
    print("保存対象URLがありません。終了します。")
    exit(0)

for url in urls:
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
    folder_path = os.path.join("data", history_label, safe_name)
    os.makedirs(folder_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_path = os.path.join(folder_path, f"{timestamp}.html")

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, allow_redirects=True)

        # 掲示板トップに戻ったら保存せず終了
        if "/board/" not in response.url:
            print(f"削除検出 → 保存停止: {url} （最終到達: {response.url}）")
            continue

        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"保存完了: {file_path}")
        else:
            print(f"ページ取得失敗 (status {response.status_code}): {url}")

    except requests.exceptions.RequestException as e:
        print(f"取得エラー: {url} - {e}")

    # index.html 更新
    html_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".html") and f != "index.html"])
    index_path = os.path.join(folder_path, "index.html")
    with open(index_path, "w", encoding="utf-8") as index_file:
        index_file.write("<html><head><meta charset='utf-8'><title>保存履歴</title></head><body>")
        index_file.write(f"<h1>保存履歴 ({url})</h1><ul>")
        for html_file in html_files:
            index_file.write(f"<li><a href='{html_file}' target='_blank'>{html_file}</a></li>")
        index_file.write("</ul></body></html>")

    print(f"index.html 更新: {index_path}")
