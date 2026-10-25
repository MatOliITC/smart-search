import traceback
from collections.abc import Iterator

import config
from errors import RagError
from extraction.extractor import extract_pages
from llm_client import embed, generate
from rag.chunking import chunk_pages
from rag.embeddings import embed_batches
from rag.prompt import NO_ANSWER, build_messages, extract_sources
from rag.vector_store import (
    delete_document_chunks,
    delete_folder_chunks,
    save_document_chunks,
    search_chunks,
)


def run_index(file, folder_id, document_id, document_name) -> Iterator[dict]:
    yield {'type': 'progress', 'stage': 'extracting'}
    pages = extract_pages(file)

    yield {'type': 'progress', 'stage': 'chunking', 'pages': len(pages)}
    chunks = chunk_pages(pages, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    embedding = []
    for embed_batch in embed_batches(chunks, config.EMBEDDING_BATCH_SIZE):
        embedding.extend(embed_batch)
        yield {
            'type': 'progress',
            'stage': 'embedding',
            'done': len(embedding),
            'total': len(chunks),
        }

    yield {'type': 'progress', 'stage': 'saving', 'chunks': len(embedding)}

    saved = save_document_chunks(
        embedding,
        folder_id,
        document_id,
        document_name,
        config.EMBEDDING_MODEL,
    )

    yield {
        'type': 'result',
        'document_id': document_id,
        'pages': len(pages),
        'chunks': saved,
        'embedding_model': config.EMBEDDING_MODEL,
    }


def run_query(folder_id, top_k, question, debug) -> Iterator[dict]:

    yield {'type': 'progress', 'stage': 'embedding_question'}

    question_vector = embed([question])[0]

    yield {'type': 'progress', 'stage': 'searching'}
    chunks = search_chunks(
        question_vector,
        folder_id,
        config.EMBEDDING_MODEL,
        top_k,
    )

    if not chunks:
        yield {
            'type': 'result',
            'question': question,
            'answer': None,
            'sources': [],
        }
        return

    yield {'type': 'progress', 'stage': 'generating'}

    messages = build_messages(question, chunks)
    response = generate(messages)

    if response.strip() == NO_ANSWER:
        answer = None
        sources = []
    else:
        answer = response
        sources = extract_sources(answer, chunks)

    result = {
        'question': question,
        'answer': answer,
        'sources': sources,
    }

    if debug:
        result['chunks'] = chunks
        result['messages'] = messages

    yield {'type': 'result', **result}


def run_delete(
    document_id: str | None, folder_id: str | None
) -> Iterator[dict]:
    if document_id:
        yield {'type': 'progress', 'stage': 'deleting_documents'}
        deleted_chunks = delete_document_chunks(document_id)

    else:
        yield {'type': 'progress', 'stage': 'deleting_folders'}
        deleted_chunks = delete_folder_chunks(folder_id)

    yield {
        'type': 'result',
        'document_id': document_id,
        'folder_id': folder_id,
        'deleted_chunks': deleted_chunks,
    }


def with_errors(events: Iterator[dict]) -> Iterator[dict]:
    try:
        for event in events:
            yield event
    except RagError as error:
        yield {'type': 'error', 'code': error.code, 'message': error.message}
    except Exception as error:
        traceback.print_exc()
        yield {'type': 'error', 'code': 'INTERNAL_ERROR', 'message': str(error)}
