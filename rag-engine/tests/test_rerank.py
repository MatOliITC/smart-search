import pytest

from rag.rerank import parse_ranking


@pytest.mark.parametrize(
    'llm_response, chunk_count, expected',
    [
        ('[3, 1, 2]', 3, [3, 1, 2]),
        ("Ecco l'ordine: [2, 1]", 3, [2, 1]),
        ('[2, 2, 1]', 3, [2, 1]),
        ('[7, 1]', 3, [1]),
        ('[0, 1]', 2, [1]),
        ('[]', 2, []),
        ('Non lo so', 2, []),
    ],
)
def test_parse_ranking(llm_response, chunk_count, expected):
    assert parse_ranking(text=llm_response, chunk_count=chunk_count) == expected
