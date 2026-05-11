from __future__ import annotations

import pytest


class TestSqliteCache:
    def test_cache_key_is_deterministic(self) -> None:
        from pathlib import Path
        import tempfile
        from src.utils.cache import SqliteCache

        with tempfile.TemporaryDirectory() as tmp:
            cache = SqliteCache(Path(tmp) / "test.sqlite")
            key1 = SqliteCache._make_key({"a": 1, "b": "x"})
            key2 = SqliteCache._make_key({"b": "x", "a": 1})
            assert key1 == key2

    def test_cache_set_and_get(self) -> None:
        from pathlib import Path
        import tempfile
        from src.utils.cache import SqliteCache

        with tempfile.TemporaryDirectory() as tmp:
            cache = SqliteCache(Path(tmp) / "test.sqlite")
            params = {"endpoint": "questions", "tag": "python"}
            cache.set(params, {"items": []})
            assert cache.get(params) == {"items": []}

    def test_cache_returns_none_for_missing_key(self) -> None:
        from pathlib import Path
        import tempfile
        from src.utils.cache import SqliteCache

        with tempfile.TemporaryDirectory() as tmp:
            cache = SqliteCache(Path(tmp) / "test.sqlite")
            assert cache.get({"missing": True}) is None


class TestStackExClientStatic:
    def test_year_to_timestamps(self) -> None:
        from src.api.stackex_client import StackExClient

        start, end = StackExClient.year_to_timestamps(2024)
        from datetime import datetime
        assert datetime.fromtimestamp(start) == datetime(2024, 1, 1, 0, 0, 0)
        assert datetime.fromtimestamp(end) == datetime(2024, 12, 31, 23, 59, 59)

    def test_year_to_timestamps_2022(self) -> None:
        from src.api.stackex_client import StackExClient

        start, end = StackExClient.year_to_timestamps(2022)
        assert end > start
        assert end - start >= 365 * 24 * 3600 - 1


class TestStackExClientIntegration:
    @pytest.mark.integration
    def test_fetch_questions_page(self) -> None:
        from src.api.stackex_client import StackExClient

        client = StackExClient()
        start, end = StackExClient.year_to_timestamps(2024)
        data = client.fetch_questions_page("python", start, end, page=1)

        assert "items" in data
        assert len(data["items"]) > 0
        item = data["items"][0]
        assert "question_id" in item
        assert "title" in item
        assert "tags" in item
        assert "creation_date" in item
        assert "python" in item["tags"]

    @pytest.mark.integration
    def test_cache_returns_same_data(self) -> None:
        from src.api.stackex_client import StackExClient

        client = StackExClient()
        start, end = StackExClient.year_to_timestamps(2024)

        data1 = client.fetch_questions_page("python", start, end, page=1)
        data2 = client.fetch_questions_page("python", start, end, page=1)

        # キャッシュから返るので完全に同一データになるはず
        assert [i["question_id"] for i in data1["items"]] == [
            i["question_id"] for i in data2["items"]
        ]
