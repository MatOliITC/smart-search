"""Unico punto di contatto con il vector DB (LanceDB)."""

import lancedb

import config

NO_CHUNKS_DELETED = 0


def save_document_chunks(
    chunks: list[dict],
    folder_id: str,
    document_id: str,
    document_name: str,
    embedding_model: str,
) -> int:
    records = [
        to_record(chunk, folder_id, document_id, document_name, embedding_model)
        for chunk in chunks
    ]

    db = lancedb.connect(config.VECTOR_DB_PATH)

    if config.VECTOR_TABLE in db.list_tables().tables:
        table = db.open_table(config.VECTOR_TABLE)
        table.delete(f'document_id = {sql_string(document_id)}')
        table.add(records)
    else:
        db.create_table(config.VECTOR_TABLE, data=records)

    return len(records)


def search_chunks(
    vector: list[float],
    folder_id: str,
    embedding_model: str,
    top_k: int,
) -> list[dict]:
    db = lancedb.connect(config.VECTOR_DB_PATH)

    if config.VECTOR_TABLE not in db.list_tables().tables:
        return []

    table = db.open_table(config.VECTOR_TABLE)
    rows = (
        table.search(vector)
        .distance_type('cosine')
        .where(
            f'folder_id = {sql_string(folder_id)} '
            f'AND embedding_model = {sql_string(embedding_model)}',
            prefilter=True,
        )
        .limit(top_k)
        .to_list()
    )

    return [to_result(row) for row in rows]


def delete_document_chunks(document_id: str) -> int:
    db = lancedb.connect(config.VECTOR_DB_PATH)

    if config.VECTOR_TABLE not in db.list_tables().tables:
        return NO_CHUNKS_DELETED

    table = db.open_table(config.VECTOR_TABLE)
    deleted = table.delete(f'document_id = {sql_string(document_id)}')
    deleted_count = deleted.num_deleted_rows

    return deleted_count


def delete_folder_chunks(folder_id: str) -> int:
    db = lancedb.connect(config.VECTOR_DB_PATH)

    if config.VECTOR_TABLE not in db.list_tables().tables:
        return NO_CHUNKS_DELETED

    table = db.open_table(config.VECTOR_TABLE)
    deleted = table.delete(f'folder_id = {sql_string(folder_id)}')
    deleted_count = deleted.num_deleted_rows
    return deleted_count


def to_result(row: dict) -> dict:
    return {
        'document_id': row['document_id'],
        'document_name': row['document_name'],
        'page': row['page'],
        'chunk_index': row['chunk_index'],
        # LanceDB dà la distanza coseno (bassa = simile): la giriamo in
        # similarità (alta = simile), come in experiments/similarity.py
        'score': 1 - row['_distance'],
        'text': row['text'],
    }


def to_record(
    chunk: dict,
    folder_id: str,
    document_id: str,
    document_name: str,
    embedding_model: str,
) -> dict:
    return {
        'id': f'{document_id}-{chunk["chunk_index"]:04d}',
        'folder_id': folder_id,
        'document_id': document_id,
        'document_name': document_name,
        'page': chunk['page'],
        'chunk_index': chunk['chunk_index'],
        'text': chunk['text'],
        'embedding_model': embedding_model,
        'vector': chunk['embedding'],
    }


def sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"
