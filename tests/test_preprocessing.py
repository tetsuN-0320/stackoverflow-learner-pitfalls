from __future__ import annotations


class TestCleaner:
    def test_remove_html(self) -> None:
        from src.preprocessing.cleaner import Cleaner
        cleaner = Cleaner()
        assert cleaner.remove_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_remove_html_empty(self) -> None:
        from src.preprocessing.cleaner import Cleaner
        cleaner = Cleaner()
        assert cleaner.remove_html("") == ""
