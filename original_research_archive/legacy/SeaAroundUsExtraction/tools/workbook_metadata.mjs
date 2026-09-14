function formatBase(value) {
  return Number.isInteger(value) ? String(value) : String(Number(value.toFixed(6)));
}

export function transferEfficiencyNumberFormat() {
  return "0.00";
}

export function transferEfficiencySpprNote(transferEfficiency) {
  const te = Number(transferEfficiency);
  return `With TE=${te.toFixed(2)}, SPPR = ${formatBase(1 / te)}^(TL-1)`;
}

export function transferEfficiencyMethodNote(transferEfficiency) {
  return `TE=${Number(transferEfficiency).toFixed(2)} trophic-chain calculation`;
}
