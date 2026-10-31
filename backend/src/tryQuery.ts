import {yieldExample} from "./doc/examples.ts";
import {queryRag} from "./ragClient.ts";

for await (const event of queryRag("f1", "Cosa significa il codice E05?", 3)) {
  console.log(event);
}
console.log("fine");

let text = "";
for await (const number of yieldExample()) {
  // Per uso con frontend
  text += number;
  console.log(number);
  // Per uso terminale
  process.stdout.write(number + " ");
}
