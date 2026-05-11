"""質問データを Stack Exchange API から取得して parquet に保存する CLI スクリプト。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import ANALYSIS_END_YEAR, ANALYSIS_START_YEAR
from src.api.data_fetcher import DataFetcher
from src.utils.logger import logger


def main() -> None:
    parser = argparse.ArgumentParser(description="Stack Overflow 質問データ取得")
    parser.add_argument("--start-year", type=int, default=ANALYSIS_START_YEAR)
    parser.add_argument("--end-year", type=int, default=ANALYSIS_END_YEAR)
    parser.add_argument(
        "--max-per-year",
        type=int,
        default=500,
        help="1言語×1年あたりの取得上限（デフォルト: 500件）",
    )
    args = parser.parse_args()

    logger.info(f"取得期間: {args.start_year}〜{args.end_year}年")
    logger.info(f"1言語×1年あたり上限: {args.max_per_year}件")

    fetcher = DataFetcher()
    df = fetcher.fetch_all_languages(
        start_year=args.start_year,
        end_year=args.end_year,
        max_per_year=args.max_per_year,
    )
    fetcher.save_questions(df)
    logger.info("完了")


if __name__ == "__main__":
    main()
