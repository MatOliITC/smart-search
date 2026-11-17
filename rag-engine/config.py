from pathlib import Path

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


LLM_BASE_URL = 'http://localhost:11434/v1'
LLM_API_KEY = 'ollama'

EMBEDDING_MODEL = 'bge-m3'
EMBEDDING_BATCH_SIZE = 32

LLM_MODEL = 'gemma3:4b'
LLM_TEMPERATURE = 0
RESPONSE_LANGUAGE = 'Italiano'

VECTOR_DB_PATH = Path(__file__).parent / 'data' / 'vectordb'
VECTOR_TABLE = 'chunks'
