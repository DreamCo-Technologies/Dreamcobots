(function () {
  function beats(group, name, topic) {
    if (name === "Poem" || name === "Haiku" || name === "Spoken word" || name === "Original verse") {
      return [
        topic + ", kept small and near.",
        "One step, then the next is clear.",
        "The hands do what the line has said.",
        "Stop before a borrowed thread."
      ];
    }
    if (group === "commercial") {
      return [
        "Open on the problem in " + topic + ".",
        "Show one step. Do not invent a price or a review.",
        "End on the result. This " + name + " is a script, not a finished ad."
      ];
    }
    if (group === "music") {
      return [
        name + " for " + topic + ": a picture, then a line you wrote.",
        "Do not use someone else's recording unless you have the right.",
        "Cut back to the result. No video file is rendered."
      ];
    }
    if (group === "long") {
      return [
        name + ": why " + topic + " matters in the first minute.",
        "One example a viewer can check.",
        "Close with what to do next. This is an outline, not a filmed show."
      ];
    }
    if (group === "note") {
      return [
        name + ": " + topic + ".",
        "Say only what you can stand behind.",
        "Leave the post unpublished until you send it."
      ];
    }
    return [
      name + ": open on " + topic + ".",
      "Show one step a viewer can copy.",
      "Close on the result. Not posted until you post it."
    ];
  }

  function clip(text, limit) {
    const clean = String(text || "").replace(/\s+/g, " ").trim();
    if (clean.length <= limit) return clean;
    const room = clean.slice(0, Math.max(0, limit - 1)).split(" ");
    room.pop();
    return (room.join(" ") || clean.slice(0, limit - 1)).replace(/\s+$/, "") + "…";
  }

  function packet(subject, when, link, formats, kind) {
    const topic = String(subject || "").replace(/\s+/g, " ").trim().slice(0, 160);
    const base = { posted: false, video_generated: false, reaches_instagram: false };
    if (topic.length < 3) return Object.assign({ accepted: false, reason: "Name the content." }, base);
    const chosen = (formats.types || []).find(function (item) { return item.id === kind; });
    if (!chosen) return Object.assign({ accepted: false, reason: "That content type is not in the list." }, base);
    const script = beats(chosen.group, chosen.name, topic);
    const schedule = String(when || "").replace(/\s+/g, " ").trim().slice(0, 80) || "Pick a time. Buddy does not know when your audience is online.";
    const cleanLink = String(link || "").replace(/\s+/g, " ").trim().slice(0, 200);
    let body = script.join(" ");
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
      kind: chosen.id,
      script: script,
      platforms: drafts,
      learned: { platforms: drafts.length, weights_trained: false, posted: false, note: formats.note },
      angles: ["Open on the problem in " + topic + ".", "Show one step a viewer can copy.", "Show the result, then how you got there."],
      shots: ["Three seconds on the problem, tight on the work.", "One step, close enough to copy.", "The result, then the line you want remembered."],
      lines: ["This is " + topic + ", in one step.", "Do this part first.", "That is the whole piece."],
      caption: clip(body, 2200),
      cost: { usd: 0, charged: false, paid_api: false, voice_clone_trained: false, image_clone_trained: false },
      schedule: schedule,
      link: cleanLink,
      reason: "Buddy wrote a " + chosen.name + " and one draft per network. It did not film, render, or publish it."
    }, base);
  }

  const learned = document.getElementById("learned");
  const kindSelect = document.getElementById("kind");
  let rules = { platforms: [], types: [] };
  Promise.all([
    fetch("data/social-formats.json").then(function (response) { return response.json(); }),
    fetch("data/social-types.json").then(function (response) { return response.json(); })
  ]).then(function (pair) {
    rules = pair[0];
    rules.types = pair[1].types;
    pair[1].types.forEach(function (item) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.name;
      kindSelect.append(option);
    });
    if (kindSelect.querySelector("[value='feed-post']")) kindSelect.value = "feed-post";
    learned.textContent = pair[0].platforms.length + " networks and " + pair[1].types.length + " content types. " + pair[1].note;
  }).catch(function () {
    learned.textContent = "The format list did not load.";
  });

  let latest = null;
  function show(result) {
    latest = result;
    const list = document.getElementById("drafts");
    list.replaceChildren();
    if (result.rows) {
      result.rows.forEach(function (row) {
        const item = document.createElement("li");
        item.textContent = row.name + ": " + row.line;
        list.append(item);
      });
    }
    (result.platforms || []).forEach(function (row) {
      const item = document.createElement("li");
      item.textContent = row.name + " (" + row.text.length + "/" + row.limit + "): " + (row.title ? row.title + " — " : "") + row.text;
      list.append(item);
    });
    if (result.script) {
      const script = document.createElement("li");
      script.textContent = "Script: " + result.script.join(" ");
      list.prepend(script);
    }
    document.getElementById("packet").textContent = result.reason || "Nothing made yet.";
  }
  document.getElementById("content-form").addEventListener("submit", function (event) {
    event.preventDefault();
    show(packet(document.getElementById("subject").value, document.getElementById("when").value, document.getElementById("link").value, rules, kindSelect.value));
  });
  document.getElementById("lineup").addEventListener("click", function () {
    const topic = document.getElementById("subject").value.replace(/\s+/g, " ").trim();
    if (topic.length < 3) {
      show({ accepted: false, reason: "Name the content." });
      return;
    }
    const rows = rules.types.map(function (item) {
      return { id: item.id, name: item.name, line: beats(item.group, item.name, topic)[0] };
    });
    show({ accepted: true, posted: false, video_generated: false, rows: rows, reason: rows.length + " types written as one line each. None were filmed or posted." });
  });
  function grant(owner, other, kind, statement) {
    const ownerName = String(owner || "").replace(/\s+/g, " ").trim().slice(0, 80);
    const otherName = String(other || "").replace(/\s+/g, " ").trim().slice(0, 80) || ownerName;
    const words = String(statement || "").replace(/\s+/g, " ").trim().toLowerCase().slice(0, 80);
    const base = { kind: kind, trained: false, rendered: false, elevenlabs_called: false, revoked: false };
    if (kind !== "voice" && kind !== "image") return Object.assign({ accepted: false, reason: "Choose voice or image." }, base);
    if (ownerName.length < 2 || words.indexOf(ownerName.toLowerCase()) === -1 || words.indexOf("allow") === -1) {
      return Object.assign({ accepted: false, reason: "The owner has to write the permission, including their name and the word allow." }, base);
    }
    if (words.indexOf(otherName.toLowerCase()) === -1) return Object.assign({ accepted: false, reason: "Name the person who may use it, in the owner's own words." }, base);
    if (/\b(child|kid|minor|teen)\b/.test(words)) return Object.assign({ accepted: false, reason: "Buddy will not take a child's voice or image." }, base);
    return Object.assign({ accepted: true, owner: ownerName, user: otherName, reason: "Permission is recorded. No voice model and no image model is in this repository, so nothing is cloned." }, base);
  }

  const grantKey = "dreamco-content-grants";
  function savedGrants() {
    try {
      const rows = JSON.parse(localStorage.getItem(grantKey) || "[]");
      return Array.isArray(rows) ? rows : [];
    } catch (error) {
      return [];
    }
  }
  function useGrant(grants, owner, other, kind) {
    const ownerName = String(owner || "").replace(/\s+/g, " ").trim().slice(0, 80);
    const otherName = String(other || "").replace(/\s+/g, " ").trim().slice(0, 80) || ownerName;
    const match = grants.find(function (item) {
      return item.accepted && !item.revoked && item.owner === ownerName && item.user === otherName && item.kind === kind;
    });
    if (!match) return { accepted: false, trained: false, rendered: false, reason: "That person has not allowed this use." };
    return { accepted: true, trained: false, rendered: false, elevenlabs_called: false, reason: match.reason };
  }

  document.getElementById("clone-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const result = grant(document.getElementById("clone-owner").value, document.getElementById("clone-user").value, document.getElementById("clone-kind").value, document.getElementById("clone-words").value);
    if (result.accepted) {
      const rows = savedGrants();
      rows.push(result);
      localStorage.setItem(grantKey, JSON.stringify(rows));
    }
    document.getElementById("clone-status").textContent = result.reason;
  });
  document.getElementById("clone-play").addEventListener("click", function () {
    const kind = document.getElementById("clone-kind").value;
    const allowed = useGrant(savedGrants(), document.getElementById("clone-owner").value, document.getElementById("clone-user").value, kind);
    const file = document.getElementById("clone-file").files[0];
    if (!allowed.accepted) {
      document.getElementById("clone-status").textContent = allowed.reason;
      return;
    }
    if (!file) {
      document.getElementById("clone-status").textContent = "Permission is not a clone. Add the owner's original file. Buddy cannot invent the voice or the face.";
      return;
    }
    const url = URL.createObjectURL(file);
    if (kind === "voice" && file.type.indexOf("audio/") === 0) {
      const audio = document.getElementById("clone-audio");
      audio.hidden = false;
      audio.src = url;
      audio.play();
      document.getElementById("clone-status").textContent = "Playing the original recording. It was not cloned.";
      return;
    }
    if (kind === "image" && file.type.indexOf("image/") === 0) {
      const photo = document.getElementById("clone-photo");
      photo.hidden = false;
      photo.src = url;
      document.getElementById("clone-status").textContent = "Showing the original photo. It was not cloned.";
      return;
    }
    document.getElementById("clone-status").textContent = "That file does not match the kind you chose.";
  });
  document.getElementById("clone-revoke").addEventListener("click", function () {
    const ownerName = document.getElementById("clone-owner").value.replace(/\s+/g, " ").trim().slice(0, 80);
    const otherName = document.getElementById("clone-user").value.replace(/\s+/g, " ").trim().slice(0, 80) || ownerName;
    const kind = document.getElementById("clone-kind").value;
    const rows = savedGrants();
    let found = false;
    rows.forEach(function (item) {
      if (item.owner === ownerName && item.user === otherName && item.kind === kind) {
        item.revoked = true;
        found = true;
      }
    });
    localStorage.setItem(grantKey, JSON.stringify(rows));
    document.getElementById("clone-status").textContent = found ? "Permission revoked." : "No matching permission to revoke.";
  });
  ["A voice model file is not in this repository.", "An image model file is not in this repository.", "ElevenLabs is not called.", "The release file says this repository is not production ready.", "Social posts are written here. Buddy does not log into the networks."].forEach(function (line) {
    const item = document.createElement("li");
    item.textContent = line;
    document.getElementById("clone-gap").append(item);
  });
  document.getElementById("speak").addEventListener("click", function () {
    if (!latest || !latest.script || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(latest.script.join(" ")));
  });
  document.getElementById("poster").addEventListener("click", function () {
    if (!latest || !latest.script) return;
    const board = document.getElementById("poster-board");
    const pen = board.getContext("2d");
    board.hidden = false;
    pen.fillStyle = "#142033";
    pen.fillRect(0, 0, board.width, board.height);
    pen.fillStyle = "#f4f7fb";
    pen.font = "28px sans-serif";
    pen.fillText(latest.script[0].slice(0, 42), 32, 160);
    pen.font = "16px sans-serif";
    pen.fillText("Drawn here. Not a person's face. $0.", 32, 210);
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
