(function () {
  const canvas = document.getElementById("board");
  const context = canvas.getContext("2d");
  const view = document.getElementById("view3d");
  const gl = view.getContext("2d");
  const status = document.getElementById("status");
  let tool = "wall";
  let mode = "edit";
  let facing = "up";
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
    draw3d();
  }

  function camera() {
    const yaw = { up: Math.PI, down: 0, right: Math.PI / 2, left: -Math.PI / 2 }[facing];
    return { x: level.player.x + 0.5, y: level.player.y + 0.5, z: 0.7, yaw: yaw };
  }

  function draw3d() {
    const cam = camera();
    const faces = [];
    function addFace(points, color, depth) {
      const flat = points.map(function (point) { return DreamGame.project(point, cam); });
      if (flat.some(function (point) { return !point; })) return;
      faces.push({ flat: flat, color: color, depth: depth });
    }
    function block(x, y, size, z0, z1, color) {
      const depth = Math.hypot(x + size / 2 - cam.x, y + size / 2 - cam.y);
      addFace([{ x: x, y: y, z: z1 }, { x: x + size, y: y, z: z1 }, { x: x + size, y: y + size, z: z1 }, { x: x, y: y + size, z: z1 }], DreamGame.shade(color, 1), depth);
      addFace([{ x: x, y: y + size, z: z0 }, { x: x + size, y: y + size, z: z0 }, { x: x + size, y: y + size, z: z1 }, { x: x, y: y + size, z: z1 }], DreamGame.shade(color, 0.72), depth + 0.2);
      addFace([{ x: x + size, y: y, z: z0 }, { x: x + size, y: y + size, z: z0 }, { x: x + size, y: y + size, z: z1 }, { x: x + size, y: y, z: z1 }], DreamGame.shade(color, 0.45), depth + 0.3);
    }
    for (let y = 0; y < level.rows; y += 1) {
      for (let x = 0; x < level.cols; x += 1) {
        const cell = level.cells[y][x];
        block(x, y, 1, 0, 0.05, "#1b2436");
        if (cell === "wall") block(x, y, 1, 0, 1.2, "#33415c");
        if (cell === "coin") block(x + 0.3, y + 0.3, 0.4, 0.2, 0.7, "#f5c542");
        if (cell === "goal") block(x, y, 1, 0, 0.12, "#3dd68c");
        if (cell === "hazard") block(x, y, 1, 0, 0.35, "#ef6461");
      }
    }
    block(level.player.x + 0.25, level.player.y + 0.25, 0.5, 0, 0.8, "#7eb6ff");
    faces.sort(function (a, b) { return b.depth - a.depth; });
    gl.fillStyle = "#070b14";
    gl.fillRect(0, 0, view.width, view.height);
    faces.forEach(function (face) {
      gl.beginPath();
      face.flat.forEach(function (point, index) {
        const sx = view.width / 2 + point.x * 280;
        const sy = view.height / 2 - point.y * 280;
        if (index === 0) gl.moveTo(sx, sy);
        else gl.lineTo(sx, sy);
      });
      gl.closePath();
      gl.fillStyle = face.color;
      gl.fill();
    });
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
      facing = "up";
      level = DreamGame.preset(button.dataset.preset);
      document.getElementById("title").value = level.title;
      draw();
      setStatus("Editing " + level.title + ". The 3D view is the same room.");
    });
  });

  document.getElementById("play").addEventListener("click", function () {
    mode = "play";
    setStatus("Playing in 3D. Arrow keys move and turn the camera. Collect the coins, then step on the goal.");
  });
  document.getElementById("stop").addEventListener("click", function () {
    mode = "edit";
    setStatus("Editing. The 3D view stays in sync.");
  });
  document.getElementById("save").addEventListener("click", function () {
    level.title = document.getElementById("title").value.trim() || "Untitled";
    level.view = "3d";
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
    facing = dir;
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
  setStatus("Editing Collect. The lower view is the same room in 3D.");
})();
