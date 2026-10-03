param([Parameter(Mandatory=$true)][int]$CliRootPid, [int]$MaxSeconds = 150)
$started = [Diagnostics.Stopwatch]::StartNew()
while ($started.Elapsed.TotalSeconds -lt $MaxSeconds) {
    $taskProcesses = @(Get-CimInstance Win32_Process -Property ProcessId,ParentProcessId,Name | Select-Object ProcessId,ParentProcessId,Name)
    $descendants = [Collections.Generic.HashSet[int]]::new()
    [void]$descendants.Add($CliRootPid)
    do {
        $changed = $false
        foreach ($row in $taskProcesses) {
            if ($descendants.Contains([int]$row.ParentProcessId) -and $descendants.Add([int]$row.ProcessId)) { $changed = $true }
        }
    } while ($changed)
    $rootAlive = @($taskProcesses | Where-Object ProcessId -eq $CliRootPid).Count -gt 0
    $childCount = @($taskProcesses | Where-Object { $_.ProcessId -ne $CliRootPid -and $descendants.Contains([int]$_.ProcessId) }).Count
    [ordered]@{ elapsed_ms = [Math]::Round($started.Elapsed.TotalMilliseconds); root_alive = $rootAlive; descendant_count = $childCount } | ConvertTo-Json -Compress
    if (-not $rootAlive) { break }
    Start-Sleep -Milliseconds 1000
}
