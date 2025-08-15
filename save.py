import os
import re
import sys
from datetime import datetime
import requests

URL_FILE = "urls.txt"  # 保存対象URL一覧

# コマンドライン引数から履歴名を受け取る
history_label = sys.argv[1] if len(sys.argv) > 1 else "history1"

# URLリスト確認
if not os.path.exists(URL_FILE):
    print(f"{URL_FILE} が見つかりません。終了します。")
    sys.exit(1)

with open(URL_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

if not urls:
    print("保存対象URLがありません。終了します。")
    sys.exit(0)

# 1つずつURLを処理（全体終了仕様なので基本は1件）
for url in urls:
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_',
                       url.replace('https://', '').replace('http://', ''))
    folder_path = os.path.join("data", history_label, safe_name)
    os.makedirs(folder_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_path = os.path.join(folder_path, f"{timestamp}.html")

    try:
        # リダイレクト先チェック用に allow_redirects=False
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"},
                           timeout=15, allow_redirects=False)

        # リダイレクトでトップページに飛ばされた場合
        if 300 <= res.status_code < 400:
            location = res.headers.get("Location", "").rstrip("/")
            if "/board/" not in location:
                print(f"削除検出（リダイレクト先がトップ）→ 保存停止: {url} （最終到達: {location}）")
                sys.exit(0)

        # 直接アクセスでトップページだった場合
        if "/board/" not in res.url:
            print(f"削除検出（直接トップ）→ 保存停止: {url} （最終到達: {res.url}）")
            sys.exit(0)

        # 正常取得時に保存
        if res.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(res.text)
            print(f"保存完了: {file_path}")
        else:
            print(f"ページ取得失敗 (status {res.status_code}): {url}")
            sys.exit(1)  # エラー終了

    except requests.exceptions.RequestException as e:
        print(f"取得エラー: {url} - {e}")
        sys.exit(1)

    # index.html 更新
