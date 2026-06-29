import re
import time
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from config import WAIT_SECONDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def scrape_rakuten_item(url: str) -> dict[str, object] | None:
    """Yahoo!ショッピングの商品ページから商品名と価格を取得する"""
    browser = None
    try:
        async with async_playwright() as pw:
            # Chromiumをヘッドレスモードで起動
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            # ページにアクセスしてJS描画完了を待つ
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            # HTMLを取得してBeautifulSoupでパース
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # 商品名をog:titleメタタグから取得（CSSクラスより安定）
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                # " : ストア名 - 通販 - Yahoo!ショッピング" の付記を除去
                raw_title: str = og_title["content"]
                name = raw_title.split(" : ")[0].strip()
            else:
                name = "不明"

            # 価格をproduct:price:amountメタタグから取得（数値のみで安定）
            price_meta = soup.find("meta", property="product:price:amount")
            if price_meta is None or not price_meta.get("content"):
                logger.warning("価格メタタグが見つかりませんでした: %s", url)
                return None

            price_str = re.sub(r"[^\d]", "", price_meta["content"])
            if not price_str:
                logger.warning("価格のパースに失敗しました（content: %s）: %s", price_meta["content"], url)
                return None

            price: int = int(price_str)

            return {
                "name": name,
                "price": price,
                "url": url,
                "scraped_at": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error("スクレイピング中にエラーが発生しました（%s）: %s", url, e)
        return None
    finally:
        # browserがcontext manager内で管理されているため、
        # async withブロック終了時に自動クローズされる
        pass


async def scrape_all(targets: list[dict[str, str]]) -> list[dict[str, object]]:
    """全ターゲット商品をスクレイピングして結果リストを返す"""
    results: list[dict[str, object]] = []
    total = len(targets)

    for i, target in enumerate(targets, start=1):
        print(f"[{i}/{total}] スクレイピング中: {target['name']}")
        result = await scrape_rakuten_item(target["url"])
        if result is not None:
            results.append(result)

        # 最後のアイテム以外はウェイトを挟む
        if i < total:
            time.sleep(WAIT_SECONDS)

    return results
