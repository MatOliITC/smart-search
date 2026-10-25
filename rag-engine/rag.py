"""Punto d'ingresso del motore RAG.

Node lo avvia come comando da terminale, ad esempio:
    python rag.py index --file C:/docs/manuale.txt --folder-id <uuid> --document-id <uuid> --document-name manuale.txt
    python rag.py query --folder-id <uuid> --question "Perché la pompa va in blocco?"
    python rag.py delete --document-id <uuid>

Protocollo: su stdout solo righe JSON, una per evento, con "type" uguale a
"progress", "result" o "error". Log e dettagli degli errori vanno su stderr.
Exit code 0 = ok, 1 = errore.
"""

import argparse
import json
import sys
import traceback

from commands import run_delete, run_index, run_query
from errors import RagError

EXIT = 0
EXIT_WITH_ERROR = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='rag.py',
        description='Motore RAG locale: indicizza documenti e risponde a domande.',
    )
    commands = parser.add_subparsers(dest='command', required=True)

    index = commands.add_parser(
        'index', help='Indicizza un documento nel vector DB'
    )
    index.add_argument(
        '--file', required=True, help='Percorso del file da indicizzare'
    )
    index.add_argument('--folder-id', required=True, help='UUID della cartella')
    index.add_argument(
        '--document-id', required=True, help='UUID del documento'
    )
    index.add_argument(
        '--document-name', required=True, help='Nome originale del file'
    )

    query = commands.add_parser(
        'query',
        help='Risponde a una domanda usando i documenti di una cartella',
    )
    query.add_argument(
        '--folder-id', required=True, help='UUID della cartella in cui cercare'
    )
    query.add_argument('--question', required=True, help="Domanda dell'utente")
    query.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Numero di chunk da recuperare (default: 5)',
    )
    query.add_argument(
        '--debug',
        action='store_true',
        help='Include chunk recuperati e prompt nel risultato',
    )

    delete = commands.add_parser(
        'delete',
        help='Rimuove dal vector DB i chunk di un documento o di una cartella',
    )
    target = delete.add_mutually_exclusive_group(required=True)
    target.add_argument('--document-id', help='UUID del documento da rimuovere')
    target.add_argument('--folder-id', help='UUID della cartella da rimuovere')

    return parser


def print_event(event: dict) -> None:
    print(json.dumps(event, ensure_ascii=False), flush=True)


def main() -> int:
    # forcing for node js
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    args = build_parser().parse_args()

    try:
        if args.command == 'index':
            for event in run_index(
                args.file, args.folder_id, args.document_id, args.document_name
            ):
                print_event(event)
            return EXIT
        if args.command == 'query':
            for event in run_query(
                args.folder_id, args.top_k, args.question, args.debug
            ):
                print_event(event)
            return EXIT
        if args.command == 'delete':
            for event in run_delete(args.document_id, args.folder_id):
                print_event(event)
            return EXIT

        print_event(
            {
                'type': 'error',
                'code': 'NOT_IMPLEMENTED',
                'message': f"Comando '{args.command}' non ancora implementato",
            }
        )
        return EXIT_WITH_ERROR
    except RagError as error:
        print_event(
            {'type': 'error', 'code': error.code, 'message': error.message}
        )
        return EXIT_WITH_ERROR
    except Exception as error:
        traceback.print_exc()
        print_event(
            {'type': 'error', 'code': 'INTERNAL_ERROR', 'message': str(error)}
        )
        return EXIT_WITH_ERROR


if __name__ == '__main__':
    sys.exit(main())
