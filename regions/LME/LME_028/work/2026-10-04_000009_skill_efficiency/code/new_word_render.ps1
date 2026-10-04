param([string]$Run)
$ErrorActionPreference = 'Stop'
$logPath = Join-Path $Run 'qa/new_word_trial.json'
$audit = Get-Content -LiteralPath $logPath -Raw -Encoding UTF8 | ConvertFrom-Json
$model = Join-Path $Run 'outputs/new_word_project/regions/LME/LME_036/papers/SCS-2007/models/36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)/model_validation'
$renderDir = Join-Path $Run 'qa/new_word_render'
New-Item -ItemType Directory -Path $renderDir -Force | Out-Null
$beforeIds = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$started = [DateTime]::UtcNow.ToString('o')
$clock = [Diagnostics.Stopwatch]::StartNew()
$word = $null
$ownedId = $null
$doc = $null
$ownedInstance = $false
$exports = @()
$errorText = $null
$tempDir = Join-Path ([IO.Path]::GetTempPath()) ('new_word_trial_' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir | Out-Null
try {
    $word = New-Object -ComObject Word.Application
    $newIds = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id } | Where-Object { $beforeIds -notcontains $_ })
    if ($newIds.Count -ne 1) { throw 'Renderer did not establish exactly one newly created Word process; no unidentified instance may be quit.' }
    $ownedId = [int]$newIds[0]
    $ownedInstance = $true
    @{stage='owned_instance'; before_pids=$beforeIds; owned_pid=$ownedId; temp_dir=$tempDir} | ConvertTo-Json -Compress
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $word.ScreenUpdating = $false
    $word.Options.UpdateLinksAtOpen = $false
    $word.Options.SaveNormalPrompt = $false
    $sources = @(
      @{name='before'; path=(Join-Path $Run 'qa/new_word_before_validation.docx')},
      @{name='final'; path=(Join-Path $model 'validation.docx')}
    )
    foreach ($source in $sources) {
        $exportClock = [Diagnostics.Stopwatch]::StartNew()
        $inputPath = Join-Path $tempDir ($source.name + '.docx')
        Copy-Item -LiteralPath $source.path -Destination $inputPath
        $pdfPath = Join-Path $tempDir ($source.name + '.pdf')
        @{stage='opening_read_only'; input=$inputPath} | ConvertTo-Json -Compress
        $doc = $word.Documents.Open($inputPath, $false, $true, $false)
        @{stage='exporting'; output=$pdfPath} | ConvertTo-Json -Compress
        $doc.ExportAsFixedFormat($pdfPath, 17)
        $pageCount = $doc.ComputeStatistics(2)
        $doc.Close(0)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)
        $doc = $null
        Copy-Item -LiteralPath $pdfPath -Destination (Join-Path $renderDir ($source.name + '.pdf'))
        $exportClock.Stop()
        $exports += @{source=$inputPath; pdf=$pdfPath; pages=$pageCount; elapsed_seconds=$exportClock.Elapsed.TotalSeconds; read_only=$true; save=$false}
    }
} catch {
    $errorText = $_.Exception.ToString()
} finally {
    if ($doc -ne $null) {
        $doc.Close(0)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)
    }
    if (($word -ne $null) -and $ownedInstance) {
        try {
            $word.Quit(0)
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
        } catch { if (!$errorText) { $errorText = $_.Exception.ToString() } }
    }
    $clock.Stop()
    $afterIds = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $op = @{operation='independent_hidden_Word_COM_render'; started_utc=$started; completed_utc=[DateTime]::UtcNow.ToString('o'); elapsed_seconds=$clock.Elapsed.TotalSeconds; before_pids=$beforeIds; owned_pid=$ownedId; after_pids=$afterIds; exports=$exports; render_calls=$exports.Count; alerts=0; macro_security=3; error=$errorText; reused_environment_knowledge=$true}
    $audit.operations += $op
    $audit | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $logPath -Encoding UTF8
    $op | ConvertTo-Json -Depth 10
    foreach ($temporaryFile in @('before.docx','final.docx','before.pdf','final.pdf')) {
        $temporaryPath = Join-Path $tempDir $temporaryFile
        if (Test-Path -LiteralPath $temporaryPath) { Remove-Item -LiteralPath $temporaryPath }
    }
    [IO.Directory]::Delete($tempDir, $false)
}
if ($errorText) { exit 1 }
