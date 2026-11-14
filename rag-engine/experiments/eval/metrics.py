def hit_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> int:
    """1 se almeno uno dei primi k chunk recuperati è giusto, altrimenti 0.

    relevant_ids non deve essere vuota: le domande senza risposta
    vanno scartate prima di chiamare questa funzione.
    """
    k_items = retrieved_ids[:k]

    for chunk_id in k_items:
        if chunk_id in relevant_ids:
            return 1
    return 0


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """1 / posizione del primo chunk giusto (contando da 1), 0.0 se manca.

    relevant_ids non deve essere vuota.
    """
    for position, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_ids:
            return 1 / position
    return 0.0


def keyword_coverage(answer: str | None, keywords: list[str]) -> float:
    """si contano le keyword trovate / il totale delle keyword.
    keywords non deve essere vuota"""

    if answer is None:
        return 0.0

    lower_answer = answer.lower()

    found_keyword = [
        keyword for keyword in keywords if keyword.lower() in lower_answer
    ]

    return len(found_keyword) / len(keywords)


def answer_presence_ok(answer: str | None, relevant: list[str]) -> bool:
    if len(relevant) and answer or not len(relevant) and not answer:
        return True
    return False
