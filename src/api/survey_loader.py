from __future__ import annotations

import pandas as pd

from config.settings import RAW_DIR
from src.utils.logger import logger


class SurveyLoader:
    """Stack Overflow Developer Survey CSV のローダー。"""

    SURVEY_DIR = RAW_DIR / "developer_survey"

    def load_year(self, year: int) -> pd.DataFrame:
        """指定年のサーベイデータを読み込む。"""
        path = self.SURVEY_DIR / str(year) / "survey_results_public.csv"
        if not path.exists():
            raise FileNotFoundError(f"サーベイデータが見つかりません: {path}")
        logger.info(f"サーベイデータ読込: {year}年")
        return pd.read_csv(path, low_memory=False)

    def load_years(self, years: list[int]) -> dict[int, pd.DataFrame]:
        """複数年のサーベイデータをまとめて読み込む。"""
        return {year: self.load_year(year) for year in years}
