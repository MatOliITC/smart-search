from collections.abc import Callable

from llm_client import embed


def embed_chunks(
    chunks: list[dict],
    batch_size: int,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[dict]:
    embedded = []
    for start in range(0, len(chunks), batch_size):
        # es. start = 0, batch = 2, i primi due chunks [0,1]
        batch = chunks[start : start + batch_size]
        # calcola gli embed tramite ollama per ognuno dei chunks nel batch passando il text
        vectors = embed([chunk['text'] for chunk in batch])
        # recupera il vettore dallo zip di batch + vectors [abbinamento 1 a 1],
        # estrai il chunk da ognuno, aggiungi alla lista embedded
        # lo spread del chunk e il suo vettore
        for chunk, vector in zip(batch, vectors):
            embedded.append({**chunk, 'embedding': vector})

        # avvisa chi ci ha chiamato: quanti chunk fatti su quanti in totale
        if on_progress:
            on_progress(len(embedded), len(chunks))

    return embedded
