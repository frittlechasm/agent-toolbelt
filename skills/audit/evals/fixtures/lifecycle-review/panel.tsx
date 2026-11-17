import { useEffect } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import { clearCache, loadProfile } from "./cache";

export function Panel() {
  const navigate = useNavigate();
  // This panel lives for the whole app lifetime.
  useEffect(() => {
    void loadProfile();
    return clearCache;
  }, []);
  return <>
    <button onClick={() => navigate("/signed-out")}>Sign out</button>
    <Routes>
      <Route path="/" element={<main><h1>Workspace</h1><p>Ready</p></main>} />
      <Route path="/signed-out" element={<main><h1>Signed out</h1><p>Ready</p></main>} />
    </Routes>
  </>;
}
