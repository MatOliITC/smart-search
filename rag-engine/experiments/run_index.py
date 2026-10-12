# """Fa la parte di Node: lancia `rag.py index` e legge i suoi eventi JSON.

# python -m experiments.run_index --file samples\\pompa_di_calore.txt
# """

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAG_SCRIPT = Path(__file__).parent.parent / 'rag.py'


def describe(event: dict) -> str:
    if event['type'] == 'progress' and event['stage'] == 'embedding':
        return f'[embedding] {event["done"]}/{event["total"]} chunk'
    if event['type'] == 'progress':
        return f'[{event["stage"]}]'
    if event['type'] == 'result':
        return (
            f'Fatto: {event["chunks"]} chunk salvati '
            f'per il documento {event["document_id"]}'
        )
    if event['type'] == 'error':
        return f'Errore {event["code"]}: {event["message"]}'
    return f'Evento sconosciuto: {event}'

def run_index(command: list[str]) -> int:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        encoding="utf-8"
    )

    for line in process.stdout:
        print('Ricevuto', line.strip())
        event = json.loads(line)
        print('   ->', describe(event))

    process.wait()
    return process.returncode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Lancia rag.py index come farebbe Node'
    )
    parser.add_argument('--file', required=True)
    parser.add_argument('--folder-id', default='f1')
    parser.add_argument('--document-id', default='d1')
    parser.add_argument('--document-name', default='documento.txt')
    args = parser.parse_args()

    command = [
        sys.executable,
        str(RAG_SCRIPT),
        'index',
        '--file',
        args.file,
        '--folder-id',
        args.folder_id,
        '--document-id',
        args.document_id,
        '--document-name',
        args.document_name,
    ]

    exit_code = run_index(command)
    print('exit code:', exit_code)