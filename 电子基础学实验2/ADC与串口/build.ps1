[CmdletBinding()]
param(
    [string]$Uv4 = $env:KEIL_UV4
)

$ErrorActionPreference = 'Stop'
if (-not $Uv4) {
    $installed = Get-Command UV4.exe -ErrorAction SilentlyContinue
    if ($installed) {
        $Uv4 = $installed.Source
    } else {
        $Uv4 = 'C:\Keil_v5\UV4\UV4.exe'
    }
}

if (-not (Test-Path -LiteralPath $Uv4 -PathType Leaf)) {
    throw 'UV4.exe was not found. Pass -Uv4 or set KEIL_UV4 to the path to UV4.exe.'
}

$uv4Path = (Resolve-Path -LiteralPath $Uv4).Path
$mdk = Join-Path $PSScriptRoot 'MDK-ARM'
$build = Start-Process -FilePath $uv4Path -WorkingDirectory $mdk `
    -ArgumentList @('-r', 'STM32F429_UART_ADC.uvprojx', '-j0', '-sg', '-o', 'build.log') `
    -WindowStyle Hidden -PassThru -Wait
$log = Join-Path $mdk 'build.log'
if (Test-Path -LiteralPath $log) {
    Get-Content -LiteralPath $log
}
exit $build.ExitCode
