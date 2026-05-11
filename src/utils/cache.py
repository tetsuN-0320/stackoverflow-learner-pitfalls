from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.utils.logger import logger


class SqliteCache:
    """Stack Exchange APIレスポンスをSQLiteにキャッシュするユーティリティ。

    同一クエリの再実行コストをゼロにし、オフライン分析も可能にする。
    TTLを過ぎたキャッシュは自動的に無効化する。
    """

    def __init__(self, db_path: Path, ttl_days: int = 30) -> None:
        self.db_path = db_path
        self.ttl = timedelta(days=ttl_days)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _make_key(params: dict[str, Any]) -> str:
        serialized = json.dumps(params, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get(self, params: dict[str, Any]) -> Any | None:
        """キャッシュを取得する。TTL切れの場合はNoneを返す。"""
        key = self._make_key(params)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value, created_at FROM cache WHERE key = ?", (key,)
            ).fetchone()

        if row is None:
            return None

        created_at = datetime.fromisoformat(row[1])
        if datetime.now() - created_at > self.ttl:
            logger.debug(f"キャッシュ期限切れ: {key[:8]}...")
            return None

        return json.loads(row[0])

    def set(self, params: dict[str, Any], value: Any) -> None:
        """レスポンスをキャッシュに保存する。"""
        key = self._make_key(params)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, created_at) VALUES (?, ?, ?)",
                (key, json.dumps(value), datetime.now().isoformat()),
            )
        logger.debug(f"キャッシュ保存: {key[:8]}...")
