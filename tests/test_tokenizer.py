from __future__ import annotations


class TestTokenizer:
    def test_tokenize_removes_stopwords(self) -> None:
        from src.preprocessing.tokenizer import Tokenizer
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("How do I get the value from a list?")
        assert "i" not in tokens
        assert "the" not in tokens
        assert "from" not in tokens

    def test_tokenize_removes_code_snippets(self) -> None:
        from src.preprocessing.tokenizer import Tokenizer
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("Use `pd.read_csv()` to load files")
        assert "pd.read_csv()" not in " ".join(tokens)
