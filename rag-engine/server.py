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


def to_ndjson(events) -> Iterator[str]:
    for event in events:
        yield json.dumps(event, ensure_ascii=False) + '\n'


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
            status_code=422, detail='You could pass one argument per time'
        )

    deleted_item = run_delete(document_id, folder_id)

    return StreamingResponse(
        to_ndjson(with_errors(deleted_item)), media_type='application/x-ndjson'
    )


@app.post('/index')
def index_item(body: IndexBody):
    file = body.file
    document_id = body.document_id
    folder_id = body.folder_id
    document_name = body.document_name

    indexed_item = run_index(file, folder_id, document_id, document_name)

    return StreamingResponse(
        to_ndjson(with_errors(indexed_item)), media_type='application/x-ndjson'
    )


@app.post('/query')
def query_item(body: QueryBody):
    folder_id = body.folder_id
    top_k = body.top_k
    question = body.question
    debug = body.debug

    query_item = run_query(folder_id, top_k, question, debug)

    return StreamingResponse(
        to_ndjson(with_errors(query_item)), media_type='application/x-ndjson'
    )
