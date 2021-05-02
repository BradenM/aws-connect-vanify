"""Converter tests."""

from pprint import pprint

import pytest
from vanify import convert

samples = {
    "APPLE": "18000027753",
    "HELP": "18002254357",
    "COCONUT": "18002626688",
    "BALL": "8001112255",
    "BAN": "8002264103",
}


@pytest.mark.parametrize("word,number", list(samples.items()))
def test_convert(word: str, number: str):
    res = convert.VanifiedResult.from_phone_number(number, 10)
    pprint(res.node_results)
    for n in res.node_results:
        print(n.score, n)
    assert any([r.current_wordified for r in res.node_results if word in r.current_wordified])


@pytest.mark.parametrize(
    "word,expect",
    [
        (
            "COCONUT",
            "1-800-COCONUT",
        ),
        (
            "BALL",
            "1-800-111-BALL",
        ),
        (
            "BAN",
            "1-800-BAN-4103",
        ),
    ],
)
def test_convert_word_results(word: str, expect: str):
    res = convert.VanifiedResult.from_phone_number(samples[word])
    w_results = res.word_results
    assert expect in w_results


# def test_word_node_score():
#     call_now = convert.WordNode(current_wordified='1800CALLNOW', current_index=11, n_chars=7, max_cont_chars=7, max_substring_length=4)
