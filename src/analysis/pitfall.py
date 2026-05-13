from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from src.preprocessing.stopwords import LANGUAGE_STOPWORDS
from src.utils.logger import logger


class PitfallExtractor:
    """ミクロ層: クラスタリング結果から「つまづきパターン」を抽出するクラス。

    各クラスタの TF-IDF 上位語をラベルとして使い、
    「Python で pandas を学ぶ人がつまづく上位パターン」を可読な形で出力する。
    """

    def label_clusters(
        self,
        df: pd.DataFrame,
        tfidf_vec: TfidfVectorizer,
        text_col: str = "title",
        top_words: int = 5,
        language: str | None = None,
    ) -> dict[int, str]:
        """各クラスタIDに対して TF-IDF 上位語を使った説明ラベルを生成する。

        グローバルIDF（全文書でfit済みのtfidf_vec）を使ってクラスタセントロイドを計算し
        上位語を抽出する。クラスタ内でIDFを再計算するとクラスタ内頻出語が浮上してしまい
        "how", "to" 等のノイズ語がラベルを汚染するため、この方式を採用する。
        """
        feature_names = np.array(tfidf_vec.get_feature_names_out())
        texts = df[text_col].fillna("").tolist()

        # 全文書をグローバルIDF（fit済み）で変換
        X = tfidf_vec.transform(texts)

        # 分析対象言語の言語名をラベルから除外するフィルタ
        lang_exclude: set[str] = set()
        if language and language in LANGUAGE_STOPWORDS:
            lang_exclude = LANGUAGE_STOPWORDS[language]

        labels: dict[int, str] = {}
        cluster_ids = sorted(df["cluster_id"].unique())

        for cluster_id in cluster_ids:
            if cluster_id == -1:
                labels[-1] = "（ノイズ）"
                continue

            mask = (df["cluster_id"] == cluster_id).values
            cluster_matrix = X[mask]

            if cluster_matrix.shape[0] == 0:
                labels[cluster_id] = f"cluster_{cluster_id}"
                continue

            # クラスタセントロイド（平均TF-IDFスコア）で特徴語を選択
            mean_scores = np.asarray(cluster_matrix.mean(axis=0)).flatten()
            sorted_idx = mean_scores.argsort()[::-1]

            top_terms: list[str] = []
            for idx in sorted_idx:
                term = feature_names[idx]
                term_words = term.lower().split()
                # 全語が言語名（"python", "python python"等）→ 除外
                if all(w in lang_exclude for w in term_words):
                    continue
                # bigram で先頭語が言語名（"python numpy", "java spring"等）→ 冗長なので除外
                if len(term_words) > 1 and term_words[0] in lang_exclude:
                    continue
                if len(term) <= 1:
                    continue
                top_terms.append(term)
                if len(top_terms) >= top_words:
                    break

            labels[cluster_id] = " / ".join(top_terms) if top_terms else f"cluster_{cluster_id}"

        return labels

    def extract_top_patterns(
        self,
        df: pd.DataFrame,
        tfidf_vec: TfidfVectorizer,
        language: str,
        top_n: int = 20,
        text_col: str = "title",
        max_cluster_size: int | None = None,
    ) -> pd.DataFrame:
        """言語別のつまづきパターントップN を DataFrame で返す。

        ノイズクラスタ（-1）は除外し、クラスタサイズ降順で返す。
        max_cluster_size を指定すると、それを超える大きすぎるクラスタ（ゴミ箱クラスタ）を除外する。
        """
        lang_df = df[df["language"] == language].copy()
        cluster_labels = self.label_clusters(lang_df, tfidf_vec, text_col, language=language)

        records: list[dict[str, Any]] = []
        for cluster_id, group in lang_df.groupby("cluster_id"):
            if cluster_id == -1:
                continue
            if max_cluster_size is not None and len(group) > max_cluster_size:
                logger.info(f"[{language}] cluster {cluster_id} size={len(group)} > {max_cluster_size}: スキップ")
                continue
            label = cluster_labels.get(cluster_id, f"cluster_{cluster_id}")
            # スコア中央値（0 の質問が多い場合は閲覧数で代替）
            median_score = group["score"].median() if "score" in group.columns else 0.0
            median_views = group["view_count"].median() if "view_count" in group.columns else 0.0
            answer_rate = group["is_answered"].mean() if "is_answered" in group.columns else 0.0

            records.append(
                {
                    "language": language,
                    "cluster_id": cluster_id,
                    "label": label,
                    "size": len(group),
                    "median_score": round(float(median_score), 2),
                    "median_views": round(float(median_views), 1),
                    "answer_rate": round(float(answer_rate), 3),
                }
            )

        result = (
            pd.DataFrame(records)
            .sort_values("size", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        logger.info(f"[{language}] つまづきパターン: {len(result)} クラスタ")
        return result

    def extract_representative_questions(
        self,
        df: pd.DataFrame,
        cluster_id: int,
        n: int = 3,
    ) -> list[dict[str, Any]]:
        """指定クラスタのスコア上位の代表質問を返す。"""
        cluster_df = df[df["cluster_id"] == cluster_id]
        top = cluster_df.nlargest(n, "score") if "score" in cluster_df.columns else cluster_df.head(n)
        return top[["question_id", "title", "score", "view_count"]].to_dict("records")

    def build_web_json(
        self,
        patterns_by_lang: dict[str, pd.DataFrame],
        df: pd.DataFrame,
        output_path: Path,
    ) -> None:
        """フロントエンド用 pitfalls.json を生成する。

        形式:
          {
            lang: [
              {cluster_id, label, size, median_score, median_views,
               answer_rate, examples: [{question_id, title, score}]}
            ]
          }
        """
        payload: dict[str, list[dict]] = {}

        for lang, patterns_df in patterns_by_lang.items():
            lang_df = df[df["language"] == lang]
            items: list[dict] = []
            for _, row in patterns_df.iterrows():
                cid = int(row["cluster_id"])
                examples = self.extract_representative_questions(lang_df, cid, n=3)
                items.append(
                    {
                        "cluster_id": cid,
                        "label": row["label"],
                        "size": int(row["size"]),
                        "median_score": row["median_score"],
                        "median_views": row["median_views"],
                        "answer_rate": row["answer_rate"],
                        "examples": examples,
                    }
                )
            payload[lang] = items

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"pitfalls.json 出力: {output_path}")
