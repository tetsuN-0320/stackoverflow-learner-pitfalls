from __future__ import annotations

from datetime import datetime
from typing import Any, Iterator

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import (
    RAW_DIR,
    STACKEX_API_KEY,
    STACKEX_APP_NAME,
    STACKEX_BASE_URL,
    STACKEX_PAGE_SIZE,
)
from src.utils.cache import SqliteCache
from src.utils.logger import logger
from src.utils.rate_limiter import RateLimiter

# マクロ・メゾ分析（タグ・日時のみ必要）とミクロ分析（本文必要）でフィルターを使い分ける
_FILTER_DEFAULT = "default"     # title, tags, creation_date, score 等
_FILTER_WITH_BODY = "withbody"  # default の全フィールド + body（HTML形式）


class StackExClient:
    """Stack Exchange API v2.3 ラッパー。レート制限・バックオフ・SQLiteキャッシュを内包する。"""

    def __init__(self) -> None:
        self.base_url = STACKEX_BASE_URL
        self.api_key = STACKEX_API_KEY
        self.cache = SqliteCache(RAW_DIR / "stackex_cache.sqlite")
        self.rate_limiter = RateLimiter()
        self.session = requests.Session()
        self.session.headers["User-Agent"] = STACKEX_APP_NAME

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
    )
    def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """GETリクエストを送信する。キャッシュヒット時はAPIを呼ばない。"""
        cache_key = {"endpoint": endpoint, **params}
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"キャッシュヒット: {endpoint}")
            return cached

        self.rate_limiter.wait_if_needed()
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        if backoff := data.get("backoff", 0):
            self.rate_limiter.wait_if_needed(backoff=backoff)

        self.cache.set(cache_key, data)
        return data

    def _common_params(self, **kwargs: Any) -> dict[str, Any]:
        return {"site": "stackoverflow", "key": self.api_key, **kwargs}

    def fetch_questions_page(
        self,
        tag: str,
        from_date: int,
        to_date: int,
        page: int = 1,
        include_body: bool = False,
    ) -> dict[str, Any]:
        """タグ・期間指定で質問を1ページ（最大100件）取得する。"""
        params = self._common_params(
            tagged=tag,
            fromdate=from_date,
            todate=to_date,
            page=page,
            pagesize=STACKEX_PAGE_SIZE,
            order="asc",
            sort="creation",
            filter=_FILTER_WITH_BODY if include_body else _FILTER_DEFAULT,
        )
        return self._get("questions", params)

    def iter_questions_by_tag(
        self,
        tag: str,
        from_date: int,
        to_date: int,
        include_body: bool = False,
    ) -> Iterator[dict[str, Any]]:
        """タグ・期間指定で全ページの質問をイテレートする。

        API の has_more フラグを見てページネーションを自動処理する。
        大量取得時は SQLite キャッシュが再実行コストを吸収する。
        """
        page = 1
        total = 0
        while True:
            data = self.fetch_questions_page(
                tag, from_date, to_date, page=page, include_body=include_body
            )
            items = data.get("items", [])
            total += len(items)
            yield from items

            quota = data.get("quota_remaining", "?")
            logger.info(
                f"  [{tag}] page={page} 取得={len(items)}件 累計={total}件 残クォータ={quota}"
            )

            if not data.get("has_more", False):
                break
            page += 1

    def fetch_tag_info(self, tags: list[str]) -> dict[str, Any]:
        """指定タグの統計情報（質問数・タグ名）を取得する。

        /tags/{tags}/info エンドポイントを使い完全一致で複数タグを一括取得する。
        inname パラメータは部分一致検索のため、想定タグが返らない場合がある。
        """
        tags_path = ";".join(tags)
        params = self._common_params(
            order="desc",
            sort="popular",
            pagesize=STACKEX_PAGE_SIZE,
        )
        return self._get(f"tags/{tags_path}/info", params)

    @staticmethod
    def year_to_timestamps(year: int) -> tuple[int, int]:
        """年をUNIXタイムスタンプの範囲（年初〜年末）に変換する。"""
        start = int(datetime(year, 1, 1).timestamp())
        end = int(datetime(year, 12, 31, 23, 59, 59).timestamp())
        return start, end
