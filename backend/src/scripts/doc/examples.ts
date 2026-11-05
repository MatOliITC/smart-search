const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function* yieldExample() {
  const list = ["uno", "due", "tre"];
  for (const item of list) {
    await wait(1000);
    yield item;
  }
}
