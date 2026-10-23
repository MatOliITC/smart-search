import pytest

from rag.chunking import chunk_pages

SMALL_CHUNK_SIZE = 30
SMALL_CHUNK_OVERLAP = 10
BIG_CHUNK_SIZE = 800
BIG_CHUNK_OVERLAP = 150

MANUAL_INTRO = (
    "Manuale d'uso - Pompa di calore aria-acqua HP-9\n\n"
    '1. Introduzione\n'
    "La pompa di calore HP-9 preleva calore dall'aria esterna"
)
MANUAL_WINTER = (
    'Il collegamento elettrico deve essere eseguito da un tecnico abilitato '
    'su una linea dedicata da 16 A.\n\n'
    '3. Funzionamento in inverno\n'
    'Con temperature esterne inferiori a 5 °C la batteria '
    "dell'unità esterna può coprirsi di brina."
)


def test_short_text():
    pages = [{'page': 1, 'text': MANUAL_INTRO}]

    result = chunk_pages(pages, BIG_CHUNK_SIZE, BIG_CHUNK_OVERLAP)
    assert result == [{'chunk_index': 0, 'page': 1, 'text': MANUAL_INTRO}]


def test_all_chunk_is_in_chunk_size():
    pages = [{'page': 1, 'text': MANUAL_INTRO}]

    results = chunk_pages(pages, SMALL_CHUNK_SIZE, SMALL_CHUNK_OVERLAP)
    assert len(results) > 1
    for result in results:
        assert len(result['text']) <= SMALL_CHUNK_SIZE


def test_chunk_index_is_progressive():
    pages = [
        {'page': 1, 'text': MANUAL_INTRO},
        {'page': 2, 'text': MANUAL_WINTER},
    ]

    results = chunk_pages(pages, SMALL_CHUNK_SIZE, SMALL_CHUNK_OVERLAP)
    indexes = [result['chunk_index'] for result in results]
    assert indexes == list(range(len(results)))


def test_chunk_in_same_page():
    pages = [
        {'page': 1, 'text': MANUAL_INTRO},
        {'page': 2, 'text': MANUAL_WINTER},
    ]

    results = chunk_pages(pages, BIG_CHUNK_SIZE, BIG_CHUNK_OVERLAP)
    assert results == [
        {'chunk_index': 0, 'page': 1, 'text': MANUAL_INTRO},
        {'chunk_index': 1, 'page': 2, 'text': MANUAL_WINTER},
    ]


@pytest.mark.parametrize('empty_text', ['', '   \n   '])
def test_without_text_dont_produce_chunks(empty_text):
    pages = [
        {'page': 1, 'text': MANUAL_INTRO},
        {'page': 2, 'text': empty_text},
        {'page': 3, 'text': MANUAL_WINTER},
    ]

    results = chunk_pages(pages, BIG_CHUNK_SIZE, BIG_CHUNK_OVERLAP)
    assert results == [
        {'chunk_index': 0, 'page': 1, 'text': MANUAL_INTRO},
        {'chunk_index': 1, 'page': 3, 'text': MANUAL_WINTER},
    ]
