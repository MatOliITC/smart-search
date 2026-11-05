import express from "express";
import {healthRouter} from "./routes/health.ts";
import {queryRouter} from "./routes/query.ts";

const app = express();

app.use(express.json());

app.use("/api/health", healthRouter);
app.use("/api/query", queryRouter);

export default app;
