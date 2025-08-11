import os
import re
import time
from datetime import datetime
import requests

INTERVAL = 600  # 秒（10分ごと）
RUN_HOURS = 6   # 最大6時間
URL_FILE = "urls.txt"

if not os.path.exists(URL_FILE):
    print(f"{URL_FILE} が見つかりません。終了します。")
    exit(1)

with open(URL_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

if not urls:
    print("保存対象URLがありません。終了します。")
    exit(0)

start_time = time.time()

for url in urls:
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
    folder_path = os.path.join("data", safe_name)
    os.makedirs(folder_path, exist_ok=True)

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
        file_path = os.path.join(folder_path, f"{timestamp}.html")

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, allow_redirects=True)

            if "/board/" not in response.url:
                print(f"削除検出 → 保存停止: {url} （最終到達: {response.url}）")
                break  # このURLの監視を終了

            if response.status_code == 200:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"保存完了: {file_path}")
            else:
                print(f"ページ取得失敗 (status {response.status_code}): {url}")

        except requests.exceptions.RequestException as e:
            print(f"取得エラー: {url} - {e}")

        # 6時間超えたら終了
        if time.time() - start_time > RUN_HOURS * 3600:
            print("6時間経過 → 終了")
            exit(0)

        time.sleep(INTERVAL)
