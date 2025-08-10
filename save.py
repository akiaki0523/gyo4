import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

def save_offline_page(url):
    # タイムスタンプ生成
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    domain = urlparse(url).netloc.replace(":", "_")
    save_dir = os.path.join("data", domain, timestamp)
    os.makedirs(save_dir, exist_ok=True)

    print(f"[INFO] 保存先: {save_dir}")

    # HTML取得
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")

    # 画像・CSSなどをダウンロード
    for tag in soup.find_all(["img", "link", "script"]):
        attr = "src" if tag.name != "link" else "href"
        if tag.has_attr(attr):
            file_url = urljoin(url, tag[attr])
            parsed = urlparse(file_url)
            if parsed.scheme.startswith("http"):
                try:
                    file_name = os.path.basename(parsed.path)
                    if not file_name:
                        file_name = "index"
                    file_path = os.path.join(save_dir, file_name)
                    
                    # ダウンロード
                    r = requests.get(file_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    r.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(r.content)

                    # HTML内リンク書き換え
                    tag[attr] = file_name
                except Exception as e:
                    print(f"[WARN] {file_url} の取得に失敗: {e}")

    # HTML保存
    html_path = os.path.join(save_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"[DONE] オフライン保存完了: {html_path}")

if __name__ == "__main__":
    urls_file = "urls.txt"
    if not os.path.exists(urls_file):
        print("urls.txt が見つかりません")
        exit(1)

    with open(urls_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("URLを指定してください")
        exit(1)

    for url in urls:
        save_offline_page(url)
