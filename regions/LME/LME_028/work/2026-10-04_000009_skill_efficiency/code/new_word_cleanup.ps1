param([string]$Run)
$ErrorActionPreference = 'Stop'
$logPath = Join-Path $Run 'qa/new_word_trial.json'
$audit = Get-Content -LiteralPath $logPath -Raw -Encoding UTF8 | ConvertFrom-Json
$failed = @($audit.operations | Where-Object { $_.operation -eq 'independent_hidden_Word_COM_render' -and $_.render_calls -eq 0 })[-1]
$newIds = @($failed.after_pids | Where-Object { $failed.before_pids -notcontains $_ })
if (($newIds.Count -ne 1) -or ($newIds[0] -ne 17616) -or ($failed.exports.Count -ne 0)) { throw 'Own orphan identity has not been proven.' }
$before = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$orphan = Get-Process -Id 17616 -ErrorAction Stop
if ($orphan.ProcessName -ne 'WINWORD') { throw 'Own orphan PID no longer identifies Word.' }
Stop-Process -Id 17616 -ErrorAction Stop
$after = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
$audit.operations += @{operation='cleanup_proven_own_failed_renderer_orphan'; utc=[DateTime]::UtcNow.ToString('o'); owned_orphan_pid=17616; before_pids=$before; after_pids=$after; basis='Exactly one new PID in the failed before/after log; no document opened; original COM binding exited'; prior_sessions_untouched=(@($before | Where-Object { $_ -ne 17616 -and $after -notcontains $_ }).Count -eq 0)}
$audit | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $logPath -Encoding UTF8
$audit.operations[-1] | ConvertTo-Json -Depth 10
