"""Unico punto di contatto con i server dei modelli.

Embedding e generazione hanno ognuno il proprio client (Ollama o OpenAI,
scelti nel .env, vedi config.PROVIDERS), entrambi tramite l'API OpenAI.
"""

from collections.abc import Iterator

from openai import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)

import config
from errors import RagError

KNOWN_API_ERRORS = (
    APIConnectionError,
    NotFoundError,
    AuthenticationError,
    RateLimitError,
)


def create_client(provider: str) -> OpenAI:
    if provider not in config.PROVIDERS:
        valid = ', '.join(config.PROVIDERS)
        raise RagError(
            'UNKNOWN_PROVIDER',
            f"Provider '{provider}' sconosciuto (validi: {valid})",
        )

    settings = config.PROVIDERS[provider]
    if not settings['api_key']:
        raise RagError(
            'MISSING_API_KEY',
            f"Manca la API key del provider '{provider}' nel file .env",
        )

    return OpenAI(base_url=settings['base_url'], api_key=settings['api_key'])


def to_rag_error(error: Exception, provider: str, model: str) -> RagError:
    base_url = config.PROVIDERS[provider]['base_url']

    if isinstance(error, APIConnectionError):
        return RagError(
            'MODEL_SERVER_UNREACHABLE',
            f'Server dei modelli non raggiungibile su {base_url}',
        )
    if isinstance(error, NotFoundError):
        return RagError(
            'MODEL_NOT_FOUND',
            f"Modello '{model}' non trovato sul server {base_url}",
        )
    if isinstance(error, AuthenticationError):
        return RagError(
            'INVALID_API_KEY',
            f"API key del provider '{provider}' non valida o revocata",
        )
    # RateLimitError (HTTP 429): OpenAI lo usa sia per le troppe richieste
    # sia per il credito esaurito.
    return RagError(
        'RATE_LIMITED',
        f"Troppe richieste o credito esaurito sul provider '{provider}'",
    )


def embed(texts: list[str]) -> list[list[float]]:
    provider = config.EMBEDDING_PROVIDER
    try:
        client = create_client(provider)
        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL, input=texts
        )

    except KNOWN_API_ERRORS as error:
        raise to_rag_error(error, provider, config.EMBEDDING_MODEL) from error

    items = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in items]


def generate_stream(messages: list[dict]) -> Iterator[str]:
    provider = config.GENERATION_PROVIDER
    try:
        client = create_client(provider)
        stream = client.chat.completions.create(
            model=config.GENERATION_MODEL,
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except KNOWN_API_ERRORS as error:
        raise to_rag_error(error, provider, config.GENERATION_MODEL) from error
