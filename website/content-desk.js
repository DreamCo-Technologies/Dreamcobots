(function () {
  function packet(subject, when, link) {
    const topic = String(subject || "").replace(/\s+/g, " ").trim().slice(0, 160);
    const base = { posted: false, video_generated: false, reaches_instagram: false };
    if (topic.length < 3) return Object.assign({ accepted: false, reason: "Name the content." }, base);
    const schedule = String(when || "").replace(/\s+/g, " ").trim().slice(0, 80);
    return Object.assign({
      accepted: true,
      angles: [
        "Open on the problem in " + topic + ".",
        "Show one step a viewer can copy.",
        "Show the result, then how you got there."
      ],
      shots: [
        "Three seconds on the problem, tight on the work.",
        "One step, close enough to copy.",
        "The result, then the line you want remembered."
      ],
      lines: [
        "This is " + topic + ", in one step.",
        "Do this part first.",
        "That is the whole piece."
      ],
      caption: topic + ". One step. Not posted until you post it.",
      schedule: schedule || "Pick a time. Buddy does not know when your audience is online.",
      link: String(link || "").replace(/\s+/g, " ").trim().slice(0, 200),
      reason: "Buddy wrote the idea, the shots, and the caption. It did not render a video or publish the post."
    }, base);
  }

  let latest = null;
  document.getElementById("content-form").addEventListener("submit", function (event) {
    event.preventDefault();
    latest = packet(document.getElementById("subject").value, document.getElementById("when").value, document.getElementById("link").value);
    document.getElementById("packet").textContent = JSON.stringify(latest, null, 2);
  });
  document.getElementById("save").addEventListener("click", function () {
    if (!latest || !latest.accepted) return;
    const file = new Blob([JSON.stringify(latest, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "buddy-content.json";
    link.click();
    URL.revokeObjectURL(link.href);
  });
  window.BuddyContent = { packet: packet };
})();
