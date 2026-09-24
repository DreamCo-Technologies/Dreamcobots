(function () {
  const weights = [".safetensors", ".bin", ".gguf", ".pt", ".pth", ".onnx", ".ckpt", ".msgpack"];
  const status = document.getElementById("desk-status");
  const view = document.getElementById("file-view");

  function say(text) { status.textContent = text; }

  function suffix(path) {
    const clean = (path || "").toLowerCase();
    const dot = clean.lastIndexOf(".");
    return dot === -1 ? "" : clean.slice(dot);
  }

  function choose(mode, kind, name, path) {
    name = (name || "").trim().replace(/^\/+|\/+$/g, "");
    path = (path || "").trim().replace(/^\/+/, "");
    if (kind !== "github" && kind !== "huggingface") throw new Error("Choose GitHub or Hugging Face.");
    if (name.indexOf("..") !== -1 || path.indexOf("..") !== -1 || name.split("/").length < 2) throw new Error("Use owner/name.");
    const page = kind === "github"
      ? "https://github.com/" + name + (path ? "/blob/main/" + path : "")
      : "https://huggingface.co/" + name + (path ? "/blob/main/" + path : "");
    if (mode === "lookup") {
      const search = kind === "github"
        ? "https://github.com/search?q=repo:" + encodeURIComponent(name) + "&type=code"
        : "https://huggingface.co/search/full-text?q=" + encodeURIComponent(name + (path ? " " + path : ""));
      return { opens: search, reads: false, reason: "Lookup opens search on the site you chose." };
    }
    if (mode === "try") return { opens: kind === "huggingface" ? "https://huggingface.co/" + name : "https://github.com/" + name, reads: false, reason: "Try opens it on its own site. Buddy does not load the weights." };
    if (mode === "test") return { opens: "model-bench.html", also: page, reads: false, reason: "Test opens the bench. The hidden check still runs on a machine you control." };
    if (weights.indexOf(suffix(path)) !== -1) return { opens: page, reads: false, reason: "This is a weight file. Buddy opens its page and does not load the weights." };
    if (!path) return { opens: page, reads: false, reason: "No file path was given, so Buddy opens the project." };
    const read = kind === "github"
      ? "https://api.github.com/repos/" + name + "/contents/" + path
      : "https://huggingface.co/" + name + "/raw/main/" + path;
    return { opens: page, readUrl: read, reads: kind === "github", reason: "Buddy is opening the text file." };
  }

  function review(text) {
    const notes = [];
    if (/ghp_|github_pat_|sk-|hf_|AKIA/.test(text)) notes.push("A key-shaped string is in the text. Remove it before saving.");
    if (/frontier model trained|beats gpt|beats claude/i.test(text)) notes.push("This claims a win or a trained frontier model. Do not ship that without a score.");
    if (/TODO|FIXME/.test(text)) notes.push("There is an unfinished note.");
    if (!notes.length) notes.push("No key, no unfinished note, and no unsupported win claim. This is not a full review.");
    return notes;
  }

  async function showFile(result) {
    view.textContent = "";
    if (!result.reads) return;
    const response = await fetch(result.readUrl, { headers: { Accept: "application/vnd.github+json" } });
    if (!response.ok) {
      say(result.reason + " The file page is open, but the text could not be read from here.");
      return;
    }
    const body = await response.json();
    if (!body.content || body.size > 100000) {
      say("The file is too large to read here. Its page is open.");
      return;
    }
    const binary = atob(body.content.replace(/\n/g, ""));
    const bytes = Uint8Array.from(binary, function (char) { return char.charCodeAt(0); });
    view.textContent = new TextDecoder().decode(bytes);
    say("File opened. No model was loaded.");
  }

  document.getElementById("desk-form").addEventListener("submit", async function (event) {
    event.preventDefault();
    const mode = document.getElementById("mode").value;
    try {
      const result = choose(mode, document.getElementById("kind").value, document.getElementById("name").value, document.getElementById("path").value);
      say(result.reason);
      document.getElementById("open-link").href = result.opens;
      document.getElementById("open-link").hidden = false;
      if (result.also) window.open(result.also, "_blank", "noopener");
      window.open(result.opens, "_blank", "noopener");
      await showFile(result);
    } catch (error) {
      say(error.message);
    }
  });

  document.getElementById("review-form").addEventListener("submit", function (event) {
    event.preventDefault();
    document.getElementById("review-out").textContent = review(document.getElementById("review-text").value).join("\n");
  });
})();
