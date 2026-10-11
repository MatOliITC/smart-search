import math
import sys

from llm_client import embed

QUESTION = "Perché la pompa si blocca quando fa molto freddo?"

SENTENCES = [
    "E05 - Blocco per bassa temperatura: la temperatura esterna è scesa sotto il limite di funzionamento di -20 °C.",
    "Con temperature esterne inferiori a 5 °C la batteria dell'unità esterna può coprirsi di brina.",
    "Il mio frigorifero si blocca quando fa molto caldo.",
    "Pulire il filtro dell'acqua ogni 6 mesi.",
    "L'unità esterna va installata su una base stabile, ad almeno 30 cm dal suolo.",
    "La ricetta della carbonara prevede guanciale, uova e pecorino.",
]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """1 = stessa direzione (significato molto simile), 0 = nessuna relazione."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else QUESTION
    vectors = embed([question] + SENTENCES)
    question_vector, sentence_vectors = vectors[0], vectors[1:]

    scores = [
        # come esce la struttura dei dati
        (cosine_similarity(question_vector, vector), sentence)
        # ciclo for sul quale iterare
        for vector, sentence in zip(sentence_vectors, SENTENCES)
    ]

    print(f"Domanda: {question}\n")
    for score, sentence in sorted(scores, reverse=True):
        print(f"{score:.3f}  {sentence}")


if __name__ == "__main__":
    main()
