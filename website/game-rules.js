(function (root) {
  const KINDS = ["empty", "wall", "coin", "goal", "hazard", "road", "parcel", "building", "room", "foundation"];
  const SOLID = { wall: true, building: true, room: true, foundation: true };

  function blank(cols, rows) {
    const cells = [];
    const heights = [];
    for (let y = 0; y < rows; y += 1) {
      const row = [];
      const ground = [];
      for (let x = 0; x < cols; x += 1) {
        row.push("empty");
        ground.push(0);
      }
      cells.push(row);
      heights.push(ground);
    }
    return { title: "Untitled", cols: cols, rows: rows, player: { x: 1, y: 1 }, cells: cells, heights: heights };
  }

  function inBounds(level, x, y) {
    return x >= 0 && y >= 0 && x < level.cols && y < level.rows;
  }

  function paint(level, x, y, tool) {
    const next = JSON.parse(JSON.stringify(level));
    if (!inBounds(next, x, y) || KINDS.indexOf(tool) === -1 && tool !== "player" && tool !== "erase" && tool !== "raise" && tool !== "lower") return next;
    if (!next.heights) next.heights = blank(next.cols, next.rows).heights;
    if (tool === "raise" || tool === "lower") {
      const current = next.heights[y][x] || 0;
      next.heights[y][x] = Math.max(0, Math.min(3, current + (tool === "raise" ? 1 : -1)));
      return next;
    }
    if (tool === "player") {
      next.player = { x: x, y: y };
      next.cells[y][x] = "empty";
      return next;
    }
    next.cells[y][x] = tool === "erase" ? "empty" : tool;
    if (next.player.x === x && next.player.y === y) next.player = { x: 1, y: 1 };
    return next;
  }

  function count(level, kind) {
    let total = 0;
    level.cells.forEach(function (row) {
      row.forEach(function (cell) { if (cell === kind) total += 1; });
    });
    return total;
  }

  function step(level, dir) {
    const next = JSON.parse(JSON.stringify(level));
    const move = { left: [-1, 0], right: [1, 0], up: [0, -1], down: [0, 1] }[dir] || [0, 0];
    const nx = next.player.x + move[0];
    const ny = next.player.y + move[1];
    if (inBounds(next, nx, ny) && !SOLID[next.cells[ny][nx]]) {
      next.player = { x: nx, y: ny };
      if (next.cells[ny][nx] === "coin") next.cells[ny][nx] = "empty";
      if (next.cells[ny][nx] === "hazard") return { level: next, status: "lost" };
    }
    for (let y = 0; y < next.rows; y += 1) {
      for (let x = next.cols - 1; x >= 0; x -= 1) {
        if (next.cells[y][x] !== "hazard") continue;
        const dest = x + 1;
        if (inBounds(next, dest, y) && next.cells[y][dest] === "empty") {
          next.cells[y][x] = "empty";
          next.cells[y][dest] = "hazard";
        }
      }
    }
    if (next.cells[next.player.y][next.player.x] === "hazard") return { level: next, status: "lost" };
    const coins = count(next, "coin");
    const goals = count(next, "goal");
    const onGoal = goals > 0 && next.cells[next.player.y][next.player.x] === "goal";
    if (coins === 0 && (goals === 0 || onGoal) && (count(level, "coin") > 0 || goals > 0)) return { level: next, status: "won" };
    return { level: next, status: "playing" };
  }

  function preset(name) {
    if (name === "town") {
      const town = blank(16, 10);
      town.title = "Town";
      town.player = { x: 2, y: 5 };
      for (let x = 2; x <= 13; x += 1) town.cells[5][x] = "road";
      town.cells[3][4] = "building";
      town.cells[3][5] = "building";
      town.cells[6][10] = "building";
      town.cells[7][8] = "room";
      town.cells[7][9] = "room";
      town.cells[2][11] = "foundation";
      town.heights[1][3] = 1;
      town.heights[2][2] = 1;
      town.heights[2][3] = 2;
      return town;
    }
    const level = blank(16, 10);
    for (let x = 0; x < level.cols; x += 1) {
      level.cells[0][x] = "wall";
      level.cells[level.rows - 1][x] = "wall";
    }
    for (let y = 0; y < level.rows; y += 1) {
      level.cells[y][0] = "wall";
      level.cells[y][level.cols - 1] = "wall";
    }
    level.player = { x: 2, y: 2 };
    if (name === "collect") {
      level.title = "Collect";
      [[4, 2], [7, 2], [10, 4], [12, 7]].forEach(function (spot) { level.cells[spot[1]][spot[0]] = "coin"; });
      level.cells[8][13] = "goal";
    } else if (name === "dodge") {
      level.title = "Dodge";
      level.cells[4][6] = "hazard";
      level.cells[4][9] = "hazard";
      level.cells[8][13] = "goal";
    } else {
      level.title = "Room";
      level.cells[5][8] = "goal";
    }
    return level;
  }

  function project(point, camera) {
    const dx = point.x - camera.x;
    const dy = point.y - camera.y;
    const cos = Math.cos(camera.yaw);
    const sin = Math.sin(camera.yaw);
    const right = dx * cos - dy * sin;
    const forward = dx * sin + dy * cos;
    if (forward < 0.15) return null;
    return { x: right / forward, y: (point.z - camera.z) / forward, depth: forward };
  }

  function shade(hex, amount) {
    const value = Math.max(0, Math.min(1, amount));
    const red = parseInt(hex.slice(1, 3), 16);
    const green = parseInt(hex.slice(3, 5), 16);
    const blue = parseInt(hex.slice(5, 7), 16);
    const mix = function (channel) { return Math.round(channel * value).toString(16).padStart(2, "0"); };
    return "#" + mix(red) + mix(green) + mix(blue);
  }

  function defaults() {
    return {
      sky: "#070b14", floor: "#1b2436", wall: "#33415c", coin: "#f5c542", goal: "#3dd68c",
      hazard: "#ef6461", player: "#7eb6ff", empty: "#101625", road: "#3d4f73", parcel: "#8d6b43",
      building: "#c4b7a6", room: "#8d99ae", foundation: "#6b705c", land: "#3f6b4a",
      wallHeight: 1.2, light: 1, win: "You won."
    };
  }

  function styleOf(level) {
    const base = defaults();
    const incoming = (level && level.style) || {};
    const hex = /^#[0-9a-fA-F]{6}$/;
    Object.keys(base).forEach(function (key) {
      if (typeof base[key] === "string" && key !== "win" && hex.test(incoming[key])) base[key] = incoming[key];
    });
    if (typeof incoming.win === "string" && incoming.win.trim()) base.win = incoming.win.trim().slice(0, 80);
    const height = Number(incoming.wallHeight);
    const light = Number(incoming.light);
    if (height >= 0.4 && height <= 2.4) base.wallHeight = height;
    if (light >= 0.4 && light <= 1) base.light = light;
    return base;
  }

  function resize(level, cols, rows) {
    const width = Math.max(8, Math.min(24, cols | 0));
    const depth = Math.max(6, Math.min(16, rows | 0));
    const next = blank(width, depth);
    next.title = level.title;
    next.style = styleOf(level);
    for (let y = 0; y < Math.min(depth, level.rows); y += 1) {
      for (let x = 0; x < Math.min(width, level.cols); x += 1) {
        next.cells[y][x] = level.cells[y][x];
        if (level.heights && level.heights[y]) next.heights[y][x] = level.heights[y][x] || 0;
      }
    }
    if (inBounds(next, level.player.x, level.player.y)) next.player = { x: level.player.x, y: level.player.y };
    return next;
  }

  root.DreamGame = { blank: blank, paint: paint, step: step, preset: preset, count: count, project: project, shade: shade, styleOf: styleOf, resize: resize };
})(typeof globalThis !== "undefined" ? globalThis : this);
