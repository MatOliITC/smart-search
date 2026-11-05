import {PORT} from "./config.ts";
import app from "./app.ts";

app.listen(PORT, () => {
  console.log(`App listen on port: ${PORT}`);
});
