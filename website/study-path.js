(function () {
  const kinds = ["text", "video", "movie", "reel", "notes", "book"];
  const study = ["owned", "youtube", "bought-book", "free-to-watch", "public-domain", "license-allows-training"];
  const stolen = ["distill", "copy the video", "copy the book", "full transcript", "download the video", "paste the page"];
  const status = document.getElementById("study-status");
  document.getElementById("study-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const kind = document.getElementById("kind").value;
    const source = document.getElementById("source").value;
    const notes = [];
    document.getElementById("views").value.split("\n").forEach(function (line) {
      const clean = line.replace(/\s+/g, " ").trim();
      if (clean && notes.indexOf(clean) === -1) notes.push(clean);
    });
    const own = document.getElementById("own").value.replace(/\s+/g, " ").trim();
    const blob = notes.concat([own, source]).join(" ").toLowerCase();
    if (kinds.indexOf(kind) === -1 || study.indexOf(source) === -1) {
      status.textContent = "Choose a book, a video, or YouTube, then write ten views.";
      return;
    }
    if (stolen.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      status.textContent = "Do not distill, download, or copy the source. Write your own view.";
      return;
    }
    if (notes.length < 10 || notes.slice(0, 10).some(function (line) { return line.length < 20; })) {
      status.textContent = "Write 10 different views before your own line. Each view needs a real sentence.";
      return;
    }
    if (own.length < 20 || notes.indexOf(own) !== -1) {
      status.textContent = "Your own line has to be new. It cannot repeat one of the ten views.";
      return;
    }
    const saved = JSON.parse(localStorage.getItem("dreamco-perspectives") || "[]");
    saved.push({ source: source, kind: kind, benchmark: document.getElementById("benchmark").value.trim() });
    localStorage.setItem("dreamco-perspectives", JSON.stringify(saved.slice(-40)));
    status.textContent = "Stored your ten views and your own line. The video or book was not downloaded, and no weight was trained.";
  });

  document.getElementById("any-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const clean = document.getElementById("any-note").value.replace(/\s+/g, " ").trim();
    const box = document.getElementById("any-status");
    if (stolen.some(function (phrase) { return clean.toLowerCase().indexOf(phrase) !== -1; })) {
      box.textContent = "Do not distill or copy the source. Write from the comparison.";
      return;
    }
    if (clean.length < 20) {
      box.textContent = "Give a real note. One word is not enough to compare.";
      return;
    }
    const topic = clean.split(/\s+/).slice(0, 4).join(" ");
    box.textContent = "Compared ten ways around " + topic + ". Kept our line. Did not keep the note and did not train a weight.";
  });
})();
