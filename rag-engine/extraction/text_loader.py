from pathlib import Path

ENCODINGS = ("utf-8-sig", "cp1252")

def string_normalizer(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()

def load_parse_text(path: Path) -> list[dict]:
    raw = path.read_bytes()

    for encoding in ENCODINGS:
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Encoding non riconosciuto per il file {path.name}")

    text = string_normalizer(text)

    if not text:
        raise ValueError(f"Il file {path.name} non contiene testo")

    return [{"page": 1, "text": text}]
