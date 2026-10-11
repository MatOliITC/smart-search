import argparse

import lancedb

import config
from rag.vector_store import sql_string


def db_inspect(folder_id: str | None):
    db = lancedb.connect(config.VECTOR_DB_PATH)
    table = db.open_table(config.VECTOR_TABLE)

    if folder_id:
        chunks = (
            table.search()
            .where(f'folder_id = {sql_string(folder_id)}')
            .to_list()
        )
        if not chunks:
            print(f'Nessun chunk trovato per la cartella {folder_id}')
            return
    else:
        chunks = table.to_arrow().to_pylist()

    documents = []

    for chunk in chunks:
        document_id = chunk['document_id']
        if document_id not in documents:
            documents.append(document_id)

    chunk_per_documents = []
    for document in documents:
        current_document_chunks = [
            chunk for chunk in chunks if chunk['document_id'] == document
        ]
        chunk_per_documents.append(
            {
                'document_id': document,
                'chunks': sorted(
                    current_document_chunks, key=lambda x: x['chunk_index']
                ),
            }
        )

    for item in chunk_per_documents:
        print(
            'Documento:',
            item['document_id'],
            '|',
            item['chunks'][0]['folder_id'],
            '|',
            f'{len(item["chunks"])} chunks',
        )
        for chunk in item['chunks']:
            print(
                f'chunk {chunk["chunk_index"]}',
                '|',
                f'page {chunk["page"]}',
                '|',
                f'{len(chunk["text"])} caratteri',
                '|',
                chunk['text'][:50].replace('\n', ' '),
            )


if __name__ == '__main__':
    # python -m experiments.inspect_db
    # python -m experiments.inspect_db --folder-id f1

    parser = argparse.ArgumentParser(
        description="Leggi cosa c'è nel database dei chunk"
    )
    parser.add_argument(
        '--folder-id',
        help='ID della cartella da ispezionare nel database dei chunk',
    )
    args = parser.parse_args()

    db_inspect(args.folder_id)
