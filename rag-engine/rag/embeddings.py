from collections.abc import Iterator

from llm_client import embed


def embed_batches(
    chunks: list[dict],
    batch_size: int,
) -> Iterator[list[dict]]:
    for start in range(0, len(chunks), batch_size):
        # es. start = 0, batch = 2, i primi due chunks [0,1]
        batch = chunks[start : start + batch_size]
        # calcola gli embed tramite l'llm di coding per ognuno dei chunks nel batch
        # passando il text
        vectors = embed([chunk['text'] for chunk in batch])

        embedded = []
        # recupera il vettore dallo zip di batch + vectors [abbinamento 1 a 1],
        # estrai il chunk da ognuno, aggiungi alla lista embedded
        # lo spread del chunk e il suo vettore
        for chunk, vector in zip(batch, vectors):
            embedded.append({**chunk, 'embedding': vector})

        # consegna a chi chiama i chunk di questo batch, poi passa al successivo
        yield embedded
