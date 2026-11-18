import pytest

from config import vector_table_name


@pytest.mark.parametrize(
    'model_name, expected',
    [
        ('bge-m3', 'chunks_bge-m3'),
        ('text-embedding-3-small', 'chunks_text-embedding-3-small'),
        ('nomic-embed-text:latest', 'chunks_nomic-embed-text_latest'),
    ],
)
def test_vector_table_name(model_name, expected):
    assert vector_table_name(model_name) == expected
