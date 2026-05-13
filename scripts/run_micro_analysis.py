"""Day 7: ミクロ分析（TF-IDF + HDBSCAN クラスタリング＋つまづきパターン抽出）を実行するスクリプト。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from config.settings import ANALYSIS_DIR, PROCESSED_DIR, ROOT_DIR
from src.analysis.clustering import QuestionClusterer
from src.analysis.pitfall import PitfallExtractor
from src.utils.logger import logger

LANGUAGES = ["python", "javascript", "java", "go"]


def _tags_to_str(tags_val: object) -> str:
    """タグ列（list / numpy array）をスペース区切り文字列に変換する。

    ハイフン付きタグ（python-3.x, django-views等）はアンダースコアに置換して
    TF-IDFが1トークンとして扱えるようにする（django_views → "djangoviews"にならない）。
    """
    if isinstance(tags_val, (list, np.ndarray)):
        return " ".join(str(t).replace("-", "_") for t in tags_val)
    return ""


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    questions_df = pd.read_parquet(PROCESSED_DIR / "questions.parquet")
    logger.info(f"質問数: {len(questions_df):,}")

    # タイトル＋タグを結合した特徴量列を追加（タグがクラスタ識別力を大幅向上させる）
    questions_df = questions_df.copy()
    questions_df["text_combined"] = (
        questions_df["title"].fillna("") + " " + questions_df["tags"].apply(_tags_to_str)
    )

    all_clusters: list[pd.DataFrame] = []
    patterns_by_lang: dict[str, pd.DataFrame] = {}
    tfidf_by_lang = {}

    extractor = PitfallExtractor()

    for lang in LANGUAGES:
        logger.info(f"\n=== {lang} ===")
        clusterer = QuestionClusterer(
            max_features=5_000,
            n_components=50,
            min_cluster_size=25,
            min_samples=3,
        )
        clustered_df = clusterer.fit_transform(
            questions_df, text_col="text_combined", language=lang
        )
        all_clusters.append(clustered_df)

        tfidf_vec = clusterer.tfidf_vectorizer
        tfidf_by_lang[lang] = tfidf_vec

        if tfidf_vec is None:
            logger.warning(f"[{lang}] TF-IDFベクトライザーが未フィット")
            continue

        patterns = extractor.extract_top_patterns(
            clustered_df, tfidf_vec, language=lang, top_n=20,
            text_col="text_combined", max_cluster_size=200,
        )
        patterns_by_lang[lang] = patterns

        print(f"\n[{lang}] つまづきパターントップ10:")
        for _, row in patterns.head(10).iterrows():
            print(
                f"  cluster {int(row['cluster_id']):>3}  "
                f"size={int(row['size']):>4}  "
                f"answer_rate={row['answer_rate']:.0%}  "
                f"{row['label']}"
            )

    # クラスタ結果を parquet 保存
    clusters_df = pd.concat(all_clusters, ignore_index=True)
    out_clusters = ANALYSIS_DIR / "clusters.parquet"
    clusters_df.to_parquet(out_clusters, index=False)
    logger.info(f"clusters.parquet 保存: {out_clusters}")

    # パターン一覧を parquet 保存
    if patterns_by_lang:
        pitfalls_df = pd.concat(patterns_by_lang.values(), ignore_index=True)
        out_pitfalls = ANALYSIS_DIR / "pitfalls.parquet"
        pitfalls_df.to_parquet(out_pitfalls, index=False)
        logger.info(f"pitfalls.parquet 保存: {out_pitfalls}")

    # フロントエンド用 JSON 生成
    out_json = ROOT_DIR / "web" / "static" / "data" / "pitfalls.json"
    extractor.build_web_json(patterns_by_lang, clusters_df, out_json)

    logger.info("Day 7 完了")


if __name__ == "__main__":
    main()
