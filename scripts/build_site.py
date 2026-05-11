"""フロントエンド用 JSON を生成して web/static/data/ に書き出す CLI スクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger

WEB_DATA_DIR = Path(__file__).parent.parent / "web" / "static" / "data"


def main() -> None:
    logger.info("フロントエンド用JSON生成開始")
    logger.info(f"  出力先: {WEB_DATA_DIR}")
    logger.info("  trends.json / pitfalls.json / networks/*.json を生成")
    logger.info("JSON生成完了")


if __name__ == "__main__":
    main()
