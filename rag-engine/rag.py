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

import config
from errors import RagError
from extraction.extractor import extract_pages
from rag.chunking import chunk_pages
from rag.embeddings import embed_chunks
from rag.vector_store import save_document_chunks


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


def emit(event_type: str, **data) -> None:
    event = {'type': event_type, **data}
    print(json.dumps(event, ensure_ascii=False), flush=True)


def run_index(args: argparse.Namespace) -> int:
    emit('progress', stage='extracting')
    pages = extract_pages(args.file)

    emit('progress', stage='chunking', pages=len(pages))
    chunks = chunk_pages(pages, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    chunks = embed_chunks(
        chunks,
        config.EMBEDDING_BATCH_SIZE,
        on_progress=lambda done, total: emit(
            'progress', stage='embedding', done=done, total=total
        ),
    )

    emit('progress', stage='saving', chunks=len(chunks))
    saved = save_document_chunks(
        chunks,
        args.folder_id,
        args.document_id,
        args.document_name,
        config.EMBEDDING_MODEL,
    )

    emit(
        'result',
        document_id=args.document_id,
        pages=len(pages),
        chunks=saved,
        embedding_model=config.EMBEDDING_MODEL,
    )
    return 0


def main() -> int:
    # forcing for node js
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    args = build_parser().parse_args()

    try:
        if args.command == 'index':
            return run_index(args)

        emit(
            'error',
            code='NOT_IMPLEMENTED',
            message=f"Comando '{args.command}' non ancora implementato",
        )
        return 1
    except RagError as error:
        emit('error', code=error.code, message=error.message)
        return 1
    except Exception as error:
        traceback.print_exc()
        emit('error', code='INTERNAL_ERROR', message=str(error))
        return 1


if __name__ == '__main__':
    sys.exit(main())
