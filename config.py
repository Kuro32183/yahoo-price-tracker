# 監視商品リスト（name: 表示名, url: 楽天商品ページURL）
TARGETS: list[dict[str, str]] = [
    {
        "name": "Logicool 商品",
        "url": "https://store.shopping.yahoo.co.jp/logicool/4943765064572.html",
    },
]

# データ保存先
DATA_DIR: str = "data"
CSV_FILE: str = "data/prices.csv"

# リクエスト間隔（秒）
WAIT_SECONDS: int = 2
