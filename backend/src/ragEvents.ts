type ProgressStage =
  | "extracting"
  | "chunking"
  | "embedding"
  | "saving"
  | "embedding_question"
  | "searching"
  | "generating"
  | "deleting_documents"
  | "deleting_folders";

type ProgressEvent = {
  type: "progress";
  stage: ProgressStage;
  pages?: number;
  done?: number;
  total?: number;
  chunks?: number;
};

type TokenEvent = {type: "token"; text: string};

export type Source = {
  number: number;
  document_id: string;
  document_name: string;
  page: number;
};

type QueryResultEvent = {
  type: "result";
  question: string;
  answer: string | null;
  sources: Source[];
};

type ErrorEvent = {type: "error"; code: string; message: string};

export type RagEvent =
  | ProgressEvent
  | TokenEvent
  | QueryResultEvent
  | ErrorEvent;

export const RAG_EVENT = {
  PROGRESS: "progress",
  TOKEN: "token",
  RESULT: "result",
  ERROR: "error",
} as const;
