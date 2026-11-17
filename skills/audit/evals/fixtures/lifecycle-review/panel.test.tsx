import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { expect, test, vi } from "vitest";
import { Panel } from "./panel";

vi.mock("./cache", () => ({ loadProfile: vi.fn(async () => ({})), clearCache: vi.fn() }));

test("sign out navigates to the signed-out page", async () => {
  render(<MemoryRouter initialEntries={["/"]}><Panel /></MemoryRouter>);
  await userEvent.click(screen.getByRole("button", { name: "Sign out" }));
  expect(screen.getByText("Ready")).toBeTruthy();
});
