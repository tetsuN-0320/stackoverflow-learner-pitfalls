from __future__ import annotations

import pandas as pd


class TrendAnalyzer:
    """マクロ層: 言語別質問数の時系列分析を担うクラス。

    Developer Survey の「使用言語」データとの突合も行う。
    Day 5 で実装する。
    """

    def compute_yearly_counts(self, df: pd.DataFrame) -> pd.DataFrame:
        """言語×年の質問数集計テーブルを返す。"""
        raise NotImplementedError("Day 5 で実装")

    def merge_survey_data(
        self,
        trend_df: pd.DataFrame,
        survey_dfs: dict[int, pd.DataFrame],
    ) -> pd.DataFrame:
        """API質問数とDeveloper Survey使用率を結合する。"""
        raise NotImplementedError("Day 5 で実装")
