import pytest

from rag.prompt import extract_sources

CHUNKS = [
    {
        'document_id': 'd1',
        'document_name': 'pompa_di_calore.txt',
        'page': 5,
        'text': 'Lorem ipsum dolor sit amet consectetur',
    },
    {
        'document_id': 'd1',
        'document_name': 'pompa_di_calore.txt',
        'page': 9,
        'text': 'Lorem ipsum dolor sit amet consectetur.',
    },
    {
        'document_id': 'd1',
        'document_name': 'pompa_di_calore.txt',
        'page': 29,
        'text': 'Lorem ipsum dolor sit amet consectetur.',
    },
]


def test_quote_return_first_chunk():
    answer = 'Vero [1]. Vero anche [1].'

    result = extract_sources(answer, CHUNKS)
    assert result == [
        {
            'number': 1,
            'document_id': 'd1',
            'document_name': 'pompa_di_calore.txt',
            'page': 5,
        }
    ]


def test_multiple_quotes():
    answer = 'Vero [2][3]. Anche [1][2].'

    result = extract_sources(answer, CHUNKS)
    assert result == [
        {
            'number': 2,
            'document_id': 'd1',
            'document_name': 'pompa_di_calore.txt',
            'page': 9,
        },
        {
            'number': 3,
            'document_id': 'd1',
            'document_name': 'pompa_di_calore.txt',
            'page': 29,
        },
        {
            'number': 1,
            'document_id': 'd1',
            'document_name': 'pompa_di_calore.txt',
            'page': 5,
        },
    ]


@pytest.mark.parametrize('answer', ['Vero [12].', 'Vero. [0]', 'Vero.'])
def test_returns_no_sources(answer):
    result = extract_sources(answer, CHUNKS)
    assert result == []
