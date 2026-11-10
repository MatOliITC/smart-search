import argparse
import json
from pathlib import Path

import config
from experiments.eval.metrics import hit_at_k, reciprocal_rank
from llm_client import embed
from rag.vector_store import search_chunks

GOLDEN_PATH = Path(__file__).parent / 'eval' / 'golden.jsonl'


def load_golden(path: Path) -> list[dict]:

    tests = []

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():
                data = json.loads(line)
                tests.append(data)

    return tests


def retrieve_ids(question: str, folder_id: str, top_k: int) -> list[str]:
    vector = embed([question])[0]
    chunks = search_chunks(vector, folder_id, config.EMBEDDING_MODEL, top_k)
    ids = []
    for chunk in chunks:
        ids.append(f'{chunk["document_id"]}-{chunk["chunk_index"]:04d}')

    return ids


def calculate_avg(items: list[float]) -> float:
    return sum(items) / len(items)


def print_results(title: str, results: list[dict], top_k: int):

    all_hits_1 = [result['hit_1'] for result in results]
    all_hits_k = [result['hits_k'] for result in results]
    ranking = [result['ranking'] for result in results]

    print(f'===== {title} ({len(all_hits_1)} domande), top-k {top_k}')
    print(f'Hit@1: {calculate_avg(all_hits_1):.3f}')
    print(f'Hit@{top_k}: {calculate_avg(all_hits_k):.3f}')
    print(f'MRR: {calculate_avg(ranking):.3f}')
    print('')


def main(top_k: int):
    golden_dataset = load_golden(GOLDEN_PATH)
    results = []

    for data in golden_dataset:
        if not data['relevant']:
            continue

        question = data['question']
        relevant = data['relevant']
        folder_id = data['folder_id']
        category = data['category']
        ids = retrieve_ids(question, folder_id, top_k)

        hit_1 = hit_at_k(ids, relevant, 1)
        hit_k = hit_at_k(ids, relevant, top_k)
        rank = reciprocal_rank(ids, relevant)

        results.append(
            {
                'hit_1': hit_1,
                'hits_k': hit_k,
                'ranking': rank,
                'category': category,
            }
        )

        print('--------')
        print('Question', question)
        print('Retrieved ids', ids)
        print('Relevant ids', relevant)
        print('........')
        print('Hit 1: ', hit_1)
        print(f'Hit {top_k}:', hit_k)
        print('Rank: ', rank)

    print('')
    print_results('tutte', results, top_k)

    categories = sorted({result['category'] for result in results})

    for category in categories:
        same_category = [
            result for result in results if result['category'] == category
        ]
        print_results(category, same_category, top_k)

    print('')

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testa la validità del rag')
    parser.add_argument('--top-k', type=int, default=5)

    args = parser.parse_args()

    exit_code = main(args.top_k)
    print('exit code:', exit_code)
