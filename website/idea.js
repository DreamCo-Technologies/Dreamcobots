(function () {
  const stolen = ["copy the course", "download the lessons", "scrape codecademy", "scrape the course"];
  const pages = {
    game: "game-builder.html",
    simulation: "game-builder.html",
    music: "music-creator.html",
    video: "studio.html",
    software: "codelab.html",
    school: "train-own.html",
    course: "train-own.html",
    hardware: "",
    invention: ""
  };

  function kind(text) {
    const lowered = text.toLowerCase();
    const names = ["simulation", "game", "music", "video", "hardware", "invention", "school", "course", "software"];
    for (let index = 0; index < names.length; index += 1) {
      if (lowered.indexOf(names[index]) !== -1) return names[index];
    }
    return "software";
  }

  document.getElementById("idea-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const status = document.getElementById("idea-status");
    const link = document.getElementById("idea-link");
    link.replaceChildren();
    const text = document.getElementById("idea").value.replace(/\s+/g, " ").trim();
    const notes = document.getElementById("notes").value.split("\n").map(function (note) {
      return note.replace(/\s+/g, " ").trim();
    }).filter(function (note) { return note.length >= 20; });
    const blob = (text + " " + notes.join(" ")).toLowerCase();
    if (stolen.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) {
      status.textContent = "Do not copy a course. Paste notes you wrote.";
      return;
    }
    if (text.length < 8) {
      status.textContent = "Describe the idea in a sentence.";
      return;
    }
    const chosen = kind(text);
    const page = pages[chosen];
    localStorage.setItem("dreamco-idea", JSON.stringify({ kind: chosen, notes: notes.length }));
    status.textContent = "Plan only. Nothing was built. " + (notes.length >= 2 ? "Your two notes were kept in this browser." : "Paste two notes you wrote before this counts as study.");
    if (page) {
      const anchor = document.createElement("a");
      anchor.href = page;
      anchor.textContent = "Open the existing " + chosen + " page";
      link.append(anchor);
    }
  });
})();
