"""タグ統計を Stack Exchange API から取得する CLI スクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger


def main() -> None:
    logger.info("タグ統計取得開始")
    from src.api.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    df = fetcher.fetch_tag_statistics()
    logger.info(f"取得完了: {len(df)}件")


if __name__ == "__main__":
    main()
