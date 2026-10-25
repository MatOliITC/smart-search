import pytest

from rag.prompt import (
    SYSTEM_PROMPT,
    build_messages,
    extract_sources,
    format_chunk,
)

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


def test_chunk_is_correctly_formatted():
    value = format_chunk(1, CHUNKS[0])

    expected = (
        '=== SOURCE [1] (pompa_di_calore.txt, page 5) ===\n'
        'Lorem ipsum dolor sit amet consectetur\n'
        '=== END OF SOURCE [1] ==='
    )

    assert value == expected


def test_build_messages_structure():
    value = build_messages('This is my question', CHUNKS)

    assert len(value) == 2
    assert value[0]['role'] == 'system'
    assert value[0]['content'] == SYSTEM_PROMPT
    assert value[1]['role'] == 'user'


def test_build_messages_returned_content():
    value = build_messages('This is my question', CHUNKS)
    expected = [
        {
            'role': 'system',
            'content': SYSTEM_PROMPT,
        },
        {
            'role': 'user',
            'content': (
                '=== SOURCE [1] (pompa_di_calore.txt, page 5) ===\n'
                'Lorem ipsum dolor sit amet consectetur\n'
                '=== END OF SOURCE [1] ===\n\n'
                '=== SOURCE [2] (pompa_di_calore.txt, page 9) ===\n'
                'Lorem ipsum dolor sit amet consectetur.\n'
                '=== END OF SOURCE [2] ===\n\n'
                '=== SOURCE [3] (pompa_di_calore.txt, page 29) ===\n'
                'Lorem ipsum dolor sit amet consectetur.\n=== END OF SOURCE [3] ===\n\n'
                'Question: This is my question'
            ),
        },
    ]

    assert value == expected
