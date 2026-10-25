# 1. Import
#    - json
#    - Iterator (collections.abc)
#    - FastAPI (da fastapi), StreamingResponse (da fastapi.responses)
#    - BaseModel (da pydantic: arriva installato insieme a FastAPI)
#    - run_delete (da commands)

import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from commands import run_delete

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
    deleted_item = run_delete(document_id, folder_id)

    return StreamingResponse(
        to_ndjson(deleted_item), media_type='application/x-ndjson'
    )
