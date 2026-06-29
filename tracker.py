import os
import logging
from datetime import datetime

import pandas as pd

from config import DATA_DIR, CSV_FILE

logger = logging.getLogger(__name__)


def save_prices(results: list[dict[str, object]]) -> None:
    """スクレイピング結果をCSVに保存（既存ファイルがあれば追記）"""
    os.makedirs(DATA_DIR, exist_ok=True)
    new_df = pd.DataFrame(results)

    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df.to_csv(CSV_FILE, index=False)
    logger.info("価格データを保存しました: %s", CSV_FILE)


def detect_changes(results: list[dict[str, object]]) -> list[dict[str, object]]:
    """前回との価格変動を検知して変動リストを返す（初回実行時は空リスト）"""
    if not os.path.exists(CSV_FILE):
        return []

    try:
        df = pd.read_csv(CSV_FILE)
    except pd.errors.EmptyDataError:
        return []
    changes: list[dict[str, object]] = []

    for result in results:
        url = result["url"]
        curr_price = int(result["price"])

        # 同じURLの過去データを取得
        history = df[df["url"] == url].reset_index(drop=True)

        # 比較に必要な履歴が2件未満の場合はスキップ
        if len(history) < 2:
            continue

        prev_price = int(history.iloc[-2]["price"])

        # 価格が変動していた場合のみ記録
        if curr_price != prev_price:
            diff = curr_price - prev_price
            diff_pct = round((diff / prev_price) * 100, 1)
            changes.append({
                "name": result["name"],
                "prev_price": prev_price,
                "curr_price": curr_price,
                "diff": diff,
                "diff_pct": diff_pct,
                "url": url,
            })

    return changes


def print_summary(results: list[dict[str, object]], changes: list[dict[str, object]]) -> None:
    """実行結果のサマリーをコンソールに出力する"""
    separator = "=" * 50
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(separator)
    print(f"実行日時      : {now}")
    print(f"取得成功件数  : {len(results)} 件")
    print(f"価格変動件数  : {len(changes)} 件")

    if changes:
        print()
        print("【価格変動あり】")
        for c in changes:
            direction = "↑" if c["diff"] > 0 else "↓"
            print(f"  {c['name']}")
            print(f"    前回: ¥{c['prev_price']:,}  →  現在: ¥{c['curr_price']:,}")
            print(f"    変動: {direction}{abs(c['diff']):,}円 ({c['diff_pct']:+.1f}%)")

    print(separator)
