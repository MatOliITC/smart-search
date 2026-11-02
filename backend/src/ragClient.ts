import type {DeleteEvent, IndexEvent, QueryEvent} from "./ragEvents.ts";

const RAG_URL = "http://127.0.0.1:8000";

async function* readEvents<T>(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<T> {
  const decoder = new TextDecoder();
  let buffer = "";

  for await (const bytes of body) {
    buffer += decoder.decode(bytes, {stream: true});
    const lines = buffer.split("\n");
    buffer = lines.pop()!;

    for (const line of lines) {
      if (!line) continue;
      const event = JSON.parse(line) as T;
      yield event;
    }
  }
}

export async function* queryRag(
  folderId: string,
  question: string,
  topK: number,
): AsyncGenerator<QueryEvent> {
  const response = await fetch(`${RAG_URL}/query`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      folder_id: folderId,
      question: question,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Errore ${response.status}: ${detail}`);
  }

  // shortform, identica a un ciclo loop for con dentro yield
  yield* readEvents<QueryEvent>(response.body!);
}

export async function* indexRag(
  file: string,
  folderId: string,
  documentId: string,
  documentName: string,
): AsyncGenerator<IndexEvent> {
  const response = await fetch(`${RAG_URL}/index`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      file,
      folder_id: folderId,
      document_id: documentId,
      document_name: documentName,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Errore ${response.status}: ${detail}`);
  }

  yield* readEvents<IndexEvent>(response.body!);
}

export async function* deleteRag(
  documentId: string | null,
  folderId: string | null,
): AsyncGenerator<DeleteEvent> {
  const response = await fetch(`${RAG_URL}/delete`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      document_id: documentId,
      folder_id: folderId,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Errore ${response.status}: ${detail}`);
  }

  yield* readEvents<DeleteEvent>(response.body!);
}
