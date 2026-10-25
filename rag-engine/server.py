import json
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from commands import run_delete, with_errors

app = FastAPI()


class DeleteBody(BaseModel):
    document_id: str | None = None
    folder_id: str | None = None


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
