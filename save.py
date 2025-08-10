import sys
import os
import re
import requests
import shutil
from datetime import datetime
from bs4 import BeautifulSoup

URLS_FILE = "urls.txt"
DATA_DIR = "data"
ARCHIVE_URL = "https://web.archive.org/save/"

def load_urls():
    if not os.path.exists(URLS_FILE):
        return []
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def safe_folder_name(url):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))

def save_html(url):
    folder_path = os.path.join(DATA_DIR, safe_folder_name(url))
    os.makedirs(folder_path, exist_ok=True)

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.encoding = response.apparent_encoding
    html = response.text

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    file_path = os.path.join(folder_path, f"{timestamp}.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[保存完了] {file_path}")
    return folder_path

def send_to_archive(url):
    try:
        r = requests.get(ARCHIVE_URL + url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            print(f"[Archive.org] 保存リクエスト成功: {url}")
        else:
            print(f"[Archive.org] 保存失敗: {url} ({r.status_code})")
    except Exception as e:
        print(f"[Archive.org] エラー: {e}")

def remove_unused_folders(valid_urls):
    valid_folders = {safe_folder_name(url) for url in valid_urls}
    if not os.path.exists(DATA_DIR):
        return
    for folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder)
        if os.path.isdir(folder_path) and folder not in valid_folders:
            shutil.rmtree(folder_path)
            print(f"[削除] {folder_path}")

def main():
    urls = load_urls()
    if not urls:
        print("urls.txt にURLがありません")
        sys.exit(0)

    for url in urls:
        folder = save_html(url)
        send_to_archive(url)

    remove_unused_folders(urls)

if __name__ == "__main__":
    main()

