"""Day 5: マクロトレンド分析を実行するスクリプト。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from config.settings import ANALYSIS_DIR, PROCESSED_DIR, ROOT_DIR
from src.analysis.trend import TrendAnalyzer
from src.api.survey_loader import SurveyLoader
from src.utils.logger import logger


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    # 質問データとタグ統計を読み込む
    questions_df = pd.read_parquet(PROCESSED_DIR / "questions.parquet")
    tags_df = pd.read_parquet(PROCESSED_DIR / "tags.parquet")
    logger.info(f"質問: {len(questions_df):,}件 / タグ: {len(tags_df)}件")

    # Developer Survey を読み込む
    loader = SurveyLoader()
    survey_dfs: dict[int, pd.DataFrame] = {}
    for year in [2022, 2023, 2024]:
        try:
            df = loader.load_year(year)
            survey_dfs[year] = df
            logger.info(f"Survey {year}: {len(df):,}行")
        except FileNotFoundError as e:
            logger.warning(f"Survey {year}: {e}")

    analyzer = TrendAnalyzer()

    # Developer Survey トレンド集計
    logger.info("=== Developer Survey トレンド集計 ===")
    survey_trend = analyzer.compute_survey_trend(survey_dfs)
    print("\n--- survey_trend ---")
    print(survey_trend.to_string(index=False))

    # 質問指標を集計
    logger.info("=== 質問指標集計 ===")
    yearly_counts = analyzer.compute_yearly_counts(questions_df)
    print("\n--- yearly_counts ---")
    print(yearly_counts.to_string(index=False))

    # 結合
    merged = analyzer.merge_survey_data(yearly_counts, survey_trend)

    # parquet 保存
    out_parquet = ANALYSIS_DIR / "trends.parquet"
    merged.to_parquet(out_parquet, index=False)
    logger.info(f"trends.parquet 保存: {out_parquet}")

    # フロントエンド用 JSON 生成
    out_json = ROOT_DIR / "web" / "static" / "data" / "trends.json"
    analyzer.build_web_json(survey_trend, tags_df, out_json)

    # 確認
    with open(out_json) as f:
        payload = json.load(f)
    print("\n--- trends.json ---")
    print(f"years: {payload['years']}")
    for lang, info in payload["languages"].items():
        print(
            f"  {lang}: usage_pct={info['usage_pct']} "
            f"want_pct={info['want_pct']} "
            f"total_questions={info['total_questions']:,}"
        )

    logger.info("Day 5 完了")


if __name__ == "__main__":
    main()
