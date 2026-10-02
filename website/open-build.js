(function () {
  const refused = ["copy gpt", "copy claude", "distill gpt", "distill claude", "proprietary weights", "closed weights"];
  const slug = /^[A-Za-z0-9][A-Za-z0-9._-]{0,80}\/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$/;
  const secret = /ghp_|github_pat_|sk-|hf_|AKIA/;
  const status = document.getElementById("build-status");

  document.getElementById("build-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const source = document.getElementById("source").value;
    const name = document.getElementById("name").value.trim();
    const goal = document.getElementById("goal").value;
    const sample = document.getElementById("sample").value;
    const blob = (source + " " + name + " " + goal).toLowerCase().replace(/[-_\/]/g, " ");
    const link = document.getElementById("build-link");
    function stop(text) { status.textContent = text; link.hidden = true; }
    if (refused.some(function (phrase) { return blob.indexOf(phrase) !== -1; })) return stop("Closed weights are not a starting point.");
    if (!slug.test(name)) return stop("Use owner/name.");
    if (secret.test(sample)) return stop("A key-shaped string is in the pasted code. Remove it. The code was not run.");
    if (!document.getElementById("license-ok").checked || !document.getElementById("owns").checked || !document.getElementById("hidden").checked) {
      return stop("You need a license that allows training, data you own, and a hidden test.");
    }
    link.hidden = false;
    link.href = (source === "github" ? "https://github.com/" : "https://huggingface.co/") + name;
    link.textContent = "Open this open-source starting point";
    status.textContent = "Plan accepted. Read the license, then train on a machine you control. This page did not build a frontier model, did not run the pasted code, and did not score anyone else's benchmark.";
  });
})();
