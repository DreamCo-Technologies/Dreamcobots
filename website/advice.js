(function () {
  function deviceClass(memory) {
    if (memory <= 4) return "phone";
    if (memory <= 8) return "small-laptop";
    if (memory <= 16) return "everyday-laptop";
    return "large-computer";
  }
  function lines(topic, memory) {
    const rules = {
      phone: "Write and review here. Do not load a weight file or a clone model on this device.",
      "small-laptop": "Load one model. Use 16-bit only for about 1B parameters or fewer. Use 4-bit for a 7B model, and leave 2GB free.",
      "everyday-laptop": "A 7B model can fit in 4-bit or 8-bit. Still unload it before you load a second one.",
      "large-computer": "You can study a larger open model. Keep one heavy model loaded, and do not upload another person's voice or face."
    };
    const topics = {
      weights: "Read the license on the model card before you download. A catalog row is not a benchmark score.",
      clone: "Consent has to match the exact file. A child is refused. Kokoro speaks, but it does not clone.",
      plans: "A lesson marked ready is not a trained model. A passing check does not give permission to act.",
      content: "The script costs nothing here. Playing it uses this browser's voice, not a copied person."
    };
    return [rules[deviceClass(memory)] || rules["small-laptop"], topics[topic] || topics.weights];
  }
  function remember(memory, cores) {
    const list = JSON.parse(localStorage.getItem("buddy-devices") || "[]");
    list.push({ memory: memory, cores: cores, at: new Date().toISOString() });
    localStorage.setItem("buddy-devices", JSON.stringify(list.slice(-20)));
    return list.length;
  }
  function show(topic) {
    const memory = navigator.deviceMemory || 8;
    const cores = navigator.hardwareConcurrency || 0;
    let saved = 0;
    try { saved = remember(memory, cores); } catch (error) { saved = 0; }
    const spot = document.getElementById("advice");
    if (!spot) return;
    spot.textContent = lines(topic, memory).join(" ") + " This browser has " + saved + " local device note" + (saved === 1 ? "" : "s") + ". They are not uploaded, and they are not one owner's laptop.";
  }
  window.BuddyAdvice = { show: show, lines: lines };
})();
