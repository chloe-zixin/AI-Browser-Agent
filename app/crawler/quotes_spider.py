import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any
from playwright.sync_api import sync_playwright


SOURCE_ID = "quotes.toscrape.com"
SOURCE_URL = "https://quotes.toscrape.com/"


def record_key(quote: dict[str, Any]) -> tuple[str, str]:
    normalized_text = re.sub(r"\s+", " ", str(quote.get("quote") or "")).strip().casefold()
    normalized_author = re.sub(r"\s+", " ", str(quote.get("author") or "")).strip().casefold()
    return normalized_text, normalized_author


def deduplicate_quotes(quotes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_quotes: list[dict[str, Any]] = []
    seen = set()
    for quote in quotes:
        key = record_key(quote)
        if not key[0] or key in seen:
            continue
        seen.add(key)
        unique_quotes.append(quote)
    return unique_quotes


def crawl_quotes(pages: int = 10, headless: bool = False) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_page()

            page.goto(SOURCE_URL, wait_until="domcontentloaded", timeout=30000)

            page_num = 1

            while page_num <= pages:
                print(f"正在抓取第 {page_num} 页...")
                page.wait_for_selector(".quote", timeout=15000)

                quotes = page.locator(".quote")
                count = quotes.count()

                for i in range(count):
                    quote = quotes.nth(i)

                    text = quote.locator(".text").text_content()
                    author = quote.locator(".author").text_content()
                    tags = quote.locator(".tags .tag").all_text_contents()
                    normalized_text = str(text or "").strip()
                    normalized_author = str(author or "").strip()
                    if not normalized_text:
                        continue
                    stable_key = "\0".join(
                        record_key({"quote": normalized_text, "author": normalized_author})
                    )

                    results.append({
                        "page": page_num,
                        "quote": normalized_text,
                        "author": normalized_author,
                        "tags": tags,
                        "record_id": hashlib.sha256(stable_key.encode("utf-8")).hexdigest(),
                        "source_id": SOURCE_ID,
                        "source_url": page.url,
                        "captured_at": captured_at,
                    })

                next_btn = page.locator(".next a")

                if next_btn.count() > 0 and page_num < pages:
                    next_btn.click()
                    page.wait_for_timeout(2000)
                    page_num += 1
                else:
                    break
        finally:
            browser.close()

    return results


def save_quotes_to_json(data, output_path="data/quotes_all.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功保存 {len(data)} 条数据到 {output_path}")