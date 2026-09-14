param(
    [ValidateSet('global', 'eez')][string]$Scope = 'global',
    [switch]$SummaryOnly,
    [switch]$RegionsOnly
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
$nodePath = Join-Path $runtimeRoot 'bin/node.exe'
$packages = Join-Path $runtimeRoot 'node_modules'
if (!(Test-Path -LiteralPath $nodePath) -or !(Test-Path -LiteralPath (Join-Path $packages '@oai/artifact-tool'))) {
    throw 'The Codex bundled spreadsheet runtime is unavailable. Load workspace dependencies in Codex first.'
}
$scratch = Join-Path $projectRoot '.superpowers/workbook-runtime'
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
$junction = Join-Path $scratch 'node_modules'
if (!(Test-Path -LiteralPath $junction)) {
    New-Item -ItemType Junction -Path $junction -Target $packages | Out-Null
}
$loader = Join-Path $scratch 'loader.mjs'
@'
import {registerHooks,createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const artifactUrl=pathToFileURL(createRequire(import.meta.url).resolve('@oai/artifact-tool')).href;
registerHooks({resolve(specifier,context,next){return next(specifier==='@oai/artifact-tool'?artifactUrl:specifier,context)}});
'@ | Set-Content -LiteralPath $loader -Encoding utf8
$exportArguments = @("--scope-label=$Scope", "--output-directory=${Scope}_output")
if ($SummaryOnly) { $exportArguments += '--summary-only' }
if ($RegionsOnly) { $exportArguments += '--regions-only' }
$loaderUri = ([System.Uri]::new($loader)).AbsoluteUri
& $nodePath --import $loaderUri (Join-Path $projectRoot 'SeaAroundUsExtraction/tools/build_workbooks.mjs') @exportArguments
exit $LASTEXITCODE
