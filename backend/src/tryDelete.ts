import {deleteRag} from "./ragClient.ts";
import {RAG_EVENT} from "./ragEvents.ts";

for await (const event of deleteRag("d4", null)) {
  switch (event.type) {
    case RAG_EVENT.PROGRESS:
      console.log(event.stage);
      break;

    case RAG_EVENT.RESULT:
      console.log("Deleted chunks:", event.deleted_chunks);
      break;

    case RAG_EVENT.ERROR:
      console.log(`Error: ${event.code} message: ${event.message}`);
      break;
  }
}
