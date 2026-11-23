import pytest

from rag.rerank import (
    RERANK_SYSTEM_PROMPT,
    build_rerank_messages,
    parse_ranking,
)

CHUNKS = [
    {
        'document_id': 'd1',
        'document_name': 'doc1.txt',
        'page': 2,
        'chunk_index': 1,
        'score': 0.456,
        'text': 'Testo del primo chunk',
    },
    {
        'document_id': 'd2',
        'document_name': 'doc2.txt',
        'page': 3,
        'chunk_index': 4,
        'score': 0.325,
        'text': 'Testo del secondo chunk',
    },
]
SYSTEM = 0
USER = 1


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


def test_build_rerank_messages():
    messages = build_rerank_messages(
        question='This is a question?', chunks=CHUNKS
    )
    found_roles = [message['role'] for message in messages]
    user_content = messages[USER]['content']

    assert found_roles == ['system', 'user']
    assert messages[SYSTEM]['content'] == RERANK_SYSTEM_PROMPT
    assert user_content.startswith('=== SOURCE [1]')
    assert 'SOURCE [2]' in user_content
    assert 'Testo del primo chunk' in user_content
    assert 'Testo del secondo chunk' in user_content
    assert user_content.endswith('Question: This is a question?')
