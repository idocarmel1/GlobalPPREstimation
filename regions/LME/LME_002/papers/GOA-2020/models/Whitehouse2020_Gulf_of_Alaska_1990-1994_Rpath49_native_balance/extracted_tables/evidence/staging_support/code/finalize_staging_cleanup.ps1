$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$workspace = (Resolve-Path -LiteralPath '.').Path.TrimEnd('\')
$runRelative = 'regions/LME/LME_002/work/2026-11-14_191000_native_balance_diagnostics'
$run = (Resolve-Path -LiteralPath (Join-Path $workspace $runRelative)).Path.TrimEnd('\')
$variantRelative = 'regions/LME/LME_002/papers/GOA-2020/models/Whitehouse2020_Gulf_of_Alaska_1990-1994_Rpath49_native_balance'
$variant = (Resolve-Path -LiteralPath (Join-Path $workspace $variantRelative)).Path
$evidence = Join-Path $variant 'extracted_tables/evidence'
$native = Join-Path $evidence 'native_reproduction'
$manifestPath = Join-Path $native 'native_manifest.json'
$receiptPath = Join-Path $run 'cleanup_receipt.json'
$retainedReceipt = Join-Path $evidence 'cleanup_receipt.json'
$allowed = @('outputs/native_balance','outputs/diagnostics','code','qa')
function Hash-File([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Relative-Workspace([string]$Path) { [IO.Path]::GetRelativePath($workspace,$Path).Replace('\','/') }
function Relative-Evidence([string]$Path) { [IO.Path]::GetRelativePath($evidence,$Path).Replace('\','/') }
function Write-Json([string]$Path,$Value) { [IO.File]::WriteAllText($Path,($Value | ConvertTo-Json -Depth 30)+"`n",[Text.UTF8Encoding]::new($false)) }
function Assert-InRun([string]$Path) {
    $full=[IO.Path]::GetFullPath($Path)
    if (-not $full.StartsWith($run+'\',[StringComparison]::OrdinalIgnoreCase) -or -not $full.StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Out-of-scope target: $full" }
    return $full
}
function Safe-Tree([string]$Path) {
    $full=(Resolve-Path -LiteralPath $Path).Path
    [void](Assert-InRun $full)
    $cursor=$full
    while ($true) {
        $item=Get-Item -LiteralPath $cursor -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse ancestor rejected: $cursor" }
        if ($cursor.Equals($workspace,[StringComparison]::OrdinalIgnoreCase)) { break }
        $cursor=[IO.Path]::GetDirectoryName($cursor)
        if ($cursor.Length -lt $workspace.Length) { throw 'Ancestor walk escaped workspace' }
    }
    $stack=[Collections.Generic.Stack[string]]::new()
    $items=[Collections.Generic.List[object]]::new()
    $stack.Push($full)
    while ($stack.Count -gt 0) {
        $item=Get-Item -LiteralPath $stack.Pop() -Force
        [void](Assert-InRun $item.FullName)
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse target rejected: $($item.FullName)" }
        $items.Add($item)
        if ($item.PSIsContainer) { foreach ($child in Get-ChildItem -LiteralPath $item.FullName -Force) { $stack.Push($child.FullName) } }
    }
    return $items.ToArray()
}
function Save-Receipt {
    Write-Json $receiptPath $script:receipt
    Copy-Item -LiteralPath $receiptPath -Destination $retainedReceipt -Force
    if ((Hash-File $receiptPath) -ne (Hash-File $retainedReceipt)) { throw 'Final cleanup receipt copy mismatch' }
}

if (-not $run.Equals((Join-Path $workspace $runRelative).Replace('/','\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected run resolution' }
if (Test-Path -LiteralPath $receiptPath) { throw 'Final cleanup receipt already exists; inspect before any rerun' }
$manifestHash=Hash-File $manifestPath
$manifest=Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json -AsHashtable
foreach ($entry in @($manifest.files)+@($manifest.source_references)) {
    if ((Hash-File ([IO.Path]::GetFullPath((Join-Path $native $entry.path)))) -ne $entry.sha256) { throw "Native evidence/source mismatch: $($entry.path)" }
}
$previousReceipt=Join-Path $native 'verification/cleanup_receipt.json'
$previous=Get-Content -LiteralPath $previousReceipt -Raw | ConvertFrom-Json -AsHashtable
if ($previous.status -ne 'completed' -or -not $previous.post_delete_verified) { throw 'Earlier dependency cleanup incomplete' }
$priorHash=Hash-File $previousReceipt
$existingHashes=@{}
foreach ($file in Get-ChildItem -LiteralPath $variant -Recurse -File -Force) {
    if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Reparse file cannot count as retained canonical evidence' }
    $hash=Hash-File $file.FullName
    if (-not $existingHashes.ContainsKey($hash)) { $existingHashes[$hash]=[Collections.Generic.List[string]]::new() }
    $existingHashes[$hash].Add($file.FullName)
}
$dispositions=[Collections.Generic.List[object]]::new()
$targets=[Collections.Generic.List[object]]::new()
$newCopies=0
$totalFiles=[long]0
$totalBytes=[long]0
foreach ($relative in $allowed) {
    $target=Assert-InRun (Join-Path $run $relative)
    $items=@(Safe-Tree $target)
    $files=@($items | Where-Object { -not $_.PSIsContainer } | Sort-Object FullName)
    $bytes=[long]0
    foreach ($file in $files) {
        $hash=Hash-File $file.FullName
        $within=[IO.Path]::GetRelativePath($target,$file.FullName).Replace('\','/')
        $retention='existing_exact_copy'
        if ($relative -eq 'outputs/native_balance') {
            $matches=@($manifest.files | Where-Object { $_.role -eq 'native_output' -and $_.path -eq $within })
            if ($matches.Count -ne 1 -or $matches[0].sha256 -ne $hash) { throw "Native output not in retained manifest: $within" }
            $destination=Join-Path $native $within
        } elseif ($relative -eq 'outputs/diagnostics') {
            $destination=Join-Path $variant ('results/diagnostics/'+$within)
        } else {
            if ($existingHashes.ContainsKey($hash)) {
                $destination=($existingHashes[$hash] | Sort-Object | Select-Object -First 1)
            } else {
                $destination=Join-Path $evidence ('staging_support/'+$relative+'/'+$within)
                if (Test-Path -LiteralPath $destination) { throw "Nonidentical retention destination already exists: $destination" }
                [void](New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force)
                Copy-Item -LiteralPath $file.FullName -Destination $destination
                $retention='newly_retained_exact_copy'
                $newCopies++
                $existingHashes[$hash]=[Collections.Generic.List[string]]::new()
                $existingHashes[$hash].Add($destination)
            }
        }
        if ((Hash-File $destination) -ne $hash) { throw "Retained counterpart mismatch: $($file.FullName)" }
        $dispositions.Add([ordered]@{source_path=(Relative-Workspace $file.FullName); source_absolute_path=$file.FullName; retained_path=(Relative-Workspace $destination); retained_evidence_relative_path=(Relative-Evidence $destination); sha256=$hash; bytes=$file.Length; disposition=$retention; target=$relative})
        $bytes += [long]$file.Length
    }
    $targets.Add([ordered]@{run_relative_path=$relative; absolute_path=$target; file_count=$files.Count; directory_count=@($items | Where-Object PSIsContainer).Count; total_bytes=$bytes})
    $totalFiles += [long]$files.Count
    $totalBytes += $bytes
    Write-Output "Retained and verified $relative ($($files.Count) files)"
}
if (@($dispositions | Where-Object { $_.target -eq 'outputs/native_balance' }).Count -ne 25) { throw 'Expected exactly 25 work native outputs' }
$script:receipt=[ordered]@{schema_version=1; stage='final_staging_cleanup'; authorization='Coordinator confirmed first evidence-index pass complete and explicitly authorized bounded staging retention and cleanup.'; run_id=(Split-Path $run -Leaf); started_at_utc=[DateTime]::UtcNow.ToString('o'); status='prepared'; prior_cleanup=[ordered]@{path=(Relative-Workspace $previousReceipt); evidence_relative_path=(Relative-Evidence $previousReceipt); sha256=$priorHash; files_removed=$previous.total_files_removed; bytes_removed=$previous.total_bytes_removed}; native_manifest=[ordered]@{path=(Relative-Workspace $manifestPath); sha256=$manifestHash}; executed_script=[ordered]@{path=(Relative-Workspace $PSCommandPath); sha256=(Hash-File $PSCommandPath)}; targets=$targets.ToArray(); file_dispositions=$dispositions.ToArray(); newly_retained_files=$newCopies; total_staging_files=$totalFiles; total_staging_bytes=$totalBytes; removed=@(); empty_container_cleanup=@(); post_delete_verified=$false; protected_inputs_changed=$false}
Save-Receipt
$removed=[Collections.Generic.List[object]]::new()
try {
    foreach ($targetRecord in $targets) {
        $target=Assert-InRun $targetRecord.absolute_path
        $items=@(Safe-Tree $target)
        if (@($items | Where-Object { -not $_.PSIsContainer }).Count -ne $targetRecord.file_count) { throw "Staging target changed: $target" }
        foreach ($entry in $dispositions | Where-Object { $_.target -eq $targetRecord.run_relative_path }) {
            if ((Hash-File $entry.source_absolute_path) -ne $entry.sha256 -or (Hash-File (Join-Path $workspace $entry.retained_path)) -ne $entry.sha256) { throw 'Staging or retained bytes changed after inventory' }
        }
        Remove-Item -LiteralPath $target -Recurse -Force
        if (Test-Path -LiteralPath $target) { throw "Staging target remained: $target" }
        $removed.Add([ordered]@{path=$targetRecord.run_relative_path; absent_after=$true; file_count=$targetRecord.file_count; bytes=$targetRecord.total_bytes; removed_at_utc=[DateTime]::UtcNow.ToString('o')})
        $receipt.removed=$removed.ToArray()
        $receipt.status='in_progress'
        Save-Receipt
        Write-Output "Removed $($targetRecord.run_relative_path)"
    }
    $emptyRemoved=[Collections.Generic.List[string]]::new()
    foreach ($emptyName in @('outputs','inputs')) {
        $empty=Assert-InRun (Join-Path $run $emptyName)
        if (Test-Path -LiteralPath $empty) {
            $items=@(Safe-Tree $empty)
            if ($items.Count -ne 1 -or -not $items[0].PSIsContainer) { throw "Expected empty staging container: $emptyName" }
            Remove-Item -LiteralPath $empty -Force
            if (Test-Path -LiteralPath $empty) { throw 'Empty staging container remained' }
            $emptyRemoved.Add($emptyName)
        }
    }
    foreach ($entry in $dispositions) { if ((Hash-File (Join-Path $workspace $entry.retained_path)) -ne $entry.sha256) { throw 'Post-cleanup retained counterpart mismatch' } }
    foreach ($entry in @($manifest.files)+@($manifest.source_references)) { if ((Hash-File ([IO.Path]::GetFullPath((Join-Path $native $entry.path)))) -ne $entry.sha256) { throw 'Post-cleanup native/source mismatch' } }
    if ((Hash-File $manifestPath) -ne $manifestHash -or (Hash-File $previousReceipt) -ne $priorHash) { throw 'Historical receipt or manifest changed' }
    $notesRelative=[IO.Path]::GetRelativePath($run,(Join-Path $variant 'model_notes.md')).Replace('\','/')
    $evidenceRelative=[IO.Path]::GetRelativePath($run,$evidence).Replace('\','/')
    $readme="# Completed LME_002 native balance and diagnostics run`n`nResults and limitations: [model notes]($notesRelative). Reproduction, verification and source evidence: [retained model evidence]($evidenceRelative/).`n`nTask staging and downloaded runtime dependencies were removed after exact-byte retention checks. [Cleanup receipt](cleanup_receipt.json) records every final staging file disposition and links the earlier dependency-cleanup inventory. No scientific computation was rerun during cleanup.`n"
    [IO.File]::WriteAllText((Join-Path $run 'README.md'),$readme,[Text.UTF8Encoding]::new($false))
    $receipt.empty_container_cleanup=$emptyRemoved.ToArray()
    $receipt.status='completed'
    $receipt.post_delete_verified=$true
    $receipt.completed_at_utc=[DateTime]::UtcNow.ToString('o')
    $receipt.retained_file_dispositions_verified=$dispositions.Count
    $receipt.historical_native_and_source_references_verified=$manifest.files.Count+$manifest.source_references.Count
    $receipt.run_readme=[ordered]@{path=(Relative-Workspace (Join-Path $run 'README.md')); sha256=(Hash-File (Join-Path $run 'README.md'))}
} catch {
    $receipt.status='failed_or_partial'
    $receipt.error=$_.Exception.Message
    throw
} finally { Save-Receipt }
$remaining=@(Get-ChildItem -LiteralPath $run -Force | Select-Object -ExpandProperty Name | Sort-Object)
if (($remaining -join '|') -ne 'cleanup_receipt.json|README.md') { throw 'Unexpected final run contents' }
[ordered]@{status=$receipt.status; files_retained_and_removed=$totalFiles; bytes_removed=$totalBytes; newly_retained_files=$newCopies; receipt=(Relative-Workspace $retainedReceipt); receipt_sha256=(Hash-File $retainedReceipt); remaining_run_files=$remaining} | ConvertTo-Json
