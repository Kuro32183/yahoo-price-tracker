# Yahoo!ショッピング 価格監視ツール

Yahoo!ショッピングの商品価格を定期取得し、変動を検知するPythonツール。

## 機能
- Playwrightによる動的ページのスクレイピング
- OGPメタタグで安定した価格・商品名取得
- CSV形式で価格履歴を蓄積
- 前回価格との比較・変動率の表示

## 技術スタック
- Python / Playwright / BeautifulSoup / pandas

## セットアップ
\`\`\`bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
\`\`\`

## 使い方
\`\`\`bash
python main.py
\`\`\`

## 出力例
\`\`\`
[CHANGE] ロジクールG ゲーミングキーボード
  ↑ ¥30,000 → ¥32,700 (+9.0%)
\`\`\`
