import pytest

from experiments.eval.metrics import hit_at_k, reciprocal_rank

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
