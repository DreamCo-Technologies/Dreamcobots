(() => {
  const line = document.createElement("p");
  line.id = "live-feed";
  line.textContent = "Loading the latest commit…";
  document.body.appendChild(line);
  fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/commits/main").then((response) => response.json()).then((data) => {
    line.textContent = "Latest commit " + (data.sha || "").slice(0, 7) + " " + ((data.commit || {}).message || "").split("\n")[0];
  }).catch(() => { line.textContent = "Latest commit is not loaded."; });
})();
