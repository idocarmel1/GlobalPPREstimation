import assert from "node:assert/strict";
import test from "node:test";

import {
  transferEfficiencyNumberFormat,
  transferEfficiencySpprNote,
  transferEfficiencyMethodNote,
} from "../tools/workbook_metadata.mjs";

test("TE=0.05 workbook metadata is displayed without rounding to 0.1", () => {
  assert.equal(transferEfficiencyNumberFormat(), "0.00");
  assert.equal(transferEfficiencySpprNote(0.05), "With TE=0.05, SPPR = 20^(TL-1)");
  assert.equal(transferEfficiencyMethodNote(0.05), "TE=0.05 trophic-chain calculation");
});

test("TE=0.10 metadata remains mathematically accurate", () => {
  assert.equal(transferEfficiencySpprNote(0.1), "With TE=0.10, SPPR = 10^(TL-1)");
  assert.equal(transferEfficiencyMethodNote(0.1), "TE=0.10 trophic-chain calculation");
});
