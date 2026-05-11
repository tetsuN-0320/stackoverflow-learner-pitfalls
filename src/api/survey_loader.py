from __future__ import annotations

import pandas as pd

from config.settings import RAW_DIR
from src.utils.logger import logger


class SurveyLoader:
    """Stack Overflow Developer Survey CSV のローダー。"""

    SURVEY_DIR = RAW_DIR / "developer_survey"

    # ダウンロード元によってファイル名が異なるため、両方を探す
    _CANDIDATES = ["results.csv", "survey_results_public.csv"]

    def load_year(self, year: int) -> pd.DataFrame:
        """指定年のサーベイデータを読み込む。"""
        year_dir = self.SURVEY_DIR / str(year)
        for name in self._CANDIDATES:
            path = year_dir / name
            if path.exists():
                logger.info(f"サーベイデータ読込: {year}年 ({name})")
                return pd.read_csv(path, low_memory=False)
        raise FileNotFoundError(
            f"サーベイデータが見つかりません: {year_dir} に {self._CANDIDATES} のいずれかを配置してください"
        )

    def load_years(self, years: list[int]) -> dict[int, pd.DataFrame]:
        """複数年のサーベイデータをまとめて読み込む。"""
        return {year: self.load_year(year) for year in years}
