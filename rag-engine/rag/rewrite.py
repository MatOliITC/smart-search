MAX_RESPONSE_LENGTH = 300

REWRITE_SYSTEM_PROMPT = (
    'You are a question rewriter. Rewrite the question in a form '
    'that is suitable for document retrieval and search.\n'
    'Keep codes, proper names, and numbers unchanged (e.g., E05, HP-9).\n'
    'Do not add any facts that are not present in the original question.\n'
    'Respond ONLY with the rewritten question, on a single line, '
    'with no explanations or introductory text.'
)


def merge_results(a: list[dict], b: list[dict]) -> list[dict]:
    merged = {}

    for result in a + b:
        key = (result['document_id'], result['chunk_index'])

        if key not in merged or result['score'] > merged[key]['score']:
            merged[key] = result

    return sorted(
        merged.values(), key=lambda chunk: chunk['score'], reverse=True
    )


def build_rewrite_messages(question: str) -> list[dict]:
    messages = [
        {'role': 'system', 'content': REWRITE_SYSTEM_PROMPT},
        {'role': 'user', 'content': question},
    ]

    return messages


def clean_rewrite(text: str, question: str) -> str:
    text = text.strip()
    text = next(
        (line.strip() for line in text.splitlines() if line.strip()), ''
    )
    text = text.strip('"\'').strip()

    if not text or len(text) > MAX_RESPONSE_LENGTH:
        return question

    return text
