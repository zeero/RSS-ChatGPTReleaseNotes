import os
import feedgenerator
from playwright.sync_api import sync_playwright
from icecream import ic

OUTPUT_DIR = "public"  # GitHub Pages 用ディレクトリ
RSS_FILE = f"{OUTPUT_DIR}/rss.xml"
FEED_URL = "https://help.openai.com/en/articles/6825453-chatgpt-release-notes"

def fetch_release_notes():
    """Playwright を使って最新の ChatGPT リリースノートを取得"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        })
        page.goto(FEED_URL)
        page.wait_for_selector("article", timeout=120000)

        articles = page.locator("article").first.locator("h2").all()
        items = []

        for article in articles:
            # ic(article)
            title = article.text_content()
            link = FEED_URL  # 固定ページのため
            description = ""

            items.append({"title": title, "link": link, "description": description})

        browser.close()
        return items


def generate_rss(items):
    """取得した記事リストから RSS フィードを生成"""
    feed = feedgenerator.Rss201rev2Feed(
        title="ChatGPT Release Notes",
        link=FEED_URL,
        description="Latest updates from ChatGPT",
        language="en",
    )

    for item in items:
        feed.add_item(
            title=item["title"],
            link=item["link"],
            description=item["description"],
        )

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        feed.write(f, "utf-8")


if __name__ == "__main__":
    release_notes = fetch_release_notes()
    generate_rss(release_notes)
    print(f"RSS feed generated at {RSS_FILE}")

