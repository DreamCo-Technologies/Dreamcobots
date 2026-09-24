(function () {
  const kinds = ["text", "video", "movie", "reel", "notes"];
  const status = document.getElementById("study-status");
  document.getElementById("study-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const benchmark = document.getElementById("benchmark").value.trim();
    const kind = document.getElementById("kind").value;
    const note = document.getElementById("note").value.replace(/\s+/g, " ").trim();
    const hidden = document.getElementById("hidden").value.replace(/\s+/g, " ").trim();
    const rights = document.getElementById("rights").checked;
    if (!benchmark || kinds.indexOf(kind) === -1) {
      status.textContent = "Name one benchmark and choose text, video, movie, reel, or notes.";
      return;
    }
    if (!rights) {
      status.textContent = kind === "text" || kind === "notes"
        ? "Do not train on a resource you do not have the right to use."
        : "A video, movie, or reel can be studied only when you have the right to use it.";
      return;
    }
    if (note.length < 20) {
      status.textContent = "Write what you learned in your own words. The file itself is not uploaded.";
      return;
    }
    if (hidden.length < 10) {
      status.textContent = "Keep one question the note does not answer.";
      return;
    }
    const saved = JSON.parse(localStorage.getItem("dreamco-study-notes") || "[]");
    saved.push({ benchmark: benchmark, kind: kind, at: new Date().toISOString() });
    localStorage.setItem("dreamco-study-notes", JSON.stringify(saved.slice(-40)));
    status.textContent = "The note is the lesson for " + benchmark + ". No file was uploaded, no weight was trained, and the benchmark score did not change.";
  });
})();
