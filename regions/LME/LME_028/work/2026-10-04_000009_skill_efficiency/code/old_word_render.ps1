$ErrorActionPreference = 'Stop'
$trialRoot = Split-Path -Parent $PSScriptRoot
$isolatedRoot = Join-Path $trialRoot 'outputs/old_word_project'
$reportRoot = Join-Path $isolatedRoot 'regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/model_validation'
$qaRoot = Join-Path $reportRoot 'work/2026-10-04_000009_old_word_trial/qa'
$renderRoot = Join-Path $env:TEMP ('codex-old-word-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $renderRoot | Out-Null
$beforeIds = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$wordApp = $null
$ownedInstance = $false
$renderRecords = @()
$startUtc = [DateTime]::UtcNow.ToString('o')
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class WordOwnerPid { [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId); }'
try {
    $wordApp = New-Object -ComObject Word.Application
    $newIds = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object { $beforeIds -notcontains $_.Id } | ForEach-Object { $_.Id })
    if ($newIds.Count -ne 1) { throw 'Word COM creation did not establish one independent new process; no document opened.' }
    [uint32]$createdPid = $newIds[0]
    $ownedInstance = $true
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordApp.ScreenUpdating = $false
    $wordApp.Options.UpdateLinksAtOpen = $false
    $wordApp.Options.SaveNormalPrompt = $false
    $targets = @(
        @{ label = 'before'; path = (Join-Path $qaRoot 'before.docx') },
        @{ label = 'after'; path = (Join-Path $reportRoot 'validation.docx') }
    )
    foreach ($target in $targets) {
        $copyPath = Join-Path $renderRoot ($target.label + '.docx')
        $pdfPath = Join-Path $renderRoot ($target.label + '.pdf')
        Copy-Item -LiteralPath $target.path -Destination $copyPath
        $docObj = $null
        try {
            $docObj = $wordApp.Documents.Open($copyPath, $false, $true, $false)
            $docObj.ExportAsFixedFormat($pdfPath, 17)
            $renderRecords += @{ label = $target.label; pdf = $pdfPath; read_only = $true; bytes = (Get-Item -LiteralPath $pdfPath).Length; source = $target.path }
        } finally {
            if ($null -ne $docObj) { $docObj.Close(0); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($docObj) }
        }
    }
} finally {
    if ($null -ne $wordApp) {
        if ($ownedInstance) { $wordApp.Quit(0) }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp)
    }
}
$remainingBefore = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object { $beforeIds -contains $_.Id } | ForEach-Object { $_.Id })
$record = @{ start_utc = $startUtc; end_utc = [DateTime]::UtcNow.ToString('o'); created_word_process_id = $createdPid; prior_word_process_ids = $beforeIds; surviving_prior_word_process_ids = $remainingBefore; independent_hidden_instance = $ownedInstance; documents = $renderRecords; temp_root = $renderRoot; word_exports = $renderRecords.Count }
$record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $trialRoot 'qa/old_word_fallback_render.json') -Encoding utf8
$record | ConvertTo-Json -Depth 10
