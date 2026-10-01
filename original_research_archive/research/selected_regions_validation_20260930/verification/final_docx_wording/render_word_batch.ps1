$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../../../'))
$taskProof = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'patch_proof.json') -Raw | ConvertFrom-Json
$taskHelper = Join-Path $taskRoot 'regions/LME_038/validation_reports/38_38003_Java_Sea_normalized_BA_completed_(mid1970s)/reproduction/render_word.ps1'
$taskHelperSha = (Get-FileHash -LiteralPath $taskHelper -Algorithm SHA256).Hash.ToLower()
$taskLog = Join-Path $PSScriptRoot 'native_word_render.log'
"Renderer retained helper: $taskHelper`nHelper SHA256: $taskHelperSha`nRead-only exports; a separate owned hidden Word instance for each export." | Set-Content -LiteralPath $taskLog -Encoding UTF8
foreach ($taskFile in $taskProof.files) {
    foreach ($taskPhase in @('before','after')) {
        $taskOut = Join-Path $PSScriptRoot ("render/$($taskFile.unit)/$taskPhase")
        [void](New-Item -ItemType Directory -Path $taskOut -Force)
        $taskInput = if ($taskPhase -eq 'before') { Join-Path $PSScriptRoot "before/$($taskFile.unit).docx" } else { Join-Path $taskRoot $taskFile.path }
        $taskExpected = if ($taskPhase -eq 'before') { $taskFile.before_sha256 } else { $taskFile.after_sha256 }
        if ((Get-FileHash -LiteralPath $taskInput -Algorithm SHA256).Hash.ToLower() -ne $taskExpected) { throw "Hash mismatch before render: $taskInput" }
        $taskPdf = Join-Path $taskOut 'report.pdf'
        "START $($taskFile.unit) $taskPhase" | Tee-Object -FilePath $taskLog -Append
        & $taskHelper -InputDocx $taskInput -OutputPdf $taskPdf | Tee-Object -FilePath $taskLog -Append
        if ((Get-FileHash -LiteralPath $taskInput -Algorithm SHA256).Hash.ToLower() -ne $taskExpected) { throw "Read-only render changed DOCX: $taskInput" }
        if (-not (Test-Path -LiteralPath $taskPdf)) { throw "No PDF: $taskPdf" }
        "END $($taskFile.unit) $taskPhase PDF bytes $((Get-Item -LiteralPath $taskPdf).Length) DOCX SHA unchanged" | Tee-Object -FilePath $taskLog -Append
    }
}
