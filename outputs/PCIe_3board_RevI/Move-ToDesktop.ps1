[CmdletBinding()]
param(
    [string]$Source = 'C:\Users\micro\Documents\ChatGPT\pcie switch 2',
    [string]$DestinationRoot = 'C:\Users\micro\Desktop\方案'
)
$ErrorActionPreference = 'Stop'
# Run after closing KiCad files and this project's active terminal sessions.
$sourceResolved = (Resolve-Path -LiteralPath $Source).Path.TrimEnd('\')
$expectedSource = 'C:\Users\micro\Documents\ChatGPT\pcie switch 2'
if ($sourceResolved -ine $expectedSource) { throw 'Unexpected source: refusing to move another directory.' }
$destinationResolved = [IO.Path]::GetFullPath($DestinationRoot).TrimEnd('\')
if ($destinationResolved -ine 'C:\Users\micro\Desktop\方案') { throw 'Unexpected destination root.' }
$target = [IO.Path]::GetFullPath((Join-Path $destinationResolved 'pcie switch 2'))
if (-not $target.StartsWith($destinationResolved + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target escapes destination root.' }
if (Test-Path -LiteralPath $target) { throw "Destination already exists; no files were overwritten: $target" }
if (-not (Test-Path -LiteralPath (Join-Path $sourceResolved 'outputs\PCIe_3board_RevI\BUILD.json'))) { throw 'Expected Rev I project is missing.' }
if (-not (Test-Path -LiteralPath $destinationResolved)) { New-Item -ItemType Directory -Path $destinationResolved | Out-Null }
$ignorePath = Join-Path $destinationResolved '.gitignore'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$ignoreText = if (Test-Path -LiteralPath $ignorePath) { [IO.File]::ReadAllText($ignorePath) } else { '' }
$rule = '/pcie switch 2/'
$newIgnoreText = $ignoreText
if (($ignoreText -split '\r?\n') -notcontains $rule) { $newIgnoreText = $ignoreText.TrimEnd() + "`r`n`r`n# Local KiCad E1.S / vertical M.2 layout project`r`n$rule`r`n" }
# Validate exact absolute paths above; use PowerShell end-to-end for the directory move.
Set-Location -LiteralPath $destinationResolved
Move-Item -LiteralPath $sourceResolved -Destination $target
if (-not (Test-Path -LiteralPath (Join-Path $target 'outputs\PCIe_3board_RevI\BUILD.json'))) { throw 'Move verification failed; inspect paths before proceeding.' }
if ($newIgnoreText -ne $ignoreText) {
    if (Test-Path -LiteralPath $ignorePath) { Copy-Item -LiteralPath $ignorePath -Destination ($ignorePath + '.' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.bak') }
    [IO.File]::WriteAllText($ignorePath,$newIgnoreText,$utf8)
}
Write-Output "Moved project to $target"
Write-Output "Updated $ignorePath"
