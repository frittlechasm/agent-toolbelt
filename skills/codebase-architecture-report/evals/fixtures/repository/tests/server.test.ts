import request from "supertest";
import { describe, expect, it } from "vitest";
import { app } from "../src/server";

describe("request boundaries", () => {
  it("rejects an order without a bearer token", async () => {
    const response = await request(app).post("/orders").send({ items: [] });
    expect(response.status).toBe(401);
  });
  it.todo("does not charge the same order twice after a provider timeout");
});
