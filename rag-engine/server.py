"""Ingresso HTTP del motore RAG (l'ingresso da terminale è rag.py).

Avvio: uvicorn server:app --host 127.0.0.1 --port 8000

Ogni rotta risponde in streaming (NDJSON): una riga JSON per evento, con gli
stessi eventi del CLI. Gli errori del motore arrivano come evento "error"
nello stream (lo status 200 è già partito); un body non valido riceve 422.
"""

import json
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from commands import run_delete, run_index, run_query, with_errors

app = FastAPI()


class DeleteBody(BaseModel):
    document_id: str | None = None
    folder_id: str | None = None


class IndexBody(BaseModel):
    file: str
    folder_id: str
    document_id: str
    document_name: str


class QueryBody(BaseModel):
    folder_id: str
    top_k: int = 5
    question: str
    debug: bool = False


def to_ndjson(events: Iterator[dict]) -> Iterator[str]:
    for event in events:
        yield json.dumps(event, ensure_ascii=False) + '\n'


def stream_events(events: Iterator[dict]) -> StreamingResponse:
    return StreamingResponse(
        to_ndjson(with_errors(events)), media_type='application/x-ndjson'
    )


@app.post('/delete')
def delete_item(body: DeleteBody):
    document_id = body.document_id
    folder_id = body.folder_id

    if not document_id and not folder_id:
        raise HTTPException(
            status_code=422, detail='Missing document or folder id'
        )

    if document_id and folder_id:
        raise HTTPException(
            status_code=422, detail='Pass only one of document_id or folder_id'
        )

    return stream_events(run_delete(document_id, folder_id))


@app.post('/index')
def index_item(body: IndexBody):
    events = run_index(
        body.file, body.folder_id, body.document_id, body.document_name
    )
    return stream_events(events)


@app.post('/query')
def query_item(body: QueryBody):
    events = run_query(body.folder_id, body.top_k, body.question, body.debug)
    return stream_events(events)
