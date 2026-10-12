"""Unico punto di contatto con il server dei modelli (oggi Ollama, via API compatibile OpenAI)."""

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
