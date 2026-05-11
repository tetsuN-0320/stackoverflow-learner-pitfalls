from __future__ import annotations

import pytest


class TestStackExClient:
    def test_cache_key_is_deterministic(self) -> None:
        from src.utils.cache import SqliteCache
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            cache = SqliteCache(Path(tmp) / "test.sqlite")
            params = {"a": 1, "b": "x"}
            key1 = SqliteCache._make_key(params)
            key2 = SqliteCache._make_key({"b": "x", "a": 1})
            assert key1 == key2

    def test_cache_set_and_get(self) -> None:
        from src.utils.cache import SqliteCache
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            cache = SqliteCache(Path(tmp) / "test.sqlite")
            params = {"endpoint": "questions", "tag": "python"}
            cache.set(params, {"items": []})
            result = cache.get(params)
            assert result == {"items": []}

    @pytest.mark.integration
    def test_fetch_questions_real_api(self) -> None:
        from src.api.stackex_client import StackExClient
        client = StackExClient()
        result = client.fetch_questions_by_tag("python", from_date=1700000000, to_date=1700100000)
        assert "items" in result
