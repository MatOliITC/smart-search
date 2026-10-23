import re
from typing import NamedTuple


class Unit(NamedTuple):
    text: str
    joiner: str


LEVELS = [
    (lambda text: re.split(r'\n\s*\n', text), '\n\n'),  # paragrafi
    (lambda text: text.split('\n'), '\n'),  # righe
    (lambda text: re.split(r'(?<=[.!?;])\s+', text), ' '),  # frasi
    (lambda text: text.split(' '), ' '),  # parole
]


def chunk_pages(
    pages: list[dict], chunk_size: int, chunk_overlap: int
) -> list[dict]:
    chunks = []
    for page in pages:
        if not page['text'].strip():
            continue

        for text in chunk_text(page['text'], chunk_size, chunk_overlap):
            chunks.append(
                {'chunk_index': len(chunks), 'page': page['page'], 'text': text}
            )
    return chunks


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    units = split_into_units(text, chunk_size, level=0, joiner='')
    return merge_units(units, chunk_size, chunk_overlap)


def split_into_units(
    text: str, chunk_size: int, level: int, joiner: str
) -> list[Unit]:
    if len(text) <= chunk_size or level == len(LEVELS):
        return [Unit(text, joiner)]

    split, level_joiner = LEVELS[level]
    parts = []
    for part in split(text):  # A. taglia
        if part.strip():  # C. se non è vuoto...
            parts.append(part.strip())  # B. ...aggiungilo senza spazi

    units = []
    for i, part in enumerate(parts):
        part_joiner = joiner if i == 0 else level_joiner
        units.extend(split_into_units(part, chunk_size, level + 1, part_joiner))
    return units


def merge_units(
    units: list[Unit], chunk_size: int, chunk_overlap: int
) -> list[str]:
    chunks = []
    current: list[Unit] = []

    for unit in units:
        if current and length(current + [unit]) > chunk_size:
            chunks.append(join(current))
            current = overlap_tail(current, chunk_overlap)
            if current and length(current + [unit]) > chunk_size:
                current = []
        current.append(unit)

    if current:
        chunks.append(join(current))
    return chunks


def overlap_tail(units: list[Unit], chunk_overlap: int) -> list[Unit]:
    tail: list[Unit] = []
    for unit in reversed(units):
        if length([unit] + tail) > chunk_overlap:
            break
        tail.insert(0, unit)
    return tail


def join(units: list[Unit]) -> str:
    text = units[0].text
    for unit in units[1:]:
        text += unit.joiner + unit.text
    return text


def length(units: list[Unit]) -> int:
    return len(join(units))
