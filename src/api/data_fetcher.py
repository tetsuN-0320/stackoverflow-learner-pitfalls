from __future__ import annotations

import yaml
import pandas as pd

from config.settings import (
    ANALYSIS_END_YEAR,
    ANALYSIS_START_YEAR,
    PROCESSED_DIR,
    ROOT_DIR,
)
from src.api.stackex_client import StackExClient
from src.utils.logger import logger

# 全件取得は API クォータに当たるため、年あたりこの件数でサンプリングする
_MAX_PER_YEAR = 500  # 5ページ分


class DataFetcher:
    """target_languages.yml に基づき全言語の質問・タグデータを取得するオーケストレーター。"""

    def __init__(self) -> None:
        self.client = StackExClient()
        with open(ROOT_DIR / "config" / "target_languages.yml", encoding="utf-8") as f:
            self.config: dict = yaml.safe_load(f)

    def fetch_all_languages(
        self,
        start_year: int = ANALYSIS_START_YEAR,
        end_year: int = ANALYSIS_END_YEAR,
        max_per_year: int = _MAX_PER_YEAR,
    ) -> pd.DataFrame:
        """全対象言語の質問データを年別にサンプリングして取得する。

        Python など質問数が多い言語は年に数十万件あるため全件取得は不可能。
        年あたり max_per_year 件に制限することで全 10 年・4 言語を現実的な
        API コール数（200〜400 回）で取得できる。
        """
        all_questions: list[dict] = []

        for lang_key, lang_cfg in self.config["languages"].items():
            tag = lang_cfg["tag"]
            display = lang_cfg["display_name"]
            logger.info(f"=== {display} ({tag}) 取得開始 ===")

            for year in range(start_year, end_year + 1):
                from_ts, to_ts = StackExClient.year_to_timestamps(year)
                count = 0

                for q in self.client.iter_questions_by_tag(tag, from_ts, to_ts):
                    q["language"] = lang_key
                    q["year"] = year
                    all_questions.append(q)
                    count += 1
                    if count >= max_per_year:
                        break

                logger.info(f"  {display} {year}: {count}件")

        df = pd.DataFrame(all_questions)
        logger.info(f"全取得完了: {len(df):,}件")
        return df

    def fetch_tag_statistics(self) -> pd.DataFrame:
        """全対象言語の主要タグの統計情報（質問数など）を取得する。"""
        all_tags: list[dict] = []

        for lang_key, lang_cfg in self.config["languages"].items():
            display = lang_cfg["display_name"]
            tags_to_fetch = [lang_cfg["tag"]] + lang_cfg.get("related_tags", [])
            logger.info(f"タグ統計取得: {display} ({len(tags_to_fetch)}タグ)")

            data = self.client.fetch_tag_info(tags_to_fetch)
            for tag_info in data.get("items", []):
                tag_info["language"] = lang_key
                all_tags.append(tag_info)

        df = pd.DataFrame(all_tags)
        logger.info(f"タグ統計取得完了: {len(df)}件")
        return df

    def save_questions(self, df: pd.DataFrame) -> None:
        """質問データを parquet に保存する。"""
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        path = PROCESSED_DIR / "questions.parquet"
        df.to_parquet(path, index=False)
        logger.info(f"保存: {path} ({len(df):,}件)")

    def save_tags(self, df: pd.DataFrame) -> None:
        """タグ統計を parquet に保存する。"""
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        path = PROCESSED_DIR / "tags.parquet"
        df.to_parquet(path, index=False)
        logger.info(f"保存: {path} ({len(df)}件)")
