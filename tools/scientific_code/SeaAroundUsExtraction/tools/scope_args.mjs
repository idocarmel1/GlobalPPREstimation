function valueFor(argv, prefix) {
  const item = argv.find((value) => value.startsWith(prefix));
  return item ? item.slice(prefix.length) : undefined;
}

export function resolveReleaseArgs(argv) {
  const legacyGlobal = argv.includes("--global");
  const scopeLabel = valueFor(argv, "--scope-label=") ?? (legacyGlobal ? "global" : "pilot");
  const outputDirectory = valueFor(argv, "--output-directory=")
    ?? (scopeLabel === "pilot" ? "output" : scopeLabel === "global" ? "global_output" : `${scopeLabel}_output`);
  for (const [label, value] of [["scope label", scopeLabel], ["output directory", outputDirectory]]) {
    if (!/^[A-Za-z0-9_-]+$/.test(value)) {
      throw new Error(`Invalid ${label}: ${value}`);
    }
  }
  return {
    scopeLabel,
    outputDirectory,
    isGlobal: scopeLabel.startsWith("global"),
    previewDirectoryName: `${scopeLabel}_workbook_previews`,
  };
}
