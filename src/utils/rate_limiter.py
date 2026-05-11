from __future__ import annotations

import time
from collections import deque
from datetime import datetime, timedelta

from src.utils.logger import logger


class RateLimiter:
    """Stack Exchange APIのレート制限を管理するクラス。

    認証ありで1日10,000リクエストの上限がある。
    APIから backoff パラメータが返った場合はその秒数だけ必ず待機する。
    """

    def __init__(self, max_requests_per_day: int = 10_000) -> None:
        self.max_requests_per_day = max_requests_per_day
        self._request_times: deque[datetime] = deque()

    def wait_if_needed(self, backoff: int = 0) -> None:
        """バックオフ待機と日次制限チェックを行い、リクエスト時刻を記録する。"""
        if backoff > 0:
            logger.warning(f"APIからバックオフ指示: {backoff}秒待機します")
            time.sleep(backoff)

        now = datetime.now()
        cutoff = now - timedelta(days=1)
        while self._request_times and self._request_times[0] < cutoff:
            self._request_times.popleft()

        if len(self._request_times) >= self.max_requests_per_day:
            oldest = self._request_times[0]
            wait_seconds = int((oldest + timedelta(days=1) - now).total_seconds()) + 1
            logger.warning(f"日次リクエスト上限に到達。{wait_seconds}秒後に再開します")
            time.sleep(wait_seconds)

        self._request_times.append(datetime.now())

    @property
    def remaining_requests(self) -> int:
        """本日の残りリクエスト可能数を返す。"""
        cutoff = datetime.now() - timedelta(days=1)
        recent = sum(1 for t in self._request_times if t > cutoff)
        return self.max_requests_per_day - recent
