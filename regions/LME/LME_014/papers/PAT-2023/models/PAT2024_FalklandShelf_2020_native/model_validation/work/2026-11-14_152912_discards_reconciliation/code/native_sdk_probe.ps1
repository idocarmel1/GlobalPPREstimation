$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$runDirectory = if ($env:PPR_NATIVE_RUN) {$env:PPR_NATIVE_RUN} else {Split-Path -Parent $PSScriptRoot}
$qaDirectory = Join-Path $runDirectory 'qa/source'
$outputDirectory = Join-Path $runDirectory 'outputs/source'
$modelDirectory = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $runDirectory))
$paperDirectory = Split-Path -Parent (Split-Path -Parent $modelDirectory)
$nativeSource = (Get-ChildItem -LiteralPath (Join-Path $paperDirectory 'sources') -Filter '*.eweaccdb').FullName
$nativeCopy = Join-Path $qaDirectory 'native_sdk_probe.eweaccdb'
$installDirectory = 'C:/Program Files/Ecopath with Ecosim 40 years 6.7.0.18865_64-bit'
$assemblyPath = Join-Path $installDirectory 'EwECore.dll'
$hashBefore = (Get-FileHash -LiteralPath $nativeSource -Algorithm SHA256).Hash.ToLowerInvariant()
[System.IO.File]::Copy($nativeSource, $nativeCopy, $true)

function Read-ScalarProperties($value) {
    $answer = [ordered]@{}
    foreach ($property in $value.GetType().GetProperties()) {
        if ($property.GetIndexParameters().Count -ne 0) { continue }
        if ($property.PropertyType.IsPrimitive -or $property.PropertyType.IsEnum -or $property.PropertyType -eq [string]) {
            try {
                $v = $property.GetValue($value, $null)
                if ($v -is [single]) {$v=[double]$v}
                if ($property.PropertyType.IsEnum) {$v=[string]$v}
                $answer[$property.Name] = $v
            } catch { $answer[$property.Name] = [ordered]@{unavailable=$_.Exception.Message} }
        }
    }
    return $answer
}

function Read-Groups($core) {
    $answer = [ordered]@{}
    foreach ($sequence in @(14,25,27,28,32,35,36)) {
        $inputGroup = $core.get_EcopathGroupInputs($sequence)
        $outputGroup = $core.get_EcopathGroupOutputs($sequence)
        $answer[[string]$sequence] = [ordered]@{input=(Read-ScalarProperties $inputGroup);output=(Read-ScalarProperties $outputGroup)}
    }
    return $answer
}

function Read-FlowArrays($data) {
    $answer = [ordered]@{}
    foreach ($field in $data.GetType().GetFields()) {
        if ($field.Name -notmatch '^(Ex|BA|B|QB|EE|DetEaten|DetPassedOn|DetPassedProp|FlowToDet|InputToDet|Discard|DiscardFate|PropDiscard|PropDiscardMort|fCatch|DC|det)$') {continue}
        $value = $field.GetValue($data)
        if ($value -is [Array]) {
            $dimensions = @(for ($d=0;$d -lt $value.Rank;$d++) {$value.GetLength($d)})
            $flat = [System.Collections.Generic.List[object]]::new()
            foreach ($item in $value) {if ($item -is [single]) {$flat.Add([double]$item)} else {$flat.Add($item)}}
            $answer[$field.Name] = [ordered]@{dimensions=$dimensions;flat_values=$flat.ToArray();orientation='CLR row-major flattening; retain native 0-based array slots and source group index mapping'}
        }
    }
    return $answer
}

$result = [ordered]@{
    source_sha256_before=$hashBefore
    native_source=$nativeSource
    isolated_copy=$nativeCopy
    installed_directory=$installDirectory
    assembly_sha256=(Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256).Hash.ToLowerInvariant()
    assembly_file_version=[Diagnostics.FileVersionInfo]::GetVersionInfo($assemblyPath).FileVersion
    original_saved_version='6.6.8.18072'
    native_engine_run_performed=$false
    normalization_requested=$false
    save_called=$false
    warnings_capture='Core scalar status flags and thrown exceptions; publisher message collection inspected separately if available.'
}
$core = $null
try {
    $assembly = [Reflection.Assembly]::LoadFrom($assemblyPath)
    $core = New-Object EwECore.cCore
    # These are indexed .NET properties in installed EwE 6.7. DefaultOutputPath
    # is getter-only; OutputPath is the ordinary writable path property.
    $result.autosave = [ordered]@{}
    foreach ($component in [Enum]::GetValues([EwEUtils.Core.eAutosaveTypes])) {
        if ([int]$component -eq 0) {continue} # NotSet is not a component.
        $core.set_Autosave($component, $false)
        $core.set_CustomAutosaveFolder($component, $qaDirectory)
        $result.autosave[[string]$component] = $core.get_Autosave($component)
    }
    $core.OutputPath = $qaDirectory
    $result.core_version = $result.assembly_file_version
    $result.output_path = $core.OutputPath
    $result.loaded = $core.LoadModel($nativeCopy)
    if (-not $result.loaded) { throw 'Native API LoadModel returned false.' }
    $result.group_count = $core.nGroups
    $result.model_name = $core.Name
    $result.before_run_groups = Read-Groups $core
    $result.run_return = $core.RunEcopath()
    $result.native_engine_run_performed = $true
    $result.is_model_balanced = $core.IsModelBalanced()
    $result.after_run_groups = Read-Groups $core
    $result.after_run_flow_arrays = Read-FlowArrays $core.EcopathDataStructures
    $result.messages_public_properties = @($core.Messages.GetType().GetProperties() | ForEach-Object ToString)
    $result.messages_public_methods = @($core.Messages.GetType().GetMethods() | Where-Object { -not $_.IsSpecialName -and $_.DeclaringType -eq $core.Messages.GetType() } | ForEach-Object ToString)
    $result.ecopath_data_public_fields = @($core.EcopathDataStructures.GetType().GetFields() | ForEach-Object ToString)
} catch {
    $result.failure = $_.Exception.ToString()
} finally {
    if ($null -ne $core) { try {$core.Dispose()} catch {$result.dispose_failure=$_.Exception.Message} }
    $result.source_sha256_after=(Get-FileHash -LiteralPath $nativeSource -Algorithm SHA256).Hash.ToLowerInvariant()
    $result.source_unchanged=($hashBefore -eq $result.source_sha256_after)
    try { $result.isolated_copy_sha256_after=(Get-FileHash -LiteralPath $nativeCopy -Algorithm SHA256).Hash.ToLowerInvariant() }
    catch { $result.isolated_copy_hash_unavailable=$_.Exception.Message }
    $json = $result | ConvertTo-Json -Depth 30
    [IO.File]::WriteAllText((Join-Path $outputDirectory 'native_sdk_probe.json'), $json, [Text.UTF8Encoding]::new($false))
    [ordered]@{loaded=$result.loaded;native_engine_run_performed=$result.native_engine_run_performed;run_return=$result.run_return;is_model_balanced=$result.is_model_balanced;source_unchanged=$result.source_unchanged;failure=$result.failure} | ConvertTo-Json -Depth 4
}
