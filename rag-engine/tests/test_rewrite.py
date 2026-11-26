import pytest

from rag.rewrite import (
    REWRITE_SYSTEM_PROMPT,
    build_rewrite_messages,
    clean_rewrite,
    merge_results,
)


@pytest.mark.parametrize(
    'a, b, expect',
    [
        (
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.4,
                }
            ],
            [
                {
                    'document_id': 'd3',
                    'chunk_index': 3,
                    'score': 0.6,
                }
            ],
            [
                {
                    'document_id': 'd3',
                    'chunk_index': 3,
                    'score': 0.6,
                },
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.4,
                },
            ],
        ),
        (
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.4,
                }
            ],
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.6,
                }
            ],
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.6,
                },
            ],
        ),
        (
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.9,
                }
            ],
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.6,
                }
            ],
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.9,
                },
            ],
        ),
        (
            [
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.4,
                },
                {
                    'document_id': 'd4',
                    'chunk_index': 1,
                    'score': 0.6,
                },
            ],
            [],
            [
                {
                    'document_id': 'd4',
                    'chunk_index': 1,
                    'score': 0.6,
                },
                {
                    'document_id': 'd2',
                    'chunk_index': 1,
                    'score': 0.4,
                },
            ],
        ),
    ],
)
def test_merge_results(a, b, expect):
    assert merge_results(a, b) == expect


def test_build_rewrite_messages():
    SYSTEM_PROMPT = 0
    USER_PROMPT = 1
    messages = build_rewrite_messages(question='Question?')

    assert messages[SYSTEM_PROMPT]['role'] == 'system'
    assert messages[SYSTEM_PROMPT]['content'] == REWRITE_SYSTEM_PROMPT
    assert messages[USER_PROMPT]['content'] == 'Question?'


@pytest.mark.parametrize(
    'text, expect',
    [
        (' codice E05 caldaia ', 'codice E05 caldaia'),
        ('codice E05 caldaia\nHo riscritto la domanda.', 'codice E05 caldaia'),
        ('"codice E05 caldaia"', 'codice E05 caldaia'),
        ('', 'Question?'),
        (' \n ', 'Question?'),
        (None, 'Question?'),
        ('x' * 301, 'Question?'),
    ],
)
def test_clean_rewrite(text, expect):
    assert clean_rewrite(text=text, question='Question?') == expect
