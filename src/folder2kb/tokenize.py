"""Shared tokenizer for indexing and querying (Latin words + CJK uni/bigrams)."""

from __future__ import annotations

import re

# CJK Unified Ideographs (+Ext A), compatibility ideographs, Hiragana, Katakana, Hangul.
_CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af"
_TOKEN_RE = re.compile(rf"[{_CJK}]+|[^\W_{_CJK}]+", re.UNICODE)
_CJK_RE = re.compile(rf"^[{_CJK}]+$")


def tokenize(text: str) -> list[str]:
    """Tokenize mixed Chinese/English text.

    - Latin/numeric runs become lowercase words (``"Refund-Policy"`` -> ``["refund", "policy"]``).
    - CJK runs become character unigrams plus overlapping bigrams
      (``"退货政策"`` -> ``["退", "货", "政", "策", "退货", "货政", "政策"]``).
    """
    tokens: list[str] = []
    for match in _TOKEN_RE.finditer(text.lower()):
        run = match.group(0)
        if _CJK_RE.match(run):
            tokens.extend(run)
            tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
        else:
            tokens.append(run)
    return tokens
