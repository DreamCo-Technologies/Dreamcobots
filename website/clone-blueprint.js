(function () {
  const cores = navigator.hardwareConcurrency || 0;
  const memory = navigator.deviceMemory || 0;
  const platform = navigator.platform || "";
  const tooSmall = memory > 0 && memory < 16;
  const machine = document.getElementById("machine");
  machine.textContent = "This browser reports " + (cores || "an unknown number of") + " cores"
    + (memory ? " and about " + memory + "GB." : ". It does not report exact memory.")
    + " Platform: " + (platform || "unknown") + ". "
    + (tooSmall ? "Under 16GB is too small to train a clone. " : "")
    + "This page cannot see a serial number, and it does not receive recordings or photos.";

  fetch("data/clone-blueprint.json").then(function (response) { return response.json(); }).then(function (plan) {
    document.getElementById("lead").textContent = "The live page is this site. It does not train a clone. Training, if it ever runs, runs on the computer of the person who asked. The repository is not production ready.";
    const list = document.getElementById("steps");
    plan.steps.forEach(function (step) {
      const item = document.createElement("li");
      item.textContent = step;
      list.append(item);
    });
  }).catch(function () {
    document.getElementById("lead").textContent = "The blueprint did not load.";
  });
  if (window.BuddyAdvice) window.BuddyAdvice.show("clone");
})();
