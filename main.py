import asyncio

from config import TARGETS
from scraper import scrape_all
from tracker import detect_changes, save_prices, print_summary


async def main() -> None:
    # 1. 全商品をスクレイピング
    results = await scrape_all(TARGETS)

    # 2. 保存前に前回との価格変動を検知
    changes = detect_changes(results)

    # 3. スクレイピング結果をCSVに保存
    save_prices(results)

    # 4. サマリーを表示
    print_summary(results, changes)


if __name__ == "__main__":
    asyncio.run(main())
