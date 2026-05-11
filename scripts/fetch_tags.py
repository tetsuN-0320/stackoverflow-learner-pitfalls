"""タグ統計を Stack Exchange API から取得して parquet に保存する CLI スクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.data_fetcher import DataFetcher
from src.utils.logger import logger


def main() -> None:
    fetcher = DataFetcher()
    df = fetcher.fetch_tag_statistics()
    fetcher.save_tags(df)
    logger.info("完了")


if __name__ == "__main__":
    main()
