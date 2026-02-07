# --- CONFIGURATION ---
$ScriptPath = Join-Path (Get-Location) "git-dashboard-windows.py"
$BinDir = Join-Path $HOME ".local/bin"
$BinLink = Join-Path $BinDir "repos.ps1"

Write-Host "--- Starting Git Repo Dashboard Setup (Windows) ---" -ForegroundColor Cyan

# 1. Create Bin Directory if it doesn't exist
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir | Out-Null
}

# 2. Check Dependencies (Python & Tkinter)
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install it from python.org or the Microsoft Store."
    exit
}
pip install python-dotenv --quiet

# 3. Create a wrapper script (since Windows doesn't do 'ln -s' for scripts easily)
# Using 'pythonw' instead of 'python' prevents a black console window from staying open
$WrapperContent = "Start-Process pythonw -ArgumentList `"$ScriptPath`" -WindowStyle Hidden"
Set-Content -Path $BinLink -Value $WrapperContent

# 4. Add to PowerShell Profile (Equivalent to .zshrc)
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}

# Define the function for the profile
$FuncCmd = "`nfunction repos { & `"$BinLink`" }"

# Clean up old versions and add the new function
$ProfileContent = Get-Content $PROFILE
$NewContent = $ProfileContent | Where-Object { $_ -notmatch 'function repos' }
$NewContent + $FuncCmd | Set-Content $PROFILE

Write-Host "✔ Configuration updated in $PROFILE" -ForegroundColor Green
Write-Host "------------------------------------------"
Write-Host "DONE! Refresh your shell to start:"
Write-Host ". `$PROFILE" -ForegroundColor Yellow
Write-Host "Then simply type 'repos' to launch."