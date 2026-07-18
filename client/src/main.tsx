import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// In development, unregister any stale service workers to prevent stale cache issues.
// In production, register the service worker for offline support.
if ("serviceWorker" in navigator) {
  if (import.meta.env.DEV) {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      registrations.forEach((r) => r.unregister());
    });
  } else {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    });
  }
}

createRoot(document.getElementById("root")!).render(<App />);
