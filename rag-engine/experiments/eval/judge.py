from rag.prompt import format_chunk

JUDGE_SYSTEM_PROMPT = (
    'You are a strict judge. Check whether every claim in the answer is '
    'supported by the sources. Pay close attention to negations, times and '
    'numbers (for example "prohibited" versus "allowed").\n'
    'Respond with:\n'
    '- First line: exactly FAITHFUL or UNFAITHFUL.\n'
    '- Second line: the reason, in one sentence.'
)


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
