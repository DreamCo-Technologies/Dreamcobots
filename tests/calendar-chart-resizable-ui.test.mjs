import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

function read(path) { return fs.readFileSync(path, "utf8"); }

test("calendar wrapper uses react-day-picker v9 component and class contracts", () => {
  const source = read("client/src/components/ui/calendar.tsx");
  assert.match(source, /month_caption/);
  assert.match(source, /button_previous/);
  assert.match(source, /Chevron:/);
});

test("chart wrapper exposes typed Recharts v3 tooltip and legend payloads", () => {
  const source = read("client/src/components/ui/chart.tsx");
  assert.match(source, /type TooltipPayloadItem/);
  assert.match(source, /type LegendPayloadItem/);
  assert.match(source, /ResponsiveContainer/);
});

test("resizable wrapper maps legacy direction to the v4 orientation API", () => {
  const source = read("client/src/components/ui/resizable.tsx");
  assert.match(source, /direction\?: "horizontal" \| "vertical"/);
  assert.match(source, /orientation\?: "horizontal" \| "vertical"/);
  assert.match(source, /resolvedOrientation/);
});
