$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$workspace = (Resolve-Path -LiteralPath '.').Path.TrimEnd('\')
$runRelative = 'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
$run = (Resolve-Path -LiteralPath (Join-Path $workspace $runRelative)).Path
$variantRelative = 'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
$evidence = Join-Path $workspace ($variantRelative + '/extracted_tables/evidence/native_reproduction')
$verification = Join-Path $evidence 'verification'
$receiptPath = Join-Path $run 'qa/cleanup_receipt.json'
$retainedReceipt = Join-Path $verification 'cleanup_receipt.json'
function Hash-File([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Relative-Workspace([string]$Path) { [IO.Path]::GetRelativePath($workspace,$Path).Replace('\','/') }
function Write-Json([string]$Path,$Value) { [IO.File]::WriteAllText($Path,($Value | ConvertTo-Json -Depth 30)+"`n",[Text.UTF8Encoding]::new($false)) }
$receipt = Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json -AsHashtable
if ($receipt.status -ne 'failed_or_partial' -or $receipt.deleted.Count -ne 6) { throw 'Expected the six completed deletions and reporting failure receipt' }
$priorReceipt = Join-Path $run 'qa/cleanup_receipt_initial_reporting_failure.json'
$retainedPrior = Join-Path $verification 'cleanup_receipt_initial_reporting_failure.json'
Copy-Item -LiteralPath $receiptPath -Destination $priorReceipt
Copy-Item -LiteralPath $receiptPath -Destination $retainedPrior
if ((Hash-File $priorReceipt) -ne (Hash-File $retainedPrior)) { throw 'Prior receipt copy mismatch' }
$inventoryPath = Join-Path $workspace $receipt.inventory.work_path
$retainedInventory = Join-Path $workspace $receipt.inventory.retained_path
if ((Hash-File $inventoryPath) -ne $receipt.inventory.sha256 -or (Hash-File $retainedInventory) -ne $receipt.inventory.sha256) { throw 'Inventory hash mismatch' }
$inventory = Get-Content -LiteralPath $inventoryPath -Raw | ConvertFrom-Json -AsHashtable
$allowed = @('inputs/native_R_runtime','inputs/native_runtime_tools','inputs/native_R_library','inputs/native_runtime_downloads','outputs/native_variant_stage','outputs/native_variant_writer_input.json')
if ($inventory.targets.Count -ne 6) { throw 'Unexpected inventory target count' }
$fileCount = [long]0
$byteCount = [long]0
foreach ($target in $inventory.targets) {
    if ($target.run_relative_path -notin $allowed) { throw 'Unexpected inventoried target' }
    $expected = [IO.Path]::GetFullPath((Join-Path $run $target.run_relative_path))
    if (-not $expected.Equals($target.absolute_path,[StringComparison]::OrdinalIgnoreCase) -or -not $expected.StartsWith($run+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Inventory target resolution mismatch' }
    if (Test-Path -LiteralPath $expected) { throw "Target remains: $expected" }
    $fileCount += [long]$target.file_count
    $byteCount += [long]$target.total_bytes
}
$manifestPath = Join-Path $workspace $receipt.native_manifest.path
if ((Hash-File $manifestPath) -ne $receipt.native_manifest.sha256) { throw 'Retained native manifest changed' }
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json -AsHashtable
$verified = 0
foreach ($entry in @($manifest.files) + @($manifest.source_references)) {
    $path = [IO.Path]::GetFullPath((Join-Path $evidence $entry.path))
    if ((Hash-File $path) -ne $entry.sha256) { throw "Retained evidence/source mismatch: $path" }
    $verified++
}
foreach ($entry in $manifest.files | Where-Object { $_.role -eq 'native_output' }) {
    $path = Join-Path $run ('outputs/native_balance/' + $entry.path)
    if ((Hash-File $path) -ne $entry.sha256) { throw "Work native output mismatch: $path" }
    $verified++
}
foreach ($entry in $receipt.retained_imports) {
    if ((Hash-File (Join-Path $workspace $entry.path)) -ne $entry.sha256) { throw 'Retained import mismatch' }
    $verified++
}
foreach ($keep in @('outputs/native_balance','outputs/diagnostics','code','qa')) {
    if (-not (Test-Path -LiteralPath (Join-Path $run $keep) -PathType Container)) { throw "Required run directory missing: $keep" }
}
if ((Hash-File (Join-Path $workspace $receipt.cleanup_script.retained_path)) -ne $receipt.cleanup_script.sha256) { throw 'Original executed cleanup script changed' }
$retainedScript = Join-Path $verification 'verify_cleanup_completion.ps1'
Copy-Item -LiteralPath $PSCommandPath -Destination $retainedScript
if ((Hash-File $PSCommandPath) -ne (Hash-File $retainedScript)) { throw 'Recovery verification script copy mismatch' }
$receipt.reporting_recovery = [ordered]@{reason=$receipt.error; prior_receipt_path=(Relative-Workspace $retainedPrior); prior_receipt_sha256=(Hash-File $retainedPrior); description='All six deletions and protected-file checks had completed; only ordered-dictionary aggregation for receipt totals failed. This script performs no deletion and verifies absence, inventory and protected files again before finalizing totals.'; verification_script_path=(Relative-Workspace $retainedScript); verification_script_sha256=(Hash-File $retainedScript)}
[void]$receipt.Remove('error')
$receipt.status='completed'
$receipt.post_delete_verified=$true
$receipt.completed_at_utc=[DateTime]::UtcNow.ToString('o')
$receipt.protected_file_hashes_verified=$verified
$receipt.total_files_removed=$fileCount
$receipt.total_bytes_removed=$byteCount
Write-Json $receiptPath $receipt
Copy-Item -LiteralPath $receiptPath -Destination $retainedReceipt -Force
if ((Hash-File $receiptPath) -ne (Hash-File $retainedReceipt)) { throw 'Final receipt copy mismatch' }
[ordered]@{status=$receipt.status; targets_removed=$receipt.deleted.Count; files_removed=$fileCount; bytes_removed=$byteCount; receipt=(Relative-Workspace $retainedReceipt); receipt_sha256=(Hash-File $retainedReceipt); protected_files_verified=$verified} | ConvertTo-Json
