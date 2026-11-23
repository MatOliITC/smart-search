import re

from rag.prompt import format_chunk

RERANK_SYSTEM_PROMPT = (
    'You will receive a question and a set of numbered '
    'sources (=== SOURCE [position] ...).\n'
    'You must rank the sources so that the one that answers '
    'the question most accurately is placed first, followed by '
    'the others in descending order of relevance.\n'
    'You must respond ONLY with the source numbers in JSON format, '
    'for example [3, 1, 2], without adding any other text.'
)


def parse_ranking(text: str, chunk_count: int) -> list[int]:
    match = re.search(r'\[([^\]]+)\]', text)
    parsed_int = (
        [int(number) for number in re.findall(r'\d+', match.group(1))]
        if match
        else []
    )

    seen = set()
    unique_numbers = []

    for num in parsed_int:
        if num not in seen:
            if num > 0 and num <= chunk_count:
                unique_numbers.append(num)
            seen.add(num)

    return unique_numbers


def build_rerank_messages(question: str, chunks: list[dict]) -> list[dict]:
    formatted_chunks = [
        format_chunk(i + 1, chunk) for i, chunk in enumerate(chunks)
    ]

    context = '\n\n'.join(formatted_chunks)
    user_content = f'{context}\n\nQuestion: {question}'
    messages = [
        {'role': 'system', 'content': RERANK_SYSTEM_PROMPT},
        {'role': 'user', 'content': user_content},
    ]

    return messages
