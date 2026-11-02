import {indexRag} from "./ragClient.ts";
import {INDEX_STAGES, RAG_EVENT} from "./ragEvents.ts";

for await (const event of indexRag(
  "C:/Users/Matteo Olivieri/Desktop/ITC/POC/RAG/smart-search/rag-engine/samples/tagliando_auto.txt",
  "f12",
  "d4",
  "tagliando_prova.txt",
)) {
  switch (event.type) {
    case RAG_EVENT.PROGRESS:
      console.log(event.stage);
      switch (event.stage) {
        case INDEX_STAGES.EMBEDDING:
          console.log(`${event.done}/${event.total}`);
          break;
      }
      break;

    case RAG_EVENT.RESULT:
      console.log("---------");
      console.log("Result:");
      console.log("---------");
      console.log("Chunks:", event.chunks);
      break;

    case RAG_EVENT.ERROR:
      console.log(`Error: ${event.code} message: ${event.message}`);
      break;
  }
}
