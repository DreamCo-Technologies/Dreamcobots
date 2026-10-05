(() => {
  const line = document.getElementById("live-feed") || document.body.appendChild(document.createElement("p"));
  const runLine = document.getElementById("live-run") || document.body.appendChild(document.createElement("p"));
  line.id = "live-feed";
  runLine.id = "live-run";
  line.textContent = "Loading the latest commit…";
  runLine.textContent = "Loading the latest run…";
  fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/commits/main").then((response) => {
    const remaining = response.headers.get("x-ratelimit-remaining");
    if (!response.ok) { line.textContent = "Commit feed blocked. Remaining requests: " + (remaining || "0") + "."; return null; }
    return response.json().then((data) => ({ data, remaining }));
  }).then((result) => {
    if (!result) return;
    const message = ((result.data.commit || {}).message || "").split("\n")[0];
    line.textContent = "Latest commit " + (result.data.sha || "").slice(0, 7) + ": " + message + ". Remaining this hour: " + (result.remaining || "unknown") + ".";
  }).catch(() => { line.textContent = "Latest commit is not loaded."; });
  fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/actions/runs?per_page=1").then((response) => response.ok ? response.json() : null).then((data) => {
    const run = data && (data.workflow_runs || [])[0];
    runLine.textContent = run ? "Latest run " + run.name + " " + (run.conclusion || run.status) : "Latest run is not loaded.";
  }).catch(() => { runLine.textContent = "Latest run is not loaded."; });
})();
