from llm_client import create_client
from rag.prompt import format_chunk

JUDGE_SYSTEM_PROMPT = (
    'You are a strict judge. Check whether every claim in the answer is '
    'supported by the sources. Pay close attention to negations, times and '
    'numbers (for example "prohibited" versus "allowed").\n'
    'Respond with:\n'
    '- First line: exactly FAITHFUL or UNFAITHFUL.\n'
    '- Second line: the reason, in one sentence.'
)

JUDGE_PROVIDER = 'openai'
JUDGE_MODEL = 'gpt-5.4-mini'


def build_judge_messages(
    question: str, chunks: list[dict], answer: str
) -> list[dict]:
    formatted_chunks = [
        format_chunk(i + 1, chunk) for i, chunk in enumerate(chunks)
    ]
    context = '\n\n'.join(formatted_chunks)
    user_content = f'{context}\n\nQuestion: {question}\n\nAnswer: {answer}'

    return [
        {'role': 'system', 'content': JUDGE_SYSTEM_PROMPT},
        {'role': 'user', 'content': user_content},
    ]


def parse_verdict(text: str) -> bool | None:
    first_line = text.splitlines()[0].strip() if text.splitlines() else ''

    if first_line == 'FAITHFUL':
        return True
    if first_line == 'UNFAITHFUL':
        return False
    return None


def judge(
    question: str, chunks: list[dict], answer: str
) -> tuple[bool | None, str]:
    client = create_client(JUDGE_PROVIDER)
    messages = build_judge_messages(
        question=question, chunks=chunks, answer=answer
    )
    response = client.chat.completions.create(
        model=JUDGE_MODEL, messages=messages, temperature=0
    )

    text = response.choices[0].message.content
    return parse_verdict(text), text


if __name__ == '__main__':
    chunk = {
        'document_name': 'regolamento_condominio.txt',
        'page': 1,
        'text': (
            'Per garantire il riposo di tutti è vietato produrre rumori '
            'molesti dalle ore 14 alle ore 16 e dalle ore 22 alle ore 8. Nei '
            'giorni festivi il silenzio va rispettato anche dalle ore 12 alle '
            'ore 16. Strumenti musicali, elettrodomestici rumorosi e feste '
            'vanno limitati agli orari consentiti.'
        ),
    }
    question = 'In quali orari non si può fare rumore nel condominio?'
    cases = [
        (
            'Si può fare rumore nel condominio dalle ore 8 alle ore 14, '
            'dalle ore 16 alle ore 19 e dalle ore 22 alle ore 8 [1]. Nei '
            'giorni festivi il silenzio va rispettato anche dalle ore 12 '
            'alle ore 16 [1].',
            False,
        ),
        (
            'Nel condominio è vietato produrre rumori molesti dalle 14 alle '
            '16 e dalle 22 alle 8 [1]; nei giorni festivi anche dalle 12 '
            'alle 16 [1].',
            True,
        ),
    ]

    for answer, expected in cases:
        verdict, text = judge(question=question, answer=answer, chunks=[chunk])
        print('--------')
        print(f'Risposta: {answer}')
        print(f'Atteso: {expected} | Giudice: {verdict}')
        print(f'Testo del giudice: {text}')
