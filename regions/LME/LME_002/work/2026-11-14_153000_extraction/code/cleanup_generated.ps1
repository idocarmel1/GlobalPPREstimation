$ErrorActionPreference = 'Stop'
$workspacePath = (Get-Location).Path
$runPath = (Resolve-Path -LiteralPath 'regions/LME/LME_002/work/2026-11-14_153000_extraction').Path
$plan = Get-Content -LiteralPath (Join-Path $runPath 'qa/cleanup_plan.json') -Raw | ConvertFrom-Json
$checked = @()
foreach ($relativeTarget in $plan.targets) {
    $absoluteTarget = [IO.Path]::GetFullPath((Join-Path $workspacePath $relativeTarget))
    if (-not $absoluteTarget.StartsWith($runPath + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw "Cleanup target escapes task run: $absoluteTarget" }
    if (Test-Path -LiteralPath $absoluteTarget) {
        $item = Get-Item -LiteralPath $absoluteTarget -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse target: $absoluteTarget" }
        if ($item.PSIsContainer) {
            $links = @(Get-ChildItem -LiteralPath $absoluteTarget -Force -Recurse | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
            if ($links.Count -gt 0) { throw "Reparse descendant in $absoluteTarget" }
        }
        $checked += $absoluteTarget
    }
}
foreach ($absoluteTarget in $checked) { Remove-Item -LiteralPath $absoluteTarget -Recurse -Force }
foreach ($absoluteTarget in $checked) { if (Test-Path -LiteralPath $absoluteTarget) { throw "Cleanup incomplete: $absoluteTarget" } }
@{status='removed_verified_temporary_targets'; target_count=$checked.Count; source_originals_retained=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runPath 'qa/cleanup_receipt.json') -Encoding utf8
Write-Output "Removed $($checked.Count) verified temporary targets; original sources retained."
