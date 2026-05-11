from __future__ import annotations

from typing import Any

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

    def fetch_questions_by_tag(
        self,
        tag: str,
        from_date: int,
        to_date: int,
        page: int = 1,
    ) -> dict[str, Any]:
        """タグ指定で質問一覧を取得する。日付はUNIXタイムスタンプで渡す。"""
        params = self._common_params(
            tagged=tag,
            fromdate=from_date,
            todate=to_date,
            page=page,
            pagesize=STACKEX_PAGE_SIZE,
            order="desc",
            sort="creation",
        )
        return self._get("questions", params)

    def fetch_tag_info(self, tags: list[str]) -> dict[str, Any]:
        """タグの統計情報（質問数・タグ名）を取得する。"""
        params = self._common_params(
            inname=";".join(tags),
            order="desc",
            sort="popular",
            pagesize=STACKEX_PAGE_SIZE,
        )
        return self._get("tags", params)
