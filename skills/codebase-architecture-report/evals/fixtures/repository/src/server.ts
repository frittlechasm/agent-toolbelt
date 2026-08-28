import express from "express";
import { authenticate, requireScope } from "./auth";
import { chargeOrder } from "./billing";
import { createOrder } from "./orders";

export const app = express();
app.use(express.json({ limit: "32kb" }));
app.get("/ready", (_req, res) => res.json({ status: "ready" }));
app.post("/orders", authenticate, requireScope("orders:write"), async (req, res) => {
  const order = await createOrder(req.user.id, req.body.items);
  res.status(201).json(order);
});
app.post("/orders/:id/charge", authenticate, requireScope("billing:write"), async (req, res) => {
  try {
    res.json(await chargeOrder(req.params.id, req.user.id));
  } catch {
    res.status(502).json({ error: "billing_unavailable" });
  }
});
if (process.env.NODE_ENV !== "test") app.listen(3000);
