param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$graphRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$provenanceRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$obsoleteNames = @('cache', 'converted', '.graphify_labels.json', '.graphify_python', '.graphify_root', 'benchmark.json', 'BENCHMARK.txt', 'COMPLETION_REPORT.md', 'completion_verification.json', 'cost.json', 'manifest.json', 'publication_manifest.json', 'refresh_audit.json', 'semantic_cache_acceptance.json', 'source_hashes.json')
$rows = foreach ($name in $obsoleteNames) {
    $target = [IO.Path]::GetFullPath((Join-Path $graphRoot $name))
    if (-not $target.StartsWith($graphRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Target escapes canonical graph directory: $target" }
    if (-not (Test-Path -LiteralPath $target)) { continue }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Unexpected reparse target: $target" }
    $files = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $target -File -Recurse -Force) } else { @($item) }
    if ($item.PSIsContainer) {
        $reparse = @(Get-ChildItem -LiteralPath $target -Directory -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
        if ($reparse.Count) { throw "Unexpected nested reparse path: $target" }
    }
    foreach ($file in $files) {
        [PSCustomObject]@{ path = 'tools/knowledge_graph/' + $file.FullName.Substring($graphRoot.Length + 1).Replace('\', '/'); bytes = $file.Length; disposition = 'Removed superseded graph snapshot metadata/cache; current authoritative artifacts and provenance remain in canonical graph home.' }
    }
}
$rows | Export-Csv -LiteralPath (Join-Path $provenanceRoot 'cleanup_dispositions.csv') -NoTypeInformation -Encoding utf8
if ($Apply) {
    if (-not (Test-Path -LiteralPath (Join-Path $provenanceRoot 'completion_verification.json'))) { throw 'Current graph integrity verification is required before obsolete cleanup.' }
    foreach ($name in $obsoleteNames) {
        $target = [IO.Path]::GetFullPath((Join-Path $graphRoot $name))
        if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
    }
}
[PSCustomObject]@{ apply = [bool]$Apply; obsolete_files = @($rows).Count; graph_root = $graphRoot } | ConvertTo-Json -Compress
