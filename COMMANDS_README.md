### 0. Preparazione (Terminale 1)

```powershell
# Entra nel motore Python
cd rag-engine

# Attiva l'ambiente virtuale
.venv\Scripts\Activate.ps1

# Controlla che Ollama abbia bge-m3 e gemma3:4b
ollama list
```

### 1. Il motore RAG passo per passo (Terminale 1)

```powershell
# Embedding: similarità tra una domanda e alcune frasi
python -m experiments.similarity "Perché la pompa si blocca quando fa molto freddo?"

# Chunking: quanti chunk e di che lunghezza
python -m experiments.chunk_stats --file samples\pompa_di_calore.txt

# Indicizza un documento (stesso --document-id: sostituisce i chunk, non li duplica)
python -m experiments.run_index --file samples\condizionatore_split.txt --folder-id f1 --document-id d4 --document-name condizionatore_split.txt

# Indicizza con l'output grezzo letto da Node (una riga JSON per evento)
python rag.py index --file samples\condizionatore_split.txt --folder-id f1 --document-id d4 --document-name condizionatore_split.txt

# Mostra documenti e chunk salvati nel vector DB
python -m experiments.inspect_db --folder-id f1

# Domanda: risposta con le fonti
python -m experiments.run_query --question "Cosa significa il codice E05?" --folder-id f1

# Domanda con i chunk recuperati e il loro punteggio
python -m experiments.run_query --question "Cosa significa il codice E05?" --folder-id f1 --debug

# Domanda con l'output grezzo: i token arrivano uno alla volta
python rag.py query --folder-id f1 --question "Cosa significa il codice E05?" --top-k 3

# Domanda senza risposta nei documenti: answer null
python -m experiments.run_query --question "Come si cambia l'olio?" --folder-id f1

# Errore gestito: evento FILE_NOT_FOUND
python -m experiments.run_index --file nonesiste.txt
```

### 2. Il motore via HTTP (Terminale 2)

```powershell
# Entra nel motore Python e attiva l'ambiente
cd rag-engine
.venv\Scripts\Activate.ps1

# Avvia il server FastAPI sulla porta 8000
uvicorn server:app --host 127.0.0.1 --port 8000
```

Dal Terminale 1:

```powershell
# Domanda al server Python, in streaming
curl.exe -N -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{\"folder_id\": \"f1\", \"question\": \"Cosa significa il codice E05?\", \"top_k\": 3}'
```

### 3. Node / Express davanti al motore (Terminale 3)

```powershell
# Entra nel backend
cd backend

# Avvia Express sulla porta 4000
node src/server.ts
```

Dal Terminale 1:

```powershell
# Controlla che il backend risponda
curl.exe http://localhost:4000/api/health

# Domanda attraverso tutta la catena: Express -> FastAPI -> modelli
curl.exe -N -X POST http://localhost:4000/api/query -H "Content-Type: application/json" -d '{\"folderId\": \"f1\", \"question\": \"Cosa significa il codice E05?\"}'

# Domanda senza "question": errore 400 dal backend
curl.exe -i -X POST http://localhost:4000/api/query -H "Content-Type: application/json" -d '{\"folderId\": \"f1\"}'
```
