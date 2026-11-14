$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$workspace = (Resolve-Path -LiteralPath '.').Path.TrimEnd('\')
$runRelative = 'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
$run = (Resolve-Path -LiteralPath (Join-Path $workspace $runRelative)).Path.TrimEnd('\')
$variantRelative = 'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
$variant = (Resolve-Path -LiteralPath (Join-Path $workspace $variantRelative)).Path
$evidence = Join-Path $variant 'extracted_tables/evidence/native_reproduction'
$verification = Join-Path $evidence 'verification'
$manifestPath = Join-Path $evidence 'native_manifest.json'
$receiptPath = Join-Path $run 'qa/cleanup_receipt.json'
$retainedReceipt = Join-Path $verification 'cleanup_receipt.json'
$inventoryPath = Join-Path $run 'qa/cleanup_inventory.json'
$retainedInventory = Join-Path $verification 'cleanup_inventory.json'
$allowedTargets = @('inputs/native_R_runtime', 'inputs/native_runtime_tools', 'inputs/native_R_library', 'inputs/native_runtime_downloads', 'outputs/native_variant_stage', 'outputs/native_variant_writer_input.json')

function Hash-File([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Relative-Workspace([string]$Path) { [IO.Path]::GetRelativePath($workspace, $Path).Replace('\','/') }
function Write-Json([string]$Path, $Value) { [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 30) + "`n", [Text.UTF8Encoding]::new($false)) }
function Assert-InRun([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($run + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Target outside exact run: $full" }
    if (-not $full.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Target outside workspace: $full" }
    return $full
}
function Assert-AncestorsNoReparse([string]$Path) {
    $cursor = $Path
    while ($cursor.Length -ge $workspace.Length) {
        $item = Get-Item -LiteralPath $cursor -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point rejected: $cursor" }
        if ($cursor.Equals($workspace, [StringComparison]::OrdinalIgnoreCase)) { return }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
    }
    throw "Ancestor walk escaped workspace: $Path"
}
function Get-SafeTree([string]$Path) {
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    [void](Assert-InRun $resolved)
    Assert-AncestorsNoReparse $resolved
    $queue = [Collections.Generic.Stack[string]]::new()
    $queue.Push($resolved)
    $items = [Collections.Generic.List[object]]::new()
    while ($queue.Count -gt 0) {
        $item = Get-Item -LiteralPath $queue.Pop() -Force
        [void](Assert-InRun $item.FullName)
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point rejected: $($item.FullName)" }
        $items.Add($item)
        if ($item.PSIsContainer) {
            foreach ($child in Get-ChildItem -LiteralPath $item.FullName -Force) {
                if (($child.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse point rejected: $($child.FullName)" }
                $queue.Push($child.FullName)
            }
        }
    }
    return $items.ToArray()
}

if (-not $run.Equals((Join-Path $workspace $runRelative).Replace('/','\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected resolved run path' }
$manifestHash = Hash-File $manifestPath
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$checkedEvidence = [Collections.Generic.List[object]]::new()
foreach ($entry in @($manifest.files) + @($manifest.source_references)) {
    $path = [IO.Path]::GetFullPath((Join-Path $evidence $entry.path))
    if ((Hash-File $path) -ne $entry.sha256) { throw "Retained evidence/source hash mismatch: $path" }
    $checkedEvidence.Add([ordered]@{path=(Relative-Workspace $path); sha256=$entry.sha256})
}
if (@($manifest.files | Where-Object role -eq 'native_output').Count -ne 25) { throw 'Expected 25 retained native outputs' }
foreach ($entry in $manifest.files | Where-Object role -eq 'native_output') {
    $original = Join-Path $run ('outputs/native_balance/' + $entry.path)
    if ((Hash-File $original) -ne $entry.sha256) { throw "Work native output differs from retained evidence: $original" }
    $checkedEvidence.Add([ordered]@{path=(Relative-Workspace $original); sha256=$entry.sha256})
}
$reviewPath = Join-Path $verification 'independent_native_variant_review.json'
$review = Get-Content -LiteralPath $reviewPath -Raw | ConvertFrom-Json
if ($review.result -ne 'pass_no_material_mismatches' -or @($review.failures).Count -ne 0 -or $review.checks.variant_roundtrip -ne 2) { throw 'Independent canonical/import/roundtrip checks not complete' }
if ((Hash-File (Join-Path $variant 'model.json')) -ne $review.variant_sha256) { throw 'Canonical variant changed since independent review' }
$retainedImports = [Collections.Generic.List[object]]::new()
foreach ($name in @('Basic_input.csv','Diet_composition.csv','Landings.csv','Discards.csv','Detritus_fate.csv','Biomass_accumulation.csv','TL.xlsx','Metadata.xlsx')) {
    $path = Join-Path $variant ('extracted_tables/' + $name)
    $staged = Join-Path $run ('outputs/native_variant_stage/' + $name)
    $hash = Hash-File $path
    if ((Hash-File $staged) -ne $hash) { throw "Retained import differs from staging: $name" }
    $retainedImports.Add([ordered]@{path=(Relative-Workspace $path); sha256=$hash})
}

$inventory = [Collections.Generic.List[object]]::new()
foreach ($relative in $allowedTargets) {
    $target = Assert-InRun (Join-Path $run $relative)
    if (-not (Test-Path -LiteralPath $target)) { throw "Expected task target missing before cleanup: $target" }
    $items = @(Get-SafeTree $target)
    $files = @($items | Where-Object { -not $_.PSIsContainer } | Sort-Object FullName)
    $fileRecords = @($files | ForEach-Object { [ordered]@{path=([IO.Path]::GetRelativePath($target, $_.FullName).Replace('\','/')); bytes=$_.Length; sha256=(Hash-File $_.FullName)} })
    $inventory.Add([ordered]@{run_relative_path=$relative; absolute_path=$target; kind=$(if ((Get-Item -LiteralPath $target).PSIsContainer) {'directory'} else {'file'}); file_count=$files.Count; directory_count=@($items | Where-Object PSIsContainer).Count; total_bytes=($files | Measure-Object -Property Length -Sum).Sum; files=$fileRecords})
    Write-Output "Inventoried $relative ($($files.Count) files)"
}
$inventoryDocument = [ordered]@{schema_version=1; run_id=(Split-Path $run -Leaf); prepared_at_utc=[DateTime]::UtcNow.ToString('o'); targets=$inventory.ToArray()}
Write-Json $inventoryPath $inventoryDocument
Copy-Item -LiteralPath $inventoryPath -Destination $retainedInventory -Force
$inventoryHash = Hash-File $inventoryPath
if ((Hash-File $retainedInventory) -ne $inventoryHash) { throw 'Retained cleanup inventory copy mismatch' }
$retainedScript = Join-Path $verification 'cleanup_native_temporary.ps1'
Copy-Item -LiteralPath $PSCommandPath -Destination $retainedScript -Force
if ((Hash-File $retainedScript) -ne (Hash-File $PSCommandPath)) { throw 'Retained cleanup script copy mismatch' }

$deletions = [Collections.Generic.List[object]]::new()
$receipt = [ordered]@{schema_version=1; run_id=(Split-Path $run -Leaf); authorization='Coordinator explicitly authorized only six task-created temporary targets after retained-evidence verification.'; started_at_utc=[DateTime]::UtcNow.ToString('o'); status='prepared'; native_manifest=[ordered]@{path=(Relative-Workspace $manifestPath); sha256=$manifestHash; retained_files_verified=$manifest.files.Count; external_references_verified=$manifest.source_references.Count}; independent_review=[ordered]@{path=(Relative-Workspace $reviewPath); result=$review.result; variant_sha256=$review.variant_sha256; roundtrip_checks=$review.checks.variant_roundtrip}; inventory=[ordered]@{work_path=(Relative-Workspace $inventoryPath); retained_path=(Relative-Workspace $retainedInventory); sha256=$inventoryHash}; retained_imports=$retainedImports.ToArray(); cleanup_script=[ordered]@{retained_path=(Relative-Workspace $retainedScript); sha256=(Hash-File $retainedScript)}; target_count=$allowedTargets.Count; deleted=@(); exclusions=@('outputs/native_balance','outputs/diagnostics','code','all other QA','all original model/source inputs','project registry and map'); post_delete_verified=$false}
Write-Json $receiptPath $receipt
Copy-Item -LiteralPath $receiptPath -Destination $retainedReceipt -Force
try {
    foreach ($targetRecord in $inventory) {
        $target = Assert-InRun $targetRecord.absolute_path
        $current = @(Get-SafeTree $target)
        if (@($current | Where-Object { -not $_.PSIsContainer }).Count -ne $targetRecord.file_count) { throw "Target changed after inventory: $target" }
        foreach ($fileRecord in $targetRecord.files) {
            $filePath = $(if ($targetRecord.kind -eq 'file') {$target} else {Join-Path $target $fileRecord.path})
            if ((Hash-File $filePath) -ne $fileRecord.sha256) { throw "Target file changed after inventory: $filePath" }
        }
        if ($targetRecord.kind -eq 'directory') { Remove-Item -LiteralPath $target -Recurse -Force }
        else { Remove-Item -LiteralPath $target -Force }
        if (Test-Path -LiteralPath $target) { throw "Target remained after cleanup: $target" }
        $deletions.Add([ordered]@{path=$targetRecord.run_relative_path; absolute_path=$target; file_count=$targetRecord.file_count; total_bytes=$targetRecord.total_bytes; absent_after=$true; deleted_at_utc=[DateTime]::UtcNow.ToString('o')})
        $receipt.deleted=$deletions.ToArray()
        $receipt.status='in_progress'
        Write-Json $receiptPath $receipt
        Copy-Item -LiteralPath $receiptPath -Destination $retainedReceipt -Force
        Write-Output "Removed $($targetRecord.run_relative_path)"
    }
    foreach ($entry in $checkedEvidence) { if ((Hash-File (Join-Path $workspace $entry.path)) -ne $entry.sha256) { throw "Protected evidence/source changed: $($entry.path)" } }
    foreach ($entry in $retainedImports) { if ((Hash-File (Join-Path $workspace $entry.path)) -ne $entry.sha256) { throw "Retained import changed: $($entry.path)" } }
    if ((Hash-File $manifestPath) -ne $manifestHash) { throw 'Native manifest changed during cleanup' }
    foreach ($keep in @('outputs/native_balance','outputs/diagnostics','code','qa')) { if (-not (Test-Path -LiteralPath (Join-Path $run $keep) -PathType Container)) { throw "Required retained run directory absent: $keep" } }
    $receipt.status='completed'
    $receipt.post_delete_verified=$true
    $receipt.completed_at_utc=[DateTime]::UtcNow.ToString('o')
    $receipt.protected_file_hashes_verified=$checkedEvidence.Count + $retainedImports.Count
    $receipt.total_files_removed=($inventory | Measure-Object -Property file_count -Sum).Sum
    $receipt.total_bytes_removed=($inventory | Measure-Object -Property total_bytes -Sum).Sum
} catch {
    $receipt.status='failed_or_partial'
    $receipt.error=$_.Exception.Message
    throw
} finally {
    Write-Json $receiptPath $receipt
    Copy-Item -LiteralPath $receiptPath -Destination $retainedReceipt -Force
}
if ((Hash-File $receiptPath) -ne (Hash-File $retainedReceipt)) { throw 'Retained cleanup receipt mismatch' }
[ordered]@{status=$receipt.status; targets_removed=$deletions.Count; files_removed=$receipt.total_files_removed; bytes_removed=$receipt.total_bytes_removed; receipt=(Relative-Workspace $retainedReceipt); receipt_sha256=(Hash-File $retainedReceipt); protected_files_verified=$receipt.protected_file_hashes_verified} | ConvertTo-Json
