from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

from src.preprocessing.stopwords import DOMAIN_STOPWORDS
from src.utils.logger import logger

# sklearn の英語ストップワード + ドメイン固有語を合わせた除外リスト
_TFIDF_STOPWORDS = list(ENGLISH_STOP_WORDS | DOMAIN_STOPWORDS)

try:
    import hdbscan
    _HAS_HDBSCAN = True
except ImportError:
    _HAS_HDBSCAN = False
    logger.warning("hdbscan が未インストール。クラスタリングをスキップします。")


class QuestionClusterer:
    """ミクロ層: 質問テキストのトピッククラスタリングを担うクラス。

    TF-IDF でベクトル化 → LSA（TruncatedSVD）で次元削減 → HDBSCAN でクラスタ検出。
    HDBSCAN はクラスタ数を事前指定不要で、ノイズ点（-1）を明示的に扱える。
    """

    def __init__(
        self,
        max_features: int = 5_000,
        n_components: int = 50,
        min_cluster_size: int = 25,
        min_samples: int = 3,
    ) -> None:
        self._tfidf_pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        max_features=max_features,
                        ngram_range=(1, 2),
                        sublinear_tf=True,  # log(1+tf) でスケーリング
                        min_df=3,
                        stop_words=_TFIDF_STOPWORDS,
                    ),
                ),
                ("svd", TruncatedSVD(n_components=n_components, random_state=42)),
                ("norm", Normalizer(copy=False)),
            ]
        )
        self._min_cluster_size = min_cluster_size
        self._min_samples = min_samples
        self._tfidf_vec: TfidfVectorizer | None = None

    def vectorize(self, texts: list[str]) -> np.ndarray:
        """TF-IDF + LSA でテキストをベクトル化する。"""
        vectors: np.ndarray = self._tfidf_pipeline.fit_transform(texts)
        # fit 済み TfidfVectorizer を後で特徴語抽出に使う
        self._tfidf_vec = self._tfidf_pipeline.named_steps["tfidf"]
        logger.info(f"ベクトル化完了: {vectors.shape}")
        return vectors

    def cluster(self, vectors: np.ndarray) -> np.ndarray:
        """HDBSCAN でクラスタラベルを付与する。-1 はノイズ点。"""
        if not _HAS_HDBSCAN:
            logger.warning("hdbscan 未インストール。全点をクラスタ 0 に割り当てます。")
            return np.zeros(len(vectors), dtype=int)

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self._min_cluster_size,
            min_samples=self._min_samples,
            metric="euclidean",
            cluster_selection_method="eom",
        )
        labels: np.ndarray = clusterer.fit_predict(vectors)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        noise_ratio = (labels == -1).mean()
        logger.info(
            f"クラスタ数: {n_clusters}  ノイズ比: {noise_ratio:.1%}"
        )
        return labels

    def fit_transform(
        self,
        df: pd.DataFrame,
        text_col: str = "title",
        language: str | None = None,
    ) -> pd.DataFrame:
        """指定列のテキストにクラスタIDを付与した DataFrame を返す。

        language を指定すると該当言語のみに絞って処理する。
        """
        target = df[df["language"] == language].copy() if language else df.copy()
        texts = target[text_col].fillna("").tolist()

        vectors = self.vectorize(texts)
        labels = self.cluster(vectors)

        target = target.reset_index(drop=True)
        target["cluster_id"] = labels
        return target

    @property
    def tfidf_vectorizer(self) -> TfidfVectorizer | None:
        """fit 済みの TfidfVectorizer を返す（特徴語抽出用）。"""
        return self._tfidf_vec
