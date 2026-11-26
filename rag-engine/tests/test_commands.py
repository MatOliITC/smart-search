import commands
import config

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
    return [[0.0] for _ in texts]


def fake_search_chunks(vector, folder_id, embedding_model, top_k):
    return CHUNKS


def fake_do_rerank(question, chunks):
    return chunks


def fake_do_rewrite(question):
    return 'Domanda riscritta.'


def use_fakes(monkeypatch, pieces):
    def fake_generate_stream(messages):
        yield from pieces

    monkeypatch.setattr(commands, 'embed', fake_embed)
    monkeypatch.setattr(commands, 'search_chunks', fake_search_chunks)
    monkeypatch.setattr(commands, 'generate_stream', fake_generate_stream)
    monkeypatch.setattr(commands, 'do_rerank', fake_do_rerank)
    monkeypatch.setattr(commands, 'do_rewrite', fake_do_rewrite)


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


def test_rerank_reorders_and_keeps_top_k(monkeypatch):
    many_chunks = [
        {
            'document_id': name,
            'document_name': f'{name}.txt',
            'page': 1,
            'text': f'Testo del chunk {name}.',
            'chunk_index': 0,
        }
        for name in ['A', 'B', 'C', 'D']
    ]

    def fake_search_many(vector, folder_id, embedding_model, top_k):
        return many_chunks

    def fake_reverse_rerank(question, chunks):
        return list(reversed(chunks))

    use_fakes(monkeypatch, ['Risposta [1].'])
    monkeypatch.setattr(commands, 'search_chunks', fake_search_many)
    monkeypatch.setattr(commands, 'do_rerank', fake_reverse_rerank)
    monkeypatch.setattr(config, 'RERANK_ENABLED', True)

    events = list(commands.run_query('f1', 2, 'Domanda?', True))

    stages = [event['stage'] for event in events if event['type'] == 'progress']
    assert stages == [
        'embedding_question',
        'searching',
        'reranking',
        'generating',
    ]

    result_ids = [chunk['document_id'] for chunk in events[-1]['chunks']]
    assert result_ids == ['D', 'C']


def make_chunk(document_id, score):
    return {
        'document_id': document_id,
        'document_name': f'{document_id}.txt',
        'page': 1,
        'text': f'Testo del chunk {document_id}.',
        'chunk_index': 0,
        'score': score,
    }


def test_rewrite_merges_both_searches(monkeypatch):
    embedded_texts = []

    def fake_embed_two(texts):
        embedded_texts.extend(texts)
        return [[0.0], [1.0]]

    def fake_search_by_vector(vector, folder_id, embedding_model, top_k):
        if vector == [0.0]:
            return [make_chunk('A', 0.4)]
        return [make_chunk('B', 0.7), make_chunk('A', 0.5)]

    use_fakes(monkeypatch, ['Risposta [1].'])
    monkeypatch.setattr(commands, 'embed', fake_embed_two)
    monkeypatch.setattr(commands, 'search_chunks', fake_search_by_vector)
    monkeypatch.setattr(config, 'REWRITE_ENABLED', True)

    events = list(commands.run_query('f1', 3, 'Domanda?', True))

    stages = [event['stage'] for event in events if event['type'] == 'progress']
    assert stages == [
        'rewriting',
        'embedding_question',
        'searching',
        'generating',
    ]

    assert embedded_texts == ['Domanda?', 'Domanda riscritta.']

    result_chunks = [
        (chunk['document_id'], chunk['score'])
        for chunk in events[-1]['chunks']
    ]
    assert result_chunks == [('B', 0.7), ('A', 0.5)]
