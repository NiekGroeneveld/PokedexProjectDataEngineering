# Quick Start Script for Pokemon Application
# This script will set up and run the entire application

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Pokemon Application - Quick Start" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Docker
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
    Write-Host "[OK] Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed or not running!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Step 2: Stop any existing containers
Write-Host ""
Write-Host "[2/5] Cleaning up old containers..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "[OK] Cleanup complete" -ForegroundColor Green

# Step 3: Start Blazegraph
Write-Host ""
Write-Host "[3/5] Starting Blazegraph database..." -ForegroundColor Yellow
docker-compose up -d blazegraph

Write-Host "Waiting for Blazegraph to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if Blazegraph is ready
$retries = 0
$maxRetries = 10
$blazegraphReady = $false

while ($retries -lt $maxRetries -and -not $blazegraphReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9999/bigdata/" -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        $blazegraphReady = $true
        Write-Host "[OK] Blazegraph is ready" -ForegroundColor Green
    } catch {
        $retries++
        Write-Host "Waiting... (attempt $retries/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

if (-not $blazegraphReady) {
    Write-Host "[ERROR] Blazegraph failed to start" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs blazegraph" -ForegroundColor Yellow
    exit 1
}

# Step 4: Load Pokemon data
Write-Host ""
Write-Host "[4/5] Loading Pokemon data..." -ForegroundColor Yellow

$files = @(
    "Recommender\data\pokemon_simple.ttl",
    "Recommender\data\pokemon_abilities_aligned.ttl",
    "Recommender\data\pokemon_evolution_links.ttl",
    "Recommender\data\pokemon_type_effectiveness_aligned.ttl"
)

$loadedCount = 0
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  Loading $(Split-Path $file -Leaf)..." -ForegroundColor Gray
        try {
            $result = curl.exe -X POST -H "Content-Type: application/x-turtle" --data-binary "@$file" "http://localhost:9999/bigdata/namespace/kb/sparql" 2>&1
            $loadedCount++
        } catch {
            Write-Host "  Warning: Could not load $file" -ForegroundColor Yellow
        }
    }
}

Write-Host "[OK] Loaded $loadedCount/$($files.Count) data files" -ForegroundColor Green

# Step 5: Start all services
Write-Host ""
Write-Host "[5/5] Starting backend and frontend..." -ForegroundColor Yellow
docker-compose up -d --build

Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verify services
Write-Host ""
Write-Host "=== Service Status ===" -ForegroundColor Cyan

# Check backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Backend API: http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Backend API not responding" -ForegroundColor Red
}

# Check frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost/" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Frontend: http://localhost" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Frontend not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Application Ready! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Access your Pokemon application at:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:5000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:5000/docs" -ForegroundColor White
Write-Host "  Blazegraph:   http://localhost:9999/bigdata" -ForegroundColor White
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "To stop:      docker-compose down" -ForegroundColor Yellow
Write-Host ""
