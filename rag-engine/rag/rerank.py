import re

from config import RERANK_MODEL, RERANK_PROVIDER
from llm_client import create_client
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
NO_TEMPERATURE = 0
FIRST_MESSAGE = 0


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


def apply_ranking(chunks: list[dict], ranking: list[int]) -> list[dict]:
    ranked_indices = {rank - 1 for rank in ranking}

    reranked = [chunks[rank - 1] for rank in ranking]

    remaining = [
        chunk for i, chunk in enumerate(chunks) if i not in ranked_indices
    ]

    return reranked + remaining


def do_rerank(question: str, chunks: list[dict]) -> list[dict]:
    client = create_client(provider=RERANK_PROVIDER)
    messages = build_rerank_messages(question=question, chunks=chunks)
    response = client.chat.completions.create(
        model=RERANK_MODEL, messages=messages, temperature=NO_TEMPERATURE
    )
    ranking = parse_ranking(
        text=response.choices[FIRST_MESSAGE].message.content,
        chunk_count=len(chunks),
    )
    reranking = apply_ranking(chunks=chunks, ranking=ranking)

    return reranking


if __name__ == '__main__':
    ##Test the reranked by calling this file in terminal
    import config
    from llm_client import embed
    from rag.vector_store import search_chunks

    question = 'Cosa significa il codice E05 sulla caldaia?'
    vector = embed([question])[0]
    chunks = search_chunks(
        vector, 'f1', config.EMBEDDING_MODEL, config.RERANK_CANDIDATES
    )

    print('PRIMA:')
    for chunk in chunks:
        print(f'  {chunk["document_id"]}-{chunk["chunk_index"]:04d}')

    print('DOPO:')
    for chunk in do_rerank(question, chunks):
        print(f'  {chunk["document_id"]}-{chunk["chunk_index"]:04d}')
