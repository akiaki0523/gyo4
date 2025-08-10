import os
import requests
from datetime import datetime

# 保存先フォルダ
SAVE_DIR = "data"
os.makedirs(SAVE_DIR, exist_ok=True)

# 保存対象URL（スレッドURLを入れる）
URLS = [
    "https://example.com/thread1",
    "https://example.com/thread2"
]

# 容量上限（MB）
MAX_SIZE_MB = 800  # 1GBに近づく前にアラート

def get_repo_size_mb():
    total_size = 0
    for dirpath, _, filenames in os.walk(SAVE_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def save_snapshot(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        file_path = os.path.join(SAVE_DIR, f"{safe_name}_{now}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"保存完了: {file_path}")
    except Exception as e:
        print(f"保存失敗: {url} - {e}")

if __name__ == "__main__":
    size = get_repo_size_mb()
    if size > MAX_SIZE_MB:
        print("⚠ 容量が上限に近いです。別リポジトリへ移行を検討してください。")
    for url in URLS:
        save_snapshot(url)
