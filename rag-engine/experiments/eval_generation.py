import argparse

from commands import run_query
from experiments.eval.metrics import answer_presence_ok, keyword_coverage
from experiments.eval_retrieval import GOLDEN_PATH, load_golden


def get_results(question: str, folder_id: str, top_k: int) -> dict:
    for event in run_query(folder_id, top_k, question, debug=False):
        if event['type'] == 'result':
            return event


def main(top_k):
    golden = load_golden(GOLDEN_PATH)
    coverages = []
    presences = []

    for row in golden:
        result = get_results(row['question'], row['folder_id'], top_k)
        answer = result['answer']
        relevant = row['relevant']
        question = row['question']
        presence = answer_presence_ok(answer=answer, relevant=relevant)
        presences.append(presence)

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

    print()
    print('===== Copertura keyword ======')
    print(f'Domande: {len(coverages)}')
    print(f'Top-k {top_k}: {(sum(coverages) / len(coverages)):.3f}')
    print(f'Risposte attese: {sum(presences)} / {len(presences)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Testa le keyword del generatore'
    )
    parser.add_argument('--top-k', type=int, default=5)

    args = parser.parse_args()
    main(args.top_k)
