(function (root) {
  const KINDS = ["empty", "wall", "coin", "goal", "hazard"];

  function blank(cols, rows) {
    const cells = [];
    for (let y = 0; y < rows; y += 1) {
      const row = [];
      for (let x = 0; x < cols; x += 1) row.push("empty");
      cells.push(row);
    }
    return { title: "Untitled", cols: cols, rows: rows, player: { x: 1, y: 1 }, cells: cells };
  }

  function inBounds(level, x, y) {
    return x >= 0 && y >= 0 && x < level.cols && y < level.rows;
  }

  function paint(level, x, y, tool) {
    const next = JSON.parse(JSON.stringify(level));
    if (!inBounds(next, x, y) || KINDS.indexOf(tool) === -1 && tool !== "player" && tool !== "erase") return next;
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
    if (inBounds(next, nx, ny) && next.cells[ny][nx] !== "wall") {
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

  root.DreamGame = { blank: blank, paint: paint, step: step, preset: preset, count: count };
})(typeof globalThis !== "undefined" ? globalThis : this);
