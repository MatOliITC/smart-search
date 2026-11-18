import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

PROVIDERS = {
    'ollama': {
        'base_url': 'http://localhost:11434/v1',
        'api_key': 'ollama',
    },
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'api_key': os.environ.get('OPENAI_API_KEY'),
    },
}

GENERATION_PROVIDER = os.environ.get('GENERATION_PROVIDER', 'ollama')
GENERATION_MODEL = os.environ.get('GENERATION_MODEL', 'gemma3:4b')
EMBEDDING_PROVIDER = os.environ.get('EMBEDDING_PROVIDER', 'ollama')
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'bge-m3')

EMBEDDING_BATCH_SIZE = 32

LLM_TEMPERATURE = 0
RESPONSE_LANGUAGE = 'Italiano'

VECTOR_DB_PATH = Path(__file__).parent / 'data' / 'vectordb'


def vector_table_name(embedding_model: str) -> str:
    safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', embedding_model)
    return 'chunks_' + safe_name


VECTOR_TABLE = vector_table_name(EMBEDDING_MODEL)
