"""Multilingual text normalisation for Nigerian electoral content.

Real claims arrive in English, Nigerian Pidgin, Hausa, Yoruba and Igbo, often
code-switched within a single message, with heavy typos and inconsistent diacritics.
Normalisation here is intentionally light: it must *not* destroy meaning, because
over-aggressive stemming is a common source of silent bias against exactly the languages
the official Track 1 and Track 3 briefs ask us to support.

We normalise:
  * Unicode to NFKC (so visually identical characters compare equal);
  * case, using a locale-independent lower-casing that preserves Yoruba/Hausa/Igbo
    letters (ẹ, ọ, ṣ, ɓ, ɗ, ƙ, ʼ) rather than ASCII-folding them away;
  * runs of whitespace and common punctuation noise;
  * repeated characters used for emphasis ("lateeeeee" -> "late").

We deliberately do NOT strip diacritics, because in Yoruba they are phonemic: "ọwọ"
(hand) and "owo" (money) are different words.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final

# Characters that carry meaning in Nigerian languages and must survive normalisation.
_NIGERIAN_LETTERS: Final[str] = "ẹọṣɓɗƙʼƴṅ"

_NOISE: Final[re.Pattern[str]] = re.compile(r"[\u200b-\u200f\ufeff\u00ad]")
_PUNCT_RUN: Final[re.Pattern[str]] = re.compile(r"[!?.,;:'\"“”‘’()\[\]{}<>/\\|~`^*_+=#@&$%—-]+")
_WS_RUN: Final[re.Pattern[str]] = re.compile(r"\s+")
_CHAR_REPEAT: Final[re.Pattern[str]] = re.compile(r"(.)\1{2,}")
_URL: Final[re.Pattern[str]] = re.compile(r"https?://\S+|www\.\S+")
_DIGIT_RUN: Final[re.Pattern[str]] = re.compile(r"\d{4,}")

# Conservative stop-word set. Only high-frequency function words whose removal is safe
# across the supported languages; anything ambiguous is left in place.
_STOPWORDS: Final[frozenset[str]] = frozenset(
    {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "and", "or", "but", "if", "then", "than", "so", "of", "to", "in", "on",
        "at", "by", "for", "with", "about", "as", "into", "from", "that", "this",
        "these", "those", "it", "its", "they", "them", "their", "we", "our",
        "you", "your", "he", "she", "his", "her", "not", "no", "do", "does",
        "did", "have", "has", "had", "will", "would", "can", "could", "should",
        "dey", "na", "don", "wan", "go", "fit", "sabi", "abeg", "wetin", "sake",
    }
)


def normalise(raw: str) -> str:
    """Return a normalised, comparable form of ``raw``."""
    if not raw:
        return ""
    text = unicodedata.normalize("NFKC", raw)
    text = _NOISE.sub("", text)
    text = _URL.sub(" ", text)
    text = text.lower()
    text = _PUNCT_RUN.sub(" ", text)
    # Long digit runs become a placeholder *after* punctuation is stripped, so the placeholder
    # itself is not mistaken for punctuation and removed.
    text = _DIGIT_RUN.sub(" <num> ", text)
    text = _CHAR_REPEAT.sub(r"\1\1", text)
    text = _WS_RUN.sub(" ", text).strip()
    return text


def tokenise(raw: str, drop_stopwords: bool = True) -> list[str]:
    """Tokenise normalised text into content words."""
    tokens = [t for t in normalise(raw).split(" ") if t]
    if drop_stopwords:
        kept = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
        # Never return an empty list: a claim of only stop-words is still a claim.
        return kept or tokens
    return tokens


def content_words(raw: str) -> str:
    """Space-joined content words, for vectorisers that take raw strings."""
    return " ".join(tokenise(raw))


def character_ngrams(raw: str, n: int = 4) -> list[str]:
    """Character n-grams over normalised text.

    Character n-grams are chosen over word features for matching because they survive
    typos, agglutination and code-switching far better, which is precisely what the
    official Track 1 success criteria measure ("robustness to paraphrase / typos /
    code-switching").
    """
    compact = normalise(raw).replace(" ", "_")
    if len(compact) < n:
        return [compact] if compact else []
    return [compact[i : i + n] for i in range(len(compact) - n + 1)]


def jaccard(a: str, b: str) -> float:
    """Character-4-gram Jaccard similarity. Deterministic baseline, no model."""
    sa, sb = set(character_ngrams(a)), set(character_ngrams(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
