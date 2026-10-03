param([Parameter(Mandatory=$true)][string]$Destination)
# Preparation only. Does not invoke Claude or submit an issue.
python -m runners.prepare_fixture $Destination
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
