import pytest

from experiments.eval.judge import build_judge_messages, parse_verdict


@pytest.mark.parametrize(
    'text,expected',
    [
        ('FAITHFUL\nTutto nelle fonti.', True),
        ('UNFAITHFUL\nLa fonte dice vietato.', False),
        ('La risposta sembra corretta.', None),
        ('', None),
        (' faithful \n..', None),
    ],
)
def test_parse_verdict(text, expected):
    assert parse_verdict(text) is expected


CHUNK = {
    'document_name': 'regolamento.txt',
    'page': 1,
    'text': 'Vietato fare rumore dalle 22 alle 8.',
}
QUESTION = 'This is the question'
ANSWER = 'This is the answer'
USER = 1
SYSTEM = 0


def test_build_judge_messages():
    result = build_judge_messages(
        question=QUESTION, chunks=[CHUNK], answer=ANSWER
    )

    assert len(result) == 2
    assert result[SYSTEM]['role'] == 'system' and result[USER]['role'] == 'user'
    assert 'This is the question' in result[USER]['content']
    assert 'This is the answer' in result[USER]['content']
    assert 'SOURCE [1]' in result[USER]['content']
    assert CHUNK['text'] in result[USER]['content']
