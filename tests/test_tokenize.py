from folder2kb.tokenize import tokenize


def test_english_words_lowercased() -> None:
    assert tokenize("Refund-Policy, 30 days!") == ["refund", "policy", "30", "days"]


def test_chinese_unigrams_and_bigrams() -> None:
    assert tokenize("退货政策") == ["退", "货", "政", "策", "退货", "货政", "政策"]


def test_mixed_text_splits_scripts() -> None:
    toks = tokenize("Acme小店returns")
    assert "acme" in toks and "returns" in toks
    assert "小店" in toks


def test_punctuation_breaks_cjk_runs() -> None:
    toks = tokenize("退货，政策")
    assert "货政" not in toks
    assert "退货" in toks and "政策" in toks


def test_empty() -> None:
    assert tokenize("  ，。!!") == []
