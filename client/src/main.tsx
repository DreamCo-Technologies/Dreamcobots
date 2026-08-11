import { createRoot } from "react-dom/client";
import App from "./App";
import { installBackendBridge } from "./lib/runtimeBackend";
import "./index.css";

installBackendBridge();

// GitHub Pages publishes the React client under /app/ and should not register the
// production root service worker. The static website has its own worker lifecycle.
if ("serviceWorker" in navigator && import.meta.env.VITE_GITHUB_PAGES !== "true") {
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
