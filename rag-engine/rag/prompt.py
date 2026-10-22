import re

import config

NO_ANSWER = 'NO_ANSWER'

SYSTEM_PROMPT = (
    'You are an assistant that answers questions using only the documents '
    'provided by the user.\n'
    '\n'
    'Rules:\n'
    '1. Use only the information in the provided documents. Do not use '
    'outside knowledge.\n'
    '2. If the documents do not contain the answer, including when the '
    'question is about a topic the documents do not cover, reply with '
    f'exactly {NO_ANSWER} and nothing else. Never invent an answer.\n'
    '3. Cite your sources with their number in square brackets, for example '
    '[1] or [1][2], right after the sentence they support. Only cite numbers '
    'that appear in the documents.\n'
    f'4. Always answer in {config.RESPONSE_LANGUAGE}, even if the question '
    'or the documents are in another language.\n'
    '5. Be concise.'
)


def format_chunk(position: int, chunk: dict) -> str:
    return (
        f'=== SOURCE [{position}] ({chunk["document_name"]}, '
        f'page {chunk["page"]}) ===\n'
        f'{chunk["text"]}\n'
        f'=== END OF SOURCE [{position}] ==='
    )


def build_messages(question: str, chunks: list[dict]) -> list[dict]:
    # Vengono messi dei segnaposto numerati nelle corrispondenze delle frasi dei chunk.
    # es. passiamo una lista di chunk tra i quali: {Postion:[1], file: 'document.pdf', page: 2, text: 'Il mio testo del chunk nel quale il modello farà ricerca}
    # il modello userà i segnaposto per contrassegnare le corrispondenze trovate in maniera che potremmo estrarne i sources"
    formatted_chunks = [
        format_chunk(i + 1, chunk) for i, chunk in enumerate(chunks)
    ]
    context = '\n\n'.join(formatted_chunks)
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f'{context}\n\nQuestion: {question}'},
    ]

    return messages


def extract_sources(answer: str, chunks: list[dict]) -> list[dict]:
    numbers = re.findall(r'\[(\d+)\]', answer)
    seen = set()
    unique_numbers = []
    sources = []

    for text_num in numbers:
        num = int(text_num)
        if num not in seen:
            seen.add(num)
            unique_numbers.append(num)

    for num in unique_numbers:
        if 1 <= num <= len(chunks):
            chunk = chunks[num - 1]
            sources.append(
                {
                    'number': num,
                    'document_id': chunk['document_id'],
                    'document_name': chunk['document_name'],
                    'page': chunk['page'],
                }
            )
    return sources
