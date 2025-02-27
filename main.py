from playwright.sync_api import sync_playwright
import feedgenerator
from icecream import ic

URL = "https://help.openai.com/en/articles/6825453-chatgpt-release-notes"

def fetch_release_notes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        })
        page.goto(URL, timeout=60000)
        page.wait_for_selector("article", timeout=60000)  # 記事が表示されるのを待つ
        # page.wait_for_load_state("networkidle")  # 記事が表示されるのを待つ
        # ic(page.content())
        articles = page.locator("article").first.locator("h2").all()
        
        items = []
        for article in articles[:10]:  # 最新10件を取得
            ic(article)
            title = article.text_content() or "Untitled"
            # description = article.text_content()[:200]
            description = ""
            items.append((title, URL, description))
        
        browser.close()
        return items

def generate_rss(items):
    feed = feedgenerator.Rss201rev2Feed(
        title="ChatGPT Release Notes",
        link=URL,
        description="Latest updates and release notes for ChatGPT",
        language="en",
    )

    for title, link, description in items:
        feed.add_item(title=title, link=link, description=description)

    with open("chatgpt_release_notes.xml", "w", encoding="utf-8") as f:
        feed.write(f, "utf-8")

if __name__ == "__main__":
    items = fetch_release_notes()
    generate_rss(items)
    print("RSS feed generated successfully!")

