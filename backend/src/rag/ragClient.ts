import {BASE_RAG_URL} from "../config.ts";
import type {DeleteEvent, IndexEvent, QueryEvent} from "./ragEvents.ts";

async function* streamRag<T>(
  route: string,
  body: {[key: string]: string | number | null},
): AsyncGenerator<T> {
  const response = await fetch(`${BASE_RAG_URL}/${route}`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Errore ${response.status}: ${detail}`);
  }

  // shortform, identica a un ciclo loop for con dentro yield
  yield* readEvents<T>(response.body!);
}

async function* readEvents<T>(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<T> {
  const decoder = new TextDecoder();
  let buffer = "";

  for await (const bytes of body) {
    // Trasforma i byte ricevuti da py in linee di testo
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
  const body = {
    folder_id: folderId,
    question: question,
    top_k: topK,
  };

  const stream = streamRag<QueryEvent>("query", body);

  yield* stream;
}

export async function* indexRag(
  file: string,
  folderId: string,
  documentId: string,
  documentName: string,
): AsyncGenerator<IndexEvent> {
  const body = {
    file,
    folder_id: folderId,
    document_id: documentId,
    document_name: documentName,
  };

  const stream = streamRag<IndexEvent>("index", body);

  yield* stream;
}

export async function* deleteRag(
  documentId: string | null,
  folderId: string | null,
): AsyncGenerator<DeleteEvent> {
  const body = {
    document_id: documentId,
    folder_id: folderId,
  };

  const stream = streamRag<DeleteEvent>("delete", body);

  yield* stream;
}
