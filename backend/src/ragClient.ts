import type {RagEvent} from "./ragEvents.ts";

const RAG_URL = "http://127.0.0.1:8000";

async function* readEvents(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<RagEvent> {
  const decoder = new TextDecoder();
  let buffer = "";
  for await (const bytes of body) {
    buffer += decoder.decode(bytes, {stream: true});
    const lines = buffer.split("\n");
    buffer = lines.pop()!;

    for (const line of lines) {
      if (!line) continue;
      const event = JSON.parse(line);
      yield event;
    }
  }
}

export async function* queryRag(
  folderId: string,
  question: string,
  topK: number,
): AsyncGenerator<RagEvent> {
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

  yield* readEvents(response.body!);
}
