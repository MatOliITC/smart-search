
import argparse
from extraction.extractor import extract_pages
from rag.chunking import chunk_pages
import config

def get_min_chunk_length(length: list[int]) -> int:
  return min(length)

def get_max_chunk_length(length: list[int]) -> int:
  return max(length)

def get_avg_chunk_length(length: list[int]) -> float:
  avg_length = sum(length) / len(length)
  return avg_length

def chunk_stats(file_path:str) -> dict:

  pages = extract_pages(file_path)
  chunks = chunk_pages(pages, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
  chunks_length = [len(chunk["text"]) for chunk in chunks]

  return {"total_chunks": len(chunks_length), "min_length": get_min_chunk_length(chunks_length), "max_length": get_max_chunk_length(chunks_length), "avg_length": get_avg_chunk_length(chunks_length)}


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Calcola statistiche sui chunk di un documento")
  parser.add_argument("--file", required=True, help="Percorso del file da analizzare")
  args = parser.parse_args()
  stats = chunk_stats(args.file)
  print(f"Numero totale di chunk: {stats['total_chunks']}")
  print(f"Lunghezza minima: {stats['min_length']}")
  print(f"Lunghezza massima: {stats['max_length']}")
  print(f"Lunghezza media: {stats['avg_length']:.2f}")
