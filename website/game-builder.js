(function () {
  const canvas = document.getElementById("board");
  const context = canvas.getContext("2d");
  const status = document.getElementById("status");
  let tool = "wall";
  let mode = "edit";
  let level = DreamGame.preset("collect");
  document.getElementById("title").value = level.title;

  function draw() {
    const size = canvas.width / level.cols;
    context.clearRect(0, 0, canvas.width, canvas.height);
    const colors = { empty: "#101625", wall: "#33415c", coin: "#f5c542", goal: "#3dd68c", hazard: "#ef6461" };
    for (let y = 0; y < level.rows; y += 1) {
      for (let x = 0; x < level.cols; x += 1) {
        context.fillStyle = colors[level.cells[y][x]] || colors.empty;
        context.fillRect(x * size, y * size, size - 1, size - 1);
      }
    }
    context.fillStyle = "#7eb6ff";
    context.beginPath();
    context.arc((level.player.x + 0.5) * size, (level.player.y + 0.5) * size, size * 0.3, 0, Math.PI * 2);
    context.fill();
  }

  function setStatus(text) { status.textContent = text; }

  canvas.addEventListener("click", function (event) {
    if (mode !== "edit") return;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / rect.width * level.cols);
    const y = Math.floor((event.clientY - rect.top) / rect.height * level.rows);
    level = DreamGame.paint(level, x, y, tool);
    level.title = document.getElementById("title").value.trim() || "Untitled";
    draw();
  });

  document.querySelectorAll("[data-tool]").forEach(function (button) {
    button.addEventListener("click", function () { tool = button.dataset.tool; setStatus("Tool: " + tool); });
  });
  document.querySelectorAll("[data-preset]").forEach(function (button) {
    button.addEventListener("click", function () {
      mode = "edit";
      window.clearInterval(timer);
      level = DreamGame.preset(button.dataset.preset);
      document.getElementById("title").value = level.title;
      draw();
      setStatus("Editing " + level.title + ".");
    });
  });

  document.getElementById("play").addEventListener("click", function () {
    mode = "play";
    setStatus("Playing. Arrow keys move. Collect the coins, then step on the goal. A hazard ends the game.");
  });
  document.getElementById("stop").addEventListener("click", function () {
    mode = "edit";
    setStatus("Editing.");
  });
  document.getElementById("save").addEventListener("click", function () {
    level.title = document.getElementById("title").value.trim() || "Untitled";
    const file = new Blob([JSON.stringify(level)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "dreamco-game.json";
    link.click();
    URL.revokeObjectURL(link.href);
  });
  document.getElementById("load").addEventListener("change", function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    file.text().then(function (text) {
      const loaded = JSON.parse(text);
      if (!loaded.cells || !loaded.player) throw new Error("bad");
      level = loaded;
      document.getElementById("title").value = level.title || "Untitled";
      mode = "edit";
      draw();
      setStatus("Loaded " + level.title + ".");
    }).catch(function () { setStatus("That file is not a DreamCo game."); });
  });

  window.addEventListener("keydown", function (event) {
    const dirs = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down", a: "left", d: "right", w: "up", s: "down" };
    const dir = dirs[event.key];
    if (mode !== "play" || !dir) return;
    event.preventDefault();
    const result = DreamGame.step(level, dir);
    level = result.level;
    draw();
    if (result.status === "won") {
      mode = "edit";
      setStatus("You won " + (level.title || "the game") + ".");
    } else if (result.status === "lost") {
      mode = "edit";
      setStatus("A hazard hit the player. Press a preset to try again.");
    }
  });

  draw();
  setStatus("Editing Collect. Click the grid to paint.");
})();
