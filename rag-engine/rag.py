"""Punto d'ingresso del motore RAG.

Node lo avvia come comando da terminale, ad esempio:
    python rag.py index --file C:/docs/manuale.txt --folder-id <uuid> --document-id <uuid> --document-name manuale.txt
    python rag.py query --folder-id <uuid> --question "Perché la pompa va in blocco?"
    python rag.py delete --document-id <uuid>
"""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag.py",
        description="Motore RAG locale: indicizza documenti e risponde a domande.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    index = commands.add_parser("index", help="Indicizza un documento nel vector DB")
    index.add_argument("--file", required=True, help="Percorso del file da indicizzare")
    index.add_argument("--folder-id", required=True, help="UUID della cartella")
    index.add_argument("--document-id", required=True, help="UUID del documento")
    index.add_argument("--document-name", required=True, help="Nome originale del file")

    query = commands.add_parser("query", help="Risponde a una domanda usando i documenti di una cartella")
    query.add_argument("--folder-id", required=True, help="UUID della cartella in cui cercare")
    query.add_argument("--question", required=True, help="Domanda dell'utente")
    query.add_argument("--top-k", type=int, default=5, help="Numero di chunk da recuperare (default: 5)")
    query.add_argument("--debug", action="store_true", help="Include chunk recuperati e prompt nel risultato")

    delete = commands.add_parser("delete", help="Rimuove dal vector DB i chunk di un documento o di una cartella")
    target = delete.add_mutually_exclusive_group(required=True)
    target.add_argument("--document-id", help="UUID del documento da rimuovere")
    target.add_argument("--folder-id", help="UUID della cartella da rimuovere")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(f"Comando '{args.command}' non ancora implementato. Argomenti ricevuti: {vars(args)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
