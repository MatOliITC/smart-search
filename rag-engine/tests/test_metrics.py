import pytest

from experiments.eval.metrics import (
    answer_presence_ok,
    hit_at_k,
    keyword_coverage,
    reciprocal_rank,
)

RETRIEVED = ['d1-0002', 'd4-0002', 'd5-0001', 'd3-0002', 'd4-0001']


@pytest.mark.parametrize(
    'relevant, k, expected',
    [
        (['d3-0002'], 3, 0),
        (['d1-0002'], 3, 1),
        (['d4-0002'], 5, 1),
        (['d10-0001'], 4, 0),
        (['d1-0002', 'd4-0002', 'd5-0001', 'd3-0002', 'd4-0001'], 1, 1),
    ],
)
def test_hit_at_k(relevant, k, expected):
    assert hit_at_k(RETRIEVED, relevant, k) == expected


@pytest.mark.parametrize(
    'relevant, expected',
    [
        (['d1-0002'], 1),
        (['d4-0002'], 0.5),
        (['d10-0001'], 0),
        (['d3-0002'], 0.25),
        (['d4-0002', 'd3-0002'], 0.5),
    ],
)
def test_reciprocal_rank(relevant, expected):
    assert reciprocal_rank(RETRIEVED, relevant) == expected


@pytest.mark.parametrize(
    'answer, keywords, expected',
    [
        ('Test delle mie keyword', ['test', 'mie', 'keyword'], 1.0),
        ('Test delle mie keyword', ['Altre', 'parole'], 0.0),
        ('Test delle mie keyword', ['test', 'parole'], 0.5),
        ('Test delle mie keyword', ['Delle', 'Mie', 'Keyword'], 1.0),
        (None, ['Delle', 'Mie', 'Keyword'], 0.0),
    ],
)
def test_keyword_coverage(answer, keywords, expected):
    assert keyword_coverage(answer, keywords) == expected


@pytest.mark.parametrize(
    'relevant, answer, expect',
    [
        (['Lorem Ipsum dolor sit amet'], 'This is my response', True),
        (['Lorem Ipsum dolor sit amet'], None, False),
        ([], None, True),
        ([], 'This is my response', False),
    ],
)
def test_answer_presence_ok(relevant, answer, expect):
    assert answer_presence_ok(answer, relevant) == expect
