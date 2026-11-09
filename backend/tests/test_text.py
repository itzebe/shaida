"""Tests for multilingual normalisation.

The rule these tests defend: normalisation must reduce noise **without erasing meaning**.
Yoruba diacritics are phonemic (ọwọ "hand" vs owo "money"), so stripping them would silently
change what a claim says. Hausa and Igbo hooks (ɓ ɗ ƙ ṅ) are equally load-bearing.
"""

from __future__ import annotations

from shdaida import text as T


def test_case_is_folded():
    assert T.normalise("HELLO World") == "hello world"


def test_whitespace_is_collapsed():
    assert T.normalise("a   b\n\t c") == "a b c"


def test_emphasis_repeats_are_reduced():
    assert T.normalise("lateeeee") == "latee"
    assert T.normalise("noooooo") == "noo"


def test_yoruba_diacritics_survive_normalisation():
    normalised = T.normalise("Ọwọ́ ni mo fi ra owo")
    assert "ọwọ" in normalised or "ọwọ́" in normalised
    assert "ọ" in normalised
    # And the two words must remain distinguishable after tokenising.
    assert T.normalise("ọwọ") != T.normalise("owo")


def test_house_and_igbo_hooks_survive():
    assert "ɓ" in T.normalise("Ɓera")
    assert "ƙ" in T.normalise("Ƙarƙashin")
    assert "ị" in T.normalise("Ịga n'ihu")


def test_urls_are_removed():
    assert "http" not in T.normalise("see https://example.com/claim for details")


def test_long_numbers_are_placeholderised():
    assert "<num>" in T.normalise("turnout was 123456 voters")


def test_stopwords_are_dropped_from_tokens():
    tokens = T.tokenise("the result sheet was not uploaded")
    assert "the" not in tokens
    assert "was" not in tokens
    assert "result" in tokens
    assert "uploaded" in tokens


def test_pidgin_stopwords_are_dropped():
    tokens = T.tokenise("dem say the bvas no dey work")
    assert "dey" not in tokens
    assert "bvas" in tokens


def test_tokenise_never_returns_empty_for_a_real_claim():
    """A claim made only of function words is still a claim and must not vanish."""
    assert T.tokenise("na so") != []


def test_character_ngrams_are_built_over_normalised_text():
    grams = T.character_ngrams("evidence", 4)
    assert grams == ["evid", "vide", "iden", "denc", "ence"]


def test_jaccard_is_one_for_identical_text_and_zero_for_disjoint():
    assert T.jaccard("same words here", "same words here") == 1.0
    assert T.jaccard("alpha bravo", "charlie delta") == 0.0


def test_jaccard_tolerates_a_small_typo():
    score = T.jaccard("the result sheet was not uploaded", "the result shet was not uploded")
    assert score > 0.5, "small typos must not collapse similarity"


def test_empty_input_is_handled_without_error():
    assert T.normalise("") == ""
    assert T.tokenise("") == []
    assert T.character_ngrams("", 4) == []
    assert T.jaccard("", "") == 0.0
