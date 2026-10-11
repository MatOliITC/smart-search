from pathlib import Path

from extraction.text_loader import load_parse_text

LOADERS = {
    '.txt': load_parse_text,
    '.md': load_parse_text,
}


def extract_pages(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f'File non trovato: {file_path}')

    loader = LOADERS.get(path.suffix.lower())
    if loader is None:
        supported = ', '.join(LOADERS)
        raise ValueError(
            f"Formato '{path.suffix}' non supportato. Formati gestiti: {supported}"
        )

    return loader(path)
