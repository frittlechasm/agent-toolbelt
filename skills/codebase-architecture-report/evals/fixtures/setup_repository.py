#!/usr/bin/env python3
"""Create a small source-backed service for architecture-report evals."""

from __future__ import annotations

import sys
from pathlib import Path


FILES = {
    "README.md": """# Orders API

Orders API accepts authenticated order requests, stores order state in Postgres, and charges
customers through the AcmePay HTTP API. It runs as one Kubernetes deployment.
""",
    "package.json": """{
  "scripts": {"start": "tsx src/server.ts", "test": "vitest run"},
  "dependencies": {"express": "5.1.0", "jose": "6.1.0", "pg": "8.16.0"},
  "devDependencies": {"supertest": "7.1.0", "tsx": "4.20.0", "vitest": "3.2.0"}
}
""",
    "src/server.ts": """import express from "express";
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
""",
    "src/auth.ts": """import { createRemoteJWKSet, jwtVerify } from "jose";

const keys = createRemoteJWKSet(new URL(process.env.OIDC_JWKS_URL!));
export async function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace(/^Bearer /, "");
  if (!token) return res.status(401).json({ error: "missing_token" });
  try {
    const verified = await jwtVerify(token, keys, {
      issuer: process.env.OIDC_ISSUER,
      audience: "orders-api",
    });
    req.user = { id: verified.payload.sub, scopes: verified.payload.scope?.split(" ") ?? [] };
    next();
  } catch {
    res.status(401).json({ error: "invalid_token" });
  }
}

export const requireScope = (scope) => (req, res, next) =>
  req.user.scopes.includes(scope) ? next() : res.status(403).json({ error: "forbidden" });
""",
    "src/orders.ts": """import { pool } from "./storage";

export async function createOrder(userId, items) {
  const total = items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0);
  const result = await pool.query(
    "insert into orders(user_id, items, total, status) values ($1, $2, $3, 'pending') returning *",
    [userId, JSON.stringify(items), total],
  );
  return result.rows[0];
}
""",
    "src/billing.ts": """import { pool } from "./storage";

export async function chargeOrder(orderId, userId) {
  const order = await pool.query("select * from orders where id = $1 and user_id = $2", [orderId, userId]);
  if (!order.rowCount) throw new Error("order_not_found");
  const response = await fetch(`${process.env.ACMEPAY_URL}/charges`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.ACMEPAY_TOKEN}`,
      "content-type": "application/json",
      "idempotency-key": orderId,
    },
    body: JSON.stringify({ orderId, amount: order.rows[0].total }),
  });
  if (!response.ok) throw new Error("charge_failed");
  await pool.query("update orders set status = 'paid' where id = $1", [orderId]);
  return response.json();
}
""",
    "src/storage.ts": """import pg from "pg";

export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
""",
    "tests/server.test.ts": """import request from "supertest";
import { describe, expect, it } from "vitest";
import { app } from "../src/server";

describe("request boundaries", () => {
  it("rejects an order without a bearer token", async () => {
    const response = await request(app).post("/orders").send({ items: [] });
    expect(response.status).toBe(401);
  });
  it.todo("does not charge the same order twice after a provider timeout");
});
""",
    "docs/adr/0001-order-storage.md": """# ADR 0001: Keep order state in Postgres

Status: accepted

The API owns order state in Postgres. AcmePay remains the payment system of record. Charging stays
synchronous for the first release; a queue may be considered if provider latency breaches the API
budget. We have not yet defined reconciliation after an ambiguous AcmePay timeout.
""",
    "migrations/001_orders.sql": """create table orders (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  items jsonb not null,
  total integer not null check (total >= 0),
  status text not null check (status in ('pending', 'paid')),
  created_at timestamptz not null default now()
);
""",
    "deploy/orders.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: api
          image: example/orders-api:1.0.0
          readinessProbe:
            httpGet: {path: /ready, port: 3000}
          envFrom:
            - secretRef: {name: orders-api-secrets}
""",
}


def main() -> None:
    workspace = Path(sys.argv[1])
    for relative, content in FILES.items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
