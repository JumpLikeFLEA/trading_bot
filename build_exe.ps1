# Trading 212 Bot - Headless Nuitka Build Script
$DEBUG = $args.Contains("--debug")

# Construct the command using an array for cleaner building
$ArgsList = @(
    "-m", "nuitka",
    "--standalone",
    "--onefile",
    "--follow-imports",
    "--output-dir=dist",
    "--output-filename=TradingBot"
)

# Standard Data Directories
$ArgsList += "--include-data-dir=src=src"
$ArgsList += "--include-data-dir=config=config"

# --- PLUGINS ---
$ArgsList += "--enable-plugin=numpy"
$ArgsList += "--enable-plugin=anti-bloat"

if ($DEBUG) {
    Write-Host "Building in DEBUG mode (Console enabled)..." -ForegroundColor Yellow
} else {
    Write-Host "Building in RELEASE mode (Console enabled for Headless monitoring)..." -ForegroundColor Green
    # Headless bot usually needs a console to show output/logs
    # So we don't use --windows-disable-console
}

# Entry Point
$ArgsList += "main.py"

Write-Host "Executing Headless Nuitka build..." -ForegroundColor Cyan
python @ArgsList
