# Script to load Pokemon RDF data into Blazegraph
Write-Host "=== Pokemon Data Loader ===" -ForegroundColor Cyan
Write-Host ""

# Check if Blazegraph is running
Write-Host "Checking if Blazegraph is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9999/bigdata/" -Method GET -TimeoutSec 5 -UseBasicParsing
    Write-Host "Blazegraph is running" -ForegroundColor Green
} catch {
    Write-Host "Blazegraph is not running!" -ForegroundColor Red
    Write-Host "Please start Blazegraph first: docker-compose up -d blazegraph" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Define RDF files to load
$files = @(
    "Recommender\data\pokemon_simple.ttl",
    "Recommender\data\pokemon_abilities_aligned.ttl",
    "Recommender\data\pokemon_evolution_links.ttl",
    "Recommender\data\pokemon_type_effectiveness_aligned.ttl"
)

# Load each file
$success = 0
$failed = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Loading $file..." -ForegroundColor Yellow
        try {
            $result = curl.exe -X POST `
                -H "Content-Type: application/x-turtle" `
                --data-binary "@$file" `
                "http://localhost:9999/bigdata/namespace/kb/sparql" 2>&1
            
            Write-Host "Loaded $file" -ForegroundColor Green
            $success++
        } catch {
            Write-Host "Failed to load $file" -ForegroundColor Red
            Write-Host "Error: $_" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "File not found: $file" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "=== Loading Summary ===" -ForegroundColor Cyan
Write-Host "Successfully loaded: $success files" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed files" -ForegroundColor Red
}

# Query to check data
Write-Host ""
Write-Host "Checking loaded data..." -ForegroundColor Yellow
try {
    $query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
    $encodedQuery = [System.Web.HttpUtility]::UrlEncode($query)
    $checkUrl = "http://localhost:9999/bigdata/namespace/kb/sparql?query=$encodedQuery"
    
    $result = Invoke-RestMethod -Uri $checkUrl -Method GET
    Write-Host "Total triples in database: $($result.results.bindings[0].count.value)" -ForegroundColor Green
} catch {
    Write-Host "Could not verify data count" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Data loading complete! You can now start the full application:" -ForegroundColor Green
Write-Host "docker-compose up" -ForegroundColor Cyan
