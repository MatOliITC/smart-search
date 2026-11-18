"""Unico punto di contatto con i server dei modelli.

Embedding e generazione hanno ognuno il proprio client (Ollama o OpenAI,
scelti nel .env, vedi config.PROVIDERS), entrambi tramite l'API OpenAI.
"""

from collections.abc import Iterator

from openai import APIConnectionError, NotFoundError, OpenAI

import config
from errors import RagError

embedding_base_url = config.PROVIDERS[config.EMBEDDING_PROVIDER]['base_url']
embedding_api_key = config.PROVIDERS[config.EMBEDDING_PROVIDER]['api_key']
generation_base_url = config.PROVIDERS[config.GENERATION_PROVIDER]['base_url']
generation_api_key = config.PROVIDERS[config.GENERATION_PROVIDER]['api_key']
embedding_client = OpenAI(
    base_url=embedding_base_url, api_key=embedding_api_key
)
generation_client = OpenAI(
    base_url=generation_base_url, api_key=generation_api_key
)


def embed(texts: list[str]) -> list[list[float]]:
    try:
        response = embedding_client.embeddings.create(
            model=config.EMBEDDING_MODEL, input=texts
        )

    except APIConnectionError as error:
        raise RagError(
            'MODEL_SERVER_UNREACHABLE',
            f'Server dei modelli non raggiungibile su {embedding_base_url}',
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
        stream = generation_client.chat.completions.create(
            model=config.GENERATION_MODEL,
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
            f'Server dei modelli non raggiungibile su {generation_base_url}',
        ) from error

    except NotFoundError as error:
        raise RagError(
            'MODEL_NOT_FOUND',
            f"Modello '{config.GENERATION_MODEL}' non trovato sul server",
        ) from error
