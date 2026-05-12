from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from config.settings import ANALYSIS_DIR, ROOT_DIR
from src.utils.logger import logger

# Developer Survey の言語列での正式表記
_LANG_DISPLAY: dict[str, str] = {
    "python": "Python",
    "javascript": "JavaScript",
    "java": "Java",
    "go": "Go",
}


def _lang_usage(series: pd.Series, lang_name: str) -> pd.Series:
    """セミコロン区切りの回答列から言語名を完全一致で検索する。

    str.contains('Java') だと JavaScript にもマッチするため、
    セミコロン分割後の集合で判定する。
    """
    return series.dropna().apply(lambda x: lang_name in str(x).split(";"))


class TrendAnalyzer:
    """マクロ層: 言語別トレンド分析を担うクラス。

    Developer Survey の言語使用率と Stack Overflow タグ統計を組み合わせて
    「言語の盛衰」を多角的に可視化する素材を作る。
    """

    def __init__(self) -> None:
        with open(ROOT_DIR / "config" / "target_languages.yml", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)

    def compute_survey_trend(
        self, survey_dfs: dict[int, pd.DataFrame]
    ) -> pd.DataFrame:
        """Developer Survey から言語別の使用率・習得希望率を年別に集計する。

        usage_pct  : その言語を「使ったことがある」と答えた割合
        want_pct   : その言語を「次に使いたい」と答えた割合
        aspiration : want_pct / usage_pct — 1 より大きいほど「学習需要 > 現在使用」
        """
        records: list[dict] = []
        have_col = "LanguageHaveWorkedWith"
        want_col = "LanguageWantToWorkWith"

        for year, df in sorted(survey_dfs.items()):
            if have_col not in df.columns:
                logger.warning(f"{year}年: {have_col} 列が見つかりません")
                continue

            have_series = df[have_col].dropna()
            want_series = df[want_col].dropna() if want_col in df.columns else None
            n_resp = len(have_series)

            for lang_key, lang_name in _LANG_DISPLAY.items():
                have_count = _lang_usage(have_series, lang_name).sum()
                usage_pct = round(have_count / n_resp * 100, 2)

                want_pct = None
                if want_series is not None:
                    want_count = _lang_usage(want_series, lang_name).sum()
                    want_pct = round(want_count / len(want_series) * 100, 2)

                records.append(
                    {
                        "year": year,
                        "language": lang_key,
                        "display_name": lang_name,
                        "respondents": n_resp,
                        "usage_pct": usage_pct,
                        "want_pct": want_pct,
                        "aspiration": (
                            round(want_pct / usage_pct, 3)
                            if want_pct and usage_pct > 0
                            else None
                        ),
                    }
                )
                logger.info(
                    f"  {year} {lang_name}: 使用率={usage_pct}% 希望率={want_pct}%"
                )

        return pd.DataFrame(records)

    def compute_yearly_counts(self, df: pd.DataFrame) -> pd.DataFrame:
        """質問サンプルから言語別・年別の品質指標を集計する。

        サンプリング設計上、件数は均等なため質問数ではなく
        スコア・閲覧数の中央値を指標とする。
        """
        return (
            df.groupby(["language", "year"])
            .agg(
                sample_count=("question_id", "count"),
                median_score=("score", "median"),
                median_views=("view_count", "median"),
                answer_rate=("is_answered", "mean"),
            )
            .round(2)
            .reset_index()
        )

    def merge_survey_data(
        self,
        yearly_df: pd.DataFrame,
        survey_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """質問指標と Developer Survey 使用率を year × language で結合する。"""
        return yearly_df.merge(survey_df, on=["year", "language"], how="left")

    def build_web_json(
        self,
        survey_df: pd.DataFrame,
        tags_df: pd.DataFrame,
        output_path: Path,
    ) -> None:
        """フロントエンド（Plotly）用の trends.json を生成する。

        形式:
          {
            "survey": { "years": [...], "languages": { lang: {usage_pct, want_pct} } },
            "ecosystem": { lang: { "total_questions": N, "color": "#..." } }
          }
        """
        years = sorted(survey_df["year"].unique().tolist())
        languages: dict[str, dict] = {}

        lang_config = self._config["languages"]
        for lang_key in _LANG_DISPLAY:
            sub = survey_df[survey_df["language"] == lang_key].sort_values("year")
            cfg = lang_config.get(lang_key, {})

            # タグ統計から総質問数を取得
            tag_row = tags_df[tags_df["name"] == lang_key]
            total_q = int(tag_row["count"].iloc[0]) if not tag_row.empty else 0

            languages[lang_key] = {
                "display_name": _LANG_DISPLAY[lang_key],
                "color": cfg.get("color", "#888888"),
                "usage_pct": sub["usage_pct"].tolist(),
                "want_pct": sub["want_pct"].tolist(),
                "total_questions": total_q,
            }

        payload = {"years": years, "languages": languages}
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"trends.json を出力: {output_path}")
