(() => {
  const line = document.getElementById("live-feed") || document.body.appendChild(document.createElement("p"));
  line.id = "live-feed";
  line.textContent = "Loading the latest commit…";
  fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/commits/main").then((response) => {
    const remaining = response.headers.get("x-ratelimit-remaining");
    if (!response.ok) { line.textContent = "Commit feed blocked. Remaining requests: " + (remaining || "0") + "."; return null; }
    return response.json().then((data) => ({ data, remaining }));
  }).then((result) => {
    if (!result) return;
    const message = ((result.data.commit || {}).message || "").split("\n")[0];
    line.textContent = "Latest commit " + (result.data.sha || "").slice(0, 7) + " " + message + ". Remaining this hour: " + (result.remaining || "unknown") + ".";
  }).catch(() => { line.textContent = "Latest commit is not loaded."; });
})();
