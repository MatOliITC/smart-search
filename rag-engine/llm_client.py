"""Unico punto di contatto con il server dei modelli (oggi Ollama, via API compatibile OpenAI)."""

from openai import OpenAI

import config

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def embed(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=config.EMBEDDING_MODEL, input=texts)

    items = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in items]
