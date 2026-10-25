# python -m experiments.run_query --question 'La pompa si ferma con il freddo'
#     --folder-id f1 --top-k 3

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAG_SCRIPT = Path(__file__).parent.parent / 'rag.py'


def readable_result(event: dict) -> None:
    if event['type'] == 'progress' and event['stage'] == 'embedding_question':
        print('Progress:', '[embedding question]')
        return

    if event['type'] == 'progress' and event['stage'] == 'searching':
        print('Progress:', '[searching]')
        return

    if event['type'] == 'progress' and event['stage'] == 'generating':
        print('Progress:', '[generating]')
        return

    if event['type'] == 'error':
        print('Error:', f'[error {event["code"]}]: {event["message"]}')
        return

    if event['type'] == 'result':
        print('Result:', event['type'])
        print('Question:', event['question'])

        if event['answer'] is None:
            print('Answer: no answer found in the documents.')
        else:
            print('Answer:', event['answer'])
            print('Sources:')
            for source in event['sources']:
                print(
                    f'  [{source["number"]}] {source["document_name"]}, '
                    f'page {source["page"]} ({source["document_id"]})'
                )

        if 'chunks' in event:
            print('\nChunks (debug):')
            for position, chunk in enumerate(event['chunks'], start=1):
                print(
                    f'  [{position}] {chunk["document_name"]}, '
                    f'page {chunk["page"]}, score {chunk["score"]:.3f}'
                )
                print('  ' + chunk['text'].replace('\n', '\n  '))
        return

    print('Evento sconosciuto:', event)
    return


def run_query(command: list[str]) -> int:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        encoding='utf-8',
    )

    for line in process.stdout:
        event = json.loads(line.strip())
        readable_result(event)

    process.wait()
    return process.returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Esegue una query sul motore RAG locale'
    )
    parser.add_argument('--question', required=True)
    parser.add_argument('--folder-id', required=True)
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    command = [
        sys.executable,
        str(RAG_SCRIPT),
        'query',
        '--question',
        args.question,
        '--folder-id',
        args.folder_id,
        '--top-k',
        str(args.top_k),
    ]
    if args.debug:
        command.append('--debug')

    exit_code = run_query(command)
    print('exit code:', exit_code)
