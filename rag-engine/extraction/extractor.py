from pathlib import Path

from errors import RagError
from extraction.text_loader import load_parse_text

LOADERS = {
    '.txt': load_parse_text,
    '.md': load_parse_text,
}


def extract_pages(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.is_file():
        raise RagError('FILE_NOT_FOUND', f'File non trovato: {file_path}')

    loader = LOADERS.get(path.suffix.lower())
    if loader is None:
        supported = ', '.join(LOADERS)
        raise RagError(
            'UNSUPPORTED_FORMAT',
            f"Formato '{path.suffix}' non supportato. "
            f'Formati gestiti: {supported}',
        )

    return loader(path)
