(function () {
  const saved = localStorage.getItem("dreamco-theme") || "dark";
  const mode = saved === "system"
    ? (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")
    : saved;
  document.documentElement.dataset.theme = mode;
  const style = document.createElement("style");
  style.textContent = "html[data-theme=light]{--bg:#f4f6fb;--bg2:#e8edf6;--bg3:#dde3f0;--card:#ffffff;--card2:#f7f8fc;--text:#141824;--text2:#3c465f;--text3:#5c6884;--border:rgba(20,24,36,.14);--shadow:0 4px 24px rgba(20,24,36,.08);--shadow2:0 8px 48px rgba(20,24,36,.12);}";
  document.head.appendChild(style);
})();
