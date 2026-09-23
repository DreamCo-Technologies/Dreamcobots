/* Shared Buddy desk chrome. No API keys. */
(function () {
  const current = (location.pathname.split("/").pop() || "index.html").split("?")[0];
  const links = [
    { href: "repository-guide.html", label: "Start Here" },
    { href: "buddy.html", label: "Chat" },
    { href: "chat-sync.html", label: "This chat" },
    { href: "goals.html", label: "Goals" },
    { href: "hub.html", label: "Hub" },
    { href: "learn-hf.html", label: "Learn" },
    { href: "work.html", label: "Tasks" },
    { href: "os.html", label: "OS" },
    { href: "actions.html", label: "Actions" },
    { href: "desks.html", label: "Desks" },
    { href: "sources.html", label: "Sources" },
    { href: "devices.html", label: "Devices" },
    { href: "recover.html", label: "Recover" },
    { href: "build.html", label: "Build" },
    { href: "https://github.com/DreamCo-Technologies/Dreamcobots", label: "GitHub", ext: true }
  ];
  const host = document.getElementById("desk-header");
  if (!host) return;
  const linkHtml = links.map((l) => {
    const ext = l.ext ? ' target="_blank" rel="noopener"' : "";
    const on = !l.ext && current === l.href ? " buddy-header-link-on" : "";
    return `<a class="buddy-header-link${on}" href="${l.href}"${ext}>${l.label}</a>`;
  }).join("");
  host.outerHTML = `
  <header class="buddy-simple-header">
    <a class="buddy-wordmark" href="buddy.html" aria-label="Buddy home">
      <img src="assets/images/buddy-icon-192.png" alt="" width="38" height="38" />
      <span><strong>Buddy</strong><small>by DreamCo</small></span>
    </a>
    <div class="buddy-header-actions">${linkHtml}</div>
  </header>
  <p class="desk-honest"><strong>GitHub Pages is static.</strong> Hugging Face public cards work here. GitHub live runs use cached JSON (the API is blocked from this origin). Grok teacher stays on the hosted app. No keys in this site. A closed laptop is not a worker.</p>`;
})();
