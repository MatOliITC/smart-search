import pytest

from rag.vector_store import sql_string


@pytest.mark.parametrize(
    'value, expected',
    [
        ('d1', "'d1'"),
        ("l'olio", "'l''olio'"),
        ('a b', "'a b'"),
        ('', "''"),
    ],
)
def test_returns_sql_string(value, expected):
    result = sql_string(value)
    assert result == expected
