import express from "express";
import cors from "cors";
import { env } from "./config/env.js";
import { healthRouter } from "./routes/health.js";
import { searchRouter } from "./routes/search.js";
import { mangaRouter } from "./routes/manga.js";
import { startScheduler } from "./jobs/scheduler.js";

const app = express();

app.use(cors({ origin: env.corsOrigin }));
app.use(express.json());

app.use("/health", healthRouter);
app.use("/api/search", searchRouter);
app.use("/api/manga", mangaRouter);

app.use((_req, res) => {
  res.status(404).json({ error: "Route inconnue." });
});

// eslint-disable-next-line @typescript-eslint/no-unused-vars
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error("Erreur non gérée", err);
  res.status(500).json({ error: "Erreur interne du serveur." });
});

app.listen(env.port, () => {
  console.log(`Manga tracker backend en écoute sur le port ${env.port}`);
  startScheduler();
});
