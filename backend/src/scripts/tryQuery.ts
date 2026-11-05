// import {yieldExample} from "./doc/examples.ts";
import {queryRag} from "../rag/ragClient.ts";
import {RAG_EVENT} from "../rag/ragEvents.ts";

for await (const event of queryRag("f1", "Cosa significa il codice E05?", 3)) {
  switch (event.type) {
    case RAG_EVENT.PROGRESS:
      console.log(event.stage);
      break;

    case RAG_EVENT.TOKEN:
      process.stdout.write(event.text);
      break;

    case RAG_EVENT.RESULT:
      console.log();
      if (!event.answer) {
        console.log("No answer in documents");
        break;
      }

      const sources = event.sources;
      console.log("---------");
      console.log("Sources:");
      for (const source of sources) {
        console.log("---------");
        console.log("Index:", source.number);
        console.log("Document Id:", source.document_id);
        console.log("Document name:", source.document_name);
        console.log("Page:", source.page);
        console.log("---------");
      }
      break;

    case RAG_EVENT.ERROR:
      console.log("Error code:", event.code);
      console.log("Error message:", event.message);
      break;
  }
}

// let text = "";
// for await (const number of yieldExample()) {
//   // Per uso con frontend
//   text += number;
//   console.log(number);
//   // Per uso terminale
//   process.stdout.write(number + " ");
// }
