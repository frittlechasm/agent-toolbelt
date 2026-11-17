import { StrictMode, useEffect, useState } from "react";
import { BrowserRouter } from "react-router-dom";
import { Panel } from "./panel";

function Shell() {
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);
  return <Panel key={ready ? "ready" : "boot"} />;
}

export function App() {
  return <StrictMode><BrowserRouter><Shell /></BrowserRouter></StrictMode>;
}
