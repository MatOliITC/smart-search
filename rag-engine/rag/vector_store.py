"""Unico punto di contatto con il vector DB (LanceDB)."""

import lancedb

import config


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
        table.delete(f"document_id = {sql_string(document_id)}")
        table.add(records)
    else:
        db.create_table(config.VECTOR_TABLE, data=records)

    return len(records)


def to_record(chunk: dict, folder_id: str, document_id: str, document_name: str, embedding_model: str) -> dict:
    return {
        "id": f"{document_id}-{chunk['chunk_index']:04d}",
        "folder_id": folder_id,
        "document_id": document_id,
        "document_name": document_name,
        "page": chunk["page"],
        "chunk_index": chunk["chunk_index"],
        "text": chunk["text"],
        "embedding_model": embedding_model,
        "vector": chunk["embedding"],
    }


def sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"
