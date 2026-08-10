import assert from "node:assert/strict";
import test from "node:test";

import { registerIntelligentRoutingRoutes } from "../server/intelligent-routing-routes";

test("Buddy registers task compiler and model protocol compiler APIs", () => {
  const paths: string[] = [];
  const fakeApp = {
    post(path: string, _handler: unknown) {
      paths.push(path);
      return this;
    },
  };
  registerIntelligentRoutingRoutes(fakeApp as never);
  assert.deepEqual(paths.sort(), [
    "/api/buddy/model/compile-protocol",
    "/api/buddy/task/compile",
  ]);
});
