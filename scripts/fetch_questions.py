"""質問データを Stack Exchange API から取得する CLI スクリプト。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import ANALYSIS_END_YEAR, ANALYSIS_START_YEAR
from src.utils.logger import logger


def main() -> None:
    parser = argparse.ArgumentParser(description="Stack Overflow 質問データ取得")
    parser.add_argument(
        "--languages",
        nargs="+",
        help="取得対象言語タグ（デフォルト: target_languages.yml の全言語）",
    )
    parser.add_argument(
        "--start-year", type=int, default=ANALYSIS_START_YEAR, help="取得開始年"
    )
    parser.add_argument(
        "--end-year", type=int, default=ANALYSIS_END_YEAR, help="取得終了年"
    )
    args = parser.parse_args()

    logger.info(f"質問データ取得開始: {args.start_year}〜{args.end_year}年")
    from src.api.data_fetcher import DataFetcher
    fetcher = DataFetcher()
    df = fetcher.fetch_all_languages(
        start_year=args.start_year,
        end_year=args.end_year,
    )
    logger.info(f"取得完了: {len(df)}件")


if __name__ == "__main__":
    main()
