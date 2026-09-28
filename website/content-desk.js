(function () {
  function clip(text, limit) {
    const clean = String(text || "").replace(/\s+/g, " ").trim();
    if (clean.length <= limit) return clean;
    const room = clean.slice(0, Math.max(0, limit - 1)).split(" ");
    room.pop();
    return (room.join(" ") || clean.slice(0, limit - 1)).replace(/\s+$/, "") + "…";
  }

  function packet(subject, when, link, formats) {
    const topic = String(subject || "").replace(/\s+/g, " ").trim().slice(0, 160);
    const base = { posted: false, video_generated: false, reaches_instagram: false };
    if (topic.length < 3) return Object.assign({ accepted: false, reason: "Name the content." }, base);
    const schedule = String(when || "").replace(/\s+/g, " ").trim().slice(0, 80) || "Pick a time. Buddy does not know when your audience is online.";
    const cleanLink = String(link || "").replace(/\s+/g, " ").trim().slice(0, 200);
    let body = topic + ". One step. Not posted until you post it.";
    if (cleanLink) body += " " + cleanLink;
    const drafts = (formats.platforms || []).map(function (item) {
      const room = item.id === "x" && cleanLink ? Math.max(40, item.limit - 24) : item.limit;
      const draft = { id: item.id, name: item.name, shape: item.shape, limit: item.limit, text: clip(body, room) };
      if (item.title_limit) draft.title = clip(topic, item.title_limit);
      draft.within_limit = draft.text.length <= item.limit && (!draft.title || draft.title.length <= item.title_limit);
      return draft;
    });
    return Object.assign({
      accepted: true,
      platforms: drafts,
      learned: { platforms: drafts.length, weights_trained: false, posted: false, note: formats.note },
      angles: ["Open on the problem in " + topic + ".", "Show one step a viewer can copy.", "Show the result, then how you got there."],
      shots: ["Three seconds on the problem, tight on the work.", "One step, close enough to copy.", "The result, then the line you want remembered."],
      lines: ["This is " + topic + ", in one step.", "Do this part first.", "That is the whole piece."],
      caption: clip(body, 2200),
      schedule: schedule,
      link: cleanLink,
      reason: "Buddy wrote one draft per network from public format rules. It did not train a model, render a video, or publish a post."
    }, base);
  }

  const learned = document.getElementById("learned");
  let rules = { platforms: [] };
  fetch("data/social-formats.json").then(function (response) { return response.json(); }).then(function (data) {
    rules = data;
    learned.textContent = data.platforms.length + " networks. " + data.note;
  }).catch(function () {
    learned.textContent = "The format list did not load.";
  });

  let latest = null;
  document.getElementById("content-form").addEventListener("submit", function (event) {
    event.preventDefault();
    latest = packet(document.getElementById("subject").value, document.getElementById("when").value, document.getElementById("link").value, rules);
    const list = document.getElementById("drafts");
    list.replaceChildren();
    (latest.platforms || []).forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.name + " (" + row.text.length + "/" + row.limit + "): " + (row.title ? row.title + " — " : "") + row.text;
      list.append(item);
    });
    document.getElementById("packet").textContent = latest.accepted ? latest.reason : latest.reason;
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
})();
