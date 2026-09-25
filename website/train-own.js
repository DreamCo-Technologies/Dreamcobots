(function () {
  const key = "dreamco-hide-companies";
  const hide = document.getElementById("hide");
  hide.value = localStorage.getItem(key) || "";
  const stolen = ["distill", "copy the video", "copy the page", "download the video", "full transcript"];
  const kinds = ["text", "video", "movie", "github", "huggingface", "other"];

  function company(url) {
    try {
      const parsed = new URL(url);
      const host = parsed.hostname.toLowerCase().replace(/^www\./, "");
      const parts = parsed.pathname.split("/").filter(Boolean);
      if (host === "huggingface.co" && parts.length >= 2 && ["datasets", "models", "spaces"].indexOf(parts[0]) !== -1) return parts[1].toLowerCase();
      if (host === "github.com" && parts.length) return parts[0].toLowerCase();
      return host;
    } catch (error) {
      return "";
    }
  }

  document.getElementById("train-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const status = document.getElementById("train-status");
    const used = document.getElementById("used");
    used.replaceChildren();
    const subject = document.getElementById("subject").value.replace(/\s+/g, " ").trim();
    const part = document.getElementById("part").value.replace(/\s+/g, " ").trim();
    const kind = document.getElementById("kind").value;
    const own = document.getElementById("own").value.replace(/\s+/g, " ").trim();
    const restricted = hide.value.toLowerCase().split(",").map(function (item) { return item.trim(); }).filter(Boolean);
    localStorage.setItem(key, hide.value.trim());
    const notes = [];
    document.getElementById("views").value.split("\n").forEach(function (line) {
      const bits = line.split("|");
      if (bits.length < 2) return;
      const text = bits[0].replace(/\s+/g, " ").trim();
      const source = bits.slice(1).join("|").trim();
      try {
        const url = new URL(source);
        if (text.length >= 20 && url.protocol === "https:") notes.push({ text: text, source: source, company: company(source) });
      } catch (error) { /* skip bad lines */ }
    });
    const blob = [subject, part, own].concat(notes.map(function (item) { return item.text; })).join(" ").toLowerCase();
    if (subject.length < 3 || !part) {
      status.textContent = "Name the subject and at least one part.";
      return;
    }
    if (kinds.indexOf(kind) === -1) {
      status.textContent = "Use text, video, movie, GitHub, Hugging Face, or other.";
      return;
    }
    if (stolen.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      status.textContent = "Do not copy or download the source. Write your own line.";
      return;
    }
    if (notes.length < 10) {
      status.textContent = "This part needs 10 different views, each with its own https source.";
      return;
    }
    const hit = notes.slice(0, 10).map(function (item) { return item.company; }).find(function (name) { return restricted.indexOf(name) !== -1; });
    if (hit) {
      status.textContent = hit + " is restricted. Pick another source or remove the restriction.";
      return;
    }
    if (own.length < 20 || notes.some(function (item) { return item.text === own; })) {
      status.textContent = "Your own line has to be new. It cannot repeat a view.";
      return;
    }
    const saved = JSON.parse(localStorage.getItem("dreamco-own-training") || "[]");
    saved.push({ subject: subject, part: part, kind: kind });
    localStorage.setItem("dreamco-own-training", JSON.stringify(saved.slice(-40)));
    notes.slice(0, 10).forEach(function (item) {
      const row = document.createElement("li");
      row.textContent = item.company + " — ";
      const link = document.createElement("a");
      link.href = item.source;
      link.textContent = item.source;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      row.append(link);
      used.append(row);
    });
    status.textContent = "Saved your line for " + part + ". The " + kind + " file was not stored, and no weight was trained.";
  });
})();
