import argparse

from commands import run_query
from experiments.eval.metrics import (
    answer_presence_ok,
    keyword_coverage,
    sources_in_relevant,
)
from experiments.eval_retrieval import GOLDEN_PATH, load_golden


def get_results(question: str, folder_id: str, top_k: int) -> dict:
    for event in run_query(folder_id, top_k, question, debug=False):
        if event['type'] == 'result':
            return event


def main(top_k):
    golden = load_golden(GOLDEN_PATH)
    coverages = []
    presences = []
    sources_oks = []

    for row in golden:
        result = get_results(row['question'], row['folder_id'], top_k)
        answer = result['answer']
        sources = result['sources']
        question = row['question']
        relevant = row['relevant']
        presence = answer_presence_ok(answer=answer, relevant=relevant)
        presences.append(presence)
        sources_ok = sources_in_relevant(sources=sources, relevant=relevant)
        sources_oks.append(sources_ok)

        print('--------')
        print(f'Domanda: {question}')
        print(f'Risposta: {answer}')
        print(
            f'Comportamento atteso del generatore: {"OK" if presence else "ERRORE"}'
        )

        if row['keywords']:
            coverage = keyword_coverage(answer, row['keywords'])
            coverages.append(coverage)
            print(f'Keywords: {row["keywords"]}')
            print(f'Coverage: {coverage:.3f}')

        print(f'Fonti: {"OK" if sources_ok else "ERRORE"}')

        if not sources_ok:
            quotes = [
                f'{source["document_id"]}-{source["chunk_index"]:04d}'
                for source in sources
            ]
            print(f'Fonti citate: {quotes}')

    print()
    print('===== Copertura keyword ======')
    print(f'Domande: {len(coverages)}')
    print(f'Top-k {top_k}: {(sum(coverages) / len(coverages)):.3f}')
    print(f'Risposte attese: {sum(presences)} / {len(presences)}')
    print(f'Fonti corrette: {sum(sources_oks)} / {len(sources_oks)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Testa le keyword del generatore'
    )
    parser.add_argument('--top-k', type=int, default=5)

    args = parser.parse_args()
    main(args.top_k)
