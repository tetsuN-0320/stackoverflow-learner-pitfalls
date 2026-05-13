from __future__ import annotations

# Stack Overflow 質問のテキストマイニングで頻出するが意味を持たない語
# 一般的な英語ストップワードに加えて、プログラミング文書固有の語を除外する
DOMAIN_STOPWORDS: set[str] = {
    # 動作・状態の汎用動詞（どのクラスタにも出るため識別力ゼロ）
    "use", "using", "used",
    "get", "getting", "got",
    "want", "need", "like",
    "know", "work", "working",
    "run", "running",
    "make", "try", "trying",
    "call", "calling", "return",
    "set", "add", "check",
    "fix", "fixing", "find", "finding",
    "show", "display", "create", "update",
    # プログラミング文書の汎用名詞
    "code", "function", "variable",
    "value", "type", "object",
    "class", "method", "print",
    "data", "file", "list",
    "string", "number", "output",
    "input", "result", "answer",
    "question", "example",
    "following", "below", "above",
    "way", "possible", "help",
    "issue", "problem", "error",  # どのクラスタにも出る
    "different", "simple", "new",
    "multiple", "single", "custom",
    "given", "specific", "particular",
    # 質問表現の汎用語
    "properly", "correctly", "automatically",
    "still", "already", "always",
}

# 言語名ストップワード: クラスタラベル生成時に言語固有ラベルを汚染しないよう除外する
LANGUAGE_STOPWORDS: dict[str, set[str]] = {
    "python": {"python", "py"},
    "javascript": {"javascript", "js"},
    "java": {"java"},
    "go": {"go", "golang"},
}
