# Kill all Python processes to release file locks
Write-Host "Stopping all Python processes..." -ForegroundColor Yellow

Get-Process | Where-Object {$_.ProcessName -like "*python*"} | ForEach-Object {
    Write-Host "Killing process $($_.Id) - $($_.ProcessName)" -ForegroundColor Red
    Stop-Process -Id $_.Id -Force
}

Write-Host "`nAll Python processes stopped. HDF5 file locks should be released." -ForegroundColor Green
Write-Host "You can now restart the server with: python backend/run_server.py" -ForegroundColor Cyan
