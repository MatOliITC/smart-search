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
# Mentre il modello scrive, tra "generating" e "result" arrivano i pezzi della risposta, uno per riga:
#   {"type": "token", "text": " codice"}
# Concatenati danno lo stesso testo di "answer"; chi non li usa può ignorarli e leggere solo il result.
# Risposta non trovata (cartella vuota, oppure domanda fuori tema) → "answer": null, "sources": [] (non è un errore),
# e nessun evento token: i pezzi di NO_ANSWER vengono trattenuti e mai inviati.
# Su CPU la risposta può richiedere 10-30 secondi (quasi tutti prima del primo token: il modello legge il prompt).
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

## Server HTTP (FastAPI)

Lo stesso motore è raggiungibile anche via HTTP, ed è così che lo userà Node.
I comandi sono gli stessi del CLI: `rag.py` (terminale) e `server.py` (HTTP)
chiamano le stesse funzioni di `commands.py`.

```powershell
# Avvia il server (solo su questo PC). --reload lo riavvia a ogni salvataggio, come nodemon
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Rotte (tutte `POST`, body JSON):

| Rotta | Body | Note |
|---|---|---|
| `/index` | `file`, `folder_id`, `document_id`, `document_name` | tutti obbligatori |
| `/query` | `folder_id`, `question`, `top_k` (default 5), `debug` (default false) | |
| `/delete` | `document_id` **oppure** `folder_id` | esattamente uno dei due |

La risposta è in streaming, in formato NDJSON (`Content-Type: application/x-ndjson`):
una riga JSON per evento, con gli stessi eventi del CLI (`progress`, `token` solo in `/query`,
`result`, `error`).

- **Body non valido** (campo mancante, `/delete` con nessuno o entrambi gli id) → status **422**,
  prima che lo stream parta.
- **Errore del motore** (file inesistente, Ollama spento, ...) → status **200**, e l'ultima riga
  dello stream è `{"type": "error", "code": ..., "message": ...}`: lo status era già partito.

Per vedere gli eventi arrivare uno alla volta serve `curl.exe -N`
(le `\"` servono solo a PowerShell). La pagina http://127.0.0.1:8000/docs
è comoda per provare le rotte, ma aspetta la risposta completa e mostra
"can't parse JSON" perché le righe sono più di un JSON: è normale.

```powershell
curl.exe -N -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{\"folder_id\": \"f1\", \"question\": \"Cosa significa il codice E05?\", \"top_k\": 3}'
curl.exe -N -X POST http://127.0.0.1:8000/index -H "Content-Type: application/json" -d '{\"file\": \"samples/pompa_di_calore.txt\", \"folder_id\": \"f1\", \"document_id\": \"d1\", \"document_name\": \"pompa.txt\"}'
curl.exe -N -X POST http://127.0.0.1:8000/delete -H "Content-Type: application/json" -d '{\"document_id\": \"non-esiste\"}'

# -i mostra anche status e header (es. 422 con body sbagliato)
curl.exe -i -X POST http://127.0.0.1:8000/delete -H "Content-Type: application/json" -d '{}'
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

File attuali: `test_prompt.py` (`extract_sources`, `format_chunk`, `build_messages`),
`test_chunking.py` (`chunk_pages`), `test_vector_store.py` (`sql_string`) e
`test_commands.py` (`run_query` con `NO_ANSWER` trattenuto; Ollama e DB sostituiti
con `monkeypatch`).

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

## Debug in VS Code

Serve l'estensione **Python** di Microsoft (porta con sé Python Debugger) e la
cartella `smart-search` aperta come cartella di lavoro: le configurazioni
sono in `smart-search/.vscode/launch.json`. Interprete: `Python: Select
Interpreter` → `rag-engine\.venv\Scripts\python.exe`.

1. Pallino rosso a sinistra del numero di riga (oppure F9).
2. `Ctrl+Shift+D` → scegliere la configurazione → F5:
   - **prova generate_stream**: solo `generate_stream` con un messaggio corto;
   - **rag.py query (E05)**: la query completa (cambiare la domanda in `args`);
   - **server (uvicorn)**: il server senza `--reload` (poi chiamarlo con `curl.exe`).
3. Variabili nel pannello Variables, F10 riga successiva, F5 continua.

I breakpoint scattano solo con F5: `python ...` lanciato dal terminale li ignora.
In alternativa, senza VS Code: `breakpoint()` nel codice → prompt `(Pdb)`
nel terminale (`p variabile`, `n`, `c`, `q`); da togliere dopo l'uso.

## Configurazione

I parametri sono in `config.py`: dimensione e overlap dei chunk, indirizzo del server dei modelli, modello di embedding, modello di generazione (`LLM_MODEL`), temperatura e lingua della risposta.

Le regole date al modello (prompt di sistema) sono in `rag/prompt.py`.

## Dove sta cosa

- `commands.py`: i tre comandi (`run_index`, `run_query`, `run_delete`) come generatori di eventi, più `with_errors`, che trasforma le eccezioni in eventi `error`.
- `rag.py`: ingresso da terminale (argomenti con argparse, eventi stampati su stdout, exit code).
- `server.py`: ingresso HTTP (body validato da FastAPI, eventi mandati in streaming).
- `rag/`, `extraction/`, `llm_client.py`: il motore vero e proprio (chunking, embeddings, vector DB, prompt, modelli). `llm_client.generate_stream` restituisce la risposta del modello un pezzo alla volta.
