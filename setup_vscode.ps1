# VS Code Profile Configuration for ERPOS
# This script configures a dedicated "ERPOS" profile in VS Code with recommended extensions and launches the editor.

$extensions = @(
    "ms-python.python",              # Python language support
    "ms-dotnettools.csdevkit"        # C# Dev Kit (for .NET Aspire orchestration)
)

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Configuring VS Code Profile: ERPOS" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Initialize the profile by opening the workspace once
Write-Host "Initializing ERPOS profile..." -ForegroundColor Yellow
code --profile ERPOS .
Start-Sleep -Seconds 5

# Install extensions to the profile
foreach ($ext in $extensions) {
    Write-Host "Installing extension: $ext..." -ForegroundColor Yellow
    code --profile ERPOS --install-extension $ext
}

Write-Host "`nAll extensions configured! Launching VS Code with ERPOS profile..." -ForegroundColor Green
code --profile ERPOS .

