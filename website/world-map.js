(function () {
  const canvas = document.getElementById("board");
  const context = canvas.getContext("2d");
  const view = document.getElementById("view3d");
  const gl = view.getContext("2d");
  const status = document.getElementById("status");
  let tool = "road";
  let mode = "edit";
  let level = DreamGame.preset("town");

  function draw() {
    const style = DreamGame.styleOf(level);
    const size = canvas.width / level.cols;
    for (let y = 0; y < level.rows; y += 1) {
      for (let x = 0; x < level.cols; x += 1) {
        const cell = level.cells[y][x];
        context.fillStyle = cell === "empty" ? DreamGame.shade(style.land, 0.55 + (level.heights[y][x] || 0) * 0.15) : (style[cell] || style.empty);
        context.fillRect(x * size, y * size, size - 1, size - 1);
      }
    }
    context.fillStyle = style.player;
    context.fillRect(level.player.x * size + 8, level.player.y * size + 8, size - 16, size - 16);
    draw3d(style);
  }

  function draw3d(style) {
    const cam = { x: level.player.x + 0.5, y: level.player.y + 7, z: 3.4, yaw: Math.PI };
    const faces = [];
    function addFace(points, color, depth) {
      const flat = points.map(function (point) { return DreamGame.project(point, cam); });
      if (flat.some(function (point) { return !point; })) return;
      faces.push({ flat: flat, color: color, depth: depth });
    }
    function block(x, y, size, z0, z1, color) {
      const depth = Math.hypot(x - cam.x, y - cam.y);
      addFace([{ x: x, y: y, z: z1 }, { x: x + size, y: y, z: z1 }, { x: x + size, y: y + size, z: z1 }, { x: x, y: y + size, z: z1 }], DreamGame.shade(color, style.light), depth);
      addFace([{ x: x, y: y + size, z: z0 }, { x: x + size, y: y + size, z: z0 }, { x: x + size, y: y + size, z: z1 }, { x: x, y: y + size, z: z1 }], DreamGame.shade(color, 0.7), depth + 0.2);
    }
    for (let y = 0; y < level.rows; y += 1) {
      for (let x = 0; x < level.cols; x += 1) {
        const ground = 0.15 + (level.heights[y][x] || 0) * 0.45;
        const cell = level.cells[y][x];
        block(x, y, 1, 0, ground, style.land);
        if (cell === "road") block(x, y, 1, ground, ground + 0.04, style.road);
        if (cell === "parcel") block(x, y, 1, ground, ground + 0.06, style.parcel);
        if (cell === "foundation") block(x, y, 1, ground, ground + 0.28, style.foundation);
        if (cell === "room") block(x, y, 1, ground, ground + 0.7, style.room);
        if (cell === "building") block(x, y, 1, ground, ground + 1.6, style.building);
      }
    }
    const feet = 0.15 + (level.heights[level.player.y][level.player.x] || 0) * 0.45;
    block(level.player.x + 0.25, level.player.y + 0.25, 0.5, feet, feet + 0.7, style.player);
    faces.sort(function (a, b) { return b.depth - a.depth; });
    gl.fillStyle = style.sky;
    gl.fillRect(0, 0, view.width, view.height);
    faces.forEach(function (face) {
      gl.beginPath();
      face.flat.forEach(function (point, index) {
        const sx = view.width / 2 + point.x * 220;
        const sy = view.height / 2 - point.y * 220;
        if (index === 0) gl.moveTo(sx, sy);
        else gl.lineTo(sx, sy);
      });
      gl.closePath();
      gl.fillStyle = face.color;
      gl.fill();
    });
  }

  document.getElementById("locate").addEventListener("click", function () {
    const where = document.getElementById("where");
    where.replaceChildren();
    if (!document.getElementById("use-location").checked) {
      where.textContent = "Turn on location first. It stays off until you choose it.";
      return;
    }
    if (!navigator.geolocation) {
      where.textContent = "This browser has no location. The map still works.";
      return;
    }
    navigator.geolocation.getCurrentPosition(function (pos) {
      const lat = pos.coords.latitude.toFixed(5);
      const lng = pos.coords.longitude.toFixed(5);
      const frame = document.getElementById("google-map");
      frame.hidden = true;
      frame.removeAttribute("src");
      where.textContent = "You are at " + lat + ", " + lng + ". The blocks stay on your map. ";
      if (!document.getElementById("use-google").checked) return;
      const view = document.getElementById("google-view").value;
      if (view === "maps" || view === "both") {
        frame.hidden = false;
        frame.src = "https://www.google.com/maps?q=" + encodeURIComponent(lat + "," + lng) + "&z=16&output=embed";
      }
      if (view === "earth" || view === "both") {
        const link = document.createElement("a");
        link.href = "https://earth.google.com/web/@" + lat + "," + lng + ",0a,800d,35y,0h,0t,0r";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Open this spot in Google Earth";
        where.append(link);
      }
    }, function () {
      where.textContent = "Location was blocked. The map still works without it.";
    });
  });

  canvas.addEventListener("click", function (event) {
    if (mode !== "edit") return;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / rect.width * level.cols);
    const y = Math.floor((event.clientY - rect.top) / rect.height * level.rows);
    level = DreamGame.paint(level, x, y, tool);
    draw();
  });
  document.querySelectorAll("[data-tool]").forEach(function (button) {
    button.addEventListener("click", function () {
      tool = button.dataset.tool;
      status.textContent = "Tool: " + tool;
    });
  });
  document.querySelectorAll("[data-preset]").forEach(function (button) {
    button.addEventListener("click", function () {
      mode = "edit";
      level = DreamGame.preset(button.dataset.preset);
      draw();
    });
  });
  document.getElementById("play").addEventListener("click", function () {
    mode = "play";
    status.textContent = "Walking. Arrow keys move. Buildings, foundations, and interior walls block the way.";
  });
  document.getElementById("save").addEventListener("click", function () {
    const file = new Blob([JSON.stringify(level)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "dreamco-world.json";
    link.click();
    URL.revokeObjectURL(link.href);
  });
  document.getElementById("load").addEventListener("change", function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    file.text().then(function (text) {
      const loaded = JSON.parse(text);
      if (!loaded.cells || !loaded.heights || !loaded.player) throw new Error("bad");
      level = loaded;
      mode = "edit";
      draw();
      status.textContent = "Loaded " + (level.title || "map") + ".";
    }).catch(function () { status.textContent = "That file is not a DreamCo world map."; });
  });
  window.addEventListener("keydown", function (event) {
    const dirs = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" };
    const dir = dirs[event.key];
    if (mode !== "play" || !dir) return;
    event.preventDefault();
    level = DreamGame.step(level, dir).level;
    draw();
  });
  draw();
})();
