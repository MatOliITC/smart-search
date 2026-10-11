# rag-engine

Motore RAG in Python: estrazione testo, chunking, embeddings (e in seguito vector DB, ricerca e risposta).
Tutti i comandi si lanciano dalla cartella `rag-engine`.

## Prerequisiti

- Python 3.12
- Ollama avviato (icona vicino all'orologio) con il modello di embedding scaricato:

```powershell
ollama pull bge-m3
```

## Setup (solo la prima volta)

```powershell
# Crea l'ambiente virtuale
python -m venv .venv

# Attiva l'ambiente (da ripetere in ogni nuovo terminale)
.venv\Scripts\Activate.ps1

# Installa le dipendenze (app + strumenti di sviluppo come ruff)
pip install -r requirements-dev.txt
```

Se PowerShell blocca `Activate.ps1` ("esecuzione di script disabilitata"):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Verifica Ollama

```powershell
# Ollama risponde?
curl.exe http://localhost:11434/api/version

# Modelli scaricati
ollama list
```

## Comandi

```powershell
# Aiuto: elenco comandi e argomenti
python rag.py --help
python rag.py index --help

# Indicizza documento
# Estrazione + chunking + embeddings + salvataggio nel vector DB (data/vectordb).
# Rilanciarlo con lo stesso --document-id sostituisce i chunk precedenti, non li duplica.
python rag.py index --file samples\pompa_di_calore.txt --folder-id f1 --document-id d1 --document-name pompa.txt

# Avvia esperimento: similarità tra una domanda e alcune frasi
python -m experiments.similarity
python -m experiments.similarity "Ogni quanto devo pulire il filtro?"

# Statistiche sui chunk (utile quando cambi CHUNK_SIZE in config.py)
python -m experiments.chunk_stats --file samples\pompa_di_calore.txt

# Ispeziona il vector DB: documenti e chunk salvati, con anteprima del testo
python -m experiments.inspect_db
python -m experiments.inspect_db --folder-id f1
```

`query` e `delete` esistono ma non sono ancora implementati.

## Prove di errore

```powershell
# Argomento mancante → errore di argparse, exit code 2
python rag.py index --folder-id f1 --document-id d1 --document-name x

# File inesistente → FileNotFoundError
python rag.py index --file nonesiste.txt --folder-id f1 --document-id d1 --document-name x
```

## Sperimentare dalla console Python

```powershell
python
```

```python
>>> from extraction.extractor import extract_pages
>>> from rag.chunking import chunk_pages, chunk_text
>>> from llm_client import embed

>>> pages = extract_pages("samples/pompa_di_calore.txt")
>>> chunks = chunk_pages(pages, 800, 150)      # prova anche 300, 150
>>> len(chunks)
>>> chunks[0]

>>> chunk_text("Prima frase. Seconda frase. Terza frase.", 30, 15)

>>> vectors = embed(["ciao", "buongiorno"])
>>> len(vectors[0])                            # 1024 con bge-m3

>>> exit()
```

## Lint e formattazione (Ruff)

Configurazione in `pyproject.toml`: righe da 80 caratteri, virgolette singole,
import ordinati, avviso sui `print` fuori da `rag.py` ed `experiments/`.

```powershell
# Segnala i problemi e corregge quelli correggibili in automatico
ruff check . --fix

# Riformatta tutti i file
ruff format .
```

In VS Code, con l'estensione Ruff e la cartella `smart-search` aperta,
la formattazione avviene a ogni salvataggio.

## Configurazione

I parametri sono in `config.py`: dimensione e overlap dei chunk, indirizzo del server dei modelli, modello di embedding.
