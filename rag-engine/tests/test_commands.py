import commands

CHUNKS = [
    {
        'document_id': 'd1',
        'document_name': 'pompa_di_calore.txt',
        'page': 5,
        'text': 'Il codice E05 indica il blocco per bassa temperatura.',
        'chunk_index': 5,
    },
]


def fake_embed(texts):
    return [[0.0]]


def fake_search_chunks(vector, folder_id, embedding_model, top_k):
    return CHUNKS


def use_fakes(monkeypatch, pieces):
    def fake_generate_stream(messages):
        yield from pieces

    monkeypatch.setattr(commands, 'embed', fake_embed)
    monkeypatch.setattr(commands, 'search_chunks', fake_search_chunks)
    monkeypatch.setattr(commands, 'generate_stream', fake_generate_stream)


def run(question='Cosa significa E05?'):
    return list(commands.run_query('f1', 3, question, False))


def tokens(events):
    return [event['text'] for event in events if event['type'] == 'token']


def test_no_answer_is_held_back(monkeypatch):
    use_fakes(monkeypatch, ['NO', '_', 'ANSWER'])

    events = run()

    assert tokens(events) == []
    assert events[-1] == {
        'type': 'result',
        'question': 'Cosa significa E05?',
        'answer': None,
        'sources': [],
    }


def test_held_back_pieces_are_released_together(monkeypatch):
    use_fakes(monkeypatch, ['NO', ' problem', ' [1].'])

    events = run()

    assert tokens(events) == ['NO problem', ' [1].']
    assert events[-1]['answer'] == 'NO problem [1].'


def test_normal_answer_streams_each_piece(monkeypatch):
    use_fakes(monkeypatch, ['Blocco', ' per bassa', ' temperatura [1].'])

    events = run()

    assert tokens(events) == ['Blocco', ' per bassa', ' temperatura [1].']
    assert events[-1] == {
        'type': 'result',
        'question': 'Cosa significa E05?',
        'answer': 'Blocco per bassa temperatura [1].',
        'sources': [
            {
                'number': 1,
                'document_id': 'd1',
                'document_name': 'pompa_di_calore.txt',
                'page': 5,
                'chunk_index': 5,
            },
        ],
    }
