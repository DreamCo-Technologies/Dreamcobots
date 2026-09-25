(function () {
  const kinds = ["text", "video", "movie", "reel", "notes"];
  const allowed = ["owned", "bought-with-training-license", "public-domain", "license-allows-training"];
  const refused = {
    youtube: "A YouTube page lets people watch. It does not let you download the video or train on it. This page will not download it.",
    "free-to-watch": "Free to watch is not free to train.",
    "bought-to-watch": "Buying a copy you can watch is not a license to train.",
    "found-online": "Finding a file online is not a training right."
  };
  const status = document.getElementById("study-status");
  document.getElementById("study-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const benchmark = document.getElementById("benchmark").value.trim();
    const kind = document.getElementById("kind").value;
    const source = document.getElementById("source").value;
    const note = document.getElementById("note").value.replace(/\s+/g, " ").trim();
    const hidden = document.getElementById("hidden").value.replace(/\s+/g, " ").trim();
    const rights = document.getElementById("rights").checked;
    if (refused[source]) {
      status.textContent = refused[source];
      return;
    }
    if (!benchmark || kinds.indexOf(kind) === -1 || allowed.indexOf(source) === -1) {
      status.textContent = "Use text, video, a movie, a reel, or notes that you own, bought with a training license, or that are public domain or licensed for training.";
      return;
    }
    if (!rights) {
      status.textContent = "Confirm that this source allows training, not only watching.";
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
    status.textContent = "This source can be a lesson. No file was downloaded or uploaded, and no weight was trained here. Training still happens on a machine you control.";
  });
})();
