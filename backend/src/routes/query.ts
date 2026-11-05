import {Router} from "express";
import {queryRag} from "../rag/ragClient.ts";

export const queryRouter = Router();

const DEFAULT_TOP_K = 5;

queryRouter.post("/", async (req, res) => {
  const folderId = req.body?.folderId;
  const question = req.body?.question;
  const topK = req.body?.topK ?? DEFAULT_TOP_K;

  if (typeof folderId !== "string" || folderId.trim() === "") {
    res.status(400).json({message: "folderId is required"});
    return;
  }
  if (typeof question !== "string" || question.trim() === "") {
    res.status(400).json({message: "question is required"});
    return;
  }
  if (!Number.isInteger(topK) || topK < 1) {
    res.status(400).json({message: "topK must be a positive integer"});
    return;
  }

  res.status(200).type("application/x-ndjson");

  try {
    for await (const event of queryRag(folderId, question, topK)) {
      res.write(JSON.stringify(event) + "\n");
    }
    res.end();
  } catch (error) {
    console.error("query failed:", error);

    if (!res.headersSent) {
      res.status(502).json({message: "RAG engine unavailable"});
      return;
    }

    const errorEvent = {
      type: "error",
      code: "STREAM_INTERRUPTED",
      message: "Connection with the RAG engine was interrupted",
    };
    res.write(JSON.stringify(errorEvent) + "\n");
    res.end();
  }
});
