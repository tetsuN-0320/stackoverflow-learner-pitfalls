from __future__ import annotations

from datetime import datetime

import pandas as pd
import yaml

from config.settings import ANALYSIS_END_YEAR, ANALYSIS_START_YEAR, ROOT_DIR
from src.api.stackex_client import StackExClient
from src.utils.logger import logger


class DataFetcher:
    """target_languages.yml に基づき全言語の質問・タグデータを取得するオーケストレーター。

    Day 3 で本実装する。
    """

    def __init__(self) -> None:
        self.client = StackExClient()
        with open(ROOT_DIR / "config" / "target_languages.yml", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def _year_to_timestamps(self, year: int) -> tuple[int, int]:
        """年をUNIXタイムスタンプの範囲（年初〜年末）に変換する。"""
        start = int(datetime(year, 1, 1).timestamp())
        end = int(datetime(year, 12, 31, 23, 59, 59).timestamp())
        return start, end

    def fetch_all_languages(
        self,
        start_year: int = ANALYSIS_START_YEAR,
        end_year: int = ANALYSIS_END_YEAR,
    ) -> pd.DataFrame:
        """全対象言語の質問データを年別に取得して結合する。"""
        raise NotImplementedError("Day 3 で実装")

    def fetch_tag_statistics(self) -> pd.DataFrame:
        """全対象言語の関連タグ統計を取得する。"""
        raise NotImplementedError("Day 3 で実装")
