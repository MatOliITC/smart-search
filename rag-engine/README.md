# rag-engine

Motore RAG in Python: estrazione testo, chunking, embeddings, vector DB, ricerca e risposta con fonti.
Tutti i comandi si lanciano dalla cartella `rag-engine`.

## Prerequisiti

- Python 3.12
- Ollama avviato (icona vicino all'orologio) con il modello di embedding e quello di generazione scaricati:

```powershell
ollama pull bge-m3
ollama pull gemma3:4b
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
# Su stdout stampa solo righe JSON (una per evento: progress, result, error), pensate per Node.
python rag.py index --file samples\pompa_di_calore.txt --folder-id f1 --document-id d1 --document-name pompa.txt

# Fa la parte di Node: lancia rag.py index, legge le righe JSON e le traduce in testo
# (--folder-id, --document-id e --document-name hanno valori di default: f1, d1, documento.txt)
python -m experiments.run_index --file samples\pompa_di_calore.txt
python -m experiments.run_index --file samples\tagliando_auto.txt --folder-id f2 --document-id d2 --document-name tagliando_auto.txt

# Risponde a una domanda usando solo i documenti della cartella indicata
# Cerca i --top-k chunk più pertinenti, li passa a gemma3:4b e restituisce la risposta con le fonti:
#   {"type": "result", "question": "...", "answer": "... [1].", "sources": [{"number": 1, "document_id": "d1", "document_name": "pompa.txt", "page": 1}]}
# Risposta non trovata (cartella vuota, oppure domanda fuori tema) → "answer": null, "sources": [] (non è un errore).
# Su CPU la risposta può richiedere 10-30 secondi.
python rag.py query --folder-id f1 --question "Cosa significa il codice E05?" --top-k 3
python rag.py query --folder-id f1 --question "Come si cambia l'olio?" --top-k 3

# --debug aggiunge al result anche i chunk letti dal modello (con score e testo) e i messaggi inviati
python rag.py query --folder-id f1 --question "Cosa significa il codice E05?" --debug

# Fa la parte di Node: lancia rag.py query e stampa risposta e fonti in modo leggibile
python -m experiments.run_query --question "Cosa significa il codice E05?" --folder-id f1 --top-k 3
python -m experiments.run_query --question "Cosa significa il codice E05?" --folder-id f1 --top-k 3 --debug

# Rimuove dal vector DB i chunk di un documento oppure di un'intera cartella (uno dei due argomenti)
# Il result dice quanti chunk sono stati cancellati:
#   {"type": "result", "document_id": "d2", "folder_id": null, "deleted_chunks": 1}
# Un id che non esiste (o il DB ancora vuoto) non è un errore: "deleted_chunks": 0, exit code 0.
# Attenzione: cancella davvero. Per riavere i documenti di prova, reindicizzarli con run_index (serve Ollama acceso).
python rag.py delete --document-id d2
python rag.py delete --folder-id f1

# Avvia esperimento: similarità tra una domanda e alcune frasi
python -m experiments.similarity
python -m experiments.similarity "Ogni quanto devo pulire il filtro?"

# Statistiche sui chunk (utile quando cambi CHUNK_SIZE in config.py)
python -m experiments.chunk_stats --file samples\pompa_di_calore.txt

# Ispeziona il vector DB: documenti e chunk salvati, con anteprima del testo
python -m experiments.inspect_db
python -m experiments.inspect_db --folder-id f1
```

## Prove di errore

```powershell
# Argomento mancante → errore di argparse (testo, non JSON), exit code 2
python rag.py index --folder-id f1 --document-id d1 --document-name x

# File inesistente → {"type": "error", "code": "FILE_NOT_FOUND", ...}, exit code 1
python -m experiments.run_index --file nonesiste.txt

# Formato non gestito → UNSUPPORTED_FORMAT
python -m experiments.run_index --file pyproject.toml

# Ollama spento → MODEL_SERVER_UNREACHABLE (dopo qualche secondo di tentativi)
```

Codici di errore possibili: `FILE_NOT_FOUND`, `UNSUPPORTED_FORMAT`, `UNKNOWN_ENCODING`,
`EMPTY_FILE`, `MODEL_SERVER_UNREACHABLE`, `MODEL_NOT_FOUND`, `NOT_IMPLEMENTED`,
`INTERNAL_ERROR` (errore imprevisto: il traceback completo va su stderr).

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

## Test (pytest)

I test sono in `tests/` (file `test_*.py`, funzioni `test_*`) e coprono solo le parti
deterministiche: non usano Ollama né il vector DB. Configurazione in `pyproject.toml`.

File attuali: `test_prompt.py` (`extract_sources`) e `test_chunking.py` (`chunk_pages`).

```powershell
pytest                          # tutti i test
pytest -v                       # un test per riga, con il nome
pytest tests/test_chunking.py   # solo un file
pytest -vv                      # differenze complete quando un test fallisce
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

In VS Code, con l'estensione Ruff (`charliermarsh.ruff`) installata e la
cartella `smart-search` aperta come cartella di lavoro (File → Open Folder),
a ogni salvataggio il file viene formattato e gli import riordinati
(impostazioni in `smart-search/.vscode/settings.json`). Il salvataggio non
applica le altre correzioni di `ruff check` (es. commenti oltre 80 colonne).

## Configurazione

I parametri sono in `config.py`: dimensione e overlap dei chunk, indirizzo del server dei modelli, modello di embedding, modello di generazione (`LLM_MODEL`), temperatura e lingua della risposta.

Le regole date al modello (prompt di sistema) sono in `rag/prompt.py`.
