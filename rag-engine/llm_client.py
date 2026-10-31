"""Unico punto di contatto con il server dei modelli.

Oggi è Ollama, raggiunto tramite la sua API compatibile OpenAI.
"""

from collections.abc import Iterator

from openai import APIConnectionError, NotFoundError, OpenAI

import config
from errors import RagError

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def embed(texts: list[str]) -> list[list[float]]:
    try:
        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL, input=texts
        )

    except APIConnectionError as error:
        raise RagError(
            'MODEL_SERVER_UNREACHABLE',
            f'Server dei modelli non raggiungibile su {config.LLM_BASE_URL}',
        ) from error

    except NotFoundError as error:
        raise RagError(
            'MODEL_NOT_FOUND',
            f"Modello '{config.EMBEDDING_MODEL}' non trovato sul server",
        ) from error

    items = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in items]


def generate_stream(messages: list[dict]) -> Iterator[str]:
    try:
        stream = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except APIConnectionError as error:
        raise RagError(
            'MODEL_SERVER_UNREACHABLE',
            f'Server dei modelli non raggiungibile su {config.LLM_BASE_URL}',
        ) from error

    except NotFoundError as error:
        raise RagError(
            'MODEL_NOT_FOUND',
            f"Modello '{config.LLM_MODEL}' non trovato sul server",
        ) from error
