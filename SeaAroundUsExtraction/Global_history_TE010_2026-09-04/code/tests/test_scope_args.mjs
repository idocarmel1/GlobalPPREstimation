import assert from "node:assert/strict";
import test from "node:test";

import { resolveReleaseArgs } from "../tools/scope_args.mjs";


test("legacy global flag keeps the original release paths", () => {
  assert.deepEqual(resolveReleaseArgs(["--global"]), {
    scopeLabel: "global",
    outputDirectory: "global_output",
    isGlobal: true,
    previewDirectoryName: "global_workbook_previews",
  });
});

test("named global variant routes to a separate output and preview directory", () => {
  assert.deepEqual(
    resolveReleaseArgs([
      "--scope-label=global_te005",
      "--output-directory=global_output_te005",
    ]),
    {
      scopeLabel: "global_te005",
      outputDirectory: "global_output_te005",
      isGlobal: true,
      previewDirectoryName: "global_te005_workbook_previews",
    },
  );
});
